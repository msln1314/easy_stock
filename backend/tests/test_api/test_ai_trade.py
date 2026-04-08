"""
AI交易接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestAITradeAPI:
    """AI交易接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_chat_endpoint_exists(self, session):
        """POST /api/v1/ai/chat 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/ai/chat",
            json={"message": "test"}
        )
        assert resp.status_code in [200, 400, 401]

    def test_history_endpoint_exists(self, session):
        """GET /api/v1/ai/history 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/ai/history")
        assert resp.status_code in [200, 401]

    # ===== 鉴权测试 =====

    def test_chat_requires_login(self, helper):
        """AI聊天接口需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/ai/chat",
            method="POST",
            data={"message": "你好"}
        )
        assert resp.status_code == 401

    def test_chat_with_token(self, helper, admin_token):
        """有token可以进行AI聊天"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/chat",
            admin_token,
            method="POST",
            data={"message": "查询平安银行行情"}
        )
        assert resp.status_code in [200, 400]
        if resp.status_code == 200:
            assert helper.validate_response_structure(resp)

    def test_history_requires_login(self, helper):
        """获取聊天历史需要登录"""
        resp = helper.test_public_endpoint("/api/v1/ai/history")
        assert resp.status_code == 401

    def test_history_with_token(self, helper, admin_token):
        """有token可以获取聊天历史"""
        resp = helper.test_auth_endpoint("/api/v1/ai/history", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    # ===== 参数验证测试 =====

    def test_chat_missing_message(self, helper, admin_token):
        """AI聊天缺少消息参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/chat",
            admin_token,
            method="POST",
            data={}
        )
        assert resp.status_code == 400

    def test_chat_empty_message(self, helper, admin_token):
        """AI聊天消息为空"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/chat",
            admin_token,
            method="POST",
            data={"message": ""}
        )
        assert resp.status_code == 400

    def test_chat_whitespace_message(self, helper, admin_token):
        """AI聊天消息只有空白字符"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/chat",
            admin_token,
            method="POST",
            data={"message": "   "}
        )
        assert resp.status_code == 400

    # ===== 响应结构测试 =====

    def test_chat_response_structure(self, helper, admin_token):
        """AI聊天响应结构正确"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/chat",
            admin_token,
            method="POST",
            data={"message": "你好"}
        )
        if resp.status_code == 200:
            data = resp.json()
            assert "code" in data
            assert "message" in data
            assert "data" in data

    def test_history_response_structure(self, helper, admin_token):
        """聊天历史响应结构正确"""
        resp = helper.test_auth_endpoint("/api/v1/ai/history", admin_token)
        assert resp.status_code == 200
        data = resp.json()
        assert "code" in data
        assert "message" in data
        assert "data" in data
        # 检查返回的数据结构
        result = data.get("data", {})
        assert "messages" in result
        assert "total" in result

    # ===== 查询参数测试 =====

    def test_history_with_limit(self, helper, admin_token):
        """获取聊天历史带limit参数"""
        resp = helper.test_auth_endpoint(
            "/api/v1/ai/history?limit=10",
            admin_token
        )
        assert resp.status_code == 200
        data = resp.json()
        result = data.get("data", {})
        assert isinstance(result.get("messages"), list)