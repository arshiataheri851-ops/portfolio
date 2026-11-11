"""SQLite/PostgreSQL connection adapter for the existing qmark-based SQL layer."""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path


def is_postgres() -> bool:
    return os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgresql+psycopg://"))


class Cursor:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def rowcount(self):
        return self._cursor.rowcount


class PostgresConnection:
    is_postgres = True

    def __init__(self, url: str):
        import psycopg
        from psycopg.rows import dict_row
        self._connection = psycopg.connect(url.replace("postgresql+psycopg://", "postgresql://"), row_factory=dict_row)

    def execute(self, sql, params=()):
        statement = sql
        lastrowid = None
        match = re.match(r"\s*INSERT\s+INTO\s+(positions|proofs|ticket_events)\b", statement, re.I)
        if match and " RETURNING " not in statement.upper():
            statement = statement.rstrip().rstrip(";") + " RETURNING id"
        cursor = self._connection.execute(statement.replace("?", "%s"), tuple(params or ()))
        if match:
            row = cursor.fetchone()
            lastrowid = row["id"] if row else None
            # The insert callers only use lastrowid; no result row is expected.
        return Cursor(cursor, lastrowid)

    def executemany(self, sql, rows):
        return self._connection.cursor().executemany(sql.replace("?", "%s"), rows)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()


def connect(database_path: str | Path):
    if is_postgres():
        return PostgresConnection(os.environ["DATABASE_URL"])
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection
