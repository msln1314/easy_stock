"""
API Key 同步服务
从 backend 同步有效的 API Keys
"""
import httpx
import logging
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.auth import init_api_keys, add_api_key, remove_api_key

logger = logging.getLogger(__name__)


class KeySyncService:
    """API Key 同步服务"""

    def __init__(self):
        self._backend_url: Optional[str] = None
        self._sync_interval: int = 60  # 同步间隔（秒）
        self._last_sync: Optional[datetime] = None

    async def init_from_backend(self, backend_url: str):
        """
        从 backend 初始化 API Keys

        Args:
            backend_url: backend 服务地址，如 http://localhost:8030
        """
        self._backend_url = backend_url
        await self.sync_keys()

    async def sync_keys(self) -> List[str]:
        """
        同步 API Keys

        Returns:
            List[str]: 获取到的有效 API Keys
        """
        if not self._backend_url:
            logger.warning("未配置 backend URL，无法同步 API Keys")
            return []

        try:
            # 从 backend 获取所有启用的 MCP 配置
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 需要管理员权限的接口，使用内部同步 Key
                sync_key = settings.INTERNAL_SYNC_KEY or "internal_sync_key"
                response = await client.get(
                    f"{self._backend_url}/api/v1/mcp/internal/keys",
                    headers={"X-Internal-Key": sync_key}
                )

                if response.status_code == 200:
                    data = response.json()
                    keys = data.get("keys", [])
                    init_api_keys(keys)
                    self._last_sync = datetime.now()
                    logger.info(f"成功同步 {len(keys)} 个 API Keys")
                    return keys
                else:
                    logger.warning(f"同步 API Keys 失败: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"同步 API Keys 异常: {e}")
            return []

    async def add_key_from_backend(self, service_name: str) -> bool:
        """
        从 backend 添加单个服务的 API Key

        Args:
            service_name: 服务名称

        Returns:
            bool: 是否成功添加
        """
        if not self._backend_url:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                sync_key = settings.INTERNAL_SYNC_KEY or "internal_sync_key"
                response = await client.get(
                    f"{self._backend_url}/api/v1/mcp/keys/{service_name}",
                    headers={"X-Internal-Key": sync_key}
                )

                if response.status_code == 200:
                    data = response.json()
                    api_key = data.get("api_key")
                    if api_key:
                        add_api_key(api_key)
                        logger.info(f"成功添加服务 {service_name} 的 API Key")
                        return True
                return False

        except Exception as e:
            logger.error(f"添加 API Key 异常: {e}")
            return False


# 单例
key_sync_service = KeySyncService()