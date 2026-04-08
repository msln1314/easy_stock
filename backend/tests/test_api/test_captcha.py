"""
验证码接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestCaptchaAPI:
    """验证码接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_get_captcha_endpoint_exists(self, session):
        """GET /api/v1/captcha 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/captcha")
        assert resp.status_code in [200, 400, 401]

    def test_verify_captcha_endpoint_exists(self, session):
        """POST /api/v1/captcha/verify 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/captcha/verify",
            params={"captcha_id": "test", "captcha_code": "test"}
        )
        assert resp.status_code in [200, 400, 401]

    # ===== 公开接口测试 =====

    def test_get_captcha_is_public(self, helper):
        """获取验证码接口应该是公开的"""
        resp = helper.test_public_endpoint("/api/v1/captcha")
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_verify_captcha_is_public(self, helper):
        """验证验证码接口应该是公开的"""
        resp = helper.test_public_endpoint(
            "/api/v1/captcha/verify",
            method="POST",
            data={"captcha_id": "test_id", "captcha_code": "test_code"}
        )
        # 可能返回400（验证码过期/错误）或200（验证成功）
        assert resp.status_code in [200, 400]

    # ===== 响应结构测试 =====

    def test_get_captcha_response_structure(self, helper):
        """验证码响应结构正确"""
        resp = helper.test_public_endpoint("/api/v1/captcha")
        assert resp.status_code == 200
        data = resp.json()
        assert "code" in data
        assert "message" in data
        assert "data" in data
        # 检查验证码数据结构
        captcha_data = data.get("data", {})
        assert "captcha_id" in captcha_data
        assert "image" in captcha_data

    def test_captcha_id_format(self, helper):
        """验证码ID格式正确"""
        resp = helper.test_public_endpoint("/api/v1/captcha")
        assert resp.status_code == 200
        data = resp.json()
        captcha_data = data.get("data", {})
        captcha_id = captcha_data.get("captcha_id")
        # 验证码ID应该是32位的字符串
        assert captcha_id is not None
        assert len(captcha_id) == 32

    def test_captcha_image_format(self, helper):
        """验证码图片格式正确"""
        resp = helper.test_public_endpoint("/api/v1/captcha")
        assert resp.status_code == 200
        data = resp.json()
        captcha_data = data.get("data", {})
        image = captcha_data.get("image")
        # 图片应该是base64编码的PNG
        assert image is not None
        assert image.startswith("data:image/png;base64,")

    # ===== 验证逻辑测试 =====

    def test_verify_expired_captcha(self, helper):
        """验证过期的验证码"""
        # 使用一个不存在/过期的captcha_id
        resp = helper.test_public_endpoint(
            "/api/v1/captcha/verify",
            method="POST",
            data={"captcha_id": "non_existent_id_12345", "captcha_code": "ABCD"}
        )
        assert resp.status_code == 400

    def test_verify_wrong_captcha(self, helper):
        """验证错误的验证码"""
        # 先获取验证码
        resp = helper.test_public_endpoint("/api/v1/captcha")
        assert resp.status_code == 200
        data = resp.json()
        captcha_id = data.get("data", {}).get("captcha_id")

        # 使用错误的验证码进行验证
        resp = helper.test_public_endpoint(
            "/api/v1/captcha/verify",
            method="POST",
            data={"captcha_id": captcha_id, "captcha_code": "WRONG"}
        )
        assert resp.status_code == 400

    def test_verify_missing_captcha_id(self, helper):
        """验证缺少captcha_id参数"""
        resp = helper.test_public_endpoint(
            "/api/v1/captcha/verify",
            method="POST",
            data={"captcha_code": "ABCD"}
        )
        # 缺少必要参数，应该返回错误
        assert resp.status_code in [400, 422]

    def test_verify_missing_captcha_code(self, helper):
        """验证缺少captcha_code参数"""
        resp = helper.test_public_endpoint(
            "/api/v1/captcha/verify",
            method="POST",
            data={"captcha_id": "test_id"}
        )
        # 缺少必要参数，应该返回错误
        assert resp.status_code in [400, 422]

    # ===== 多次获取验证码测试 =====

    def test_multiple_captcha_requests(self, helper):
        """多次获取验证码应该返回不同的ID"""
        resp1 = helper.test_public_endpoint("/api/v1/captcha")
        resp2 = helper.test_public_endpoint("/api/v1/captcha")

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        id1 = resp1.json().get("data", {}).get("captcha_id")
        id2 = resp2.json().get("data", {}).get("captcha_id")

        # 两次获取的验证码ID应该不同
        assert id1 != id2