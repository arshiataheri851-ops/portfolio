"""Small, fail-closed authentication primitives for the SQLite MVP.

Production deployment must set a unique 32+ character JWT secret and bootstrap
credentials through the hosting secret store. This module does not implement
tenant-scoped business queries; those remain a separate release gate.
"""
from datetime import datetime, timedelta, timezone
import os
import sqlite3

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

_hasher = PasswordHasher()
ALGORITHM = "HS256"
ISSUER = os.getenv("AUTH_ISSUER", "signaldesk-api")
AUDIENCE = os.getenv("AUTH_AUDIENCE", "signaldesk-api-api")


def secret() -> str:
    value = os.getenv("AUTH_JWT_SECRET", "")
    if len(value.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_JWT_SECRET must contain at least 32 bytes")
    return value


def initialize_auth(connection: sqlite3.Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, organization_id TEXT NOT NULL,
            email TEXT NOT NULL, password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','manager','agent','dispatcher','driver','viewer')),
            active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL,
            UNIQUE(organization_id,email),
            FOREIGN KEY(organization_id) REFERENCES organizations(id)
        )
    """)
    # Bootstrap is explicit: no default password and no public registration.
    org_name = os.getenv("BOOTSTRAP_ORG_NAME", "").strip()
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
    if org_name and email and password:
        if len(password) < 14:
            raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must be at least 14 characters")
        from uuid import uuid4
        from datetime import datetime, timezone
        org = connection.execute("SELECT id FROM organizations WHERE name=?", (org_name,)).fetchone()
        if not org:
            org_id = str(uuid4())
            connection.execute("INSERT INTO organizations(id,name,created_at) VALUES(?,?,?)",
                               (org_id, org_name, datetime.now(timezone.utc).isoformat()))
        else:
            org_id = org[0]
        user = connection.execute("SELECT id FROM users WHERE organization_id=? AND email=?",
                                  (org_id, email)).fetchone()
        if not user:
            connection.execute(
                "INSERT INTO users(id,organization_id,email,password_hash,role,active,created_at) VALUES(?,?,?,?,1,?)",
                (str(uuid4()), org_id, email, _hasher.hash(password), "admin",
                 datetime.now(timezone.utc).isoformat())
            )


def authenticate(connection: sqlite3.Connection, email: str, password: str):
    row = connection.execute(
        "SELECT id,organization_id,email,password_hash,role,active FROM users WHERE email=?",
        (email.strip().lower(),)
    ).fetchone()
    if not row or not row["active"]:
        return None
    try:
        _hasher.verify(row["password_hash"], password)
    except (VerifyMismatchError, VerificationError):
        return None
    return dict(row)


def issue_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({
        "sub": user["id"], "org_id": user["organization_id"], "role": user["role"],
        "iss": ISSUER, "aud": AUDIENCE, "iat": now,
        "exp": now + timedelta(minutes=30),
    }, secret(), algorithm=ALGORITHM)


def verify_token(token: str):
    return jwt.decode(token, secret(), algorithms=[ALGORITHM], issuer=ISSUER,
                      audience=AUDIENCE, options={"require": ["sub","org_id","role","exp","iat"]})


def create_password_hash(password: str) -> str:
    if len(password) < 14:
        raise ValueError("Password must be at least 14 characters")
    return _hasher.hash(password)
