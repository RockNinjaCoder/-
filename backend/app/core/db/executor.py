import os
from typing import Tuple, Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime


class QueryExecutor:
    """
    查询执行引擎
    负责安全执行 SQL 查询、结果格式化和异常处理
    """

    def __init__(self, db_path: str = None):
        """
        初始化查询执行器

        Args:
            db_path: 数据库路径，默认使用项目数据库
        """
        self.db_path = db_path or os.getenv("DATABASE_PATH", os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "analytics.db"
        ))
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        """初始化 SQLAlchemy 引擎"""
        db_uri = f"sqlite:///{self.db_path}"
        self._engine = create_engine(
            db_uri,
            connect_args={"check_same_thread": False}
        )

    def execute_query(self, sql: str) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        执行 SQL 查询

        Args:
            sql: SQL 语句

        Returns:
            (是否成功, 消息, 结果数据) 元组
        """
        if not sql or not sql.strip():
            return False, "SQL 语句为空", None

        is_valid, error_msg = self.validate_sql(sql)
        if not is_valid:
            return False, error_msg, None

        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                columns = result.keys()

                result_data = []
                for row in rows:
                    row_dict = {}
                    for col, val in zip(columns, row):
                        row_dict[col] = val
                    result_data.append(row_dict)

                return True, "查询执行成功", result_data

        except SQLAlchemyError as e:
            return False, f"SQL 执行错误: {str(e)}", None

    def execute_and_format(self, sql: str) -> Tuple[bool, str]:
        """
        执行查询并返回格式化后的结果

        Args:
            sql: SQL 语句

        Returns:
            (是否成功, 格式化结果字符串) 元组
        """
        success, message, data = self.execute_query(sql)

        if not success:
            return False, message

        if not data:
            return True, "查询成功，无数据返回"

        try:
            if len(data) == 1:
                result_str = json.dumps(data[0], ensure_ascii=False, indent=2)
            else:
                result_str = json.dumps(data, ensure_ascii=False, indent=2)
            return True, result_str
        except Exception as e:
            return False, f"结果格式化失败: {str(e)}"

    def validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        验证 SQL 语法和安全性

        Args:
            sql: SQL 语句

        Returns:
            (是否有效, 错误信息) 元组
        """
        sql = sql.strip()

        if not sql:
            return False, "SQL 语句为空"

        dangerous_keywords = [
            "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
            "ALTER", "TRUNCATE", "EXEC", "EXECUTE", "GRANT",
            "REVOKE", "DENY", "BACKUP", "RESTORE"
        ]

        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False, f"禁止使用 {keyword} 操作，仅支持 SELECT 查询"

        if not sql_upper.startswith("SELECT"):
            return False, "仅允许 SELECT 查询"

        sql_for_check = sql.split("/*")[0].split("--")[0].rstrip()
        if ";" in sql_for_check and not sql_for_check.rstrip().endswith(";"):
            return False, "禁止多条 SQL 语句"
        if sql_for_check.count(";") > 1:
            return False, "禁止多条 SQL 语句"

        return True, None

    def get_table_info(self) -> List[str]:
        """
        获取数据库所有表名

        Returns:
            表名列表
        """
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                return tables
        except Exception:
            return []

    def get_table_schema(self, table_name: str) -> List[Dict]:
        """
        获取指定表的结构信息

        Args:
            table_name: 表名

        Returns:
            列信息列表
        """
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = []
                for row in result.fetchall():
                    columns.append({
                        "cid": row[0],
                        "name": row[1],
                        "type": row[2],
                        "notnull": row[3],
                        "default_value": row[4],
                        "primary_key": row[5]
                    })
                return columns
        except Exception:
            return []

    def query_with_context(self, sql: str, session_id: str = None, user_query: str = None) -> Dict[str, Any]:
        """
        带上下文的查询

        Args:
            sql: SQL 语句
            session_id: 会话 ID
            user_query: 用户原始查询

        Returns:
            包含执行结果的字典
        """
        is_valid, error_msg = self.validate_sql(sql)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "sql": sql,
                "session_id": session_id,
                "user_query": user_query,
                "timestamp": datetime.now().isoformat()
            }

        success, message, data = self.execute_query(sql)

        return {
            "success": success,
            "message": message,
            "data": data,
            "sql": sql,
            "session_id": session_id,
            "user_query": user_query,
            "row_count": len(data) if data else 0,
            "timestamp": datetime.now().isoformat()
        }


query_executor = QueryExecutor()