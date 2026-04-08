"""
策略接口测试
"""
import pytest
import requests
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper

class TestStrategyAPI:
    """策略接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_get_strategies_exists(self, session):
        """GET /api/v1/strategies 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/strategies")
        assert resp.status_code in [200, 401]

    def test_get_strategy_stats_exists(self, session):
        """GET /api/v1/strategies/stats 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/strategies/stats")
        assert resp.status_code in [200, 401]

    def test_get_strategy_detail_exists(self, session):
        """GET /api/v1/strategies/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/strategies/1")
        assert resp.status_code in [200, 401, 404]

    def test_create_strategy_exists(self, session):
        """POST /api/v1/strategies 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/strategies",
            json={}
        )
        assert resp.status_code in [200, 400, 401]

    def test_update_strategy_exists(self, session):
        """PUT /api/v1/strategies/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/strategies/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 404]

    def test_delete_strategy_exists(self, session):
        """DELETE /api/v1/strategies/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/strategies/999")
        assert resp.status_code in [200, 401, 404]

    # ===== 鉴权测试 =====

    def test_get_strategies_requires_login(self, helper):
        """获取策略列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/strategies")
        assert resp.status_code == 401

    def test_get_strategies_with_token(self, helper, admin_token):
        """有token可以获取策略列表"""
        resp = helper.test_auth_endpoint("/api/v1/strategies", admin_token)
        assert resp.status_code == 200

    def test_create_strategy_requires_login(self, helper):
        """创建策略需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/strategies",
            method="POST",
            data={}
        )
        assert resp.status_code == 401