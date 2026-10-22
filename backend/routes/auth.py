"""auth.py - Login/logout routes with SQLite session storage."""

from fastapi import APIRouter, Form
from pydantic import BaseModel
from datetime import datetime
import asyncio
import sqlite3
import uuid


router = APIRouter()

# Single shared connection with WAL mode + an asyncio lock so concurrent
# async handlers never interleave writes on the same connection.
_conn = sqlite3.connect("sessions.db", check_same_thread=False)
_conn.execute("PRAGMA journal_mode=WAL")
_conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        start_time TEXT,
        end_time TEXT
    )
""")
_conn.commit()

_db_lock = asyncio.Lock()


def init_db():
    pass  # schema is created above at module load time


init_db()


class LogoutRequest(BaseModel):
    session_id: str


@router.post("/login")
async def login(name: str = Form(...), email: str = Form(...)):
    session_id = str(uuid.uuid4())
    start_time = datetime.utcnow().isoformat()

    async with _db_lock:
        _conn.execute(
            "INSERT INTO sessions (id, name, email, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
            (session_id, name, email, start_time, None),
        )
        _conn.commit()

    return {"session_id": session_id, "start_time": start_time}


@router.post("/logout")
async def logout(request: LogoutRequest):
    end_time = datetime.utcnow().isoformat()

    async with _db_lock:
        _conn.execute(
            "UPDATE sessions SET end_time = ? WHERE id = ?",
            (end_time, request.session_id),
        )
        _conn.commit()

    return {"message": "Session ended", "end_time": end_time}
