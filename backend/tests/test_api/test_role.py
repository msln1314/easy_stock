"""
角色管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestRoleAPI:
    """角色管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_role_list_endpoint_exists(self, session):
        """GET /api/v1/roles 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/roles")
        assert resp.status_code in [200, 401]

    def test_role_all_endpoint_exists(self, session):
        """GET /api/v1/roles/all 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/roles/all")
        assert resp.status_code in [200, 401]

    def test_role_detail_endpoint_exists(self, session):
        """GET /api/v1/roles/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/roles/1")
        assert resp.status_code in [200, 401, 404]

    def test_role_create_endpoint_exists(self, session):
        """POST /api/v1/roles 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/roles",
            json={"name": "test", "code": "test"}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_role_update_endpoint_exists(self, session):
        """PUT /api/v1/roles/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/roles/1",
            json={"name": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_role_delete_endpoint_exists(self, session):
        """DELETE /api/v1/roles/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/roles/999")
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_role_assign_menus_endpoint_exists(self, session):
        """PUT /api/v1/roles/{id}/menus 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/roles/1/menus",
            json={"menu_ids": []}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_role_list_requires_login(self, helper):
        """获取角色列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/roles")
        assert resp.status_code == 401

    def test_role_list_with_token(self, helper, admin_token):
        """登录用户可以获取角色列表"""
        resp = helper.test_auth_endpoint("/api/v1/roles", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_role_all_requires_admin(self, helper, user_token):
        """获取所有角色需要管理员权限"""
        # 无token应返回401
        resp_no_token = helper.test_public_endpoint("/api/v1/roles/all")
        assert resp_no_token.status_code == 401

        # 普通用户应返回403或401
        resp_user = helper.test_auth_endpoint("/api/v1/roles/all", user_token)
        assert resp_user.status_code in [401, 403]

    def test_role_create_requires_permission(self, helper, user_token):
        """创建角色需要权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/roles",
            user_token,
            method="POST",
            data={"name": "test_role", "code": "test_code"}
        )
        assert resp.status_code in [401, 403]

    def test_role_assign_menus_requires_permission(self, helper, user_token):
        """分配菜单权限需要权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/roles/1/menus",
            user_token,
            method="PUT",
            data={"menu_ids": [1, 2]}
        )
        assert resp.status_code in [401, 403]

    # ===== 参数验证测试 =====

    def test_role_create_missing_code(self, helper, admin_token):
        """创建角色缺少编码参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/roles",
            admin_token,
            method="POST",
            data={"name": "test_only"}
        )
        assert resp.status_code == 400

    def test_role_create_duplicate_code(self, helper, admin_token):
        """创建角色使用重复编码"""
        # admin角色编码已存在
        resp = helper.test_admin_endpoint(
            "/api/v1/roles",
            admin_token,
            method="POST",
            data={"name": "duplicate", "code": "admin"}
        )
        assert resp.status_code == 400

    def test_role_assign_menus_empty_list(self, helper, admin_token):
        """分配空菜单列表"""
        resp = helper.test_admin_endpoint(
            "/api/v1/roles/1/menus",
            admin_token,
            method="PUT",
            data={"menu_ids": []}
        )
        # 空列表应该是合法的
        assert resp.status_code in [200, 404]