"""
持仓接口测试
"""
import pytest
import requests
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper

class TestPositionAPI:
    """持仓接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_fetch_positions_endpoint_exists(self, session):
        """GET /api/v1/position/list 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/list")
        assert resp.status_code in [200, 401]

    def test_fetch_balance_endpoint_exists(self, session):
        """GET /api/v1/position/balance 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/balance")
        assert resp.status_code in [200, 401]

    def test_fetch_today_trades_endpoint_exists(self, session):
        """GET /api/v1/position/trades/today 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/trades/today")
        assert resp.status_code in [200, 401]

    def test_fetch_today_entrusts_endpoint_exists(self, session):
        """GET /api/v1/position/entrusts/today 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/entrusts/today")
        assert resp.status_code in [200, 401]

    def test_fetch_stock_quote_endpoint_exists(self, session):
        """GET /api/v1/position/quote/{code} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/quote/000001")
        assert resp.status_code in [200, 401, 404]

    def test_quick_buy_endpoint_exists(self, session):
        """POST /api/v1/position/quick-buy 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/position/quick-buy",
            json={"stock_code": "000001", "quantity": 100}
        )
        assert resp.status_code in [200, 400, 401]

    def test_quick_sell_endpoint_exists(self, session):
        """POST /api/v1/position/quick-sell 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/position/quick-sell",
            json={"stock_code": "000001", "quantity": 100}
        )
        assert resp.status_code in [200, 400, 401]

    def test_cancel_order_endpoint_exists(self, session):
        """POST /api/v1/position/cancel 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/position/cancel",
            json={"order_id": "test123"}
        )
        assert resp.status_code in [200, 400, 401]

    # ===== 鉴权测试 =====

    def test_positions_requires_login(self, helper):
        """获取持仓需要登录"""
        resp = helper.test_public_endpoint("/api/v1/position/list")
        assert resp.status_code == 401

    def test_balance_requires_login(self, helper):
        """获取余额需要登录"""
        resp = helper.test_public_endpoint("/api/v1/position/balance")
        assert resp.status_code == 401

    def test_quick_buy_requires_login(self, helper):
        """快捷买入需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/position/quick-buy",
            method="POST",
            data={"stock_code": "000001", "quantity": 100}
        )
        assert resp.status_code == 401

    # ===== 参数验证测试 =====

    def test_quick_buy_missing_quantity(self, helper, admin_token):
        """快捷买入缺少数量"""
        resp = helper.test_auth_endpoint(
            "/api/v1/position/quick-buy",
            admin_token,
            method="POST",
            data={"stock_code": "000001"}
        )
        assert resp.status_code == 400