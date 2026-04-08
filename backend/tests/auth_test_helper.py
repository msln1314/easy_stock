"""
鉴权测试辅助工具
"""
import requests
from typing import Optional, Dict
from tests.config import BASE_URL, REQUEST_TIMEOUT

class AuthTestHelper:
    """鉴权测试辅助类"""

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_public_endpoint(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> requests.Response:
        """测试公开接口(无需token)"""
        url = f"{BASE_URL}{path}"

        if method.upper() == "GET":
            return self.session.get(url, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "POST":
            return self.session.post(url, json=data or {}, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "PUT":
            return self.session.put(url, json=data or {}, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "DELETE":
            return self.session.delete(url, timeout=REQUEST_TIMEOUT)
        else:
            raise ValueError(f"不支持的方法: {method}")

    def test_auth_endpoint(
        self,
        path: str,
        token: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> requests.Response:
        """测试需要登录的接口"""
        url = f"{BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {token}"}

        if method.upper() == "GET":
            return self.session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "POST":
            return self.session.post(url, json=data or {}, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "PUT":
            return self.session.put(url, json=data or {}, headers=headers, timeout=REQUEST_TIMEOUT)
        elif method.upper() == "DELETE":
            return self.session.delete(url, headers=headers, timeout=REQUEST_TIMEOUT)
        else:
            raise ValueError(f"不支持的方法: {method}")

    def test_admin_endpoint(
        self,
        path: str,
        admin_token: str,
        method: str = "GET",
        data: Optional[Dict] = None
    ) -> requests.Response:
        """测试需要管理员的接口"""
        return self.test_auth_endpoint(path, admin_token, method, data)

    def login(self, username: str, password: str) -> Optional[str]:
        """登录获取token"""
        resp = self.session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )

        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("access_token")
        return None

    def validate_response_structure(self, response: requests.Response) -> bool:
        """验证响应结构是否包含必要字段"""
        try:
            data = response.json()
            return "code" in data and "message" in data
        except:
            return False