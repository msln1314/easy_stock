"""
数据库初始化脚本
"""
import asyncio
from config.database import init_db, close_db
from loguru import logger


async def init():
    """初始化数据库"""
    logger.info("开始初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    await close_db()


if __name__ == "__main__":
    asyncio.run(init())