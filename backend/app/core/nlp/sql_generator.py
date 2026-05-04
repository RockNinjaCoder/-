import os
import json
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from sqlalchemy import create_engine
import httpx

load_dotenv()


class SQLGenerator:
    """
    SQL 生成引擎
    直接使用 OpenAI API 生成 SQL，无需 LangChain SQLDatabaseToolkit
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data",
            "analytics.db"
        ))
        self.api_base = os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")
        self.api_key = os.getenv("MINIMAX_API_KEY")

    def _get_schema_context(self) -> str:
        """获取数据库 schema 上下文"""
        try:
            engine = create_engine(f"sqlite:///{self.db_path}")
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result]

                schema = "数据库表结构:\n"
                for table in tables:
                    result = conn.execute(
                        text(f"PRAGMA table_info({table})")
                    )
                    schema += f"\n表名: {table}\n"
                    for row in result:
                        schema += f"  - {row[1]} ({row[2]})\n"
                return schema
        except Exception as e:
            return f"获取 schema 失败: {str(e)}"

    def generate_sql(self, user_query: str, schemas: Optional[Dict[str, List[Dict]]] = None) -> Tuple[str, str]:
        """
        生成 SQL 语句

        Args:
            user_query: 用户自然语言查询
            schemas: 数据库 schema 信息（可选）

        Returns:
            (SQL 语句, 原始提示) 元组
        """
        schema_context = self._get_schema_context() if schemas is None else self._build_schema_context(schemas)

        prompt = f"""你是一个 SQL 专家。根据用户的自然语言描述生成 SQL 查询语句。

{schema_context}

重要规则：
1. 只生成 SELECT 查询，禁止 INSERT、UPDATE、DELETE 等修改操作
2. 使用正确的表名和列名
3. 注意数据类型（字符串需要用引号，数字不需要）
4. 如果表不存在或无法确定，返回错误信息

用户查询: {user_query}

请生成对应的 SQL 语句（只返回 SQL，不要其他解释）:"""

        try:
            response = httpx.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": "MiniMax-M2.7",
                    "messages": [
                        {"role": "system", "content": "你是一个 SQL 专家，擅长生成准确的 SQL 查询语句。"},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.3
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            import re
            content = re.sub(r"<think>.*?", "", content, flags=re.DOTALL)

            code_blocks = re.findall(r"```(?:\w+)?\s*([\s\S]*?)```", content)
            if code_blocks:
                for block in code_blocks:
                    block = block.strip()
                    if re.match(r'^\s*SELECT', block, re.IGNORECASE):
                        sql_match = re.search(r'(SELECT\s+[\s\S]+?);?\s*$', block, re.IGNORECASE)
                        if sql_match:
                            return sql_match.group(0).rstrip(';') + ';', prompt

            sql_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if re.match(r'^\s*SELECT', line, re.IGNORECASE):
                    clean_line = re.sub(r'[^\x00-\x7F]+', '', line)
                    if clean_line.upper().startswith('SELECT') and not any(word in clean_line.upper() for word in ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP']):
                        sql_lines.append(line)

            if sql_lines:
                return sql_lines[0].rstrip(';') + ';', prompt

            return content, prompt

        except Exception as e:
            return f"-- Error: {str(e)}", prompt

    def validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        验证 SQL 语法

        Args:
            sql: SQL 语句

        Returns:
            (是否有效, 错误信息) 元组
        """
        sql = sql.strip()

        if not sql:
            return False, "SQL 为空"

        if sql.startswith("-- Error:"):
            return False, sql

        sql_upper = sql.upper()

        if not sql_upper.startswith("SELECT"):
            return False, "只允许 SELECT 查询"

        dangerous_keywords = ["DROP", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False, f"禁止使用 {keyword} 操作"

        sql_for_check = sql.split("/*")[0].split("--")[0].rstrip()
        if ";" in sql_for_check and not sql_for_check.rstrip().endswith(";"):
            return False, "禁止多条 SQL 语句"
        if sql_for_check.count(";") > 1:
            return False, "禁止多条 SQL 语句"

        return True, None

    def correct_sql(self, sql: str, error: str, schemas: Optional[Dict[str, List[Dict]]] = None) -> str:
        """
        纠错 SQL

        Args:
            sql: 原始 SQL
            error: 错误信息
            schemas: 数据库 schema 信息

        Returns:
            修正后的 SQL
        """
        correction_prompt = f"""修正以下 SQL 语句的错误：

原始 SQL: {sql}
错误信息: {error}

数据库 Schema:
{self._get_schema_context()}

请生成修正后的 SQL 语句（只返回 SQL，不要其他解释）:"""

        try:
            response = httpx.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": "MiniMax-M2.7",
                    "messages": [
                        {"role": "system", "content": "你是一个 SQL 专家，擅长修正 SQL 语句错误。"},
                        {"role": "user", "content": correction_prompt}
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.3
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )

            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            import re
            content = re.sub(r"<think>.*?", "", content, flags=re.DOTALL)

            code_blocks = re.findall(r"```(?:\w+)?\s*([\s\S]*?)```", content)
            if code_blocks:
                return code_blocks[0].strip()

            sql_match = re.search(r'\b(SELECT\s+[\s\S]*?;)\s*$', content, re.MULTILINE | re.IGNORECASE)
            if sql_match:
                return sql_match.group(1).strip()

            for line in content.split('\n'):
                if line.strip().upper().startswith('SELECT'):
                    return line.strip()

            return content.strip()

        except Exception as e:
            return f"-- Correction failed: {str(e)}"

    def _build_schema_context(self, schemas: Optional[Dict[str, List[Dict]]]) -> str:
        """构建 Schema 上下文"""
        if not schemas:
            return "(暂无 schema 信息)"

        context = "数据库 Schema:\n"
        for table_name, columns in schemas.items():
            context += f"\n表名: {table_name}\n"
            for col in columns:
                context += f"  - {col['column_name']} ({col['column_type']})\n"
        return context


sql_generator = SQLGenerator()


from sqlalchemy import text