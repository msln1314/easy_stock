"""
初始化系统配置数据

包含：基础配置、安全认证、通知渠道、AI服务
"""
import asyncio
from config.database import init_db, close_db
from models.sys_config import SysConfig
from services.config import SysConfigService
from schemas.config import SysConfigCreate


async def init_all_configs():
    """初始化所有系统配置"""
    service = SysConfigService()

    # 定义所有配置项
    configs = [
        # ===== 基础配置 =====
        {
            "key": "system.name",
            "value": "策略中心",
            "category": "basic",
            "data_type": "plain",
            "access_type": "public",
            "description": "系统名称"
        },
        {
            "key": "system.version",
            "value": "1.0.0",
            "category": "basic",
            "data_type": "plain",
            "access_type": "public",
            "description": "系统版本"
        },
        {
            "key": "system.footer",
            "value": "© 2024 策略中心系统",
            "category": "basic",
            "data_type": "plain",
            "access_type": "public",
            "description": "页脚信息"
        },
        {
            "key": "login_captcha_enabled",
            "value": "false",
            "category": "security",
            "data_type": "plain",
            "access_type": "public",
            "description": "是否启用登录验证码"
        },
        {
            "key": "qmt.service_url",
            "value": "http://localhost:8009",
            "category": "basic",
            "data_type": "plain",
            "access_type": "public",
            "description": "QMT服务地址"
        },

        # ===== 安全认证配置 =====
        {
            "key": "jwt.expire_hours",
            "value": "24",
            "category": "security",
            "data_type": "plain",
            "access_type": "public",
            "description": "Token过期时间(小时)"
        },
        {
            "key": "password.min_length",
            "value": "6",
            "category": "security",
            "data_type": "plain",
            "access_type": "public",
            "description": "密码最小长度"
        },

        # ===== 通知配置 =====
        # 通知开关和默认配置名称（具体账号在通知渠道中配置）
        {
            "key": "notification.enabled",
            "value": "true",
            "category": "notification",
            "data_type": "plain",
            "access_type": "public",
            "description": "开启通知功能"
        },
        {
            "key": "notification.default_channel",
            "value": "",
            "category": "notification",
            "data_type": "plain",
            "access_type": "public",
            "description": "默认通知渠道名称（可选）"
        },

        # ===== AI服务配置 =====
        {
            "key": "ai.enabled",
            "value": "false",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "开启AI功能"
        },
        {
            "key": "ai.qmt_enabled",
            "value": "false",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "开启QMT交易（AI可执行交易操作）"
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
        },
        {
            "key": "ai.temperature",
            "value": "0.7",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "AI温度参数(0-1)"
        },
        {
            "key": "ai.max_tokens",
            "value": "2000",
            "category": "ai",
            "data_type": "plain",
            "access_type": "public",
            "description": "最大输出Token数"
        },
    ]

    created = 0
    updated = 0

    for config_data in configs:
        existing = await service.get_config_by_key(config_data["key"])
        if not existing:
            await service.create_config(SysConfigCreate(**config_data))
            print(f"[+] 创建: {config_data['key']}")
            created += 1
        else:
            # 更新描述
            if config_data.get("description"):
                await SysConfig.filter(key=config_data["key"]).update(
                    description=config_data["description"]
                )
            print(f"[-] 已存在: {config_data['key']}")
            updated += 1

    print(f"\n配置初始化完成！创建 {created} 个，跳过 {updated} 个")
    return created, updated


if __name__ == "__main__":
    async def main():
        await init_db()
        try:
            await init_all_configs()
        finally:
            await close_db()

    asyncio.run(main())