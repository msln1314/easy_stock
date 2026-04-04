"""
初始化菜单数据
"""
from tortoise import Tortoise
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# 预置菜单数据
MENUS = [
    # 一级菜单 - 监控大屏
    {
        "id": 1,
        "parent_id": None,
        "name": "监控大屏",
        "path": "/dashboard",
        "component": "views/dashboard/index",
        "icon": "GridOutline",
        "sort": 1,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "dashboard:view"
    },
    # 一级菜单 - 策略管理
    {
        "id": 2,
        "parent_id": None,
        "name": "策略管理",
        "path": "/strategy",
        "component": "views/strategy/index",
        "icon": "TrendingUpOutline",
        "sort": 2,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "strategy:view"
    },
    # 一级菜单 - 指标库管理
    {
        "id": 3,
        "parent_id": None,
        "name": "指标库管理",
        "path": "/indicator",
        "component": "views/indicator/index",
        "icon": "AnalyticsOutline",
        "sort": 3,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "indicator:view"
    },
    # 一级菜单 - 因子筛选
    {
        "id": 4,
        "parent_id": None,
        "name": "因子筛选",
        "path": "/factor-screen",
        "component": "views/factor-screen/index",
        "icon": "FilterOutline",
        "sort": 4,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "factor:screen"
    },
    # 一级菜单 - 因子库管理
    {
        "id": 5,
        "parent_id": None,
        "name": "因子库管理",
        "path": "/factor-library",
        "component": "views/factor-library/index",
        "icon": "LibraryOutline",
        "sort": 5,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "factor:library"
    },
    # 一级菜单 - 监控股票池
    {
        "id": 6,
        "parent_id": None,
        "name": "监控股票池",
        "path": "/monitor",
        "component": "views/monitor/index",
        "icon": "EyeOutline",
        "sort": 6,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "monitor:view"
    },
    # 一级菜单 - 计划任务
    {
        "id": 7,
        "parent_id": None,
        "name": "计划任务",
        "path": "/scheduler",
        "component": "views/scheduler/index",
        "icon": "TimeOutline",
        "sort": 7,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "scheduler:view"
    },
    # 一级菜单 - 系统管理（目录）
    {
        "id": 100,
        "parent_id": None,
        "name": "系统管理",
        "path": "/system",
        "component": None,
        "icon": "SettingsOutline",
        "sort": 100,
        "visible": True,
        "status": "active",
        "menu_type": "directory",
        "permission": "system:view"
    },
    # 二级菜单 - 字典管理
    {
        "id": 101,
        "parent_id": 100,
        "name": "字典管理",
        "path": "/dict",
        "component": "views/dict/index",
        "icon": "BookOutline",
        "sort": 1,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:dict"
    },
    # 二级菜单 - 系统配置
    {
        "id": 102,
        "parent_id": 100,
        "name": "系统配置",
        "path": "/config",
        "component": "views/config/index",
        "icon": "CogOutline",
        "sort": 2,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:config"
    },
    # 二级菜单 - 菜单管理
    {
        "id": 103,
        "parent_id": 100,
        "name": "菜单管理",
        "path": "/system/menu",
        "component": "views/system/menu/index",
        "icon": "ListOutline",
        "sort": 3,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:menu"
    },
    # 二级菜单 - 角色管理
    {
        "id": 104,
        "parent_id": 100,
        "name": "角色管理",
        "path": "/system/role",
        "component": "views/system/role/index",
        "icon": "ShieldOutline",
        "sort": 4,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:role"
    },
    # 二级菜单 - 用户管理
    {
        "id": 105,
        "parent_id": 100,
        "name": "用户管理",
        "path": "/system/user",
        "component": "views/system/user/index",
        "icon": "PeopleOutline",
        "sort": 5,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:user"
    },
    # 二级菜单 - 通知配置
    {
        "id": 106,
        "parent_id": 100,
        "name": "通知配置",
        "path": "/notification",
        "component": "views/notification/index",
        "icon": "ChatbubbleOutline",
        "sort": 6,
        "visible": True,
        "status": "active",
        "menu_type": "menu",
        "permission": "system:notification"
    },
]


async def init_menus():
    """初始化菜单数据"""
    from models.menu import Menu

    for menu_data in MENUS:
        existing = await Menu.get_or_none(id=menu_data["id"])
        if not existing:
            await Menu.create(**menu_data)
            print(f"创建菜单: {menu_data['name']}")
        else:
            # 更新现有菜单
            for key, value in menu_data.items():
                setattr(existing, key, value)
            await existing.save()
            print(f"更新菜单: {menu_data['name']}")

    print(f"菜单初始化完成，共 {len(MENUS)} 个")


async def main():
    """主函数"""
    await Tortoise.init(
        db_url=f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        modules={"models": ["models.menu", "models.user", "models.role", "models.role_menu", "models.user_role"]},
    )
    await Tortoise.generate_schemas()

    await init_menus()

    await Tortoise.close_connections()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())