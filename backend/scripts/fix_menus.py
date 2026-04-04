"""
修复菜单数据
"""
import asyncio
from tortoise import Tortoise
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from models.menu import Menu


async def fix_menus():
    await Tortoise.init(
        db_url=f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        modules={"models": ["models.menu"]}
    )

    # 清理所有菜单
    await Menu.all().delete()
    print("已清理旧菜单数据")

    # 正确的菜单结构
    menus = [
        # 一级菜单
        {"id": 1, "parent_id": None, "name": "监控大屏", "path": "/dashboard", "component": "views/dashboard/index", "icon": "GridOutline", "sort": 1, "visible": True, "status": "active", "menu_type": "menu", "permission": "dashboard:view"},
        {"id": 2, "parent_id": None, "name": "策略管理", "path": "/strategy", "component": "views/strategy/index", "icon": "TrendingUpOutline", "sort": 2, "visible": True, "status": "active", "menu_type": "menu", "permission": "strategy:view"},
        {"id": 3, "parent_id": None, "name": "指标库管理", "path": "/indicator", "component": "views/indicator/index", "icon": "AnalyticsOutline", "sort": 3, "visible": True, "status": "active", "menu_type": "menu", "permission": "indicator:view"},
        {"id": 4, "parent_id": None, "name": "因子筛选", "path": "/factor-screen", "component": "views/factor-screen/index", "icon": "FilterOutline", "sort": 4, "visible": True, "status": "active", "menu_type": "menu", "permission": "factor:screen"},
        {"id": 5, "parent_id": None, "name": "因子库管理", "path": "/factor-library", "component": "views/factor-library/index", "icon": "LibraryOutline", "sort": 5, "visible": True, "status": "active", "menu_type": "menu", "permission": "factor:library"},
        {"id": 6, "parent_id": None, "name": "监控股票池", "path": "/monitor", "component": "views/monitor/index", "icon": "EyeOutline", "sort": 6, "visible": True, "status": "active", "menu_type": "menu", "permission": "monitor:view"},
        {"id": 7, "parent_id": None, "name": "计划任务", "path": "/scheduler", "component": "views/scheduler/index", "icon": "TimeOutline", "sort": 7, "visible": True, "status": "active", "menu_type": "menu", "permission": "scheduler:view"},

        # 预警管理目录
        {"id": 23, "parent_id": None, "name": "预警管理", "path": "/warning", "component": None, "icon": "AlertOutline", "sort": 8, "visible": True, "status": "active", "menu_type": "directory", "permission": "warning:view"},
        {"id": 24, "parent_id": 23, "name": "卖出预警", "path": "/warning", "component": "views/warning/index", "icon": "WarningOutline", "sort": 1, "visible": True, "status": "active", "menu_type": "menu", "permission": "warning:list"},
        {"id": 25, "parent_id": 23, "name": "卖出策略配置", "path": "/strategy-config", "component": "views/strategy-config/index", "icon": "CogOutline", "sort": 2, "visible": True, "status": "active", "menu_type": "menu", "permission": "warning:config"},
        {"id": 26, "parent_id": 23, "name": "卖出信号明细", "path": "/signal", "component": "views/signal/index", "icon": "FlashOutline", "sort": 3, "visible": True, "status": "active", "menu_type": "menu", "permission": "warning:signal"},

        # 交易管理
        {"id": 22, "parent_id": None, "name": "交易管理", "path": "/trade", "component": "views/trade/index", "icon": "SwapHorizontalOutline", "sort": 9, "visible": True, "status": "active", "menu_type": "menu", "permission": "trade:view"},

        # 系统管理目录
        {"id": 100, "parent_id": None, "name": "系统管理", "path": "/system", "component": None, "icon": "SettingsOutline", "sort": 100, "visible": True, "status": "active", "menu_type": "directory", "permission": "system:view"},
        {"id": 101, "parent_id": 100, "name": "字典管理", "path": "/dict", "component": "views/dict/index", "icon": "BookOutline", "sort": 1, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:dict"},
        {"id": 102, "parent_id": 100, "name": "系统配置", "path": "/config", "component": "views/config/index", "icon": "CogOutline", "sort": 2, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:config"},
        {"id": 103, "parent_id": 100, "name": "菜单管理", "path": "/system/menu", "component": "views/system/menu/index", "icon": "ListOutline", "sort": 3, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:menu"},
        {"id": 104, "parent_id": 100, "name": "角色管理", "path": "/system/role", "component": "views/system/role/index", "icon": "ShieldOutline", "sort": 4, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:role"},
        {"id": 105, "parent_id": 100, "name": "用户管理", "path": "/system/user", "component": "views/system/user/index", "icon": "PeopleOutline", "sort": 5, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:user"},
        {"id": 106, "parent_id": 100, "name": "通知配置", "path": "/notification", "component": "views/notification/index", "icon": "ChatbubbleOutline", "sort": 6, "visible": True, "status": "active", "menu_type": "menu", "permission": "system:notification"},
    ]

    for m in menus:
        await Menu.create(**m)
        print(f"创建: {m['name']}")

    print(f"\n菜单重构完成，共 {len(menus)} 个")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(fix_menus())