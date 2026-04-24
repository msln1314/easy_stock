"""
qmt-service API Key 认证

通过调用 Backend 验证 API Key 并获取用户信息
"""
import httpx
import logging
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Optional, Dict, Any
from functools import lru_cache
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 用户信息缓存（减少 Backend 调用）
_user_cache: Dict[str, Dict[str, Any]] = {}
_cache_expire: Dict[str, float] = {}
CACHE_TTL = 300  # 缓存 5 分钟


async def verify_api_key_with_backend(api_key: str) -> Optional[Dict[str, Any]]:
    """
    调用 Backend 验证 API Key 并获取用户信息

    Args:
        api_key: 用户 API Key

    Returns:
        用户信息字典，验证失败返回 None
    """
    # 检查缓存
    if api_key in _user_cache and api_key in _cache_expire:
        if time.time() < _cache_expire[api_key]:
            return _user_cache[api_key]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.BACKEND_URL}/api/v1/internal/verify-api-key",
                headers={
                    "X-API-Key": api_key,
                    "X-Internal-Key": settings.INTERNAL_SYNC_KEY
                }
            )

            if response.status_code == 200:
                data = response.json()
                user_info = data.get("data")
                # 缓存用户信息
                _user_cache[api_key] = user_info
                _cache_expire[api_key] = time.time() + CACHE_TTL
                return user_info
            else:
                logger.warning(f"API Key 验证失败: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"调用 Backend 验证 API Key 异常: {e}")
        return None


async def sync_api_keys_from_backend() -> list:
    """
    从 Backend 同步所有有效的 API Keys

    Returns:
        API Key 列表
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.BACKEND_URL}/api/v1/internal/sync-api-keys",
                headers={
                    "X-Internal-Key": settings.INTERNAL_SYNC_KEY
                }
            )

            if response.status_code == 200:
                data = response.json()
                keys = data.get("data", {}).get("keys", [])
                logger.info(f"从 Backend 同步了 {len(keys)} 个 API Keys")
                return keys
            else:
                logger.warning(f"同步 API Keys 失败: {response.status_code}")
                return []

    except Exception as e:
        logger.error(f"同步 API Keys 异常: {e}")
        return []


# 存储有效的 API Keys 和用户信息
_valid_api_keys: Dict[str, Dict[str, Any]] = {}


def init_api_keys(keys: list):
    """初始化 API Keys"""
    global _valid_api_keys
    _valid_api_keys = {}
    for key_info in keys:
        api_key = key_info.get("api_key")
        if api_key:
            _valid_api_keys[api_key] = {
                "user_id": key_info.get("user_id"),
                "qmt_account_id": key_info.get("qmt_account_id")
            }
    logger.info(f"已加载 {len(_valid_api_keys)} 个 API Key")


def is_valid_key(api_key: str) -> bool:
    """检查 API Key 是否有效（本地缓存）"""
    return api_key in _valid_api_keys


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header)
) -> bool:
    """
    验证 API Key（中间件）

    Args:
        request: FastAPI Request
        api_key: 从 Header 中提取的 API Key

    Returns:
        bool: 验证成功返回 True

    Raises:
        HTTPException: 无效或缺失 API Key
    """
    # 健康检查和根路径不需要认证
    path = request.url.path
    if path in ['/health', '/', '/docs', '/openapi.json', '/redoc'] or path.startswith('/docs'):
        return True

    # MCP SSE 路径特殊处理
    if path.startswith('/mcp'):
        # MCP 接口需要认证
        pass

    # 检查 API Key
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="缺少 API Key，请在请求头中添加 X-API-Key"
        )

    # 系统内部 Key 直接通过（用于 backend 调用）
    if api_key == settings.INTERNAL_SYNC_KEY:
        return True

    # 先检查本地缓存
    if is_valid_key(api_key):
        return True

    # 调用 Backend 验证
    user_info = await verify_api_key_with_backend(api_key)
    if user_info:
        # 添加到本地缓存
        _valid_api_keys[api_key] = user_info
        return True

    raise HTTPException(
        status_code=401,
        detail="无效的 API Key"
    )


async def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    根据 API Key 获取用户信息

    Args:
        api_key: API Key

    Returns:
        用户信息字典
    """
    # 先检查本地缓存
    if api_key in _valid_api_keys:
        return _valid_api_keys[api_key]

    # 调用 Backend 获取
    return await verify_api_key_with_backend(api_key)