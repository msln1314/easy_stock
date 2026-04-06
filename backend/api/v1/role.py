"""
角色管理API路由
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends
from core.response import success_response, error_response
from core.auth import get_admin_user
from core.permission import require_permission
from services.role import RoleService
from schemas.role import RoleCreate, RoleUpdate, AssignMenusRequest
from models.user import User

router = APIRouter(prefix="/api/v1/roles", tags=["角色管理"])
role_service = RoleService()


@router.get("", response_model=None)
async def get_roles(
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user: User = require_permission("role:view")
):
    """获取角色列表"""
    result = await role_service.get_roles(
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return success_response(result)


@router.get("/all", response_model=None)
async def get_all_roles(user: User = Depends(get_admin_user)):
    """获取所有角色（下拉选择用）"""
    roles = await role_service.get_all_roles()
    return success_response(roles)


@router.get("/{role_id}", response_model=None)
async def get_role(role_id: int, user: User = require_permission("role:view")):
    """获取角色详情（含菜单ID）"""
    role = await role_service.get_role_with_menus(role_id)
    if not role:
        return error_response("角色不存在", 404)
    return success_response({
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "status": role.status,
        "menu_ids": role.menu_ids,
        "created_at": role.created_at.isoformat(),
        "updated_at": role.updated_at.isoformat()
    })


@router.post("", response_model=None)
async def create_role(data: RoleCreate, user: User = require_permission("role:create")):
    """创建角色"""
    # 检查角色编码是否已存在
    existing = await role_service.get_role_by_code(data.code)
    if existing:
        return error_response("角色编码已存在", 400)

    role = await role_service.create_role(data)
    return success_response({
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "created_at": role.created_at.isoformat()
    })


@router.put("/{role_id}", response_model=None)
async def update_role(role_id: int, data: RoleUpdate, user: User = require_permission("role:update")):
    """更新角色"""
    role = await role_service.update_role(role_id, data)
    if not role:
        return error_response("角色不存在", 404)
    return success_response({
        "id": role.id,
        "name": role.name,
        "code": role.code,
        "updated_at": role.updated_at.isoformat()
    })


@router.delete("/{role_id}", response_model=None)
async def delete_role(role_id: int, user: User = require_permission("role:delete")):
    """删除角色"""
    success = await role_service.delete_role(role_id)
    if not success:
        return error_response("角色不存在或有用户关联，无法删除", 400)
    return success_response(message="角色删除成功")


@router.put("/{role_id}/menus", response_model=None)
async def assign_menus(role_id: int, data: AssignMenusRequest, user: User = require_permission("role:assign")):
    """分配菜单权限"""
    success = await role_service.assign_menus(role_id, data.menu_ids)
    if not success:
        return error_response("角色不存在", 404)
    return success_response(message="菜单权限分配成功")