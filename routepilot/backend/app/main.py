from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import os
import psycopg
from app.database import connect as open_database, is_postgres
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.security import initialize_auth, authenticate, issue_token, require_roles

DB = Path(os.getenv("ROUTEPILOT_DB", str(Path(__file__).resolve().parent.parent / "routepilot.db")))
DB.parent.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="RoutePilot API", version="1.0.0", description="Fleet, GPS telemetry, delivery and proof-of-delivery API")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("ROUTEPILOT_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
if "*" in CORS_ORIGINS:
    raise RuntimeError("ROUTEPILOT_CORS_ORIGINS must list explicit origins; wildcard CORS is not allowed")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

def connect():
    return open_database(DB)

def init_db():
    if is_postgres():
        # PostgreSQL schema is managed exclusively by Alembic migrations.
        return
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS vehicles(id TEXT PRIMARY KEY, label TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'idle');
        CREATE TABLE IF NOT EXISTS positions(id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, recorded_at TEXT NOT NULL, FOREIGN KEY(vehicle_id) REFERENCES vehicles(id));
        CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY, recipient TEXT NOT NULL, address TEXT NOT NULL, route_id TEXT NOT NULL, vehicle_id TEXT, status TEXT NOT NULL DEFAULT 'scheduled', eta TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS proofs(id INTEGER PRIMARY KEY AUTOINCREMENT, delivery_id TEXT NOT NULL, recipient_name TEXT NOT NULL, method TEXT NOT NULL, note TEXT DEFAULT '', captured_at TEXT NOT NULL, FOREIGN KEY(delivery_id) REFERENCES deliveries(id));
        """)
        initialize_auth(c)
        for table in ("vehicles", "positions", "deliveries", "proofs"):
            columns = {row["name"] for row in c.execute("PRAGMA table_info(" + table + ")")}
            if "organization_id" not in columns:
                c.execute("ALTER TABLE " + table + " ADD COLUMN organization_id TEXT")
        orgs = c.execute("SELECT id FROM organizations ORDER BY created_at").fetchall()
        if len(orgs) == 1:
            org_id = orgs[0]["id"]
            for table in ("vehicles", "positions", "deliveries", "proofs"):
                c.execute("UPDATE " + table + " SET organization_id=? WHERE organization_id IS NULL", (org_id,))
            if c.execute("SELECT COUNT(*) FROM vehicles WHERE organization_id=?", (org_id,)).fetchone()[0] == 0:
                c.executemany("INSERT INTO vehicles(id,label,status,organization_id) VALUES(?,?,?,?)",
                    [("VAN-12","Van 12","on_route",org_id),("VAN-08","Van 08","on_route",org_id),("VAN-21","Van 21","delayed",org_id)])
            if c.execute("SELECT COUNT(*) FROM deliveries WHERE organization_id=?", (org_id,)).fetchone()[0] == 0:
                now=datetime.now(timezone.utc).isoformat()
                c.executemany("INSERT INTO deliveries(id,recipient,address,route_id,vehicle_id,status,eta,created_at,organization_id) VALUES(?,?,?,?,?,?,?,?,?)", [
                ("DL-2084","Northstar Studio","Berlin Mitte","R-204","VAN-12","in_transit","2026-11-11T14:25:00+01:00",now,org_id),
                ("DL-2083","Market Hall","Berlin Kreuzberg","R-204","VAN-12","delivered","2026-11-11T13:50:00+01:00",now,org_id),
                ("DL-2082","Westend Supply","Berlin Westend","R-211","VAN-21","attention","2026-11-11T14:05:00+01:00",now,org_id)])
        for table in ("vehicles", "positions", "deliveries", "proofs"):
            c.execute("CREATE INDEX IF NOT EXISTS idx_" + table + "_organization ON " + table + "(organization_id)")
init_db()

class LoginIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)

@app.post("/auth/login")
def login(data: LoginIn):
    with connect() as c:
        user = authenticate(c, data.organization_name, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": issue_token(user), "token_type": "bearer", "expires_in": 1800}

@app.get("/auth/me")
def who_am_i(user=Depends(require_roles("admin","manager","agent","dispatcher","driver","viewer"))):
    return {"id": user["id"], "email": user["email"], "organization_id": user["organization_id"], "role": user["role"]}

class VehicleIn(BaseModel):
    label: str = Field(min_length=2, max_length=80)
    status: str = Field(default="idle", pattern="^(idle|on_route|delayed|maintenance)$")
class PositionIn(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    recorded_at: datetime | None = None
class DeliveryIn(BaseModel):
    id: str = Field(min_length=3, max_length=40, pattern="^[A-Za-z0-9_-]+$")
    recipient: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=3, max_length=240)
    route_id: str = Field(min_length=2, max_length=40)
    vehicle_id: str | None = None
    eta: str | None = None
class StatusIn(BaseModel):
    status: str = Field(pattern="^(scheduled|in_transit|delivered|attention|cancelled)$")
class ProofIn(BaseModel):
    recipient_name: str
    method: str = Field(pattern="^(signature|photo|code|manual)$")
    note: str = ""

@app.get("/health")
def health():
    # Liveness only: confirms the process is responding.
    return {"status": "ok", "service": "routepilot-api"}


@app.get("/ready")
def readiness():
    # Readiness verifies that the configured persistent database is reachable.
    try:
        with connect() as c:
            c.execute("SELECT 1").fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready", "service": "routepilot-api", "database": "postgresql" if is_postgres() else "sqlite"}

@app.get("/vehicles")
def vehicles(user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        rows=c.execute("""SELECT v.*,p.latitude,p.longitude,p.recorded_at FROM vehicles v
            LEFT JOIN positions p ON p.id=(SELECT MAX(id) FROM positions WHERE vehicle_id=v.id AND organization_id=?)
            WHERE v.organization_id=? ORDER BY v.id""",(org,org)).fetchall()
    return [dict(r) for r in rows]

@app.post("/vehicles", status_code=201)
def create_vehicle(data: VehicleIn, user=Depends(require_roles("admin","dispatcher"))):
    org=user["organization_id"]; vehicle_id=data.label.upper().replace(" ","-")
    with connect() as c:
        try: c.execute("INSERT INTO vehicles(id,label,status,organization_id) VALUES(?,?,?,?)",(vehicle_id,data.label,data.status,org))
        except (sqlite3.IntegrityError, psycopg.IntegrityError): raise HTTPException(409,"Vehicle already exists")
    return {"id":vehicle_id,"label":data.label,"status":data.status}

@app.post("/vehicles/{vehicle_id}/positions", status_code=201)
def record_position(vehicle_id: str, data: PositionIn, user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]; stamp=(data.recorded_at or datetime.now(timezone.utc)).isoformat()
    with connect() as c:
        if not c.execute("SELECT 1 FROM vehicles WHERE id=? AND organization_id=?",(vehicle_id,org)).fetchone(): raise HTTPException(404,"Vehicle not found")
        cur=c.execute("INSERT INTO positions(vehicle_id,latitude,longitude,recorded_at,organization_id) VALUES(?,?,?,?,?)",(vehicle_id,data.latitude,data.longitude,stamp,org))
    return {"id":cur.lastrowid,"vehicle_id":vehicle_id,"latitude":data.latitude,"longitude":data.longitude,"recorded_at":stamp}

@app.get("/vehicles/{vehicle_id}/positions")
def position_history(vehicle_id: str, limit: int = Query(default=100, ge=1, le=1000), user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        if not c.execute("SELECT 1 FROM vehicles WHERE id=? AND organization_id=?", (vehicle_id,org)).fetchone(): raise HTTPException(404,"Vehicle not found")
        rows=c.execute("SELECT id,vehicle_id,latitude,longitude,recorded_at FROM positions WHERE vehicle_id=? AND organization_id=? ORDER BY id DESC LIMIT ?",(vehicle_id,org,limit)).fetchall()
    return [dict(row) for row in rows]

@app.get("/deliveries/{delivery_id}/proofs")
def delivery_proofs(delivery_id: str, user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        if not c.execute("SELECT 1 FROM deliveries WHERE id=? AND organization_id=?", (delivery_id,org)).fetchone(): raise HTTPException(404,"Delivery not found")
        rows=c.execute("SELECT * FROM proofs WHERE delivery_id=? AND organization_id=? ORDER BY id DESC",(delivery_id,org)).fetchall()
    return [dict(row) for row in rows]

@app.get("/deliveries")
def deliveries(status: str | None = Query(default=None), user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        sql="SELECT d.*, (SELECT COUNT(*) FROM proofs p WHERE p.delivery_id=d.id AND p.organization_id=d.organization_id) AS proof_count FROM deliveries d WHERE d.organization_id=?"
        params=[org]
        if status: sql+=" AND d.status=?"; params.append(status)
        rows=c.execute(sql+" ORDER BY d.created_at DESC",params).fetchall()
    return [dict(r) for r in rows]

@app.post("/deliveries", status_code=201)
def create_delivery(data: DeliveryIn, user=Depends(require_roles("admin","dispatcher"))):
    org=user["organization_id"]
    with connect() as c:
        if data.vehicle_id and not c.execute("SELECT 1 FROM vehicles WHERE id=? AND organization_id=?",(data.vehicle_id,org)).fetchone(): raise HTTPException(422,"Unknown vehicle_id")
        try: c.execute("INSERT INTO deliveries(id,recipient,address,route_id,vehicle_id,status,eta,created_at,organization_id) VALUES(?,?,?,?,?,'scheduled',?,?,?)",(data.id,data.recipient,data.address,data.route_id,data.vehicle_id,data.eta,datetime.now(timezone.utc).isoformat(),org))
        except sqlite3.IntegrityError: raise HTTPException(409,"Delivery ID already exists")
    return {"id":data.id,"status":"scheduled"}

@app.patch("/deliveries/{delivery_id}/status")
def update_delivery(delivery_id: str, data: StatusIn, user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        if not c.execute("SELECT 1 FROM deliveries WHERE id=? AND organization_id=?",(delivery_id,org)).fetchone(): raise HTTPException(404,"Delivery not found")
        if data.status=="delivered" and not c.execute("SELECT 1 FROM proofs WHERE delivery_id=? AND organization_id=?",(delivery_id,org)).fetchone(): raise HTTPException(409,"Record proof of delivery before marking it delivered")
        c.execute("UPDATE deliveries SET status=? WHERE id=? AND organization_id=?",(data.status,delivery_id,org))
    return {"id":delivery_id,"status":data.status}

@app.post("/deliveries/{delivery_id}/proof", status_code=201)
def add_proof(delivery_id: str, data: ProofIn, user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        if not c.execute("SELECT 1 FROM deliveries WHERE id=? AND organization_id=?",(delivery_id,org)).fetchone(): raise HTTPException(404,"Delivery not found")
        cur=c.execute("INSERT INTO proofs(delivery_id,recipient_name,method,note,captured_at,organization_id) VALUES(?,?,?,?,?,?)",(delivery_id,data.recipient_name,data.method,data.note,datetime.now(timezone.utc).isoformat(),org))
        c.execute("UPDATE deliveries SET status='delivered' WHERE id=? AND organization_id=?",(delivery_id,org))
        row=c.execute("SELECT * FROM proofs WHERE id=? AND organization_id=?",(cur.lastrowid,org)).fetchone()
    return dict(row)

@app.get("/deliveries/{delivery_id}/note")
def delivery_note(delivery_id: str, user=Depends(require_roles("admin","dispatcher","driver"))):
    org=user["organization_id"]
    with connect() as c:
        d=c.execute("SELECT * FROM deliveries WHERE id=? AND organization_id=?",(delivery_id,org)).fetchone()
        p=c.execute("SELECT * FROM proofs WHERE delivery_id=? AND organization_id=? ORDER BY id DESC LIMIT 1",(delivery_id,org)).fetchone()
    if not d: raise HTTPException(404,"Delivery not found")
    return {"document_type":"delivery_note_preview","legal_validity":False,"delivery":dict(d),"proof":dict(p) if p else None,"message":"Preview only; configure jurisdiction-specific fields and signing before legal use."}