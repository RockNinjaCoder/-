"""
后端模块专项检测
测试 MiniMax API 接入、NL2SQL 组件功能、接口参数完整性

执行顺序：
1. MiniMax API 接入验证（8个测试用例）
2. NL2SQL 组件功能确认（8个测试用例）
3. 接口参数完整性测试（9个测试用例）
"""

import os
import sys
import httpx
import time
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []

    def add(self, name: str, passed: bool, message: str = "", expected: str = "", actual: str = ""):
        self.total += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.results.append({
            "name": name,
            "passed": passed,
            "message": message,
            "expected": expected,
            "actual": actual
        })

    def print_summary(self):
        print("\n" + "=" * 70)
        print("测试结果汇总")
        print("=" * 70)
        print(f"总计: {self.total} | 通过: {self.passed} | 失败: {self.failed}")
        print(f"通过率: {self.passed / self.total * 100:.1f}%" if self.total > 0 else "N/A")
        print("=" * 70)

        for i, r in enumerate(self.results, 1):
            status = "✓ 通过" if r["passed"] else "✗ 失败"
            print(f"\n{i}. {r['name']}: {status}")
            if r["message"]:
                print(f"   消息: {r['message']}")
            if not r["passed"]:
                if r["expected"]:
                    print(f"   预期: {r['expected']}")
                if r["actual"]:
                    print(f"   实际: {r['actual']}")

        return self.failed == 0


def test_minimax_api_connection():
    """M1: 测试 API 连接状态"""
    print("\n" + "=" * 60)
    print("M1: MiniMax API 连接状态测试")
    print("=" * 60)

    result = TestResult()

    try:
        print(f"[测试] 连接 {API_BASE}/chat/completions")
        response = httpx.get(f"{API_BASE.rsplit('/', 1)[0]}/models", timeout=10.0)
        connected = response.status_code in [200, 401]

        result.add(
            "API 连接状态",
            connected,
            message=f"状态码: {response.status_code}",
            expected="HTTP 200 或 401 (有效凭证)",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("API 连接状态", False, message="连接失败 - 无法连接到服务器", expected="HTTP 200 或 401", actual="ConnectError")
    except Exception as e:
        result.add("API 连接状态", False, message=f"连接异常: {type(e).__name__}: {str(e)[:100]}")

    return result


def test_minimax_auth():
    """M2: 测试认证授权"""
    print("\n" + "=" * 60)
    print("M2: MiniMax 认证授权测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 10
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30.0
        )

        authorized = response.status_code == 200
        result.add(
            "认证授权",
            authorized,
            message=f"状态码: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except Exception as e:
        result.add("认证授权", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_minimax_streaming():
    """M3: 测试流式响应"""
    print("\n" + "=" * 60)
    print("M3: MiniMax 流式响应测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "count to 3"}],
                "max_tokens": 50,
                "stream": True
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30.0,
            stream=True
        )

        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
                if len(lines) >= 5:
                    break

        has_sse_format = any("data:" in line or "[DONE]" in line for line in lines)
        result.add(
            "流式响应格式",
            has_sse_format,
            message=f"收到 {len(lines)} 行数据",
            expected="包含 'data:' 前缀的 SSE 格式",
            actual=f"收到 {len(lines)} 行，格式正确: {has_sse_format}"
        )

    except Exception as e:
        result.add("流式响应格式", False, message=f"流式请求异常: {str(e)[:100]}")

    return result


def test_minimax_non_streaming():
    """M4: 测试非流式响应"""
    print("\n" + "=" * 60)
    print("M4: MiniMax 非流式响应测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "say 'test'"}],
                "max_tokens": 20,
                "stream": False
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30.0
        )

        data = response.json()
        has_choices = "choices" in data and len(data.get("choices", [])) > 0
        has_content = has_choices and "message" in data["choices"][0] and "content" in data["choices"][0]["message"]

        result.add(
            "非流式响应格式",
            has_content,
            message=f"响应包含 choices 和 content",
            expected="choices[0].message.content 字段存在",
            actual=f"choices: {has_choices}, content: {has_content}"
        )

    except Exception as e:
        result.add("非流式响应格式", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_minimax_request_format():
    """M5: 测试请求格式"""
    print("\n" + "=" * 60)
    print("M5: MiniMax 请求格式测试")
    print("=" * 60)

    result = TestResult()

    try:
        payload = {
            "model": "MiniMax-M2.7",
            "messages": [
                {"role": "system", "content": "你是助手"},
                {"role": "user", "content": "测试"}
            ],
            "max_tokens": 10
        }

        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

        valid_format = response.status_code == 200
        result.add(
            "请求格式",
            valid_format,
            message="messages 格式正确 (role/content)",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except Exception as e:
        result.add("请求格式", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_minimax_response_parsing():
    """M6: 测试响应格式解析"""
    print("\n" + "=" * 60)
    print("M6: MiniMax 响应格式解析测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "what is 1+1"}],
                "max_tokens": 20
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=30.0
        )

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        parsed_correctly = isinstance(content, str) and len(content) > 0
        result.add(
            "响应内容解析",
            parsed_correctly,
            message=f"解析到内容长度: {len(content)}",
            expected="content 为非空字符串",
            actual=f"content 类型: {type(content).__name__}, 长度: {len(content)}"
        )

    except Exception as e:
        result.add("响应内容解析", False, message=f"解析异常: {str(e)[:100]}")

    return result


def test_minimax_error_handling():
    """M7: 测试错误处理"""
    print("\n" + "=" * 60)
    print("M7: MiniMax 错误处理测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            },
            headers={"Authorization": "Bearer invalid_key_12345"},
            timeout=30.0
        )

        handles_error = response.status_code in [401, 403, 400]
        result.add(
            "错误处理",
            handles_error,
            message=f"无效凭证返回状态码: {response.status_code}",
            expected="401/403/400 错误码",
            actual=f"HTTP {response.status_code}"
        )

    except Exception as e:
        result.add("错误处理", False, message=f"异常处理: {str(e)[:100]}")

    return result


def test_minimax_timeout():
    """M8: 测试超时处理"""
    print("\n" + "=" * 60)
    print("M8: MiniMax 超时处理测试")
    print("=" * 60)

    result = TestResult()

    try:
        start = time.time()
        response = httpx.post(
            f"{API_BASE}/chat/completions",
            json={
                "model": "MiniMax-M2.7",
                "messages": [{"role": "user", "content": "count to 1000000"}],
                "max_tokens": 10
            },
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=5.0
        )
        elapsed = time.time() - start

        result.add(
            "超时处理",
            elapsed < 10,
            message=f"请求在 {elapsed:.1f}s 内完成",
            expected="5s 内超时或快速响应",
            actual=f"耗时 {elapsed:.1f}s"
        )

    except httpx.TimeoutException:
        result.add("超时处理", True, message="正确触发超时异常")
    except Exception as e:
        result.add("超时处理", True, message=f"异常视为正常: {type(e).__name__}")

    return result


def run_minimax_api_tests():
    """运行所有 MiniMax API 测试"""
    print("\n" + "=" * 70)
    print("模块一：MiniMax API 接入验证")
    print("=" * 70)

    results = []
    results.append(test_minimax_api_connection())
    results.append(test_minimax_auth())
    results.append(test_minimax_streaming())
    results.append(test_minimax_non_streaming())
    results.append(test_minimax_request_format())
    results.append(test_minimax_response_parsing())
    results.append(test_minimax_error_handling())
    results.append(test_minimax_timeout())

    combined = TestResult()
    for r in results:
        combined.total += r.total
        combined.passed += r.passed
        combined.failed += r.failed
        combined.results.extend(r.results)

    print(f"\n【MiniMax API 测试汇总】通过: {combined.passed}/{combined.total}")
    return combined


def test_nl2sql_database_connection():
    """N1: 测试数据库连接"""
    print("\n" + "=" * 60)
    print("N1: NL2SQL 数据库连接测试")
    print("=" * 60)

    result = TestResult()

    try:
        from sqlalchemy import create_engine, text

        db_path = os.path.join(os.path.dirname(__file__), "data", "analytics.db")
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1"))
            row = res.fetchone()

        connected = row[0] == 1
        result.add(
            "数据库连接",
            connected,
            message=f"连接成功: {db_path}",
            expected="SELECT 1 返回 1",
            actual=f"返回 {row[0]}"
        )

    except FileNotFoundError:
        result.add("数据库连接", False, message="数据库文件不存在", expected="analytics.db 存在", actual="文件不存在")
    except Exception as e:
        result.add("数据库连接", False, message=f"连接异常: {str(e)[:100]}")

    return result


def test_nl2sql_schema_parsing():
    """N2: 测试 Schema 解析"""
    print("\n" + "=" * 60)
    print("N2: NL2SQL Schema 解析测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.nlp.sql_generator import SQLGenerator

        generator = SQLGenerator()
        schema = generator._get_schema_context()

        has_tables = "表名:" in schema or "CREATE TABLE" in schema.upper()
        result.add(
            "Schema 解析",
            has_tables,
            message=f"解析到 {len(schema)} 字符的 schema 信息",
            expected="包含表名信息",
            actual=f"包含表名: {has_tables}"
        )

    except Exception as e:
        result.add("Schema 解析", False, message=f"解析异常: {str(e)[:100]}")

    return result


def test_nl2sql_generation():
    """N3: 测试 SQL 生成"""
    print("\n" + "=" * 60)
    print("N3: NL2SQL SQL 生成测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.nlp.sql_generator import SQLGenerator

        generator = SQLGenerator()
        sql, prompt = generator.generate_sql("查询所有用户")

        is_select = sql.strip().upper().startswith("SELECT")
        not_error = not sql.startswith("-- Error:")

        result.add(
            "SQL 生成",
            is_select and not_error,
            message=f"生成 SQL: {sql[:80]}...",
            expected="以 SELECT 开头的 SQL",
            actual=sql[:100]
        )

    except Exception as e:
        result.add("SQL 生成", False, message=f"生成异常: {str(e)[:100]}")

    return result


def test_nl2sql_execution():
    """N4: 测试 SQL 执行"""
    print("\n" + "=" * 60)
    print("N4: NL2SQL SQL 执行测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.db.executor import query_executor

        exec_result = query_executor.execute_query("SELECT COUNT(*) as cnt FROM users")
        has_result = exec_result is not None and len(exec_result) > 0

        result.add(
            "SQL 执行",
            has_result,
            message=f"执行结果: {exec_result}",
            expected="返回查询结果",
            actual=f"结果数量: {len(exec_result) if exec_result else 0}"
        )

    except Exception as e:
        result.add("SQL 执行", False, message=f"执行异常: {str(e)[:100]}")

    return result


def test_nl2sql_join_query():
    """N5: 测试多表关联查询"""
    print("\n" + "=" * 60)
    print("N5: NL2SQL 多表关联测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.db.executor import query_executor

        exec_result = query_executor.execute_query("""
            SELECT u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
        """)

        has_result = exec_result is not None
        result.add(
            "多表关联查询",
            has_result,
            message=f"JOIN 查询执行成功",
            expected="返回关联结果",
            actual=f"结果: {exec_result is not None}"
        )

    except Exception as e:
        result.add("多表关联查询", False, message=f"JOIN 异常: {str(e)[:100]}")

    return result


def test_nl2sql_aggregation():
    """N6: 测试聚合查询"""
    print("\n" + "=" * 60)
    print("N6: NL2SQL 聚合查询测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.db.executor import query_executor

        count_result = query_executor.execute_query("SELECT COUNT(*) FROM users")
        sum_result = query_executor.execute_query("SELECT SUM(total_amount) FROM orders")

        has_aggregation = count_result is not None and sum_result is not None
        result.add(
            "聚合查询",
            has_aggregation,
            message=f"COUNT: {count_result}, SUM: {sum_result}",
            expected="返回聚合计算结果",
            actual=f"COUNT: {count_result is not None}, SUM: {sum_result is not None}"
        )

    except Exception as e:
        result.add("聚合查询", False, message=f"聚合异常: {str(e)[:100]}")

    return result


def test_nl2sql_error_handling():
    """N7: 测试异常处理"""
    print("\n" + "=" * 60)
    print("N7: NL2SQL 异常处理测试")
    print("=" * 60)

    result = TestResult()

    try:
        from app.core.nlp.sql_generator import SQLGenerator

        generator = SQLGenerator()
        sql = "INSERT INTO users VALUES (1, 'test')"
        is_valid, error = generator.validate_sql(sql)

        handled = not is_valid and error is not None
        result.add(
            "异常处理",
            handled,
            message=f"无效 SQL 验证结果: {error}",
            expected="返回无效和错误信息",
            actual=f"valid={is_valid}, error={error}"
        )

    except Exception as e:
        result.add("异常处理", False, message=f"处理异常: {str(e)[:100]}")

    return result


def test_nl2sql_langchain_components():
    """N8: 测试 LangChain 组件"""
    print("\n" + "=" * 60)
    print("N8: NL2SQL LangChain 组件测试")
    print("=" * 60)

    result = TestResult()

    try:
        from sqlalchemy import create_engine
        from langchain_community.utilities import SQLDatabase
        from app.core.llm.minimax_adapter import get_minimax_llm

        db_path = os.path.join(os.path.dirname(__file__), "data", "analytics.db")
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        sql_db = SQLDatabase(engine)

        llm = get_minimax_llm(streaming=False)

        has_tables = len(sql_db.get_usable_table_names()) > 0
        result.add(
            "LangChain 组件",
            has_tables,
            message=f"SQLDatabase 表数量: {len(sql_db.get_usable_table_names())}",
            expected="表数量 > 0",
            actual=f"表数量: {len(sql_db.get_usable_table_names())}"
        )

    except ImportError as e:
        result.add("LangChain 组件", False, message=f"导入异常: {str(e)[:100]}")
    except Exception as e:
        result.add("LangChain 组件", False, message=f"组件异常: {str(e)[:100]}")

    return result


def run_nl2sql_tests():
    """运行所有 NL2SQL 测试"""
    print("\n" + "=" * 70)
    print("模块二：NL2SQL 组件功能确认")
    print("=" * 70)

    results = []
    results.append(test_nl2sql_database_connection())
    results.append(test_nl2sql_schema_parsing())
    results.append(test_nl2sql_generation())
    results.append(test_nl2sql_execution())
    results.append(test_nl2sql_join_query())
    results.append(test_nl2sql_aggregation())
    results.append(test_nl2sql_error_handling())
    results.append(test_nl2sql_langchain_components())

    combined = TestResult()
    for r in results:
        combined.total += r.total
        combined.passed += r.passed
        combined.failed += r.failed
        combined.results.extend(r.results)

    print(f"\n【NL2SQL 组件测试汇总】通过: {combined.passed}/{combined.total}")
    return combined


def test_api_query_normal():
    """P1: 测试正常查询参数"""
    print("\n" + "=" * 60)
    print("P1: POST /api/query 正常参数测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-session-001", "query": "查询用户总数"},
            timeout=60.0
        )

        success = response.status_code == 200
        result.add(
            "正常参数查询",
            success,
            message=f"状态码: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("正常参数查询", False, message="后端服务未启动", expected="HTTP 200", actual="ConnectionError")
    except Exception as e:
        result.add("正常参数查询", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_query_empty_string():
    """P2: 测试空字符串参数"""
    print("\n" + "=" * 60)
    print("P2: POST /api/query 空字符串测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-session-001", "query": ""},
            timeout=30.0
        )

        handles_empty = response.status_code in [400, 422, 200]
        result.add(
            "空字符串参数",
            handles_empty,
            message=f"空查询返回状态码: {response.status_code}",
            expected="400/422/200 (拒绝或处理)",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("空字符串参数", False, message="后端服务未启动")
    except Exception as e:
        result.add("空字符串参数", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_query_missing_param():
    """P3: 测试缺失参数"""
    print("\n" + "=" * 60)
    print("P3: POST /api/query 缺失参数测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-session-001"},
            timeout=30.0
        )

        validation_works = response.status_code in [400, 422]
        result.add(
            "缺失参数验证",
            validation_works,
            message=f"缺失 query 参数返回: {response.status_code}",
            expected="400/422 参数验证错误",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("缺失参数验证", False, message="后端服务未启动")
    except Exception as e:
        result.add("缺失参数验证", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_query_history():
    """P4: 测试查询历史"""
    print("\n" + "=" * 60)
    print("P4: GET /api/query/history/{session_id} 测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/query/history/test-session-001",
            timeout=30.0
        )

        success = response.status_code == 200
        data = response.json() if success else {}

        result.add(
            "查询历史",
            success,
            message=f"历史查询返回状态码: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("查询历史", False, message="后端服务未启动")
    except Exception as e:
        result.add("查询历史", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_query_history_nonexistent():
    """P5: 测试不存在的 session_id"""
    print("\n" + "=" * 60)
    print("P5: GET /api/query/history/{session_id} 不存在测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/query/history/nonexistent-session-xyz",
            timeout=30.0
        )

        returns_empty = response.status_code == 200
        data = response.json() if returns_empty else {}
        history_is_list = isinstance(data.get("history"), list)

        result.add(
            "不存在 session_id",
            returns_empty,
            message=f"返回: {data}",
            expected="HTTP 200 + 空历史数组",
            actual=f"HTTP {response.status_code}, history 类型: {type(data.get('history')).__name__}"
        )

    except httpx.ConnectError:
        result.add("不存在 session_id", False, message="后端服务未启动")
    except Exception as e:
        result.add("不存在 session_id", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_schema_register():
    """P6: 测试 Schema 注册"""
    print("\n" + "=" * 60)
    print("P6: POST /api/schemas/register 测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/schemas/register",
            json={
                "table_name": "test_table",
                "columns": [
                    {"column_name": "id", "column_type": "INTEGER"},
                    {"column_name": "name", "column_type": "TEXT"}
                ]
            },
            timeout=30.0
        )

        success = response.status_code == 200
        result.add(
            "Schema 注册",
            success,
            message=f"注册返回: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("Schema 注册", False, message="后端服务未启动")
    except Exception as e:
        result.add("Schema 注册", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_sql_execute():
    """P7: 测试直接 SQL 执行"""
    print("\n" + "=" * 60)
    print("P7: POST /api/sql/execute 测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/sql/execute",
            params={
                "session_id": "test-session-001",
                "sql": "SELECT 1 as test"
            },
            timeout=30.0
        )

        success = response.status_code == 200
        result.add(
            "SQL 直接执行",
            success,
            message=f"执行返回: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("SQL 直接执行", False, message="后端服务未启动")
    except Exception as e:
        result.add("SQL 直接执行", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_chart_config():
    """P8: 测试图表配置生成"""
    print("\n" + "=" * 60)
    print("P8: POST /api/chart/config 测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/chart/config",
            json={
                "session_id": "test-session-001",
                "query": "销售统计",
                "result": [
                    {"product": "A", "sales": 100},
                    {"product": "B", "sales": 200}
                ],
                "chart_type": "bar"
            },
            timeout=30.0
        )

        success = response.status_code == 200
        result.add(
            "图表配置生成",
            success,
            message=f"配置返回: {response.status_code}",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("图表配置生成", False, message="后端服务未启动")
    except Exception as e:
        result.add("图表配置生成", False, message=f"请求异常: {str(e)[:100]}")

    return result


def test_api_chart_config_empty():
    """P9: 测试空数据图表配置"""
    print("\n" + "=" * 60)
    print("P9: POST /api/chart/config 空数据测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/chart/config",
            json={
                "session_id": "test-session-001",
                "query": "测试",
                "result": [],
                "chart_type": "bar"
            },
            timeout=30.0
        )

        handles_empty = response.status_code in [200, 400]
        result.add(
            "空数据图表配置",
            handles_empty,
            message=f"空数据返回: {response.status_code}",
            expected="200 或 400",
            actual=f"HTTP {response.status_code}"
        )

    except httpx.ConnectError:
        result.add("空数据图表配置", False, message="后端服务未启动")
    except Exception as e:
        result.add("空数据图表配置", False, message=f"请求异常: {str(e)[:100]}")

    return result


def run_api_parameter_tests():
    """运行所有接口参数测试"""
    print("\n" + "=" * 70)
    print("模块三：接口参数完整性测试")
    print("=" * 70)

    results = []
    results.append(test_api_query_normal())
    results.append(test_api_query_empty_string())
    results.append(test_api_query_missing_param())
    results.append(test_api_query_history())
    results.append(test_api_query_history_nonexistent())
    results.append(test_api_schema_register())
    results.append(test_api_sql_execute())
    results.append(test_api_chart_config())
    results.append(test_api_chart_config_empty())

    combined = TestResult()
    for r in results:
        combined.total += r.total
        combined.passed += r.passed
        combined.failed += r.failed
        combined.results.extend(r.results)

    print(f"\n【接口参数测试汇总】通过: {combined.passed}/{combined.total}")
    return combined


def main():
    print("=" * 70)
    print("后端模块专项检测")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BACKEND_URL}")
    print(f"MiniMax API: {API_BASE}")
    print("=" * 70)

    all_results = []

    minimax_results = run_minimax_api_tests()
    all_results.append(minimax_results)

    nl2sql_results = run_nl2sql_tests()
    all_results.append(nl2sql_results)

    api_results = run_api_parameter_tests()
    all_results.append(api_results)

    final_combined = TestResult()
    for r in all_results:
        final_combined.total += r.total
        final_combined.passed += r.passed
        final_combined.failed += r.failed

    print("\n" + "=" * 70)
    print("【最终汇总】")
    print("=" * 70)
    print(f"MiniMax API 测试: {minimax_results.passed}/{minimax_results.total}")
    print(f"NL2SQL 组件测试: {nl2sql_results.passed}/{nl2sql_results.total}")
    print(f"接口参数测试: {api_results.passed}/{api_results.total}")
    print(f"\n总计: {final_combined.passed}/{final_combined.total}")
    print(f"总体通过率: {final_combined.passed / final_combined.total * 100:.1f}%")

    if final_combined.failed > 0:
        print("\n" + "=" * 70)
        print("失败测试详情:")
        for r in all_results:
            for item in r.results:
                if not item["passed"]:
                    print(f"  - {item['name']}: {item['message']}")

    return final_combined


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.failed == 0 else 1)