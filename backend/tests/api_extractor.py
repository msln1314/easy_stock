"""
FastAPI OpenAPI文档解析器
"""
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class AuthLevel(Enum):
    """鉴权级别"""
    PUBLIC = "PUBLIC"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    ADMIN_REQUIRED = "ADMIN_REQUIRED"

@dataclass
class APIInfo:
    """API信息结构"""
    path: str
    method: str
    parameters: Dict
    auth_level: AuthLevel
    tags: List[str]
    summary: str
    operation_id: str

class APIExtractor:
    """从FastAPI OpenAPI文档提取API信息"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.openapi_url = f"{base_url}/openapi.json"
        self._schema: Optional[Dict] = None

    def fetch_openapi_schema(self) -> Dict:
        """获取OpenAPI JSON文档"""
        resp = requests.get(self.openapi_url, timeout=10)
        resp.raise_for_status()
        self._schema = resp.json()
        return self._schema

    def determine_auth_level(self, path: str, method: str, operation: Dict) -> AuthLevel:
        """判断接口鉴权级别"""
        security = operation.get("security", [])

        if not security:
            return AuthLevel.PUBLIC

        # 检查是否需要管理员权限
        for sec_req in security:
            if "admin" in sec_req.get("OAuth2PasswordBearer", []):
                return AuthLevel.ADMIN_REQUIRED

        return AuthLevel.LOGIN_REQUIRED

    def extract_all_apis(self) -> List[APIInfo]:
        """提取所有API路由信息"""
        if not self._schema:
            self.fetch_openapi_schema()

        apis = []
        paths = self._schema.get("paths", {})

        for path, path_item in paths.items():
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item:
                    operation = path_item[method]

                    api_info = APIInfo(
                        path=path,
                        method=method.upper(),
                        parameters=operation.get("parameters", []),
                        auth_level=self.determine_auth_level(path, method, operation),
                        tags=operation.get("tags", []),
                        summary=operation.get("summary", ""),
                        operation_id=operation.get("operationId", "")
                    )
                    apis.append(api_info)

        return apis

    def get_api_by_path(self, path: str, method: str) -> Optional[APIInfo]:
        """根据路径和方法获取API信息"""
        apis = self.extract_all_apis()
        for api in apis:
            if api.path == path and api.method == method.upper():
                return api
        return None