"""
ETF池初始化脚本 - 预设9只行业ETF
"""
import asyncio
from config.database import init_db, close_db
from models.etf_pool import EtfPool
from loguru import logger

# 预设ETF数据（知乎文章推荐）
PRESET_ETFS = [
    {"name": "科技ETF", "code": "515000", "sector": "科技"},
    {"name": "消费ETF", "code": "159928", "sector": "消费"},
    {"name": "医药ETF", "code": "159929", "sector": "医药"},
    {"name": "金融ETF", "code": "159931", "sector": "金融"},
    {"name": "军工ETF", "code": "512660", "sector": "军工"},
    {"name": "新能源ETF", "code": "516160", "sector": "新能源"},
    {"name": "半导体ETF", "code": "512480", "sector": "半导体"},
    {"name": "有色ETF", "code": "512400", "sector": "有色金属"},
    {"name": "基建ETF", "code": "159766", "sector": "基建"},
]


async def init_etf_pool():
    """初始化ETF池数据"""
    logger.info("开始初始化ETF池...")

    for etf_data in PRESET_ETFS:
        existing = await EtfPool.filter(code=etf_data["code"]).first()
        if not existing:
            await EtfPool.create(**etf_data)
            logger.info(f"创建ETF: {etf_data['name']} ({etf_data['code']})")
        else:
            logger.info(f"ETF已存在: {etf_data['name']} ({etf_data['code']})")

    total = await EtfPool.all().count()
    logger.info(f"ETF池初始化完成，共 {total} 只ETF")


async def main():
    """主函数"""
    await init_db()
    await init_etf_pool()
    await close_db()


if __name__ == "__main__":
    asyncio.run(main())