"""
认证接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper

class TestAuthAPI:
    """认证接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_login_endpoint_exists(self, session):
        """POST /api/v1/auth/login 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "test", "password": "test"}
        )
        assert resp.status_code in [200, 400, 401, 422]

    def test_register_endpoint_exists(self, session):
        """POST /api/v1/auth/register 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_profile_endpoint_exists(self, session):
        """GET /api/v1/auth/profile 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/auth/profile")
        assert resp.status_code in [200, 401]

    def test_refresh_endpoint_exists(self, session):
        """POST /api/v1/auth/refresh 接口存在"""
        resp = session.post(f"{BASE_URL}/api/v1/auth/refresh")
        assert resp.status_code in [200, 401]

    def test_logout_endpoint_exists(self, session):
        """POST /api/v1/auth/logout 接口存在"""
        resp = session.post(f"{BASE_URL}/api/v1/auth/logout")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_login_is_public(self, helper):
        """登录接口应该是公开的"""
        resp = helper.test_public_endpoint(
            "/api/v1/auth/login",
            method="POST",
            data={"username": "admin", "password": "wrong"}
        )
        assert resp.status_code in [400, 401, 422]

    def test_register_requires_admin(self, helper, admin_token, user_token):
        """注册接口需要管理员权限"""
        # 无token → 401
        resp_no_token = helper.test_public_endpoint(
            "/api/v1/auth/register",
            method="POST",
            data={}
        )
        assert resp_no_token.status_code == 401

        # 普通用户token → 403
        resp_user = helper.test_auth_endpoint(
            "/api/v1/auth/register",
            user_token,
            method="POST",
            data={}
        )
        assert resp_user.status_code == 403

        # 管理员token → 200/400
        resp_admin = helper.test_admin_endpoint(
            "/api/v1/auth/register",
            admin_token,
            method="POST",
            data={"username": "new_user", "password": "test123", "role": "user"}
        )
        assert resp_admin.status_code in [200, 400]

    def test_profile_requires_login(self, helper):
        """获取用户信息需要登录"""
        resp = helper.test_public_endpoint("/api/v1/auth/profile")
        assert resp.status_code == 401

    def test_profile_with_token(self, helper, admin_token):
        """有token可以获取用户信息"""
        resp = helper.test_auth_endpoint("/api/v1/auth/profile", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    # ===== 参数验证测试 =====

    def test_login_missing_password(self, helper):
        """登录缺少密码参数"""
        resp = helper.test_public_endpoint(
            "/api/v1/auth/login",
            method="POST",
            data={"username": "test"}
        )
        assert resp.status_code == 422

    def test_login_missing_username(self, helper):
        """登录缺少用户名参数"""
        resp = helper.test_public_endpoint(
            "/api/v1/auth/login",
            method="POST",
            data={"password": "test"}
        )
        assert resp.status_code == 422