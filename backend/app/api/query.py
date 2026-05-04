from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime
import uuid

from app.core.db.connection import get_db

router = APIRouter()

_query_service_instance = None

def get_query_service():
    global _query_service_instance
    if _query_service_instance is None:
        from app.services.query_service import QueryService
        _query_service_instance = QueryService()
    return _query_service_instance


class QueryRequest(BaseModel):
    session_id: str
    query: str


class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    result: Optional[str] = None
    session_id: str
    user_query: str
    error: Optional[str] = None
    corrected: Optional[bool] = None


class SchemaColumn(BaseModel):
    column_name: str
    column_type: str
    description: Optional[str] = ""


@router.post("", response_model=QueryResponse)
async def execute_nl2sql_query(request: QueryRequest):
    query_service = get_query_service()
    result = await query_service.execute_natural_language_query(
        session_id=request.session_id,
        user_query=request.query
    )

    return QueryResponse(
        success=result.get("success", False),
        sql=result.get("sql"),
        result=result.get("result"),
        session_id=request.session_id,
        user_query=request.query,
        error=result.get("error"),
        corrected=result.get("corrected")
    )


@router.get("/history/{session_id}")
async def get_query_history(session_id: str, limit: int = 20):
    query_service = get_query_service()
    history = await query_service.get_query_history(session_id, limit)
    return {"session_id": session_id, "history": history}


@router.get("/schemas")
async def get_schemas():
    query_service = get_query_service()
    schemas = await query_service.get_schemas()
    return schemas


class SchemaRegisterRequest(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]
    session_id: Optional[str] = None


@router.post("/schemas/register")
async def register_schema(request: SchemaRegisterRequest):
    query_service = get_query_service()
    result = await query_service.register_schema(request.table_name, request.columns)
    return result


@router.get("/sql/validate")
async def validate_sql(sql: str):
    from app.core.db.executor import query_executor
    is_valid, error_msg = query_executor.validate_sql(sql)
    return {"valid": is_valid, "error": error_msg}


@router.post("/sql/execute")
async def execute_sql_direct(session_id: str, sql: str):
    query_service = get_query_service()
    result = await query_service.execute_sql_direct(session_id, sql)
    return result


class ChartConfigRequest(BaseModel):
    session_id: str
    query: str
    result: List[Dict[str, Any]]
    chart_type: Optional[str] = None
    x_axis_column: Optional[str] = None
    y_axis_column: Optional[str] = None


@router.post("/chart/config")
async def generate_chart_config(request: ChartConfigRequest):
    from app.services.visualization_service import VisualizationService

    viz_service = VisualizationService()
    config = viz_service.generate_chart_config(
        data=request.result,
        chart_type=request.chart_type,
        title=request.query,
        x_axis_column=request.x_axis_column,
        y_axis_column=request.y_axis_column
    )

    return {
        "success": True,
        "chart_type": config.get("chart_type", "line"),
        "config": config,
        "data": request.result
    }