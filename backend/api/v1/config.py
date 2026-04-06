"""
系统配置API路由
"""
from typing import Optional, Dict
from fastapi import APIRouter, Query, Depends
from core.response import success_response, error_response
from core.auth import get_current_user_required, get_admin_user
from schemas.config import SysConfigCreate, SysConfigUpdate
from services.config import SysConfigService
from models.user import User

router = APIRouter(prefix="/api/v1/configs", tags=["系统配置"])
service = SysConfigService()


@router.get("", response_model=None)
async def get_configs(
    category: Optional[str] = Query(None, description="类别筛选: basic/security/notification"),
    access_type: Optional[str] = Query(None, description="访问类型筛选: public/private"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    user: User = Depends(get_current_user_required)
):
    """获取系统配置列表"""
    is_admin = user.role == "admin"
    result = await service.get_configs(
        category=category,
        access_type=access_type,
        keyword=keyword,
        page=page,
        page_size=page_size,
        is_admin=is_admin
    )
    return success_response(result.dict())


@router.get("/public", response_model=None)
async def get_public_configs():
    """获取公开配置（无需认证）"""
    configs = await service.get_public_configs()
    return success_response(configs)


@router.get("/category/{category}", response_model=None)
async def get_configs_by_category(
    category: str,
    user: User = Depends(get_current_user_required)
):
    """按类别获取配置"""
    valid_categories = ["basic", "security", "notification", "ai"]
    if category not in valid_categories:
        return error_response("无效的配置类别", 400)

    is_admin = user.role == "admin"
    configs = await service.get_configs_by_category(category, is_admin)
    return success_response(configs)


@router.get("/{key}", response_model=None)
async def get_config_detail(
    key: str,
    user: User = Depends(get_current_user_required)
):
    """获取单个配置详情"""
    config = await service.get_config_by_key(key)
    if not config:
        return error_response("配置不存在", 404)

    # 私有配置需要管理员权限
    if config.access_type == "private" and user.role != "admin":
        return error_response("无权访问私有配置", 403)

    # 解密值（仅管理员）
    decrypted_value = None
    if user.role == "admin" and config.data_type == "encrypted" and config.value:
        from utils.crypto import aes_decrypt
        decrypted_value = aes_decrypt(config.value)

    return success_response({
        "id": config.id,
        "key": config.key,
        "value": config.value,
        "category": config.category,
        "data_type": config.data_type,
        "access_type": config.access_type,
        "description": config.description,
        "decrypted_value": decrypted_value,
        "created_at": config.created_at.isoformat(),
        "updated_at": config.updated_at.isoformat()
    })


@router.post("", response_model=None)
async def create_config(
    data: SysConfigCreate,
    admin: User = Depends(get_admin_user)
):
    """创建系统配置（仅管理员）"""
    # 检查key是否已存在
    existing = await service.get_config_by_key(data.key)
    if existing:
        return error_response("配置键已存在", 400)

    config = await service.create_config(data)
    return success_response({
        "id": config.id,
        "key": config.key,
        "category": config.category,
        "created_at": config.created_at.isoformat()
    })


@router.put("/{key}", response_model=None)
async def update_config(
    key: str,
    data: SysConfigUpdate,
    admin: User = Depends(get_admin_user)
):
    """更新系统配置（仅管理员）"""
    config = await service.update_config(key, data)
    if not config:
        return error_response("配置不存在", 404)

    return success_response({
        "id": config.id,
        "key": config.key,
        "updated_at": config.updated_at.isoformat()
    })


@router.delete("/{key}", response_model=None)
async def delete_config(
    key: str,
    admin: User = Depends(get_admin_user)
):
    """删除系统配置（仅管理员）"""
    success = await service.delete_config(key)
    if not success:
        return error_response("配置不存在", 404)
    return success_response(message="删除成功")


@router.post("/batch", response_model=None)
async def batch_update_configs(
    configs: Dict[str, str],
    admin: User = Depends(get_admin_user)
):
    """批量更新配置值（仅管理员）"""
    await service.batch_update(configs)
    return success_response(message="批量更新成功")