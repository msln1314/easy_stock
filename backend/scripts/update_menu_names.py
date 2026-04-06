# -*- coding: utf-8 -*-
"""
Update menu names to Chinese
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


async def update_names():
    await Tortoise.init(config=TORTOISE_ORM)

    names_map = {
        'Dashboard': '监控大屏',
        'Strategy': '策略管理',
        'Indicator': '指标库管理',
        'Factor Screen': '因子筛选',
        'System': '系统管理',
        'Dict': '字典管理',
        'Config': '系统配置',
        'Menu': '菜单管理',
        'Role': '角色管理',
        'Create Menu': '新增菜单',
        'Edit Menu': '编辑菜单',
        'Delete Menu': '删除菜单',
        'Create Role': '新增角色',
        'Edit Role': '编辑角色',
        'Delete Role': '删除角色',
        'Assign Permissions': '分配权限',
    }

    for eng_name, chn_name in names_map.items():
        menu = await Menu.get_or_none(name=eng_name)
        if menu:
            menu.name = chn_name
            await menu.save()
            print(f'Updated: {eng_name} -> {chn_name}')
        else:
            # Try to find by partial match
            menus = await Menu.filter(name__contains=eng_name).all()
            for m in menus:
                m.name = chn_name
                await m.save()
                print(f'Updated: {m.name} -> {chn_name}')

    await Tortoise.close_connections()
    print('Done!')


if __name__ == "__main__":
    asyncio.run(update_names())