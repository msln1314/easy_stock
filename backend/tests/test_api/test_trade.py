"""
交易接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper

class TestTradeAPI:
    """交易接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_fetch_positions_exists(self, session):
        """GET /api/v1/position/list 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/list")
        assert resp.status_code in [200, 401]

    def test_fetch_balance_exists(self, session):
        """GET /api/v1/position/balance 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/balance")
        assert resp.status_code in [200, 401]

    def test_buy_stock_exists(self, session):
        """POST /api/v1/position/buy 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/position/buy",
            json={"stock_code": "000001", "price": 10.0, "quantity": 100}
        )
        assert resp.status_code in [200, 400, 401]

    def test_sell_stock_exists(self, session):
        """POST /api/v1/position/sell 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/position/sell",
            json={"stock_code": "000001", "price": 10.0, "quantity": 100}
        )
        assert resp.status_code in [200, 400, 401]

    def test_trade_status_exists(self, session):
        """GET /api/v1/position/trade-status 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/trade-status")
        assert resp.status_code in [200, 401]

    def test_today_trades_exists(self, session):
        """GET /api/v1/position/trades/today 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/trades/today")
        assert resp.status_code in [200, 401]

    def test_today_entrusts_exists(self, session):
        """GET /api/v1/position/entrusts/today 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/position/entrusts/today")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_positions_requires_login(self, helper):
        """获取持仓需要登录"""
        resp = helper.test_public_endpoint("/api/v1/position/list")
        assert resp.status_code == 401

    def test_buy_requires_login(self, helper):
        """买入需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/position/buy",
            method="POST",
            data={"stock_code": "000001", "price": 10.0, "quantity": 100}
        )
        assert resp.status_code == 401

    def test_balance_requires_login(self, helper):
        """获取余额需要登录"""
        resp = helper.test_public_endpoint("/api/v1/position/balance")
        assert resp.status_code == 401

    # ===== 参数验证测试 =====

    def test_buy_missing_stock_code(self, helper, admin_token):
        """买入缺少股票代码"""
        resp = helper.test_auth_endpoint(
            "/api/v1/position/buy",
            admin_token,
            method="POST",
            data={"price": 10.0, "quantity": 100}
        )
        assert resp.status_code == 400