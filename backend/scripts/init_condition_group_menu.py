"""
初始化组合条件菜单
"""
from tortoise import Tortoise
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


async def init_condition_group_menu():
    """初始化组合条件菜单"""
    from models.menu import Menu

    # 查找预警管理父菜单
    parent = await Menu.get_or_none(id=23)
    if not parent:
        print("未找到预警管理父菜单，请先运行 init_menus.py")
        return

    # 检查是否已存在
    existing = await Menu.get_or_none(name="组合条件", parent_id=23)
    if existing:
        print("组合条件菜单已存在")
        return

    # 创建菜单
    menu = await Menu.create(
        parent_id=23,
        name="组合条件",
        path="/warning/condition-group",
        component="views/warning/ConditionGroup",
        icon="GitBranchOutline",
        sort=4,
        visible=True,
        status="active",
        menu_type="menu",
        permission="warning:condition-group"
    )

    print(f"创建菜单成功: {menu.name}")


async def main():
    """主函数"""
    await Tortoise.init(
        db_url=f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        modules={"models": ["models.menu"]},
    )
    await Tortoise.generate_schemas()

    await init_condition_group_menu()

    await Tortoise.close_connections()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())