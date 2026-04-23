"""
添加研究中心菜单
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tortoise import Tortoise
from config.database import TORTOISE_ORM
from models.menu import Menu


async def add_research_menu():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # 检查研究中心菜单是否已存在
    existing = await Menu.get_or_none(id=30)
    if existing:
        print("研究中心菜单已存在，跳过创建")
        await Tortoise.close_connections()
        return

    # 创建研究中心目录
    await Menu.create(
        id=30,
        parent_id=None,
        name="研究中心",
        path="/research",
        component=None,
        icon="SearchOutline",
        sort=10,
        visible=True,
        status="active",
        menu_type="directory",
        permission="research:view"
    )
    print("创建: 研究中心")

    # 创建AI分析子菜单
    await Menu.create(
        id=31,
        parent_id=30,
        name="AI分析",
        path="/stock-analysis",
        component="views/stock-analysis/index",
        icon="SparklesOutline",
        sort=1,
        visible=True,
        status="active",
        menu_type="menu",
        permission="research:ai-analysis"
    )
    print("创建: AI分析")

    print("\n研究中心菜单添加完成")
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_research_menu())