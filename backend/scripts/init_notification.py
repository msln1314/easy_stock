"""
初始化通知相关数据

创建通知相关的数据库表和初始数据
"""
import asyncio
from tortoise import Tortoise
from config.database import init_db, close_db


async def init_notification_tables():
    """初始化通知相关表"""
    print("正在初始化通知相关表...")

    # 初始化数据库连接
    await init_db()

    # 生成表结构
    await Tortoise.generate_schemas()

    print("通知表结构已创建")

    # 关闭数据库连接
    await close_db()

    print("初始化完成")


if __name__ == "__main__":
    asyncio.run(init_notification_tables())