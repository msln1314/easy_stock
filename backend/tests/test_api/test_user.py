"""
用户管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestUserAPI:
    """用户管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_user_list_endpoint_exists(self, session):
        """GET /api/v1/users 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/users")
        assert resp.status_code in [200, 401]

    def test_user_all_endpoint_exists(self, session):
        """GET /api/v1/users/all 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/users/all")
        assert resp.status_code in [200, 401]

    def test_user_detail_endpoint_exists(self, session):
        """GET /api/v1/users/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/users/1")
        assert resp.status_code in [200, 401, 404]

    def test_user_create_endpoint_exists(self, session):
        """POST /api/v1/users 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/users",
            json={"username": "test", "password": "test123"}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_user_update_endpoint_exists(self, session):
        """PUT /api/v1/users/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/users/1",
            json={"nickname": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_user_delete_endpoint_exists(self, session):
        """DELETE /api/v1/users/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/users/999")
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_user_reset_password_endpoint_exists(self, session):
        """PUT /api/v1/users/{id}/password 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/users/1/password",
            json={"new_password": "newpass123"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_user_assign_roles_endpoint_exists(self, session):
        """PUT /api/v1/users/{id}/roles 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/users/1/roles",
            json={"role_ids": [1]}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_user_list_requires_login(self, helper):
        """获取用户列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/users")
        assert resp.status_code == 401

    def test_user_list_with_token(self, helper, admin_token):
        """登录用户可以获取用户列表"""
        resp = helper.test_auth_endpoint("/api/v1/users", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_user_all_requires_admin(self, helper, user_token):
        """获取所有用户需要管理员权限"""
        # 无token应返回401
        resp_no_token = helper.test_public_endpoint("/api/v1/users/all")
        assert resp_no_token.status_code == 401

        # 普通用户应返回403或401
        resp_user = helper.test_auth_endpoint("/api/v1/users/all", user_token)
        assert resp_user.status_code in [401, 403]

    def test_user_create_requires_permission(self, helper, user_token):
        """创建用户需要权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/users",
            user_token,
            method="POST",
            data={"username": "new_user", "password": "test123"}
        )
        assert resp.status_code in [401, 403]

    def test_user_delete_requires_permission(self, helper, user_token):
        """删除用户需要权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/users/999",
            user_token,
            method="DELETE"
        )
        assert resp.status_code in [401, 403]

    # ===== 参数验证测试 =====

    def test_user_create_missing_password(self, helper, admin_token):
        """创建用户缺少密码参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/users",
            admin_token,
            method="POST",
            data={"username": "no_pass_user"}
        )
        assert resp.status_code == 400

    def test_user_create_missing_username(self, helper, admin_token):
        """创建用户缺少用户名参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/users",
            admin_token,
            method="POST",
            data={"password": "test123"}
        )
        assert resp.status_code == 400

    def test_user_create_duplicate_username(self, helper, admin_token):
        """创建用户使用重复用户名"""
        resp = helper.test_admin_endpoint(
            "/api/v1/users",
            admin_token,
            method="POST",
            data={"username": "admin", "password": "test123"}
        )
        assert resp.status_code == 400

    def test_user_delete_admin_account(self, helper, admin_token):
        """删除admin账户应失败"""
        resp = helper.test_admin_endpoint(
            "/api/v1/users/1",
            admin_token,
            method="DELETE"
        )
        # admin账户不能删除
        assert resp.status_code in [400, 403, 404]