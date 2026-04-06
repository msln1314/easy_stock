"""
菜单管理API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from core.response import success_response, error_response
from core.auth import get_current_user_required, get_admin_user
from core.permission import require_permission
from services.menu import MenuService
from schemas.menu import MenuCreate, MenuUpdate
from models.user import User

router = APIRouter(prefix="/api/v1/menus", tags=["菜单管理"])
menu_service = MenuService()


@router.get("", response_model=None)
async def get_menu_tree(user: User = Depends(get_admin_user)):
    """获取菜单树形列表（管理员权限）"""
    menus = await menu_service.get_menu_tree()
    return success_response(menus)


@router.get("/all", response_model=None)
async def get_all_menus(user: User = Depends(get_admin_user)):
    """获取所有菜单（扁平列表，用于权限分配）"""
    menus = await menu_service.get_all_menus()
    return success_response(menus)


@router.get("/user", response_model=None)
async def get_user_menus(user: User = require_permission("menu:view")):
    """获取当前用户菜单（根据角色权限）"""
    menus = await menu_service.get_user_menus(user.id)
    return success_response(menus)


@router.get("/{menu_id}", response_model=None)
async def get_menu(menu_id: int, user: User = Depends(get_admin_user)):
    """获取菜单详情"""
    menu = await menu_service.get_menu(menu_id)
    if not menu:
        return error_response("菜单不存在", 404)
    return success_response({
        "id": menu.id,
        "parent_id": menu.parent_id,
        "name": menu.name,
        "path": menu.path,
        "component": menu.component,
        "icon": menu.icon,
        "sort": menu.sort,
        "visible": menu.visible,
        "status": menu.status,
        "menu_type": menu.menu_type,
        "permission": menu.permission,
        "created_at": menu.created_at.isoformat(),
        "updated_at": menu.updated_at.isoformat()
    })


@router.post("", response_model=None)
async def create_menu(data: MenuCreate, user: User = require_permission("menu:create")):
    """创建菜单"""
    # 检查父菜单是否存在
    if data.parent_id:
        parent = await menu_service.get_menu(data.parent_id)
        if not parent:
            return error_response("父菜单不存在", 400)

    menu = await menu_service.create_menu(data)
    return success_response({
        "id": menu.id,
        "name": menu.name,
        "path": menu.path,
        "created_at": menu.created_at.isoformat()
    })


@router.put("/{menu_id}", response_model=None)
async def update_menu(menu_id: int, data: MenuUpdate, user: User = require_permission("menu:update")):
    """更新菜单"""
    menu = await menu_service.update_menu(menu_id, data)
    if not menu:
        return error_response("菜单不存在", 404)
    return success_response({
        "id": menu.id,
        "name": menu.name,
        "path": menu.path,
        "updated_at": menu.updated_at.isoformat()
    })


@router.delete("/{menu_id}", response_model=None)
async def delete_menu(menu_id: int, user: User = require_permission("menu:delete")):
    """删除菜单"""
    success = await menu_service.delete_menu(menu_id)
    if not success:
        return error_response("菜单不存在或有子菜单，无法删除", 400)
    return success_response(message="菜单删除成功")