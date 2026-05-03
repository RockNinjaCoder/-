from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.core.db.connection import get_db

router = APIRouter()


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "新会话"


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    is_active: int


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None


@router.post("", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    title = request.title or "新会话"

    conn = await get_db()
    await conn.execute(
        "INSERT INTO sessions (id, title, created_at, updated_at, is_active) VALUES (?, ?, ?, ?, ?)",
        (session_id, title, now, now, 1)
    )
    await conn.commit()

    return SessionResponse(
        id=session_id,
        title=title,
        created_at=now,
        updated_at=now,
        is_active=1
    )


@router.get("", response_model=list[SessionResponse])
async def list_sessions():
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, title, created_at, updated_at, is_active FROM sessions ORDER BY updated_at DESC"
    )
    rows = await cursor.fetchall()

    return [
        SessionResponse(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            is_active=row["is_active"]
        )
        for row in rows
    ]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, title, created_at, updated_at, is_active FROM sessions WHERE id = ?",
        (session_id,)
    )
    row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        is_active=row["is_active"]
    )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: UpdateSessionRequest):
    now = datetime.now().isoformat()

    conn = await get_db()
    if request.title is not None:
        await conn.execute(
            "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
            (request.title, now, session_id)
        )
    else:
        await conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?",
            (now, session_id)
        )
    await conn.commit()

    cursor = await conn.execute(
        "SELECT id, title, created_at, updated_at, is_active FROM sessions WHERE id = ?",
        (session_id,)
    )
    row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        is_active=row["is_active"]
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    conn = await get_db()
    cursor = await conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
    row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    await conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    await conn.commit()

    return {"message": "Session deleted successfully"}