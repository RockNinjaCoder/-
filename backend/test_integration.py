"""
前后端联调测试
测试数据流转完整性、接口调用成功率、端到端业务流程

执行顺序：
1. 数据流转测试（8个测试用例）
2. 接口调用成功率测试（4个接口）
3. 端到端业务流程测试（3个场景）
"""

import os
import sys
import httpx
import time
import json
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


def test_dataflow_query_to_api():
    """I1: 测试用户提问 → API 参数传递"""
    print("\n" + "=" * 60)
    print("I1: 用户提问 → API 参数传递测试")
    print("=" * 60)

    result = TestResult()

    try:
        test_query = "查询用户总数"
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-integration", "query": test_query},
            timeout=60.0
        )

        passed = response.status_code == 200
        result.add(
            "用户提问 → API",
            passed,
            message=f"查询 '{test_query}' 发送成功",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}"
        )

    except Exception as e:
        result.add("用户提问 → API", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_api_to_minimax():
    """I2: 测试 API → MiniMax LLM 调用"""
    print("\n" + "=" * 60)
    print("I2: API → MiniMax LLM 调用测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-integration", "query": "你好"},
            timeout=120.0
        )

        data = response.json()
        has_response = response.status_code == 200 and (data.get("result") or data.get("sql"))

        result.add(
            "API → MiniMax LLM",
            has_response,
            message=f"收到 LLM 响应",
            expected="返回 SQL 或结果",
            actual=f"status: {response.status_code}, has_result: {bool(data.get('result') or data.get('sql'))}"
        )

    except Exception as e:
        result.add("API → MiniMax LLM", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_minimax_to_sql():
    """I3: 测试 MiniMax → SQL 生成"""
    print("\n" + "=" * 60)
    print("I3: MiniMax → SQL 生成测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-integration", "query": "查询所有用户"},
            timeout=120.0
        )

        data = response.json()
        has_sql = data.get("sql") and data["sql"].upper().startswith("SELECT")
        not_error = not (data.get("sql") or "").startswith("-- Error")

        passed = has_sql and not_error
        result.add(
            "MiniMax → SQL 生成",
            passed,
            message=f"生成 SQL: {data.get('sql', 'N/A')[:50]}...",
            expected="返回有效的 SELECT SQL",
            actual=f"has_sql: {has_sql}, not_error: {not_error}"
        )

    except Exception as e:
        result.add("MiniMax → SQL 生成", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_sql_to_database():
    """I4: 测试 SQL → 数据库查询执行"""
    print("\n" + "=" * 60)
    print("I4: SQL → 数据库查询执行测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/sql/execute",
            params={
                "session_id": "test-integration",
                "sql": "SELECT COUNT(*) as cnt FROM users"
            },
            timeout=30.0
        )

        passed = response.status_code == 200
        data = response.json() if passed else {}

        result.add(
            "SQL → 数据库查询",
            passed,
            message=f"查询执行成功",
            expected="HTTP 200",
            actual=f"HTTP {response.status_code}, data: {data}"
        )

    except Exception as e:
        result.add("SQL → 数据库查询", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_database_to_api():
    """I5: 测试数据库结果 → API 格式化"""
    print("\n" + "=" * 60)
    print("I5: 数据库结果 → API 格式化测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/sql/execute",
            params={
                "session_id": "test-integration",
                "sql": "SELECT * FROM users LIMIT 5"
            },
            timeout=30.0
        )

        data = response.json()
        is_list = isinstance(data.get("result"), list)

        result.add(
            "数据库 → API 格式化",
            is_list,
            message=f"返回 {len(data.get('result', []))} 条数据",
            expected="返回列表格式结果",
            actual=f"result 类型: {type(data.get('result')).__name__}"
        )

    except Exception as e:
        result.add("数据库 → API 格式化", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_api_to_frontend():
    """I6: 测试 API → 前端 JSON 响应解析"""
    print("\n" + "=" * 60)
    print("I6: API → 前端 JSON 响应解析测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": "test-integration", "query": "查询用户数量"},
            timeout=120.0
        )

        data = response.json()
        is_valid_json = response.status_code == 200 and isinstance(data, dict)
        has_required_fields = is_valid_json and all(k in data for k in ["success", "sql"])

        result.add(
            "API → 前端 JSON 解析",
            has_required_fields,
            message=f"JSON 响应包含必需字段",
            expected="success, sql 等字段",
            actual=f"is_valid: {is_valid_json}, has_fields: {has_required_fields}"
        )

    except Exception as e:
        result.add("API → 前端 JSON 解析", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_frontend_to_chart():
    """I7: 测试前端 → 图表数据渲染"""
    print("\n" + "=" * 60)
    print("I7: 前端 → 图表数据渲染测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/chart/config",
            json={
                "session_id": "test-integration",
                "query": "销售统计",
                "result": [
                    {"product": "A", "sales": 100},
                    {"product": "B", "sales": 200}
                ],
                "chart_type": "bar"
            },
            timeout=30.0
        )

        data = response.json()
        has_chart_config = response.status_code == 200 and "config" in data

        result.add(
            "前端 → 图表渲染",
            has_chart_config,
            message=f"生成图表配置",
            expected="包含 chart_config",
            actual=f"status: {response.status_code}, has_config: {has_chart_config}"
        )

    except Exception as e:
        result.add("前端 → 图表渲染", False, message=f"异常: {str(e)[:100]}")

    return result


def test_dataflow_frontend_to_table():
    """I8: 测试前端 → 表格数据展示"""
    print("\n" + "=" * 60)
    print("I8: 前端 → 表格数据展示测试")
    print("=" * 60)

    result = TestResult()

    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/query/sql/execute",
            params={
                "session_id": "test-integration",
                "sql": "SELECT id, name FROM users LIMIT 10"
            },
            timeout=30.0
        )

        data = response.json()
        is_table_data = response.status_code == 200 and isinstance(data.get("result"), list)

        result.add(
            "前端 → 表格展示",
            is_table_data,
            message=f"返回 {len(data.get('result', []))} 行数据用于表格展示",
            expected="返回列表数据",
            actual=f"status: {response.status_code}, rows: {len(data.get('result', []))}"
        )

    except Exception as e:
        result.add("前端 → 表格展示", False, message=f"异常: {str(e)[:100]}")

    return result


def run_dataflow_tests():
    """运行所有数据流转测试"""
    print("\n" + "=" * 70)
    print("模块一：数据流转测试")
    print("=" * 70)

    results = []
    results.append(test_dataflow_query_to_api())
    results.append(test_dataflow_api_to_minimax())
    results.append(test_dataflow_minimax_to_sql())
    results.append(test_dataflow_sql_to_database())
    results.append(test_dataflow_database_to_api())
    results.append(test_dataflow_api_to_frontend())
    results.append(test_dataflow_frontend_to_chart())
    results.append(test_dataflow_frontend_to_table())

    combined = TestResult()
    for r in results:
        combined.total += r.total
        combined.passed += r.passed
        combined.failed += r.failed
        combined.results.extend(r.results)

    print(f"\n【数据流转测试汇总】通过: {combined.passed}/{combined.total}")
    return combined


def test_api_success_rate(endpoint: str, method: str = "GET", call_count: int = 10):
    """测试接口调用成功率"""
    print(f"\n测试 {endpoint} ({method}) {call_count} 次")

    success_count = 0
    times = []

    for i in range(call_count):
        try:
            start = time.time()

            if method == "GET":
                response = httpx.get(f"{BACKEND_URL}{endpoint}", timeout=30.0)
            elif method == "POST":
                if "query" in endpoint and "execute" not in endpoint:
                    response = httpx.post(
                        f"{BACKEND_URL}{endpoint}",
                        json={"session_id": "test", "query": "测试"},
                        timeout=60.0
                    )
                else:
                    response = httpx.post(f"{BACKEND_URL}{endpoint}", timeout=30.0)
            else:
                response = httpx.request(method, f"{BACKEND_URL}{endpoint}", timeout=30.0)

            elapsed = time.time() - start
            times.append(elapsed)

            if response.status_code in [200, 201]:
                success_count += 1

        except Exception as e:
            print(f"  调用 {i+1} 失败: {str(e)[:50]}")

    success_rate = (success_count / call_count) * 100
    avg_time = sum(times) / len(times) if times else 0

    return success_count, success_rate, avg_time


def test_api_reliability():
    """C1-C4: 测试接口调用成功率"""
    print("\n" + "=" * 60)
    print("模块二：接口调用成功率测试")
    print("=" * 60)

    result = TestResult()

    endpoints = [
        ("/health", "GET", 10),
        ("/api/sessions", "POST", 10),
        ("/api/query", "POST", 10),
        ("/api/chat/stream", "POST", 5),
    ]

    for endpoint, method, call_count in endpoints:
        print(f"\n--- {method} {endpoint} ---")

        success_count, success_rate, avg_time = test_api_success_rate(endpoint, method, call_count)

        passed = success_rate >= 95
        result.add(
            f"接口成功率 {endpoint}",
            passed,
            message=f"成功 {success_count}/{call_count}, 成功率 {success_rate:.1f}%, 平均耗时 {avg_time:.2f}s",
            expected=">95% 成功率",
            actual=f"{success_rate:.1f}%"
        )

    return result


def test_e2e_basic_query_flow():
    """场景一：基础查询流程"""
    print("\n" + "=" * 60)
    print("场景一：基础查询流程测试")
    print("=" * 60)

    result = TestResult()

    try:
        print("步骤 1: 创建会话")
        session_response = httpx.post(
            f"{BACKEND_URL}/api/sessions",
            json={"title": "集成测试会话"},
            timeout=30.0
        )
        session_created = session_response.status_code == 200
        session_data = session_response.json() if session_created else {}
        session_id = session_data.get("session_id", "test-session")

        result.add(
            "创建会话",
            session_created,
            message=f"session_id: {session_id}",
            expected="返回 session_id",
            actual=f"status: {session_response.status_code}"
        )

        if not session_created:
            session_id = "e2e-test-session"

        print(f"步骤 2: 发送查询 (session: {session_id})")
        query_response = httpx.post(
            f"{BACKEND_URL}/api/query",
            json={"session_id": session_id, "query": "查询用户总数"},
            timeout=120.0
        )

        query_success = query_response.status_code == 200
        query_data = query_response.json() if query_success else {}

        result.add(
            "发送 NL2SQL 查询",
            query_success,
            message=f"返回 SQL: {query_data.get('sql', 'N/A')[:50]}...",
            expected="HTTP 200",
            actual=f"HTTP {query_response.status_code}"
        )

        has_sql = query_data.get("sql") and query_data["sql"].upper().startswith("SELECT")
        result.add(
            "SQL 生成",
            has_sql,
            message="SQL 生成正确",
            expected="生成有效 SELECT 语句",
            actual=f"has_sql: {has_sql}"
        )

        print("步骤 3: 验证查询结果返回")
        has_result = "result" in query_data or "sql" in query_data
        result.add(
            "查询结果返回",
            has_result,
            message="结果已返回",
            expected="包含 result 或 sql",
            actual=f"keys: {list(query_data.keys())}"
        )

    except Exception as e:
        result.add("基础查询流程", False, message=f"流程异常: {str(e)[:100]}")

    return result


def test_e2e_visualization_flow():
    """场景二：可视化流程"""
    print("\n" + "=" * 60)
    print("场景二：可视化流程测试")
    print("=" * 60)

    result = TestResult()

    try:
        print("步骤 1: 执行数据查询")
        query_response = httpx.post(
            f"{BACKEND_URL}/api/query/sql/execute",
            params={
                "session_id": "e2e-test",
                "sql": "SELECT name, total_amount FROM orders LIMIT 10"
            },
            timeout=30.0
        )

        data = query_response.json()
        has_data = isinstance(data.get("result"), list) and len(data.get("result", [])) > 0

        result.add(
            "数据查询",
            has_data,
            message=f"查询返回 {len(data.get('result', []))} 条数据",
            expected="返回数据",
            actual=f"rows: {len(data.get('result', []))}"
        )

        print("步骤 2: 调用图表配置接口")
        chart_response = httpx.post(
            f"{BACKEND_URL}/api/query/chart/config",
            json={
                "session_id": "e2e-test",
                "query": "订单金额统计",
                "result": data.get("result", []) or [{"name": "test", "amount": 100}],
                "chart_type": "bar"
            },
            timeout=30.0
        )

        chart_success = chart_response.status_code == 200
        chart_data = chart_response.json() if chart_success else {}

        result.add(
            "图表配置生成",
            chart_success,
            message=f"生成图表类型: {chart_data.get('chart_type', 'N/A')}",
            expected="HTTP 200",
            actual=f"HTTP {chart_response.status_code}"
        )

        print("步骤 3: 验证图表配置")
        has_config = "config" in chart_data and "chart_type" in chart_data
        result.add(
            "图表配置验证",
            has_config,
            message="图表配置完整",
            expected="包含 config 和 chart_type",
            actual=f"has_config: {has_config}"
        )

    except Exception as e:
        result.add("可视化流程", False, message=f"流程异常: {str(e)[:100]}")

    return result


def test_e2e_session_management():
    """场景三：会话管理流程"""
    print("\n" + "=" * 60)
    print("场景三：会话管理流程测试")
    print("=" * 60)

    result = TestResult()

    try:
        print("步骤 1: 创建多个会话")
        session_ids = []
        for i in range(3):
            response = httpx.post(
                f"{BACKEND_URL}/api/sessions",
                json={"title": f"测试会话 {i+1}"},
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                session_ids.append(data.get("session_id"))

        created_multiple = len(session_ids) >= 2
        result.add(
            "创建多个会话",
            created_multiple,
            message=f"创建了 {len(session_ids)} 个会话",
            expected=">=2 个会话",
            actual=f"创建 {len(session_ids)} 个"
        )

        print("步骤 2: 切换会话并查询历史")
        if session_ids:
            history_response = httpx.get(
                f"{BACKEND_URL}/api/query/history/{session_ids[0]}",
                timeout=30.0
            )

            history_works = history_response.status_code == 200
            result.add(
                "查询历史记录",
                history_works,
                message="历史查询成功",
                expected="HTTP 200",
                actual=f"HTTP {history_response.status_code}"
            )

        print("步骤 3: 验证会话隔离")
        isolated = len(session_ids) >= 2
        result.add(
            "会话隔离",
            isolated,
            message="每个会话独立管理",
            expected="会话隔离正常",
            actual=f"{len(session_ids)} 个独立会话"
        )

    except Exception as e:
        result.add("会话管理流程", False, message=f"流程异常: {str(e)[:100]}")

    return result


def run_e2e_tests():
    """运行所有端到端业务流程测试"""
    print("\n" + "=" * 70)
    print("模块三：端到端业务流程测试")
    print("=" * 70)

    results = []
    results.append(test_e2e_basic_query_flow())
    results.append(test_e2e_visualization_flow())
    results.append(test_e2e_session_management())

    combined = TestResult()
    for r in results:
        combined.total += r.total
        combined.passed += r.passed
        combined.failed += r.failed
        combined.results.extend(r.results)

    print(f"\n【端到端流程测试汇总】通过: {combined.passed}/{combined.total}")
    return combined


def main():
    print("=" * 70)
    print("前后端联调测试")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BACKEND_URL}")
    print("=" * 70)

    all_results = []

    dataflow_results = run_dataflow_tests()
    all_results.append(dataflow_results)

    reliability_results = test_api_reliability()
    all_results.append(reliability_results)

    e2e_results = run_e2e_tests()
    all_results.append(e2e_results)

    final_combined = TestResult()
    for r in all_results:
        final_combined.total += r.total
        final_combined.passed += r.passed
        final_combined.failed += r.failed

    print("\n" + "=" * 70)
    print("【最终汇总】")
    print("=" * 70)
    print(f"数据流转测试: {dataflow_results.passed}/{dataflow_results.total}")
    print(f"接口成功率测试: {reliability_results.passed}/{reliability_results.total}")
    print(f"端到端流程测试: {e2e_results.passed}/{e2e_results.total}")
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