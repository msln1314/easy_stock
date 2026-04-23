"""
用户管理API路由
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends
from core.response import success_response, error_response
from core.auth import get_admin_user, get_current_user_required
from core.permission import require_permission
from services.user import UserService
from schemas.user import UserCreate, UserUpdate, PasswordReset, AssignRolesRequest, UserQmtAccountUpdate
from models.user import User

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])
user_service = UserService()


# ==================== 用户 API Key 管理 ====================

@router.get("/me/api-key", response_model=None)
async def get_my_api_key(user: User = Depends(get_current_user_required)):
    """获取当前用户的 API Key"""
    return success_response({
        "api_key": user.api_key,
        "has_api_key": bool(user.api_key)
    })


@router.post("/me/api-key/refresh", response_model=None)
async def refresh_my_api_key(user: User = Depends(get_current_user_required)):
    """刷新当前用户的 API Key"""
    new_api_key = User.generate_api_key()
    await User.filter(id=user.id).update(api_key=new_api_key)
    return success_response({
        "api_key": new_api_key,
        "message": "API Key 已刷新"
    })


@router.get("", response_model=None)
async def get_users(
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user: User = require_permission("user:view")
):
    """获取用户列表"""
    result = await user_service.get_users(
        role=role,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return success_response(result)


@router.get("/all", response_model=None)
async def get_all_users(user: User = Depends(get_admin_user)):
    """获取所有用户（下拉选择用）"""
    users = await user_service.get_all_users()
    return success_response(users)


@router.get("/{user_id}", response_model=None)
async def get_user(user_id: int, user: User = require_permission("user:view")):
    """获取用户详情"""
    user_obj = await user_service.get_user(user_id)
    if not user_obj:
        return error_response("用户不存在", 404)

    role_ids = await user_service.get_user_role_ids(user_id)
    return success_response({
        "id": user_obj.id,
        "username": user_obj.username,
        "email": user_obj.email,
        "nickname": user_obj.nickname,
        "role": user_obj.role,
        "status": user_obj.status,
        "last_login": user_obj.last_login.isoformat() if user_obj.last_login else None,
        "role_ids": role_ids,
        "created_at": user_obj.created_at.isoformat(),
        "updated_at": user_obj.updated_at.isoformat()
    })


@router.post("", response_model=None)
async def create_user(data: UserCreate, user: User = require_permission("user:create")):
    """创建用户"""
    # 检查用户名是否存在
    existing = await user_service.get_user_by_username(data.username)
    if existing:
        return error_response("用户名已存在", 400)

    new_user = await user_service.create_user(data)
    return success_response({
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "created_at": new_user.created_at.isoformat()
    })


@router.put("/{user_id}", response_model=None)
async def update_user(user_id: int, data: UserUpdate, user: User = require_permission("user:update")):
    """更新用户"""
    updated_user = await user_service.update_user(user_id, data)
    if not updated_user:
        return error_response("用户不存在", 404)
    return success_response({
        "id": updated_user.id,
        "username": updated_user.username,
        "updated_at": updated_user.updated_at.isoformat()
    })


@router.delete("/{user_id}", response_model=None)
async def delete_user(user_id: int, user: User = require_permission("user:delete")):
    """删除用户"""
    success = await user_service.delete_user(user_id)
    if not success:
        return error_response("用户不存在或无法删除", 400)
    return success_response(message="用户删除成功")


@router.put("/{user_id}/password", response_model=None)
async def reset_password(user_id: int, data: PasswordReset, user: User = require_permission("user:update")):
    """重置密码（管理员）"""
    success = await user_service.reset_password(user_id, data.new_password)
    if not success:
        return error_response("用户不存在", 404)
    return success_response(message="密码重置成功")


@router.put("/{user_id}/roles", response_model=None)
async def assign_roles(user_id: int, data: AssignRolesRequest, user: User = require_permission("user:assign")):
    """分配角色"""
    success = await user_service.assign_roles(user_id, data.role_ids)
    if not success:
        return error_response("用户不存在", 404)
    return success_response(message="角色分配成功")


# ==================== QMT账户管理 ====================

@router.get("/{user_id}/qmt", response_model=None)
async def get_user_qmt_account(user_id: int, current_user: User = Depends(get_admin_user)):
    """获取用户QMT账户配置"""
    # 管理员可以查看所有用户，普通用户只能查看自己
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response("无权限查看该用户QMT配置", 403)

    qmt_config = await user_service.get_qmt_account(user_id)
    if not qmt_config:
        return error_response("用户不存在", 404)
    return success_response(qmt_config)


@router.put("/{user_id}/qmt", response_model=None)
async def update_user_qmt_account(user_id: int, data: UserQmtAccountUpdate, current_user: User = Depends(get_current_user_required)):
    """更新用户QMT账户配置"""
    # 管理员可以更新所有用户，普通用户只能更新自己
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response("无权限修改该用户QMT配置", 403)

    updated_user = await user_service.update_qmt_account(user_id, data)
    if not updated_user:
        return error_response("用户不存在", 404)
    return success_response({
        "id": updated_user.id,
        "qmt_account_id": updated_user.qmt_account_id,
        "qmt_enabled": updated_user.qmt_enabled,
        "message": "QMT账户配置更新成功"
    })


@router.post("/{user_id}/qmt/enable", response_model=None)
async def enable_user_qmt(user_id: int, current_user: User = Depends(get_admin_user)):
    """启用用户QMT交易"""
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response("无权限操作", 403)

    success = await user_service.enable_qmt(user_id)
    if not success:
        return error_response("用户不存在或未绑定QMT账户", 400)
    return success_response({"message": "QMT交易已启用"})


@router.post("/{user_id}/qmt/disable", response_model=None)
async def disable_user_qmt(user_id: int, current_user: User = Depends(get_admin_user)):
    """禁用用户QMT交易"""
    if current_user.role != "admin" and current_user.id != user_id:
        return error_response("无权限操作", 403)

    success = await user_service.disable_qmt(user_id)
    if not success:
        return error_response("用户不存在", 400)
    return success_response({"message": "QMT交易已禁用"})