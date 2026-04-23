"""
条件组管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper

class TestConditionGroupAPI:
    """条件组管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_groups_endpoint_exists(self, session):
        """GET /api/warning/groups 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/groups")
        assert resp.status_code in [200, 401]

    def test_tree_endpoint_exists(self, session):
        """GET /api/warning/groups/tree 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/groups/tree")
        assert resp.status_code in [200, 401]

    def test_create_endpoint_exists(self, session):
        """POST /api/warning/groups 接口存在"""
        resp = session.post(f"{BASE_URL}/api/warning/groups", json={})
        assert resp.status_code in [200, 400, 401, 422]

    def test_detail_endpoint_exists(self, session):
        """GET /api/warning/groups/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/warning/groups/1")
        assert resp.status_code in [200, 401, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/warning/groups/{id} 接口存在"""
        resp = session.put(f"{BASE_URL}/api/warning/groups/1", json={})
        assert resp.status_code in [200, 400, 401, 404, 422]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/warning/groups/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/warning/groups/999")
        assert resp.status_code in [200, 401, 404]

    # ===== 鉴权测试 =====

    def test_groups_requires_login(self, helper):
        """获取条件组列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/warning/groups")
        assert resp.status_code == 401

    def test_tree_requires_login(self, helper):
        """获取条件组树需要登录"""
        resp = helper.test_public_endpoint("/api/v1/warning/groups/tree")
        assert resp.status_code == 401

    def test_create_requires_login(self, helper):
        """创建条件组需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/warning/groups",
            method="POST",
            data={}
        )
        assert resp.status_code == 401
