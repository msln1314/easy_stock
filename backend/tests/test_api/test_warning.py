"""
预警管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper

class TestWarningAPI:
    """预警管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_indicators_endpoint_exists(self, session):
        """GET /api/warning/indicators 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/indicators")
        assert resp.status_code in [200, 401]

    def test_conditions_list_endpoint_exists(self, session):
        """GET /api/warning/conditions 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/conditions")
        assert resp.status_code in [200, 401]

    def test_conditions_create_endpoint_exists(self, session):
        """POST /api/warning/conditions 接口存在"""
        resp = session.post(f"{BASE_URL}/api/warning/conditions", json={})
        assert resp.status_code in [200, 400, 401, 422]

    def test_stocks_endpoint_exists(self, session):
        """GET /api/warning/stocks 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/stocks")
        assert resp.status_code in [200, 401]

    def test_conditions_init_endpoint_exists(self, session):
        """POST /api/warning/conditions/init 接口存在"""
        resp = session.post(f"{BASE_URL}/api/warning/conditions/init")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_indicators_requires_login(self, helper):
        """获取指标列表需要登录"""
        resp = helper.test_public_endpoint("/api/warning/indicators")
        assert resp.status_code == 401

    def test_conditions_requires_login(self, helper):
        """获取条件列表需要登录"""
        resp = helper.test_public_endpoint("/api/warning/conditions")
        assert resp.status_code == 401

    def test_stocks_requires_login(self, helper):
        """获取股票列表需要登录"""
        resp = helper.test_public_endpoint("/api/warning/stocks")
        assert resp.status_code == 401
