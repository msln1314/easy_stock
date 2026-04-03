# -*- coding: utf-8 -*-
"""
Database initialization script
Create initial admin user, system dictionaries, basic configs
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from tortoise import Tortoise
import bcrypt

from config.database import TORTOISE_ORM
from models.user import User
from models.dict_type import DictType
from models.dict_item import DictItem
from models.sys_config import SysConfig
from utils.crypto import aes_encrypt


def hash_password(password: str) -> str:
    """Hash password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def init_data():
    """Initialize data"""
    # Initialize database connection
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    print("Starting data initialization...")

    # 1. Create initial admin user
    admin_exists = await User.get_or_none(username="admin")
    if not admin_exists:
        admin = await User.create(
            username="admin",
            password=hash_password("admin123"),
            email="admin@example.com",
            nickname="Administrator",
            role="admin",
            status="active"
        )
        print(f"[OK] Created admin user: {admin.username} (password: admin123)")
    else:
        print("[OK] Admin user already exists")

    # 2. Create system dictionary types
    dict_types_data = [
        {"code": "strategy_status", "name": "Strategy Status", "category": "system", "description": "Strategy running status"},
        {"code": "execute_mode", "name": "Execute Mode", "category": "system", "description": "Strategy execute mode"},
        {"code": "warning_level", "name": "Warning Level", "category": "system", "description": "Warning level type"},
        {"code": "indicator_type", "name": "Indicator Type", "category": "system", "description": "Technical indicator type"},
    ]

    for dt_data in dict_types_data:
        dt = await DictType.get_or_none(code=dt_data["code"])
        if not dt:
            dt = await DictType.create(**dt_data, access_type="public", status="active")
            print(f"[OK] Created dict type: {dt.name}")

            # Create corresponding dict items
            if dt_data["code"] == "strategy_status":
                items = [
                    {"code": "running", "name": "Running", "sort": 1},
                    {"code": "paused", "name": "Paused", "sort": 2},
                    {"code": "stopped", "name": "Stopped", "sort": 3},
                ]
            elif dt_data["code"] == "execute_mode":
                items = [
                    {"code": "auto", "name": "Auto Trade", "sort": 1},
                    {"code": "alert", "name": "Alert Only", "sort": 2},
                    {"code": "simulate", "name": "Simulation", "sort": 3},
                ]
            elif dt_data["code"] == "warning_level":
                items = [
                    {"code": "high", "name": "High Risk", "sort": 1},
                    {"code": "medium", "name": "Medium Risk", "sort": 2},
                    {"code": "low", "name": "Low Risk", "sort": 3},
                ]
            elif dt_data["code"] == "indicator_type":
                items = [
                    {"code": "ma", "name": "MA", "sort": 1},
                    {"code": "macd", "name": "MACD", "sort": 2},
                    {"code": "rsi", "name": "RSI", "sort": 3},
                    {"code": "kdj", "name": "KDJ", "sort": 4},
                    {"code": "boll", "name": "Bollinger", "sort": 5},
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
                print(f"  [OK] Created dict item: {item_data['name']}")

    # 3. Create basic system configs
    configs_data = [
        {"key": "system_name", "value": "Strategy Center", "category": "basic", "description": "System name"},
        {"key": "system_version", "value": "1.0.0", "category": "basic", "description": "System version"},
        {"key": "system_description", "value": "Stock Trading Strategy Management System", "category": "basic", "description": "System description"},
        {"key": "jwt_expire_minutes", "value": "1440", "category": "security", "description": "JWT expire time (minutes)"},
        {"key": "password_min_length", "value": "6", "category": "security", "description": "Password min length"},
        {"key": "login_max_attempts", "value": "5", "category": "security", "description": "Max login attempts"},
        {"key": "email_enabled", "value": "false", "category": "notification", "description": "Enable email notification"},
        {"key": "email_smtp_server", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "SMTP server"},
        {"key": "email_username", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "Email username"},
        {"key": "email_password", "value": "", "category": "notification", "data_type": "encrypted", "access_type": "private", "description": "Email password"},
    ]

    for cfg_data in configs_data:
        cfg = await SysConfig.get_or_none(key=cfg_data["key"])
        if not cfg:
            value = cfg_data["value"]
            # Encrypt sensitive configs
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
            print(f"[OK] Created system config: {cfg_data['key']}")

    print("\nData initialization completed!")
    print("=" * 50)
    print("Admin account: admin")
    print("Admin password: admin123")
    print("=" * 50)

    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_data())