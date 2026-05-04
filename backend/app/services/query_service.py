import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid

from app.core.db.connection import get_db
from app.core.db.executor import query_executor

_lazy_sql_generator = None

def get_sql_generator():
    global _lazy_sql_generator
    if _lazy_sql_generator is None:
        from app.core.nlp.sql_generator import SQLGenerator
        _lazy_sql_generator = SQLGenerator()
    return _lazy_sql_generator


class QueryService:
    """
    查询服务层
    整合 SQL 生成、查询执行、结果处理
    """

    def __init__(self):
        self._sql_generator = None

    @property
    def sql_generator(self):
        if self._sql_generator is None:
            self._sql_generator = get_sql_generator()
        return self._sql_generator

    async def execute_natural_language_query(
        self,
        session_id: str,
        user_query: str
    ) -> Dict[str, Any]:
        """
        执行自然语言查询

        Args:
            session_id: 会话 ID
            user_query: 用户自然语言查询

        Returns:
            查询结果字典
        """
        log_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = await get_db()
        await conn.execute(
            "INSERT INTO query_logs (id, session_id, user_query, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (log_id, session_id, user_query, None, now)
        )
        await conn.commit()

        try:
            sql, prompt = self.sql_generator.generate_sql(user_query)
            await self._update_query_log(log_id, sql=sql)

            if sql.startswith("-- Error:"):
                await self._update_query_log(log_id, status="failed", error_message=sql)
                return {
                    "success": False,
                    "error": sql,
                    "sql": None,
                    "session_id": session_id,
                    "user_query": user_query
                }

            is_valid, error_msg = self.sql_generator.validate_sql(sql)
            if not is_valid:
                await self._update_query_log(log_id, status="failed", error_message=error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "sql": sql,
                    "session_id": session_id,
                    "user_query": user_query
                }

            success, result = query_executor.execute_and_format(sql)

            if success:
                await self._update_query_log(log_id, status="success", execution_result=result)
                return {
                    "success": True,
                    "sql": sql,
                    "result": result,
                    "session_id": session_id,
                    "user_query": user_query
                }
            else:
                corrected_sql = self.sql_generator.correct_sql(sql, result)
                await self._update_query_log(log_id, sql=corrected_sql, error_message=result)

                if corrected_sql.startswith("-- Correction failed:"):
                    await self._update_query_log(log_id, status="failed", error_message=result)
                    return {
                        "success": False,
                        "error": result,
                        "sql": sql,
                        "session_id": session_id,
                        "user_query": user_query
                    }

                success, result = query_executor.execute_and_format(corrected_sql)
                if success:
                    await self._update_query_log(log_id, status="success", execution_result=result)
                    return {
                        "success": True,
                        "sql": corrected_sql,
                        "result": result,
                        "session_id": session_id,
                        "user_query": user_query,
                        "corrected": True
                    }
                else:
                    await self._update_query_log(log_id, status="failed", error_message=result)
                    return {
                        "success": False,
                        "error": result,
                        "sql": corrected_sql,
                        "session_id": session_id,
                        "user_query": user_query
                    }

        except Exception as e:
            await self._update_query_log(log_id, status="failed", error_message=str(e))
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "user_query": user_query
            }

    async def execute_sql_direct(
        self,
        session_id: str,
        sql: str
    ) -> Dict[str, Any]:
        """
        直接执行 SQL 查询

        Args:
            session_id: 会话 ID
            sql: SQL 语句

        Returns:
            查询结果字典
        """
        is_valid, error_msg = query_executor.validate_sql(sql)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "session_id": session_id
            }

        success, result = query_executor.execute_and_format(sql)

        return {
            "success": success,
            "result": result if success else None,
            "error": result if not success else None,
            "sql": sql,
            "session_id": session_id
        }

    async def get_query_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取查询历史

        Args:
            session_id: 会话 ID
            limit: 返回数量限制

        Returns:
            查询历史列表
        """
        conn = await get_db()
        cursor = await conn.execute(
            """SELECT id, user_query, generated_sql, execution_result, status, error_message, created_at
               FROM query_logs WHERE session_id = ? ORDER BY created_at DESC LIMIT ?""",
            (session_id, limit)
        )
        rows = await cursor.fetchall()

        return [
            {
                "id": row["id"],
                "user_query": row["user_query"],
                "generated_sql": row["generated_sql"],
                "execution_result": row["execution_result"],
                "status": row["status"],
                "error_message": row["error_message"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

    async def get_schemas(self) -> Dict[str, List[Dict]]:
        """
        获取数据库 schema 信息

        Returns:
            Schema 字典
        """
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
                "description": row["description"] if row["description"] else ""
            })

        return schemas

    async def register_schema(
        self,
        table_name: str,
        columns: List[Dict]
    ) -> Dict[str, Any]:
        """
        注册数据库 schema

        Args:
            table_name: 表名
            columns: 列信息列表

        Returns:
            注册结果
        """
        conn = await get_db()
        now = datetime.now().isoformat()

        for col in columns:
            schema_id = str(uuid.uuid4())
            await conn.execute(
                """INSERT INTO db_schemas (id, table_name, column_name, column_type, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    schema_id,
                    table_name,
                    col["column_name"],
                    col.get("column_type", "TEXT"),
                    col.get("description", ""),
                    now
                )
            )

        await conn.commit()

        return {
            "success": True,
            "message": f"Schema for table '{table_name}' registered successfully",
            "table_name": table_name,
            "column_count": len(columns)
        }

    async def _update_query_log(
        self,
        log_id: str,
        status: str = None,
        sql: str = None,
        execution_result: str = None,
        error_message: str = None
    ):
        """更新查询日志"""
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)
        if sql is not None:
            updates.append("generated_sql = ?")
            params.append(sql)
        if execution_result is not None:
            updates.append("execution_result = ?")
            params.append(execution_result)
        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)

        if updates:
            params.append(log_id)
            conn = await get_db()
            await conn.execute(
                f"UPDATE query_logs SET {', '.join(updates)} WHERE id = ?",
                params
            )
            await conn.commit()


query_service = QueryService()