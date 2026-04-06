"""
权限检查装饰器
"""
from typing import Callable
from fastapi import Depends, HTTPException, status
from models.user import User
from core.auth import get_current_user_required
from services.permission import PermissionService


def require_permission(permission: str):
    """
    权限检查装饰器
    用于保护API接口，检查用户是否有指定权限

    Args:
        permission: 权限标识，如 "user:create", "menu:delete"

    Returns:
        Depends对象，用于FastAPI路由依赖注入
    """
    async def permission_checker(user: User = Depends(get_current_user_required)) -> User:
        # 超级管理员拥有所有权限
        if user.role == "admin":
            return user

        # 检查用户是否有指定权限
        has_perm = await PermissionService.has_permission(user, permission)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission}"
            )
        return user

    return Depends(permission_checker)


def require_admin():
    """
    管理员权限检查装饰器
    仅允许管理员访问
    """
    async def admin_checker(user: User = Depends(get_current_user_required)) -> User:
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        return user

    return Depends(admin_checker)


def require_menu_access(menu_path: str):
    """
    菜单访问权限检查装饰器
    检查用户是否有访问指定菜单路径的权限

    Args:
        menu_path: 菜单路径，如 "/system/menu"

    Returns:
        Depends对象，用于FastAPI路由依赖注入
    """
    async def menu_checker(user: User = Depends(get_current_user_required)) -> User:
        # 超级管理员拥有所有权限
        if user.role == "admin":
            return user

        # 检查菜单访问权限
        has_access = await PermissionService.check_menu_access(user, menu_path)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权访问菜单: {menu_path}"
            )
        return user

    return Depends(menu_checker)