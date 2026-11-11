from datetime import datetime, timezone, timedelta
from pathlib import Path
import sqlite3
import os
import psycopg
from app.database import connect as open_database, is_postgres
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.security import initialize_auth, authenticate, issue_token, require_roles

DB=Path(os.getenv("SIGNALDESK_DB",str(Path(__file__).resolve().parent.parent/"signaldesk.db")))
DB.parent.mkdir(parents=True,exist_ok=True)
app=FastAPI(title="SignalDesk API",version="1.0.0",description="Persistent service request intake, assignment and SLA triage API")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("SIGNALDESK_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
if "*" in CORS_ORIGINS:
    raise RuntimeError("SIGNALDESK_CORS_ORIGINS must list explicit origins; wildcard CORS is not allowed")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
def db():
    return open_database(DB)

def init():
    if is_postgres():
        # Alembic owns the schema; this step only provisions the configured bootstrap admin.
        with db() as c:
            initialize_auth(c)
        return
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tickets(id TEXT PRIMARY KEY,title TEXT NOT NULL,queue TEXT NOT NULL,account_tier TEXT NOT NULL,priority TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'open',assignee TEXT,created_at TEXT NOT NULL,due_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS ticket_events(id INTEGER PRIMARY KEY AUTOINCREMENT,ticket_id TEXT NOT NULL,event_type TEXT NOT NULL,actor TEXT NOT NULL,details TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(ticket_id) REFERENCES tickets(id))""")
        initialize_auth(c)
        for table in ("tickets", "ticket_events"):
            columns = {row["name"] for row in c.execute("PRAGMA table_info(" + table + ")")}
            if "organization_id" not in columns:
                c.execute("ALTER TABLE " + table + " ADD COLUMN organization_id TEXT")
        orgs=c.execute("SELECT id FROM organizations ORDER BY created_at").fetchall()
        if len(orgs)==1:
            org_id=orgs[0]["id"]
            for table in ("tickets","ticket_events"):
                c.execute("UPDATE " + table + " SET organization_id=? WHERE organization_id IS NULL",(org_id,))
            if c.execute("SELECT COUNT(*) FROM tickets WHERE organization_id=?",(org_id,)).fetchone()[0]==0:
                now=datetime.now(timezone.utc)
                rows=[
                ("SD-1048","Payment confirmation delayed","Checkout","Enterprise","High","open",None,now.isoformat(),(now+timedelta(minutes=12)).isoformat(),org_id),
                ("SD-1047","Update billing contact details","Billing","Standard","Medium","open",None,now.isoformat(),(now+timedelta(hours=3)).isoformat(),org_id),
                ("SD-1046","Webhook events not received","Integrations","Enterprise","High","open",None,now.isoformat(),(now+timedelta(minutes=8)).isoformat(),org_id),
                ("SD-1045","Export monthly usage report","Reporting","Standard","Low","open",None,now.isoformat(),(now+timedelta(days=1)).isoformat(),org_id),
                ("SD-1044","Invite link expired","Accounts","Growth","Medium","open",None,now.isoformat(),(now+timedelta(minutes=24)).isoformat(),org_id)]
                c.executemany("INSERT INTO tickets(id,title,queue,account_tier,priority,status,assignee,created_at,due_at,organization_id) VALUES(?,?,?,?,?,?,?,?,?,?)",rows)
        for table in ("tickets","ticket_events"):
            c.execute("CREATE INDEX IF NOT EXISTS idx_" + table + "_organization ON " + table + "(organization_id)")
init()

class LoginIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)

@app.post("/auth/login")
def login(data: LoginIn):
    with db() as c:
        user = authenticate(c, data.organization_name, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": issue_token(user), "token_type": "bearer", "expires_in": 1800}

@app.get("/auth/me")
def who_am_i(user=Depends(require_roles("admin","manager","agent","dispatcher","driver","viewer"))):
    return {"id": user["id"], "email": user["email"], "organization_id": user["organization_id"], "role": user["role"]}

class TicketIn(BaseModel):
    id:str=Field(min_length=3,max_length=40,pattern="^[A-Za-z0-9_-]+$")
    title:str=Field(min_length=3,max_length=200)
    queue:str=Field(min_length=2,max_length=80)
    account_tier:str=Field(default="Standard",pattern="^(Standard|Growth|Enterprise)$")
    priority:str=Field(default="Medium",pattern="^(Low|Medium|High)$")
    due_at:datetime
class AssignmentIn(BaseModel):
    assignee:str=Field(min_length=1,max_length=100)
class StatusIn(BaseModel):
    status:str

def serialize(row):
    item=dict(row)
    due=datetime.fromisoformat(item["due_at"])
    if due.tzinfo is None: due=due.replace(tzinfo=timezone.utc)
    seconds=(due-datetime.now(timezone.utc)).total_seconds()
    item["seconds_to_sla"]=int(seconds)
    item["sla_state"]="at_risk" if seconds<=1800 and item["status"]!="resolved" else "safe"
    weights={"High":3,"Medium":2,"Low":1}
    item["priority_score"]=weights.get(item["priority"],1)*25+(40 if seconds<=1800 else 0)+(15 if item["account_tier"]=="Enterprise" else 0)
    return item

@app.get("/health")
def health():
    # Liveness only: confirms the process is responding.
    return {"status": "ok", "service": "signaldesk-api"}


@app.get("/ready")
def readiness():
    # Readiness verifies that the configured persistent database is reachable.
    try:
        with db() as c:
            c.execute("SELECT 1").fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready", "service": "signaldesk-api", "database": "postgresql" if is_postgres() else "sqlite"}

@app.get("/tickets")
def list_tickets(status:str|None=Query(None),queue:str|None=Query(None),priority:str|None=Query(None),sla_state:str|None=Query(None),q:str|None=Query(None),user=Depends(require_roles("admin","manager","agent","viewer"))):
    org=user["organization_id"]; clauses=["organization_id=?"]; values=[org]
    for key,value in (("status",status),("queue",queue),("priority",priority)):
        if value: clauses.append(key+"=?"); values.append(value)
    if q: clauses.append("(id LIKE ? OR title LIKE ? OR queue LIKE ?)"); values += [f"%{q}%"]*3
    sql="SELECT * FROM tickets WHERE "+" AND ".join(clauses)
    with db() as c: rows=c.execute(sql,values).fetchall()
    items=[serialize(r) for r in rows]
    if sla_state:
        if sla_state not in {"at_risk","safe"}: raise HTTPException(422,"sla_state must be at_risk or safe")
        items=[item for item in items if item["sla_state"]==sla_state]
    return sorted(items,key=lambda x:x["priority_score"],reverse=True)

@app.post("/tickets",status_code=201)
def create_ticket(data:TicketIn,user=Depends(require_roles("admin","manager","agent"))):
    org=user["organization_id"]
    with db() as c:
        try:
            c.execute("INSERT INTO tickets(id,title,queue,account_tier,priority,status,assignee,created_at,due_at,organization_id) VALUES(?,?,?,?,?,'open',NULL,?,?,?)",(data.id,data.title,data.queue,data.account_tier,data.priority,datetime.now(timezone.utc).isoformat(),data.due_at.isoformat(),org))
        except (sqlite3.IntegrityError, psycopg.IntegrityError): raise HTTPException(409,"Ticket ID already exists")
        c.execute("INSERT INTO ticket_events(ticket_id,event_type,actor,details,created_at,organization_id) VALUES(?,?,?,?,?,?)",(data.id,"created",user["email"],"Ticket created",datetime.now(timezone.utc).isoformat(),org))
        row=c.execute("SELECT * FROM tickets WHERE id=? AND organization_id=?",(data.id,org)).fetchone()
    return serialize(row)

@app.patch("/tickets/{ticket_id}/assign")
def assign(ticket_id:str,data:AssignmentIn,user=Depends(require_roles("admin","manager","agent"))):
    org=user["organization_id"]
    with db() as c:
        ticket=c.execute("SELECT status FROM tickets WHERE id=? AND organization_id=?",(ticket_id,org)).fetchone()
        if not ticket: raise HTTPException(404,"Ticket not found")
        if ticket["status"]=="resolved": raise HTTPException(409,"Resolved tickets cannot be assigned")
        c.execute("UPDATE tickets SET assignee=? WHERE id=? AND organization_id=?",(data.assignee,ticket_id,org))
        c.execute("INSERT INTO ticket_events(ticket_id,event_type,actor,details,created_at,organization_id) VALUES(?,?,?,?,?,?)",(ticket_id,"assigned",user["email"],"Assigned to "+data.assignee,datetime.now(timezone.utc).isoformat(),org))
        return serialize(c.execute("SELECT * FROM tickets WHERE id=? AND organization_id=?",(ticket_id,org)).fetchone())

@app.patch("/tickets/{ticket_id}/status")
def set_status(ticket_id:str,data:StatusIn,user=Depends(require_roles("admin","manager","agent"))):
    if data.status not in {"open","in_progress","resolved"}: raise HTTPException(422,"Unsupported status")
    org=user["organization_id"]
    with db() as c:
        before=c.execute("SELECT status FROM tickets WHERE id=? AND organization_id=?",(ticket_id,org)).fetchone()
        if not before: raise HTTPException(404,"Ticket not found")
        c.execute("UPDATE tickets SET status=? WHERE id=? AND organization_id=?",(data.status,ticket_id,org))
        c.execute("INSERT INTO ticket_events(ticket_id,event_type,actor,details,created_at,organization_id) VALUES(?,?,?,?,?,?)",(ticket_id,"status_changed",user["email"],before["status"]+" -> "+data.status,datetime.now(timezone.utc).isoformat(),org))
        return serialize(c.execute("SELECT * FROM tickets WHERE id=? AND organization_id=?",(ticket_id,org)).fetchone())

@app.get("/tickets/{ticket_id}/events")
def ticket_events(ticket_id:str,limit:int=Query(default=100,ge=1,le=500),user=Depends(require_roles("admin","manager","agent","viewer"))):
    org=user["organization_id"]
    with db() as c:
        if not c.execute("SELECT 1 FROM tickets WHERE id=? AND organization_id=?",(ticket_id,org)).fetchone(): raise HTTPException(404,"Ticket not found")
        rows=c.execute("SELECT id,ticket_id,event_type,actor,details,created_at FROM ticket_events WHERE ticket_id=? AND organization_id=? ORDER BY id DESC LIMIT ?",(ticket_id,org,limit)).fetchall()
    return [dict(row) for row in rows]

@app.get("/analytics/summary")
def summary(user=Depends(require_roles("admin","manager","agent","viewer"))):
    org=user["organization_id"]
    with db() as c: rows=c.execute("SELECT * FROM tickets WHERE organization_id=?",(org,)).fetchall()
    items=[serialize(r) for r in rows]
    return {"total":len(items),"open":sum(x["status"]=="open" for x in items),"at_risk":sum(x["sla_state"]=="at_risk" for x in items),"resolved":sum(x["status"]=="resolved" for x in items),"by_queue":{q:sum(x["queue"]==q for x in items) for q in sorted({x["queue"] for x in items})}}
