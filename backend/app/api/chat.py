from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.core.db.connection import get_db

router = APIRouter()


class SendMessageRequest(BaseModel):
    session_id: str
    content: str
    role: str = "user"


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str


@router.post("", response_model=MessageResponse)
async def send_message(request: SendMessageRequest):
    message_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn = await get_db()

    cursor = await conn.execute(
        "SELECT id FROM sessions WHERE id = ?", (request.session_id,)
    )
    session = await cursor.fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await conn.execute(
        "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (message_id, request.session_id, request.role, request.content, now)
    )

    await conn.execute(
        "UPDATE sessions SET updated_at = ? WHERE id = ?",
        (now, request.session_id)
    )

    await conn.commit()

    return MessageResponse(
        id=message_id,
        session_id=request.session_id,
        role=request.role,
        content=request.content,
        created_at=now
    )


@router.get("/session/{session_id}", response_model=list[MessageResponse])
async def get_messages(session_id: str, limit: int = 50, offset: int = 0):
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC LIMIT ? OFFSET ?",
        (session_id, limit, offset)
    )
    rows = await cursor.fetchall()

    return [
        MessageResponse(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"]
        )
        for row in rows
    ]