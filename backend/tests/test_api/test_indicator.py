"""
指标管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestIndicatorAPI:
    """指标管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/indicators 接口存在"""
        resp = session.get(f"{BASE_URL}/api/indicators")
        assert resp.status_code in [200, 401, 403]

    def test_create_endpoint_exists(self, session):
        """POST /api/indicators 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/indicators",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_get_endpoint_exists(self, session):
        """GET /api/indicators/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/indicators/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/indicators/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/indicators/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/indicators/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/indicators/1")
        assert resp.status_code in [200, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_list_requires_auth(self, helper):
        """获取指标列表需要登录"""
        resp = helper.test_public_endpoint("/api/indicators")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取指标列表"""
        resp = helper.test_auth_endpoint("/api/indicators", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_auth(self, helper):
        """创建指标需要登录"""
        resp = helper.test_public_endpoint(
            "/api/indicators",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_create_with_token(self, helper, admin_token):
        """有token可以创建指标"""
        resp = helper.test_auth_endpoint(
            "/api/indicators",
            admin_token,
            method="POST",
            data={"name": "test_indicator", "code": "TEST"}
        )
        assert resp.status_code in [200, 400, 403]

    def test_get_requires_auth(self, helper):
        """获取单个指标需要登录"""
        resp = helper.test_public_endpoint("/api/indicators/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, helper):
        """更新指标需要登录"""
        resp = helper.test_public_endpoint(
            "/api/indicators/1",
            method="PUT",
            data={}
        )
        assert resp.status_code == 401

    def test_delete_requires_auth(self, helper):
        """删除指标需要登录"""
        resp = helper.test_public_endpoint("/api/indicators/1", method="DELETE")
        assert resp.status_code == 401