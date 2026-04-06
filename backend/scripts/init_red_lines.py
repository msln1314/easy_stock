"""
初始化交易红线规则

运行此脚本将预置的红线规则写入数据库
"""
import asyncio
from loguru import logger
from config.database import init_db, close_db
from models.trade_red_line import TradeRedLine, PRESET_RED_LINES


async def init_red_lines():
    """初始化红线规则"""
    logger.info("开始初始化交易红线规则...")

    for preset in PRESET_RED_LINES:
        rule_key = preset.get("rule_key")
        exists = await TradeRedLine.filter(rule_key=rule_key).exists()

        if exists:
            logger.info(f"红线规则已存在: {rule_key}, 跳过")
            continue

        try:
            await TradeRedLine.create(**preset)
            logger.info(f"创建红线规则: {rule_key} - {preset.get('rule_name')}")
        except Exception as e:
            logger.error(f"创建红线规则失败: {rule_key}, {e}")

    # 统计创建的规则数量
    total = await TradeRedLine.all().count()
    enabled = await TradeRedLine.filter(is_enabled=True).count()
    logger.info(f"红线规则初始化完成, 共 {total} 条规则, 已启用 {enabled} 条")


async def main():
    """主函数"""
    await init_db()
    try:
        await init_red_lines()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())