"""
字典管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestDictAPI:
    """字典管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 字典类型连通性测试 =====

    def test_dict_types_list_endpoint_exists(self, session):
        """GET /api/v1/dict/types 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/dict/types")
        assert resp.status_code in [200, 401]

    def test_dict_types_detail_endpoint_exists(self, session):
        """GET /api/v1/dict/types/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/dict/types/1")
        assert resp.status_code in [200, 401, 404]

    def test_dict_types_create_endpoint_exists(self, session):
        """POST /api/v1/dict/types 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/dict/types",
            json={"code": "test", "name": "测试字典"}
        )
        assert resp.status_code in [200, 400, 401]

    def test_dict_types_update_endpoint_exists(self, session):
        """PUT /api/v1/dict/types/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/dict/types/1",
            json={"name": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 404]

    def test_dict_types_delete_endpoint_exists(self, session):
        """DELETE /api/v1/dict/types/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/dict/types/999")
        assert resp.status_code in [200, 401, 404]

    # ===== 字典项连通性测试 =====

    def test_dict_items_list_endpoint_exists(self, session):
        """GET /api/v1/dict/items 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/dict/items")
        assert resp.status_code in [200, 401]

    def test_dict_items_by_type_endpoint_exists(self, session):
        """GET /api/v1/dict/types/{code}/items 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/dict/types/test/items")
        assert resp.status_code in [200, 401, 404]

    def test_dict_items_tree_endpoint_exists(self, session):
        """GET /api/v1/dict/items/tree 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/dict/items/tree?type_id=1")
        assert resp.status_code in [200, 401, 404]

    def test_dict_items_create_endpoint_exists(self, session):
        """POST /api/v1/dict/items 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/dict/items",
            json={"type_id": 1, "code": "test", "name": "测试项"}
        )
        assert resp.status_code in [200, 400, 401, 404]

    # ===== 鉴权测试 =====

    def test_dict_types_requires_login(self, helper):
        """获取字典类型列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/dict/types")
        assert resp.status_code == 401

    def test_dict_types_with_token(self, helper, admin_token):
        """登录用户可以获取字典类型列表"""
        resp = helper.test_auth_endpoint("/api/v1/dict/types", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_dict_items_requires_login(self, helper):
        """获取字典项列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/dict/items")
        assert resp.status_code == 401

    def test_dict_items_with_token(self, helper, admin_token):
        """登录用户可以获取字典项列表"""
        resp = helper.test_auth_endpoint("/api/v1/dict/items", admin_token)
        assert resp.status_code == 200

    def test_dict_types_create_requires_login(self, helper):
        """创建字典类型需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/dict/types",
            method="POST",
            data={"code": "new_dict", "name": "新字典"}
        )
        assert resp.status_code == 401

    # ===== 参数验证测试 =====

    def test_dict_types_create_missing_code(self, helper, admin_token):
        """创建字典类型缺少编码参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/dict/types",
            admin_token,
            method="POST",
            data={"name": "no_code"}
        )
        assert resp.status_code == 400

    def test_dict_items_create_missing_type_id(self, helper, admin_token):
        """创建字典项缺少类型ID"""
        resp = helper.test_admin_endpoint(
            "/api/v1/dict/items",
            admin_token,
            method="POST",
            data={"code": "test_item", "name": "测试项"}
        )
        assert resp.status_code in [400, 404]

    def test_dict_items_tree_missing_type_id(self, helper, admin_token):
        """获取字典项树缺少类型ID"""
        resp = helper.test_admin_endpoint("/api/v1/dict/items/tree", admin_token)
        assert resp.status_code in [400, 404]