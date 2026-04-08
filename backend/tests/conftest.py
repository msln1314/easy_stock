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

@pytest.fixture(scope="session")
def admin_token(session):
    """获取管理员token"""
    resp = session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    if resp.status_code == 200:
        data = resp.json()
        # 兼容两种响应格式
        if isinstance(data, dict) and "data" in data:
            return data.get("data", {}).get("access_token")
        return data.get("access_token")
    pytest.skip(f"管理员登录失败，跳过需要admin_token的测试: {resp.text}")

@pytest.fixture(scope="session")
def user_token(session, admin_token):
    """获取普通用户token"""
    # 先尝试登录，如果失败则创建用户
    resp = session.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": USER_USERNAME, "password": USER_PASSWORD}
    )
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict) and "data" in data:
            return data.get("data", {}).get("access_token")
        return data.get("access_token")

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
            # 再次尝试登录
            resp = session.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": USER_USERNAME, "password": USER_PASSWORD}
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "data" in data:
                    return data.get("data", {}).get("access_token")
                return data.get("access_token")

    pytest.skip(f"普通用户登录失败，跳过需要user_token的测试")

@pytest.fixture
def auth_headers(admin_token):
    """返回认证headers"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    """返回普通用户认证headers"""
    return {"Authorization": f"Bearer {user_token}"}