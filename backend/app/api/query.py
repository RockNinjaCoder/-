from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
import json

from app.core.db.connection import get_db

router = APIRouter()


class QueryRequest(BaseModel):
    session_id: str
    query: str


class QueryResponse(BaseModel):
    id: str
    session_id: str
    user_query: str
    generated_sql: Optional[str]
    execution_result: Optional[str]
    status: str
    error_message: Optional[str] = None


@router.post("", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    return QueryResponse(
        id="temp-id",
        session_id=request.session_id,
        user_query=request.query,
        generated_sql=None,
        execution_result=None,
        status="pending"
    )


@router.get("/schemas")
async def get_schemas():
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, table_name, column_name, column_type, description FROM db_schemas"
    )
    rows = await cursor.fetchall()

    schemas = {}
    for row in rows:
        table_name = row["table_name"]
        if table_name not in schemas:
            schemas[table_name] = []
        schemas[table_name].append({
            "column_name": row["column_name"],
            "column_type": row["column_type"],
            "description": row["description"]
        })

    return schemas


@router.post("/schemas/register")
async def register_schema(table_name: str, columns: list[dict]):
    import uuid
    now = datetime.now().isoformat()
    conn = await get_db()

    for col in columns:
        schema_id = str(uuid.uuid4())
        await conn.execute(
            "INSERT INTO db_schemas (id, table_name, column_name, column_type, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (schema_id, table_name, col["column_name"], col.get("column_type", "TEXT"), col.get("description", ""), now)
        )

    await conn.commit()
    return {"message": "Schema registered successfully"}


from datetime import datetime