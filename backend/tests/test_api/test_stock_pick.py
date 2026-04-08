"""
选股管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestStockPickAPI:
    """选股管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/stock-pick 接口存在"""
        resp = session.get(f"{BASE_URL}/api/stock-pick")
        assert resp.status_code in [200, 401, 403]

    def test_create_endpoint_exists(self, session):
        """POST /api/stock-pick 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/stock-pick",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_get_endpoint_exists(self, session):
        """GET /api/stock-pick/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/stock-pick/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/stock-pick/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/stock-pick/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/stock-pick/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/stock-pick/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_execute_endpoint_exists(self, session):
        """POST /api/stock-pick/{id}/execute 接口存在"""
        resp = session.post(f"{BASE_URL}/api/stock-pick/1/execute")
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_results_endpoint_exists(self, session):
        """GET /api/stock-pick/{id}/results 接口存在"""
        resp = session.get(f"{BASE_URL}/api/stock-pick/1/results")
        assert resp.status_code in [200, 401, 403, 404]

    def test_history_endpoint_exists(self, session):
        """GET /api/stock-pick/history 接口存在"""
        resp = session.get(f"{BASE_URL}/api/stock-pick/history")
        assert resp.status_code in [200, 401, 403]

    # ===== 鉴权测试 =====

    def test_list_requires_auth(self, helper):
        """获取选股策略列表需要登录"""
        resp = helper.test_public_endpoint("/api/stock-pick")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取选股策略列表"""
        resp = helper.test_auth_endpoint("/api/stock-pick", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_auth(self, helper):
        """创建选股策略需要登录"""
        resp = helper.test_public_endpoint(
            "/api/stock-pick",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_create_with_token(self, helper, admin_token):
        """有token可以创建选股策略"""
        resp = helper.test_auth_endpoint(
            "/api/stock-pick",
            admin_token,
            method="POST",
            data={"name": "test_strategy", "conditions": []}
        )
        assert resp.status_code in [200, 400, 403]

    def test_get_requires_auth(self, helper):
        """获取单个选股策略需要登录"""
        resp = helper.test_public_endpoint("/api/stock-pick/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, helper):
        """更新选股策略需要登录"""
        resp = helper.test_public_endpoint(
            "/api/stock-pick/1",
            method="PUT",
            data={}
        )
        assert resp.status_code == 401

    def test_delete_requires_auth(self, helper):
        """删除选股策略需要登录"""
        resp = helper.test_public_endpoint("/api/stock-pick/1", method="DELETE")
        assert resp.status_code == 401

    def test_execute_requires_auth(self, helper):
        """执行选股策略需要登录"""
        resp = helper.test_public_endpoint(
            "/api/stock-pick/1/execute",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_execute_with_token(self, helper, admin_token):
        """有token可以执行选股策略"""
        resp = helper.test_auth_endpoint(
            "/api/stock-pick/1/execute",
            admin_token,
            method="POST",
            data={}
        )
        assert resp.status_code in [200, 400, 403, 404]

    def test_results_requires_auth(self, helper):
        """获取选股结果需要登录"""
        resp = helper.test_public_endpoint("/api/stock-pick/1/results")
        assert resp.status_code == 401

    def test_results_with_token(self, helper, admin_token):
        """有token可以获取选股结果"""
        resp = helper.test_auth_endpoint("/api/stock-pick/1/results", admin_token)
        assert resp.status_code in [200, 404]

    def test_history_requires_auth(self, helper):
        """获取选股历史需要登录"""
        resp = helper.test_public_endpoint("/api/stock-pick/history")
        assert resp.status_code == 401

    def test_history_with_token(self, helper, admin_token):
        """有token可以获取选股历史"""
        resp = helper.test_auth_endpoint("/api/stock-pick/history", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)