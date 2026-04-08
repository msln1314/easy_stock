"""
条件组接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestConditionGroupAPI:
    """条件组接口测试"""

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
        resp = session.post(
            f"{BASE_URL}/api/warning/groups",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    # ===== 鉴权测试 =====

    def test_groups_requires_login(self, helper):
        """获取条件组列表需要登录"""
        resp = helper.test_public_endpoint("/api/warning/groups")
        assert resp.status_code == 401

    def test_groups_with_token(self, helper, admin_token):
        """有token可以获取条件组列表"""
        resp = helper.test_auth_endpoint("/api/warning/groups", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_tree_requires_login(self, helper):
        """获取条件组树形结构需要登录"""
        resp = helper.test_public_endpoint("/api/warning/groups/tree")
        assert resp.status_code == 401

    def test_tree_with_token(self, helper, admin_token):
        """有token可以获取条件组树形结构"""
        resp = helper.test_auth_endpoint("/api/warning/groups/tree", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_login(self, helper):
        """创建条件组需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups",
            method="POST",
            data={"group_name": "test", "logic_type": "AND"}
        )
        assert resp.status_code == 401

    # ===== 响应结构测试 =====

    def test_groups_response_structure(self, helper, admin_token):
        """条件组列表响应结构正确"""
        resp = helper.test_auth_endpoint("/api/warning/groups", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        assert "code" in data
        assert "message" in data
        assert "data" in data

    def test_tree_response_structure(self, helper, admin_token):
        """条件组树形结构响应正确"""
        resp = helper.test_auth_endpoint("/api/warning/groups/tree", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        assert "code" in data
        assert "message" in data

    # ===== 查询参数测试 =====

    def test_groups_with_parent_id(self, helper, admin_token):
        """获取条件组带parent_id参数"""
        resp = helper.test_auth_endpoint(
            "/api/warning/groups?parent_id=1",
            admin_token
        )
        assert resp.status_code == 200

    # ===== 详情接口测试 =====

    def test_detail_requires_login(self, helper):
        """获取条件组详情需要登录"""
        resp = helper.test_public_endpoint("/api/warning/groups/1")
        assert resp.status_code == 401

    def test_detail_not_found(self, helper, admin_token):
        """获取不存在的条件组详情"""
        resp = helper.test_auth_endpoint(
            "/api/warning/groups/999999",
            admin_token
        )
        assert resp.status_code == 404

    def test_detail_with_token(self, helper, admin_token):
        """有token可以获取条件组详情"""
        # 先尝试获取存在的条件组，如果没有则跳过
        resp = helper.test_auth_endpoint("/api/warning/groups/1", admin_token)
        # 可能是404（不存在）或200（存在）
        assert resp.status_code in [200, 404]

    # ===== 更新接口测试 =====

    def test_update_requires_login(self, helper):
        """更新条件组需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1",
            method="PUT",
            data={"group_name": "test"}
        )
        assert resp.status_code == 401

    def test_update_not_found(self, helper, admin_token):
        """更新不存在的条件组"""
        resp = helper.test_auth_endpoint(
            "/api/warning/groups/999999",
            admin_token,
            method="PUT",
            data={"group_name": "test"}
        )
        assert resp.status_code == 404

    # ===== 删除接口测试 =====

    def test_delete_requires_login(self, helper):
        """删除条件组需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1",
            method="DELETE"
        )
        assert resp.status_code == 401

    def test_delete_not_found(self, helper, admin_token):
        """删除不存在的条件组"""
        resp = helper.test_auth_endpoint(
            "/api/warning/groups/999999",
            admin_token,
            method="DELETE"
        )
        assert resp.status_code == 404

    # ===== 条件项接口测试 =====

    def test_add_item_requires_login(self, helper):
        """添加条件项需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1/items",
            method="POST",
            data={"condition_id": 1}
        )
        assert resp.status_code == 401

    def test_remove_item_requires_login(self, helper):
        """移除条件项需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1/items/1",
            method="DELETE"
        )
        assert resp.status_code == 401

    def test_reorder_items_requires_login(self, helper):
        """重新排序条件项需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1/items/reorder",
            method="PUT",
            data=[1, 2, 3]
        )
        assert resp.status_code == 401

    # ===== 子分组接口测试 =====

    def test_create_subgroup_requires_login(self, helper):
        """创建子分组需要登录"""
        resp = helper.test_public_endpoint(
            "/api/warning/groups/1/subgroups",
            method="POST",
            data={"group_name": "test", "logic_type": "AND"}
        )
        assert resp.status_code == 401

    def test_create_subgroup_parent_not_found(self, helper, admin_token):
        """创建子分组时父分组不存在"""
        resp = helper.test_auth_endpoint(
            "/api/warning/groups/999999/subgroups",
            admin_token,
            method="POST",
            data={"group_name": "test", "logic_type": "AND"}
        )
        assert resp.status_code == 404