# -*- coding: utf-8 -*-
"""
Initialize permission data - menus, roles, and role-menu associations
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from tortoise import Tortoise
from config.database import TORTOISE_ORM
from models.menu import Menu
from models.role import Role
from models.role_menu import RoleMenu
from models.user_role import UserRole
from models.user import User


async def init_permission_data():
    """Initialize permission data"""
    # Initialize database connection
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("Starting permission data initialization...")
    print("=" * 50)

    # 1. Create default roles
    roles_data = [
        {"name": "Administrator", "code": "admin", "description": "System administrator with full permissions", "status": "active"},
        {"name": "Normal User", "code": "user", "description": "Normal user with limited permissions", "status": "active"},
    ]

    created_roles = {}
    for role_data in roles_data:
        role = await Role.get_or_none(code=role_data["code"])
        if not role:
            role = await Role.create(**role_data)
            print(f"[OK] Created role: {role.name} ({role.code})")
        else:
            print(f"[OK] Role already exists: {role.name}")
        created_roles[role_data["code"]] = role

    # 2. Create menus
    menus_data = [
        # Level 1 - Directories
        {"name": "监控大屏", "path": "/dashboard", "icon": "GridOutline", "sort": 1, "menu_type": "menu", "permission": "dashboard:view"},
        {"name": "策略管理", "path": "/strategy", "icon": "TrendingUpOutline", "sort": 2, "menu_type": "menu", "permission": "strategy:view"},
        {"name": "指标库管理", "path": "/indicator", "icon": "AnalyticsOutline", "sort": 3, "menu_type": "menu", "permission": "indicator:view"},
        {"name": "因子筛选", "path": "/factor-screen", "icon": "FilterOutline", "sort": 4, "menu_type": "menu", "permission": "factor:view"},
        {"name": "因子库管理", "path": "/factor-library", "icon": "LibraryOutline", "sort": 5, "menu_type": "menu", "permission": "factor:library"},
        {"name": "监控股票池", "path": "/monitor", "icon": "EyeOutline", "sort": 6, "menu_type": "menu", "permission": "monitor:view"},
        {"name": "选股策略", "path": "/stock-pick", "icon": "TrendingUpOutline", "sort": 7, "menu_type": "menu", "permission": "stockpick:view"},
        {"name": "计划任务", "path": "/scheduler", "icon": "TimeOutline", "sort": 8, "menu_type": "menu", "permission": "scheduler:view"},
        {"name": "交易管理", "path": "/trade", "icon": "SwapHorizontalOutline", "sort": 9, "menu_type": "menu", "permission": "trade:view"},
        {"name": "系统管理", "path": "/system", "icon": "CogOutline", "sort": 100, "menu_type": "directory", "permission": None},

        # Level 2 - System menus
        {"parent_name": "系统管理", "name": "字典管理", "path": "/dict", "icon": "BookOutline", "sort": 1, "menu_type": "menu", "permission": "dict:view"},
        {"parent_name": "系统管理", "name": "系统配置", "path": "/config", "icon": "SettingsOutline", "sort": 2, "menu_type": "menu", "permission": "config:view"},
        {"parent_name": "系统管理", "name": "菜单管理", "path": "/system/menu", "icon": "ListOutline", "sort": 3, "menu_type": "menu", "permission": "menu:view"},
        {"parent_name": "系统管理", "name": "角色管理", "path": "/system/role", "icon": "ShieldOutline", "sort": 4, "menu_type": "menu", "permission": "role:view"},

        # Buttons - Menu management
        {"parent_path": "/system/menu", "name": "新增菜单", "path": "", "sort": 1, "menu_type": "button", "permission": "menu:create"},
        {"parent_path": "/system/menu", "name": "编辑菜单", "path": "", "sort": 2, "menu_type": "button", "permission": "menu:update"},
        {"parent_path": "/system/menu", "name": "删除菜单", "path": "", "sort": 3, "menu_type": "button", "permission": "menu:delete"},

        # Buttons - Role management
        {"parent_path": "/system/role", "name": "新增角色", "path": "", "sort": 1, "menu_type": "button", "permission": "role:create"},
        {"parent_path": "/system/role", "name": "编辑角色", "path": "", "sort": 2, "menu_type": "button", "permission": "role:update"},
        {"parent_path": "/system/role", "name": "删除角色", "path": "", "sort": 3, "menu_type": "button", "permission": "role:delete"},
        {"parent_path": "/system/role", "name": "分配权限", "path": "", "sort": 4, "menu_type": "button", "permission": "role:assign"},
    ]

    # First pass: create all menus without parent
    created_menus = {}
    path_to_id = {}  # path -> id mapping for parent lookup

    for menu_data in menus_data:
        if "parent_name" not in menu_data and "parent_path" not in menu_data:
            menu = await Menu.get_or_none(path=menu_data["path"])
            if not menu:
                menu = await Menu.create(
                    parent_id=None,
                    name=menu_data["name"],
                    path=menu_data["path"],
                    icon=menu_data.get("icon"),
                    sort=menu_data.get("sort", 0),
                    visible=True,
                    status="active",
                    menu_type=menu_data["menu_type"],
                    permission=menu_data.get("permission")
                )
                print(f"[OK] Created menu: {menu.name} ({menu.path})")
            else:
                print(f"[OK] Menu already exists: {menu.name}")
            path_to_id[menu_data["path"]] = menu.id
            created_menus[menu_data["name"]] = menu

    # Second pass: create menus with parent (by name)
    for menu_data in menus_data:
        if "parent_name" in menu_data:
            parent_id = path_to_id.get(menu_data.get("parent_path", ""))
            if not parent_id:
                # Try to find parent by name
                parent_name = menu_data["parent_name"]
                parent_menu = await Menu.get_or_none(name=parent_name)
                if parent_menu:
                    parent_id = parent_menu.id
                else:
                    print(f"[WARN] Parent menu not found: {parent_name}")
                    continue

            menu = await Menu.get_or_none(path=menu_data["path"])
            if not menu:
                menu = await Menu.create(
                    parent_id=parent_id,
                    name=menu_data["name"],
                    path=menu_data.get("path", ""),
                    icon=menu_data.get("icon"),
                    sort=menu_data.get("sort", 0),
                    visible=menu_data.get("visible", True),
                    status="active",
                    menu_type=menu_data["menu_type"],
                    permission=menu_data.get("permission")
                )
                print(f"[OK] Created menu: {menu.name} (parent: {menu_data['parent_name']})")
            else:
                print(f"[OK] Menu already exists: {menu.name}")
            path_to_id[menu_data.get("path", "")] = menu.id
            created_menus[menu_data["name"]] = menu

    # Third pass: create buttons with parent (by path)
    for menu_data in menus_data:
        if "parent_path" in menu_data:
            parent_path = menu_data["parent_path"]
            parent_id = path_to_id.get(parent_path)
            if not parent_id:
                print(f"[WARN] Parent menu not found by path: {parent_path}")
                continue

            # For buttons, use permission as unique identifier
            menu = await Menu.get_or_none(parent_id=parent_id, permission=menu_data["permission"])
            if not menu:
                menu = await Menu.create(
                    parent_id=parent_id,
                    name=menu_data["name"],
                    path=menu_data.get("path", ""),
                    icon=menu_data.get("icon"),
                    sort=menu_data.get("sort", 0),
                    visible=menu_data.get("visible", False),
                    status="active",
                    menu_type=menu_data["menu_type"],
                    permission=menu_data.get("permission")
                )
                print(f"[OK] Created button: {menu.name} (permission: {menu.permission})")
            else:
                print(f"[OK] Button already exists: {menu.name}")
            created_menus[menu_data["name"]] = menu

    # 3. Assign all menus to admin role
    admin_role = created_roles.get("admin")
    if admin_role:
        all_menus = await Menu.all()
        for menu in all_menus:
            existing = await RoleMenu.get_or_none(role_id=admin_role.id, menu_id=menu.id)
            if not existing:
                await RoleMenu.create(role_id=admin_role.id, menu_id=menu.id)
        print(f"[OK] Assigned all menus to admin role ({len(all_menus)} menus)")

    # 4. Assign basic menus to user role
    user_role = created_roles.get("user")
    if user_role:
        basic_menu_paths = ["/dashboard", "/strategy", "/indicator", "/factor-screen", "/factor-library", "/monitor", "/stock-pick", "/scheduler", "/trade", "/dict"]
        for path in basic_menu_paths:
            menu = await Menu.get_or_none(path=path)
            if menu:
                existing = await RoleMenu.get_or_none(role_id=user_role.id, menu_id=menu.id)
                if not existing:
                    await RoleMenu.create(role_id=user_role.id, menu_id=menu.id)
        print(f"[OK] Assigned basic menus to user role")

    # 5. Assign admin role to admin user
    admin_user = await User.get_or_none(username="admin")
    if admin_user and admin_role:
        existing = await UserRole.get_or_none(user_id=admin_user.id, role_id=admin_role.id)
        if not existing:
            await UserRole.create(user_id=admin_user.id, role_id=admin_role.id)
            print(f"[OK] Assigned admin role to admin user")

    print("\nPermission data initialization completed!")
    print("=" * 50)

    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_permission_data())