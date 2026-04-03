"""
数据库配置 - Tortoise-ORM
"""
from tortoise import Tortoise
from config.settings import DB_URL, BASE_DIR

# Tortoise-ORM配置
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": f"{BASE_DIR}/data/stock_policy.db",
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.strategy", "models.indicator", "models.signal", "models.risk", "models.warning", "models.indicator_library", "models.scheduler", "models.user", "models.dict_type", "models.dict_item", "models.sys_config", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_timezone": "Asia/Shanghai",
}


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()