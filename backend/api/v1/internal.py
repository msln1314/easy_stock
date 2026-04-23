"""
API Key 验证接口

供 qmt-service 等微服务验证 API Key 并获取用户信息
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from core.response import success_response
from models.user import User
from services.user import UserService

router = APIRouter(prefix="/api/v1/internal", tags=["内部接口"])


@router.get("/verify-api-key", summary="验证 API Key")
async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")
):
    """
    验证 API Key 并返回用户信息

    qmt-service 等微服务调用此接口验证用户的 API Key

    Args:
        x_api_key: 要验证的用户 API Key
        x_internal_key: 内部服务调用的安全 Key（防止外部直接调用）

    Returns:
        用户信息（如果 API Key 有效）
    """
    # 验证内部调用 Key（防止外部直接调用此接口）
    from config.settings import QMT_API_KEY
    if x_internal_key != QMT_API_KEY:
        raise HTTPException(status_code=403, detail="无效的内部调用 Key")

    # 验证用户 API Key
    if not x_api_key:
        raise HTTPException(status_code=401, detail="缺少 API Key")

    # 查找绑定了此 API Key 的用户（使用 api_key 字段）
    user = await User.get_or_none(api_key=x_api_key, status="active")

    if not user:
        raise HTTPException(status_code=401, detail="无效的 API Key")

    # 返回用户信息
    return success_response({
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "qmt_account_id": user.qmt_account_id,
        "qmt_account_name": user.qmt_account_name,
        "qmt_client_path": user.qmt_client_path,
        "qmt_session_id": user.qmt_session_id,
        "qmt_enabled": user.qmt_enabled
    })


@router.post("/sync-api-keys", summary="同步所有有效 API Keys")
async def sync_api_keys(
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Key")
):
    """
    同步所有有效的 API Keys（供 qmt-service 启动时调用）

    Args:
        x_internal_key: 内部服务调用的安全 Key

    Returns:
        所有启用用户的 API Keys
    """
    from config.settings import QMT_API_KEY
    if x_internal_key != QMT_API_KEY:
        raise HTTPException(status_code=403, detail="无效的内部调用 Key")

    # 获取所有有 API Key 的活跃用户
    users = await User.filter(api_key__isnull=False, status="active").all()

    api_keys = []
    for user in users:
        if user.api_key:
            api_keys.append({
                "api_key": user.api_key,
                "user_id": user.id,
                "qmt_account_id": user.qmt_account_id
            })

    # 同时返回内部同步 Key
    api_keys.append({
        "api_key": QMT_API_KEY,
        "user_id": 0,
        "qmt_account_id": "internal"
    })

    return success_response({"keys": api_keys, "total": len(api_keys)})