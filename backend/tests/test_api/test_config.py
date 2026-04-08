"""
系统配置接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestConfigAPI:
    """系统配置接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_config_list_endpoint_exists(self, session):
        """GET /api/v1/configs 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/configs")
        assert resp.status_code in [200, 401]

    def test_config_public_endpoint_exists(self, session):
        """GET /api/v1/configs/public 接口存在（公开接口）"""
        resp = session.get(f"{BASE_URL}/api/v1/configs/public")
        assert resp.status_code == 200

    def test_config_by_category_endpoint_exists(self, session):
        """GET /api/v1/configs/category/{category} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/configs/category/basic")
        assert resp.status_code in [200, 401, 400]

    def test_config_detail_endpoint_exists(self, session):
        """GET /api/v1/configs/{key} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/configs/test_key")
        assert resp.status_code in [200, 401, 404]

    def test_config_create_endpoint_exists(self, session):
        """POST /api/v1/configs 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/configs",
            json={"key": "test", "value": "test"}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_config_update_endpoint_exists(self, session):
        """PUT /api/v1/configs/{key} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/configs/test_key",
            json={"value": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_config_delete_endpoint_exists(self, session):
        """DELETE /api/v1/configs/{key} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/configs/test_key")
        assert resp.status_code in [200, 401, 403, 404]

    def test_config_batch_update_endpoint_exists(self, session):
        """POST /api/v1/configs/batch 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/configs/batch",
            json={"test_key": "test_value"}
        )
        assert resp.status_code in [200, 401, 403]

    # ===== 鉴权测试 =====

    def test_config_public_is_public(self, helper):
        """公开配置接口无需认证"""
        resp = helper.test_public_endpoint("/api/v1/configs/public")
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_config_list_requires_login(self, helper):
        """获取配置列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/configs")
        assert resp.status_code == 401

    def test_config_list_with_token(self, helper, admin_token):
        """登录用户可以获取配置列表"""
        resp = helper.test_auth_endpoint("/api/v1/configs", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_config_create_requires_admin(self, helper, user_token):
        """创建配置需要管理员权限"""
        # 无token应返回401
        resp_no_token = helper.test_public_endpoint(
            "/api/v1/configs",
            method="POST",
            data={"key": "new_config", "value": "test"}
        )
        assert resp_no_token.status_code == 401

        # 普通用户应返回403或401
        resp_user = helper.test_auth_endpoint(
            "/api/v1/configs",
            user_token,
            method="POST",
            data={"key": "new_config", "value": "test"}
        )
        assert resp_user.status_code in [401, 403]

    def test_config_update_requires_admin(self, helper, user_token):
        """更新配置需要管理员权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/configs/test_key",
            user_token,
            method="PUT",
            data={"value": "updated"}
        )
        assert resp.status_code in [401, 403]

    def test_config_delete_requires_admin(self, helper, user_token):
        """删除配置需要管理员权限"""
        resp = helper.test_auth_endpoint(
            "/api/v1/configs/test_key",
            user_token,
            method="DELETE"
        )
        assert resp.status_code in [401, 403]

    # ===== 参数验证测试 =====

    def test_config_create_missing_key(self, helper, admin_token):
        """创建配置缺少key参数"""
        resp = helper.test_admin_endpoint(
            "/api/v1/configs",
            admin_token,
            method="POST",
            data={"value": "test"}
        )
        assert resp.status_code == 400

    def test_config_by_category_invalid(self, helper, admin_token):
        """使用无效类别获取配置"""
        resp = helper.test_admin_endpoint("/api/v1/configs/category/invalid_category", admin_token)
        assert resp.status_code == 400

    def test_config_batch_update_empty(self, helper, admin_token):
        """批量更新配置传入空对象"""
        resp = helper.test_admin_endpoint(
            "/api/v1/configs/batch",
            admin_token,
            method="POST",
            data={}
        )
        # 空对象可能成功或失败，取决于实现
        assert resp.status_code in [200, 400]