"""
数据库初始化脚本
创建初始管理员用户、系统预置字典、基础配置
"""
import asyncio
from tortoise import Tortoise
from passlib.context import CryptContext

from config.database import TORTOISE_ORM
from models.user import User
from models.dict_type import DictType
from models.dict_item import DictItem
from models.sys_config import SysConfig
from utils.crypto import aes_encrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_data():
    """初始化数据"""
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("开始初始化数据...")

    # 1. 创建初始管理员用户
    admin_exists = await User.get_or_none(username="admin")
    if not admin_exists:
        admin = await User.create(
            username="admin",
            password=pwd_context.hash("admin123"),
            email="admin@example.com",
            nickname="系统管理员",
            role="admin",
            status="active"
        )
        print(f"✓ 创建管理员用户: {admin.username} (密码: admin123)")
    else:
        print("✓ 管理员用户已存在")

    # 2. 创建系统预置字典类型
    dict_types_data = [
        {"code": "strategy_status", "name": "策略状态", "category": "system", "description": "策略运行状态"},
        {"code": "execute_mode", "name": "执行模式", "category": "system", "description": "策略执行模式"},
        {"code": "warning_level", "name": "预警级别", "category": "system", "description": "预警级别类型"},
        {"code": "indicator_type", "name": "指标类型", "category": "system", "description": "技术指标类型"},
    ]

    for dt_data in dict_types_data:
        dt = await DictType.get_or_none(code=dt_data["code"])
        if not dt:
            dt = await DictType.create(**dt_data, access_type="public", status="active")
            print(f"✓ 创建字典类型: {dt.name}")

            # 创建对应的字典项
            if dt_data["code"] == "strategy_status":
                items = [
                    {"code": "running", "name": "运行中", "sort": 1},
                    {"code": "paused", "name": "已暂停", "sort": 2},
                    {"code": "stopped", "name": "已停止", "sort": 3},
                ]
            elif dt_data["code"] == "execute_mode":
                items = [
                    {"code": "auto", "name": "自动交易", "sort": 1},
                    {"code": "alert", "name": "信号提醒", "sort": 2},
                    {"code": "simulate", "name": "模拟运行", "sort": 3},
                ]
            elif dt_data["code"] == "warning_level":
                items = [
                    {"code": "high", "name": "高风险", "sort": 1},
                    {"code": "medium", "name": "中风险", "sort": 2},
                    {"code": "low", "name": "低风险", "sort": 3},
                ]
            elif dt_data["code"] == "indicator_type":
                items = [
                    {"code": "ma", "name": "移动平均线", "sort": 1},
                    {"code": "macd", "name": "MACD", "sort": 2},
                    {"code": "rsi", "name": "RSI", "sort": 3},
                    {"code": "kdj", "name": "KDJ", "sort": 4},
                    {"code": "boll", "name": "布林带", "sort": 5},
                ]
            else:
                items = []

            for item_data in items:
                await DictItem.create(
                    type_id=dt.id,
                    code=item_data["code"],
                    name=item_data["name"],
                    sort=item_data["sort"],
                    status="active"
                )
                print(f"  ✓ 创建字典项: {item_data['name']}")

    # 3. 创建基础系统配置
    configs_data = [
        {"key": "system_name", "value": "策略中心系统", "category": "basic", "description": "系统名称"},
        {"key": "system_version", "value": "1.0.0", "category": "basic", "description": "系统版本"},
        {"key": "system_description", "value": "股票交易策略管理系统", "category": "basic", "description": "系统描述"},
        {"key": "jwt_expire_minutes", "value": "1440", "category": "security", "description": "JWT过期时间(分钟)"},
        {"key": "password_min_length", "value": "6", "category": "security", "description": "密码最小长度"},
        {"key": "login_max_attempts", "value": "5", "category": "security", "description": "最大登录尝试次数"},
        {"key": "email_enabled", "value": "false", "category": "notification", "description": "是否启用邮件通知"},
        {"key": "email_smtp_server", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "SMTP服务器"},
        {"key": "email_username", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "邮箱用户名"},
        {"key": "email_password", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "邮箱密码"},
    ]

    for cfg_data in configs_data:
        cfg = await SysConfig.get_or_none(key=cfg_data["key"])
        if not cfg:
            value = cfg_data["value"]
            # 加密敏感配置
            if cfg_data.get("data_type") == "encrypted" and value:
                value = aes_encrypt(value)

            await SysConfig.create(
                key=cfg_data["key"],
                value=value,
                category=cfg_data.get("category", "basic"),
                data_type=cfg_data.get("data_type", "plain"),
                access_type=cfg_data.get("access_type", "public"),
                description=cfg_data.get("description", "")
            )
            print(f"✓ 创建系统配置: {cfg_data['key']}")

    print("\n数据初始化完成!")
    print("=" * 50)
    print("管理员账号: admin")
    print("管理员密码: admin123")
    print("=" * 50)

    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_data())