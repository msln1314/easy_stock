"""
初始化AI配置数据
"""
import asyncio
from models.sys_config import SysConfig
from services.config import SysConfigService
from schemas.config import SysConfigCreate


async def init_ai_configs():
    """初始化AI配置"""
    service = SysConfigService()

    # 定义AI配置项
    ai_configs = [
        {
            "key": "ai.qmt_enabled",
            "value": "false",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "开启QMT交易（开启后AI可执行交易操作）"
        },
        {
            "key": "ai.openai_api_key",
            "value": "",
            "category": "ai",
            "data_type": "encrypted",
            "access_type": "private",
            "description": "OpenAI API密钥"
        },
        {
            "key": "ai.openai_base_url",
            "value": "https://api.openai.com/v1",
            "category": "ai",
            "data_type": "plain",
            "access_type": "private",
            "description": "OpenAI API地址（可配置代理）"
        },
        {
            "key": "ai.openai_model",
            "value": "gpt-4o-mini",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "OpenAI模型名称"
        }
    ]

    for config_data in ai_configs:
        existing = await service.get_config_by_key(config_data["key"])
        if not existing:
            await service.create_config(SysConfigCreate(**config_data))
            print(f"✓ 创建配置: {config_data['key']}")
        else:
            print(f"- 配置已存在: {config_data['key']}")

    print("\nAI配置初始化完成！")
    print("请在系统配置页面设置 ai.openai_api_key 并开启QMT交易")


if __name__ == "__main__":
    from config.database import init_db, close_db

    async def main():
        await init_db()
        try:
            await init_ai_configs()
        finally:
            await close_db()

    asyncio.run(main())