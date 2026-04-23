"""
数据库配置 - Tortoise-ORM
"""
from tortoise import Tortoise
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Tortoise-ORM配置 - MySQL
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": DB_HOST,
                "port": DB_PORT,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "database": DB_NAME,
                "charset": "utf8mb4",
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.strategy", "models.indicator", "models.signal", "models.risk", "models.warning", "models.indicator_library", "models.scheduler", "models.user", "models.dict_type", "models.dict_item", "models.sys_config", "models.monitor_pool", "models.menu", "models.role", "models.role_menu", "models.user_role", "models.factor", "models.stock_pick", "models.condition_group", "models.stock_analysis", "models.trade_red_line", "models.trade_log", "models.etf_pool", "models.rotation_strategy", "models.etf_score", "models.rotation_signal", "models.rotation_position", "models.rotation_backtest", "models.mcp_config", "models.dashboard_layout", "aerich.models"],
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