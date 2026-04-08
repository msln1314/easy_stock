"""
通知管理接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestNotificationAPI:
    """通知管理接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 通知渠道连通性测试 =====

    def test_notification_channels_endpoint_exists(self, session):
        """GET /api/notification/channels 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/channels")
        assert resp.status_code in [200, 401]

    def test_notification_channel_types_endpoint_exists(self, session):
        """GET /api/notification/channels/types 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/channels/types")
        assert resp.status_code in [200, 401]

    def test_notification_channel_create_endpoint_exists(self, session):
        """POST /api/notification/channels 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/notification/channels",
            json={"channel_type": "dingtalk", "channel_name": "test", "config": {}}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_notification_channel_update_endpoint_exists(self, session):
        """PUT /api/notification/channels/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/notification/channels/1",
            json={"channel_name": "updated"}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_notification_channel_delete_endpoint_exists(self, session):
        """DELETE /api/notification/channels/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/notification/channels/999")
        assert resp.status_code in [200, 401, 403, 404]

    def test_notification_channel_test_endpoint_exists(self, session):
        """POST /api/notification/channels/{id}/test 接口存在"""
        resp = session.post(f"{BASE_URL}/api/notification/channels/1/test")
        assert resp.status_code in [200, 400, 401, 403, 404]

    # ===== 通知记录连通性测试 =====

    def test_notification_logs_endpoint_exists(self, session):
        """GET /api/notification/logs 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/logs")
        assert resp.status_code in [200, 401]

    def test_notification_logs_stats_endpoint_exists(self, session):
        """GET /api/notification/logs/stats 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/logs/stats")
        assert resp.status_code in [200, 401]

    def test_notification_logs_clear_endpoint_exists(self, session):
        """DELETE /api/notification/logs 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/notification/logs")
        assert resp.status_code in [200, 401, 403]

    # ===== 通知模板连通性测试 =====

    def test_notification_templates_endpoint_exists(self, session):
        """GET /api/notification/templates 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/templates")
        assert resp.status_code in [200, 401]

    def test_notification_template_types_endpoint_exists(self, session):
        """GET /api/notification/templates/types 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/templates/types")
        assert resp.status_code in [200, 401]

    # ===== 通知对象连通性测试 =====

    def test_notification_recipients_endpoint_exists(self, session):
        """GET /api/notification/recipients 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/recipients")
        assert resp.status_code in [200, 401]

    def test_notification_recipient_groups_endpoint_exists(self, session):
        """GET /api/notification/recipient-groups 接口存在"""
        resp = session.get(f"{BASE_URL}/api/notification/recipient-groups")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_notification_channels_accessible(self, helper, admin_token):
        """获取通知渠道列表"""
        resp = helper.test_auth_endpoint("/api/notification/channels", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_notification_logs_accessible(self, helper, admin_token):
        """获取通知记录列表"""
        resp = helper.test_auth_endpoint("/api/notification/logs", admin_token)
        assert resp.status_code == 200

    def test_notification_logs_stats_accessible(self, helper, admin_token):
        """获取通知统计"""
        resp = helper.test_auth_endpoint("/api/notification/logs/stats", admin_token)
        assert resp.status_code == 200

    def test_notification_channel_create_with_admin(self, helper, admin_token):
        """管理员创建通知渠道"""
        resp = helper.test_admin_endpoint(
            "/api/notification/channels",
            admin_token,
            method="POST",
            data={
                "channel_type": "webhook",
                "channel_name": "test_webhook",
                "config": {"url": "https://example.com/webhook"}
            }
        )
        # 可能成功或失败(名称重复)
        assert resp.status_code in [200, 400]

    def test_notification_channel_test_with_admin(self, helper, admin_token):
        """管理员测试通知渠道"""
        resp = helper.test_admin_endpoint(
            "/api/notification/channels/1/test",
            admin_token,
            method="POST"
        )
        assert resp.status_code in [200, 400, 404]

    # ===== 参数验证测试 =====

    def test_notification_channel_create_invalid_type(self, helper, admin_token):
        """创建通知渠道使用无效类型"""
        resp = helper.test_admin_endpoint(
            "/api/notification/channels",
            admin_token,
            method="POST",
            data={"channel_type": "invalid_type", "channel_name": "test", "config": {}}
        )
        assert resp.status_code == 400

    def test_notification_channel_create_missing_name(self, helper, admin_token):
        """创建通知渠道缺少名称"""
        resp = helper.test_admin_endpoint(
            "/api/notification/channels",
            admin_token,
            method="POST",
            data={"channel_type": "dingtalk", "config": {}}
        )
        assert resp.status_code == 400

    def test_notification_recipient_create_missing_contact(self, helper, admin_token):
        """创建通知对象缺少联系方式"""
        resp = helper.test_admin_endpoint(
            "/api/notification/recipients",
            admin_token,
            method="POST",
            data={"name": "no_contact_user"}
        )
        assert resp.status_code == 400

    def test_notification_logs_stats_invalid_days(self, helper, admin_token):
        """获取通知统计使用无效天数"""
        resp = helper.test_admin_endpoint("/api/notification/logs/stats?days=100", admin_token)
        # days范围是1-30，超出应返回400或限制处理
        assert resp.status_code in [200, 400]