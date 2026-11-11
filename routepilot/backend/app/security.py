"""Authentication helpers. Configure AUTH_JWT_SECRET and bootstrap admin via secrets."""
from datetime import datetime, timedelta, timezone
import os
import sqlite3
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_hasher = PasswordHasher()
_bearer = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"
ISSUER = os.getenv("AUTH_ISSUER", "routepilot-api")
AUDIENCE = os.getenv("AUTH_AUDIENCE", "routepilot-api")


def secret() -> str:
    value = os.getenv("AUTH_JWT_SECRET", "")
    if len(value.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_JWT_SECRET must contain at least 32 bytes")
    return value


def initialize_auth(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, organization_id TEXT NOT NULL,
        email TEXT NOT NULL, password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','manager','agent','dispatcher','driver','viewer')),
        active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL,
        UNIQUE(organization_id,email),
        FOREIGN KEY(organization_id) REFERENCES organizations(id))""")
    org_name = os.getenv("BOOTSTRAP_ORG_NAME", "").strip()
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
    if bool(org_name or email or password) and not (org_name and email and password):
        raise RuntimeError("Set all BOOTSTRAP_ORG_NAME, BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD")
    if org_name:
        if len(password) < 14:
            raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must be at least 14 characters")
        org = connection.execute("SELECT id FROM organizations WHERE name=?", (org_name,)).fetchone()
        org_id = org["id"] if org else str(uuid4())
        if not org:
            connection.execute("INSERT INTO organizations VALUES(?,?,?)",
                               (org_id, org_name, datetime.now(timezone.utc).isoformat()))
        user = connection.execute("SELECT id FROM users WHERE organization_id=? AND email=?",
                                  (org_id, email)).fetchone()
        if not user:
            connection.execute(
                "INSERT INTO users(id,organization_id,email,password_hash,role,active,created_at) VALUES(?,?,?,?,?,1,?)",
                (str(uuid4()), org_id, email, _hasher.hash(password), "admin",
                 datetime.now(timezone.utc).isoformat()))


def authenticate(connection: sqlite3.Connection, email: str, password: str):
    row = connection.execute(
        "SELECT id,organization_id,email,password_hash,role,active FROM users WHERE email=?",
        (email.strip().lower(),)).fetchone()
    if not row:
        # Perform a dummy hash verification to reduce account-enumeration timing differences.
        try:
            _hasher.verify(_hasher.hash("dummy-password-value"), password)
        except Exception:
            pass
        return None
    if not row["active"]:
        return None
    try:
        _hasher.verify(row["password_hash"], password)
    except (VerifyMismatchError, VerificationError):
        return None
    return dict(row)


def issue_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": user["id"], "org_id": user["organization_id"],
        "iss": ISSUER, "aud": AUDIENCE, "iat": now,
        "exp": now + timedelta(minutes=30)}, secret(), algorithm=ALGORITHM)


def verify_token(token: str):
    return jwt.decode(token, secret(), algorithms=[ALGORITHM], issuer=ISSUER,
        audience=AUDIENCE, options={"require": ["sub","org_id","exp","iat"]})


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = verify_token(credentials.credentials)
    except (jwt.InvalidTokenError, RuntimeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token",
                            headers={"WWW-Authenticate": "Bearer"})
    # Re-read user state from the DB on every request so deactivation takes effect immediately.
    db_path = os.getenv("ROUTEPILOT_DB", "")
    if not db_path:
        raise HTTPException(status_code=503, detail="Authentication database is not configured")
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT id, organization_id, email, role, active FROM users WHERE id=?",
            (claims["sub"],)).fetchone()
    if not row or not row["active"] or row["organization_id"] != claims["org_id"]:
        raise HTTPException(status_code=401, detail="User is inactive or no longer valid")
    return dict(row)


def require_roles(*roles):
    def dependency(user=Depends(current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency


def create_password_hash(password: str) -> str:
    if len(password) < 14:
        raise ValueError("Password must be at least 14 characters")
    return _hasher.hash(password)
