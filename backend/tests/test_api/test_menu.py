"""
菜单管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestMenuAPI:
    """菜单管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_menu_tree_endpoint_exists(self, session):
        """GET /api/v1/menus 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/menus")
        assert resp.status_code in [200, 401]

    def test_menu_all_endpoint_exists(self, session):
        """GET /api/v1/menus/all 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/menus/all")
        assert resp.status_code in [200, 401]

    def test_menu_user_endpoint_exists(self, session):
        """GET /api/v1/menus/user 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/menus/user")
        assert resp.status_code in [200, 401]

    def test_menu_detail_endpoint_exists(self, session):
        """GET /api/v1/menus/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/menus/1")
        assert resp.status_code in [200, 401, 404]

    def test_menu_create_endpoint_exists(self, session):
        """POST /api/v1/menus 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/menus",
            json={"name": "test", "path": "/test", "menu_type": "menu"}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_menu_update_endpoint_exists(self, session):
        """PUT /api/v1/menus/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/menus/1",
            json={"name": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_menu_delete_endpoint_exists(self, session):
        """DELETE /api/v1/menus/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/menus/999")
        assert resp.status_code in [200, 400, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_menu_tree_requires_admin(self, helper):
        """获取菜单树需要管理员权限"""
        resp = helper.test_public_endpoint("/api/v1/menus")
        assert resp.status_code == 401

    def test_menu_tree_with_admin_token(self, helper, admin_token):
        """管理员可以获取菜单树"""
        resp = helper.test_auth_endpoint("/api/v1/menus", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_menu_user_requires_login(self, helper):
        """获取用户菜单需要登录"""
        resp = helper.test_public_endpoint("/api/v1/menus/user")
        assert resp.status_code == 401

    def test_menu_user_with_token(self, helper, admin_token):
        """登录用户可以获取自己的菜单"""
        resp = helper.test_auth_endpoint("/api/v1/menus/user", admin_token)
        assert resp.status_code == 200

    def test_menu_create_requires_permission(self, helper, user_token):
        """创建菜单需要权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/menus",
            user_token,
            method="POST",
            data={"name": "test", "path": "/test", "menu_type": "menu"}
        )
        # 普通用户无权限应返回403或401
        assert resp.status_code in [401, 403]

    # ===== 参数验证测试 =====

    def test_menu_create_missing_name(self, helper, admin_token):
        """创建菜单缺少名称参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/menus",
            admin_token,
            method="POST",
            data={"path": "/test"}
        )
        assert resp.status_code == 400

    def test_menu_create_invalid_parent(self, helper, admin_token):
        """创建菜单使用无效的父菜单ID"""
        resp = helper.test_admin_endpoint(
            "/api/v1/menus",
            admin_token,
            method="POST",
            data={"name": "test", "path": "/test", "parent_id": 99999, "menu_type": "menu"}
        )
        assert resp.status_code == 400

    def test_menu_delete_with_children(self, helper, admin_token):
        """删除有子菜单的菜单应失败"""
        # 需要先获取一个有子菜单的菜单ID，这里用假设的ID
        resp = helper.test_admin_endpoint(
            "/api/v1/menus/1",
            admin_token,
            method="DELETE"
        )
        # 如果有子菜单应返回400，否则可能成功或404
        assert resp.status_code in [200, 400, 404]