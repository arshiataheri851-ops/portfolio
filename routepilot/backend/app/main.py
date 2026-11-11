from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB = Path(__file__).resolve().parent.parent / "routepilot.db"
app = FastAPI(title="RoutePilot API", version="1.0.0", description="Fleet, GPS telemetry, delivery and proof-of-delivery API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles(id TEXT PRIMARY KEY, label TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'idle');
        CREATE TABLE IF NOT EXISTS positions(id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, recorded_at TEXT NOT NULL, FOREIGN KEY(vehicle_id) REFERENCES vehicles(id));
        CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY, recipient TEXT NOT NULL, address TEXT NOT NULL, route_id TEXT NOT NULL, vehicle_id TEXT, status TEXT NOT NULL DEFAULT 'scheduled', eta TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS proofs(id INTEGER PRIMARY KEY AUTOINCREMENT, delivery_id TEXT NOT NULL, recipient_name TEXT NOT NULL, method TEXT NOT NULL, note TEXT DEFAULT '', captured_at TEXT NOT NULL, FOREIGN KEY(delivery_id) REFERENCES deliveries(id));
        """)
        if c.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0] == 0:
            c.executemany("INSERT INTO vehicles(id,label,status) VALUES(?,?,?)", [("VAN-12","Van 12","on_route"),("VAN-08","Van 08","on_route"),("VAN-21","Van 21","delayed")])
        if c.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0] == 0:
            now=datetime.now(timezone.utc).isoformat()
            c.executemany("INSERT INTO deliveries(id,recipient,address,route_id,vehicle_id,status,eta,created_at) VALUES(?,?,?,?,?,?,?,?)", [
            ("DL-2084","Northstar Studio","Berlin Mitte","R-204","VAN-12","in_transit","2026-11-11T14:25:00+01:00",now),
            ("DL-2083","Market Hall","Berlin Kreuzberg","R-204","VAN-12","delivered","2026-11-11T13:50:00+01:00",now),
            ("DL-2082","Westend Supply","Berlin Westend","R-211","VAN-21","attention","2026-11-11T14:05:00+01:00",now)])
init_db()

class VehicleIn(BaseModel):
    label: str
    status: str = "idle"
class PositionIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    recorded_at: datetime | None = None
class DeliveryIn(BaseModel):
    id: str
    recipient: str
    address: str
    route_id: str
    vehicle_id: str | None = None
    eta: str | None = None
class StatusIn(BaseModel):
    status: str
class ProofIn(BaseModel):
    recipient_name: str
    method: str = Field(pattern="^(signature|photo|code|manual)$")
    note: str = ""

@app.get("/health")
def health():
    return {"status":"ok","service":"routepilot-api","database":"sqlite"}

@app.get("/vehicles")
def vehicles():
    with connect() as c:
        rows=c.execute("""SELECT v.*, p.latitude,p.longitude,p.recorded_at FROM vehicles v LEFT JOIN positions p ON p.id=(SELECT MAX(id) FROM positions WHERE vehicle_id=v.id) ORDER BY v.id""").fetchall()
        return [dict(r) for r in rows]

@app.post("/vehicles", status_code=201)
def create_vehicle(data: VehicleIn):
    with connect() as c:
        try: c.execute("INSERT INTO vehicles(id,label,status) VALUES(?,?,?)",(data.label.upper().replace(" ","-"),data.label,data.status))
        except sqlite3.IntegrityError: raise HTTPException(409,"Vehicle already exists")
    return {"id":data.label.upper().replace(" ","-"),"label":data.label,"status":data.status}

@app.post("/vehicles/{vehicle_id}/positions", status_code=201)
def record_position(vehicle_id: str, data: PositionIn):
    stamp=(data.recorded_at or datetime.now(timezone.utc)).isoformat()
    with connect() as c:
        if not c.execute("SELECT 1 FROM vehicles WHERE id=?",(vehicle_id,)).fetchone(): raise HTTPException(404,"Vehicle not found")
        cur=c.execute("INSERT INTO positions(vehicle_id,latitude,longitude,recorded_at) VALUES(?,?,?,?)",(vehicle_id,data.latitude,data.longitude,stamp))
    return {"id":cur.lastrowid,"vehicle_id":vehicle_id,"latitude":data.latitude,"longitude":data.longitude,"recorded_at":stamp}

@app.get("/deliveries")
def deliveries(status: str | None = Query(default=None)):
    with connect() as c:
        sql="SELECT d.*, (SELECT COUNT(*) FROM proofs p WHERE p.delivery_id=d.id) AS proof_count FROM deliveries d"
        rows=c.execute(sql+" WHERE status=? ORDER BY created_at DESC" if status else sql+" ORDER BY created_at DESC",(status,) if status else ()).fetchall()
        return [dict(r) for r in rows]

@app.post("/deliveries", status_code=201)
def create_delivery(data: DeliveryIn):
    with connect() as c:
        try: c.execute("INSERT INTO deliveries VALUES(?,?,?,?,?,'scheduled',?,?)",(data.id,data.recipient,data.address,data.route_id,data.vehicle_id,data.eta,datetime.now(timezone.utc).isoformat()))
        except sqlite3.IntegrityError: raise HTTPException(409,"Delivery ID already exists")
    return {"id":data.id,"status":"scheduled"}

@app.patch("/deliveries/{delivery_id}/status")
def update_delivery(delivery_id: str, data: StatusIn):
    if data.status not in {"scheduled","in_transit","delivered","attention","cancelled"}: raise HTTPException(422,"Unsupported status")
    with connect() as c:
        cur=c.execute("UPDATE deliveries SET status=? WHERE id=?",(data.status,delivery_id))
        if not cur.rowcount: raise HTTPException(404,"Delivery not found")
    return {"id":delivery_id,"status":data.status}

@app.post("/deliveries/{delivery_id}/proof", status_code=201)
def add_proof(delivery_id: str, data: ProofIn):
    with connect() as c:
        if not c.execute("SELECT 1 FROM deliveries WHERE id=?",(delivery_id,)).fetchone(): raise HTTPException(404,"Delivery not found")
        cur=c.execute("INSERT INTO proofs(delivery_id,recipient_name,method,note,captured_at) VALUES(?,?,?,?,?)",(delivery_id,data.recipient_name,data.method,data.note,datetime.now(timezone.utc).isoformat()))
        c.execute("UPDATE deliveries SET status='delivered' WHERE id=?",(delivery_id,))
        row=c.execute("SELECT * FROM proofs WHERE id=?",(cur.lastrowid,)).fetchone()
    return dict(row)

@app.get("/deliveries/{delivery_id}/note")
def delivery_note(delivery_id: str):
    with connect() as c:
        d=c.execute("SELECT * FROM deliveries WHERE id=?",(delivery_id,)).fetchone()
        p=c.execute("SELECT * FROM proofs WHERE delivery_id=? ORDER BY id DESC LIMIT 1",(delivery_id,)).fetchone()
    if not d: raise HTTPException(404,"Delivery not found")
    return {"document_type":"delivery_note_preview","legal_validity":False,"delivery":dict(d),"proof":dict(p) if p else None,"message":"Preview only; configure jurisdiction-specific fields and signing before legal use."}
