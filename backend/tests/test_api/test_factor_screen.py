"""
因子筛选接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestFactorScreenAPI:
    """因子筛选接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/factor-screen 接口存在"""
        resp = session.get(f"{BASE_URL}/api/factor-screen")
        assert resp.status_code in [200, 401, 403]

    def test_create_endpoint_exists(self, session):
        """POST /api/factor-screen 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/factor-screen",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_get_endpoint_exists(self, session):
        """GET /api/factor-screen/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/factor-screen/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/factor-screen/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/factor-screen/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/factor-screen/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/factor-screen/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_screen_endpoint_exists(self, session):
        """POST /api/factor-screen/screen 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/factor-screen/screen",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_factors_endpoint_exists(self, session):
        """GET /api/factor-screen/factors 接口存在"""
        resp = session.get(f"{BASE_URL}/api/factor-screen/factors")
        assert resp.status_code in [200, 401, 403]

    # ===== 鉴权测试 =====

    def test_list_requires_auth(self, helper):
        """获取因子筛选列表需要登录"""
        resp = helper.test_public_endpoint("/api/factor-screen")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取因子筛选列表"""
        resp = helper.test_auth_endpoint("/api/factor-screen", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_auth(self, helper):
        """创建因子筛选需要登录"""
        resp = helper.test_public_endpoint(
            "/api/factor-screen",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_create_with_token(self, helper, admin_token):
        """有token可以创建因子筛选"""
        resp = helper.test_auth_endpoint(
            "/api/factor-screen",
            admin_token,
            method="POST",
            data={"name": "test_screen", "factors": []}
        )
        assert resp.status_code in [200, 400, 403]

    def test_get_requires_auth(self, helper):
        """获取单个因子筛选需要登录"""
        resp = helper.test_public_endpoint("/api/factor-screen/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, helper):
        """更新因子筛选需要登录"""
        resp = helper.test_public_endpoint(
            "/api/factor-screen/1",
            method="PUT",
            data={}
        )
        assert resp.status_code == 401

    def test_delete_requires_auth(self, helper):
        """删除因子筛选需要登录"""
        resp = helper.test_public_endpoint("/api/factor-screen/1", method="DELETE")
        assert resp.status_code == 401

    def test_screen_requires_auth(self, helper):
        """执行因子筛选需要登录"""
        resp = helper.test_public_endpoint(
            "/api/factor-screen/screen",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_screen_with_token(self, helper, admin_token):
        """有token可以执行因子筛选"""
        resp = helper.test_auth_endpoint(
            "/api/factor-screen/screen",
            admin_token,
            method="POST",
            data={"factors": []}
        )
        assert resp.status_code in [200, 400, 403]

    def test_factors_requires_auth(self, helper):
        """获取可用因子列表需要登录"""
        resp = helper.test_public_endpoint("/api/factor-screen/factors")
        assert resp.status_code == 401

    def test_factors_with_token(self, helper, admin_token):
        """有token可以获取可用因子列表"""
        resp = helper.test_auth_endpoint("/api/factor-screen/factors", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)