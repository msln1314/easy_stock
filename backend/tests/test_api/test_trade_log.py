"""
交易日志接口测试
"""
import pytest
import requests
from datetime import datetime, timedelta
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper


class TestTradeLogAPI:
    """交易日志接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/v1/trade-log/list 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/trade-log/list")
        assert resp.status_code in [200, 401]

    def test_action_types_endpoint_exists(self, session):
        """GET /api/v1/trade-log/action-types 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/trade-log/action-types")
        assert resp.status_code in [200, 401]

    def test_statistics_endpoint_exists(self, session):
        """GET /api/v1/trade-log/statistics 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/trade-log/statistics")
        assert resp.status_code in [200, 401]

    def test_stats_endpoint_exists(self, session):
        """GET /api/v1/trade-log/stats 接口存在（别名）"""
        resp = session.get(f"{BASE_URL}/api/v1/trade-log/stats")
        assert resp.status_code in [200, 401]

    def test_by_type_endpoint_exists(self, session):
        """GET /api/v1/trade-log/by-type 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/trade-log/by-type")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_list_requires_login(self, helper):
        """获取日志列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/list")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取日志列表"""
        resp = helper.test_auth_endpoint("/api/v1/trade-log/list", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_action_types_requires_login(self, helper):
        """获取行为类型需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/action-types")
        assert resp.status_code == 401

    def test_action_types_with_token(self, helper, admin_token):
        """有token可以获取行为类型"""
        resp = helper.test_auth_endpoint("/api/v1/trade-log/action-types", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "types" in result

    def test_statistics_requires_login(self, helper):
        """获取统计数据需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/statistics")
        assert resp.status_code == 401

    def test_statistics_with_token(self, helper, admin_token):
        """有token可以获取统计数据"""
        resp = helper.test_auth_endpoint("/api/v1/trade-log/statistics", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        # 检查统计数据结构
        assert "period_days" in result
        assert "action_statistics" in result

    # ===== 响应结构测试 =====

    def test_list_response_structure(self, helper, admin_token):
        """日志列表响应结构正确"""
        resp = helper.test_auth_endpoint("/api/v1/trade-log/list", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "logs" in result
        assert "total" in result
        assert "limit" in result
        assert "offset" in result

    def test_statistics_response_structure(self, helper, admin_token):
        """统计数据响应结构正确"""
        resp = helper.test_auth_endpoint("/api/v1/trade-log/statistics", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "buy_statistics" in result
        assert "sell_statistics" in result
        assert "audit_statistics" in result

    # ===== 查询参数测试 =====

    def test_list_with_limit(self, helper, admin_token):
        """获取日志列表带limit参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/list?limit=10",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert result.get("limit") == 10

    def test_list_with_offset(self, helper, admin_token):
        """获取日志列表带offset参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/list?offset=5",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert result.get("offset") == 5

    def test_statistics_with_days(self, helper, admin_token):
        """获取统计数据带days参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/statistics?days=7",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert result.get("period_days") == 7

    def test_by_type_with_days(self, helper, admin_token):
        """按类型统计带days参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/by-type?days=7",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "period_days" in result
        assert "statistics" in result

    # ===== 详情接口测试 =====

    def test_detail_requires_login(self, helper):
        """获取日志详情需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/detail/1")
        assert resp.status_code == 401

    def test_detail_not_found(self, helper, admin_token):
        """获取不存在的日志详情"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/detail/999999",
            admin_token
        )
        assert resp.status_code == 404

    # ===== 订单相关日志测试 =====

    def test_order_logs_requires_login(self, helper):
        """获取订单日志需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/order/test123")
        assert resp.status_code == 401

    def test_order_logs_with_token(self, helper, admin_token):
        """有token可以获取订单日志"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/order/test_order_id",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "order_id" in result
        assert "logs" in result

    # ===== 股票相关日志测试 =====

    def test_stock_logs_requires_login(self, helper):
        """获取股票日志需要登录"""
        resp = helper.test_public_endpoint("/api/v1/trade-log/stock/000001")
        assert resp.status_code == 401

    def test_stock_logs_with_token(self, helper, admin_token):
        """有token可以获取股票日志"""
        resp = helper.test_auth_endpoint(
            "/api/v1/trade-log/stock/000001",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "stock_code" in result
        assert "logs" in result

    # ===== 每日汇总测试 =====

    def test_daily_summary_requires_login(self, helper):
        """获取每日汇总需要登录"""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = helper.test_public_endpoint(f"/api/v1/trade-log/summary/{today}")
        assert resp.status_code == 401

    def test_daily_summary_with_token(self, helper, admin_token):
        """有token可以获取每日汇总"""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = helper.test_auth_endpoint(
            f"/api/v1/trade-log/summary/{today}",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "summary_date" in result

    def test_range_summary_requires_login(self, helper):
        """获取时间段汇总需要登录"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp = helper.test_public_endpoint(
            f"/api/v1/trade-log/summary/range?start_date={yesterday}&end_date={today}"
        )
        assert resp.status_code == 401

    def test_range_summary_with_token(self, helper, admin_token):
        """有token可以获取时间段汇总"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp = helper.test_auth_endpoint(
            f"/api/v1/trade-log/summary/range?start_date={yesterday}&end_date={today}",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert "start_date" in result
        assert "end_date" in result
        assert "summaries" in result

    # ===== 生成汇总测试 =====

    def test_generate_summary_requires_login(self, helper):
        """生成每日汇总需要登录"""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = helper.test_public_endpoint(
            f"/api/v1/trade-log/summary/generate?summary_date={today}",
            method="POST"
        )
        assert resp.status_code == 401

    def test_generate_summary_with_token(self, helper, admin_token):
        """有token可以生成每日汇总"""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = helper.test_auth_endpoint(
            f"/api/v1/trade-log/summary/generate?summary_date={today}",
            admin_token,
            method="POST"
        )
        assert resp.status_code == 200