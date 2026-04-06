"""
权限服务
"""
from typing import List, Optional
from models.user import User
from models.user_role import UserRole
from models.role_menu import RoleMenu
from models.menu import Menu


class PermissionService:
    """权限服务"""

    @staticmethod
    async def get_user_permissions(user_id: int) -> List[str]:
        """获取用户所有权限标识"""
        # 获取用户所有角色
        user_roles = await UserRole.filter(user_id=user_id).all()
        role_ids = [ur.role_id for ur in user_roles]

        if not role_ids:
            return []

        # 获取角色关联的菜单ID
        role_menus = await RoleMenu.filter(role_id__in=role_ids).all()
        menu_ids = list(set([rm.menu_id for rm in role_menus]))

        if not menu_ids:
            return []

        # 获取菜单的权限标识
        menus = await Menu.filter(
            id__in=menu_ids,
            status="active"
        ).all()

        permissions = []
        for m in menus:
            if m.permission:
                permissions.append(m.permission)

        return permissions

    @staticmethod
    async def has_permission(user: User, permission: str) -> bool:
        """检查用户是否有指定权限"""
        # 超级管理员拥有所有权限
        if user.role == "admin":
            return True

        permissions = await PermissionService.get_user_permissions(user.id)
        return permission in permissions

    @staticmethod
    async def get_user_menu_ids(user: User) -> List[int]:
        """获取用户可访问的菜单ID列表"""
        # 超级管理员拥有所有菜单
        if user.role == "admin":
            menus = await Menu.filter(status="active").all()
            return [m.id for m in menus]

        # 获取用户所有角色
        user_roles = await UserRole.filter(user_id=user.id).all()
        role_ids = [ur.role_id for ur in user_roles]

        if not role_ids:
            return []

        # 获取角色关联的菜单ID
        role_menus = await RoleMenu.filter(role_id__in=role_ids).all()
        menu_ids = list(set([rm.menu_id for rm in role_menus]))

        return menu_ids

    @staticmethod
    async def check_menu_access(user: User, menu_path: str) -> bool:
        """检查用户是否有访问某个菜单的权限"""
        # 超级管理员拥有所有权限
        if user.role == "admin":
            return True

        menu_ids = await PermissionService.get_user_menu_ids(user)
        if not menu_ids:
            return False

        # 查找菜单
        menu = await Menu.get_or_none(path=menu_path, status="active")
        if not menu:
            return False

        return menu.id in menu_ids