"""
pytest配置和fixtures
"""
import pytest
import requests
from test_config import BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD, USER_USERNAME, USER_PASSWORD

@pytest.fixture(scope="session")
def session():
    """创建requests session"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    s.close()

def _get_captcha_and_login(session, username, password):
    """获取验证码并登录"""
    # 获取验证码
    captcha_resp = session.get(f"{BASE_URL}/api/v1/captcha")
    if captcha_resp.status_code != 200:
        return None

    captcha_data = captcha_resp.json().get("data", {})
    captcha_id = captcha_data.get("captcha_id")

    # 登录
    login_resp = session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
            "captcha_id": captcha_id,
            "captcha_code": "1234"  # 测试环境可能使用固定验证码
        }
    )

    if login_resp.status_code == 200:
        data = login_resp.json()
        if isinstance(data, dict) and "data" in data:
            return data.get("data", {}).get("access_token")
        return data.get("access_token")

    # 如果验证码方式失败，尝试不带验证码登录（开发环境）
    login_resp = session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    if login_resp.status_code == 200:
        data = login_resp.json()
        if isinstance(data, dict) and "data" in data:
            return data.get("data", {}).get("access_token")
        return data.get("access_token")

    return None

@pytest.fixture(scope="session")
def admin_token(session):
    """获取管理员token"""
    token = _get_captcha_and_login(session, ADMIN_USERNAME, ADMIN_PASSWORD)
    if token:
        return token
    pytest.skip(f"管理员登录失败，跳过需要admin_token的测试")

@pytest.fixture(scope="session")
def user_token(session, admin_token):
    """获取普通用户token"""
    token = _get_captcha_and_login(session, USER_USERNAME, USER_PASSWORD)
    if token:
        return token

    # 如果登录失败，用管理员账号创建测试用户
    if admin_token:
        session.headers.update({"Authorization": f"Bearer {admin_token}"})
        create_resp = session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "username": USER_USERNAME,
                "password": USER_PASSWORD,
                "role": "user"
            }
        )
        session.headers.pop("Authorization", None)

        if create_resp.status_code in [200, 201]:
            token = _get_captcha_and_login(session, USER_USERNAME, USER_PASSWORD)
            if token:
                return token

    pytest.skip(f"普通用户登录失败，跳过需要user_token的测试")

@pytest.fixture
def auth_headers(admin_token):
    """返回认证headers"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    """返回普通用户认证headers"""
    return {"Authorization": f"Bearer {user_token}"}