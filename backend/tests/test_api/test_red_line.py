"""
交易红线接口测试
"""
import pytest
import requests
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper

class TestRedLineAPI:
    """交易红线接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_get_switch_exists(self, session):
        """GET /api/v1/red-line/switch 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/red-line/switch")
        assert resp.status_code in [200, 401]

    def test_set_switch_exists(self, session):
        """POST /api/v1/red-line/switch 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/red-line/switch",
            json={"enabled": True}
        )
        assert resp.status_code in [200, 401, 403]

    def test_get_rules_exists(self, session):
        """GET /api/v1/red-line/rules 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/red-line/rules")
        assert resp.status_code in [200, 401]

    def test_create_rule_exists(self, session):
        """POST /api/v1/red-line/rules 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/red-line/rules",
            json={}
        )
        assert resp.status_code in [200, 400, 401]

    def test_audit_test_exists(self, session):
        """POST /api/v1/red-line/audit/test 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/red-line/audit/test",
            json={"stock_code": "000001", "price": 10.0, "quantity": 100}
        )
        assert resp.status_code in [200, 400, 401]

    def test_get_statistics_exists(self, session):
        """GET /api/v1/red-line/statistics 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/red-line/statistics")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_get_switch_requires_login(self, helper):
        """获取红线开关需要登录"""
        resp = helper.test_public_endpoint("/api/v1/red-line/switch")
        assert resp.status_code == 401

    def test_set_switch_requires_admin(self, helper, admin_token, user_token):
        """设置红线开关需要管理员权限"""
        # 普通用户 → 403
        resp = helper.test_auth_endpoint(
            "/api/v1/red-line/switch",
            user_token,
            method="PUT",
            data={"enabled": True}
        )
        assert resp.status_code == 403

        # 管理员 → 200
        resp_admin = helper.test_admin_endpoint(
            "/api/v1/red-line/switch",
            admin_token,
            method="PUT",
            data={"enabled": True}
        )
        assert resp_admin.status_code == 200

    def test_audit_test_requires_login(self, helper):
        """测试红线校验需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/red-line/audit/test",
            method="POST",
            data={"stock_code": "000001", "price": 10.0, "quantity": 100}
        )
        assert resp.status_code == 401