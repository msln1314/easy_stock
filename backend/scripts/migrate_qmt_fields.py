# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加 QMT 账户字段和 MCP 配置表
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from tortoise import Tortoise
from config.database import TORTOISE_ORM


async def migrate():
    """执行数据库迁移"""
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)

    print("开始数据库迁移...")

    # 获取数据库连接
    conn = Tortoise.get_connection("default")

    # 先检查表结构，获取已有字段
    columns_result = await conn.execute_query(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 't_user'"
    )
    # columns_result 是 (affected_rows, rows) 格式，rows 是字典列表
    existing_columns = {row['COLUMN_NAME'] for row in columns_result[1]}

    # 定义需要添加的 QMT 字段
    qmt_fields = [
        ("qmt_account_id", "VARCHAR(50) NULL COMMENT 'QMT账户ID/账号'"),
        ("qmt_account_name", "VARCHAR(100) NULL COMMENT 'QMT账户名称'"),
        ("qmt_client_path", "VARCHAR(200) NULL COMMENT 'QMT客户端路径'"),
        ("qmt_session_id", "INT DEFAULT 123456 COMMENT 'QMT会话ID'"),
        ("qmt_api_key", "VARCHAR(100) NULL COMMENT 'QMT API Key(加密存储)'"),
        ("qmt_enabled", "BOOLEAN DEFAULT FALSE COMMENT '是否启用QMT交易'"),
    ]

    print("\n添加 QMT 字段到 t_user 表:")
    for field_name, field_def in qmt_fields:
        if field_name in existing_columns:
            print(f"  [--] 字段已存在: {field_name}")
        else:
            try:
                sql = f"ALTER TABLE t_user ADD COLUMN {field_name} {field_def}"
                await conn.execute_query(sql)
                print(f"  [OK] 已添加: {field_name}")
            except Exception as e:
                print(f"  [FAIL] {field_name}: {e}")

    # 创建 MCP 配置表
    create_mcp_table_sql = """
    CREATE TABLE IF NOT EXISTS t_mcp_config (
        id INT PRIMARY KEY AUTO_INCREMENT,
        service_name VARCHAR(50) UNIQUE NOT NULL COMMENT '服务名称',
        service_url VARCHAR(200) NOT NULL COMMENT '服务地址',
        api_key VARCHAR(100) NULL COMMENT 'API Key(加密存储)',
        enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
        description VARCHAR(500) NULL COMMENT '描述',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) COMMENT 'MCP服务配置表'
    """

    print("\n创建 MCP 配置表:")
    try:
        await conn.execute_query(create_mcp_table_sql)
        print("  [OK] t_mcp_config 表创建成功")
    except Exception as e:
        if "already exists" in str(e):
            print("  [--] t_mcp_config 表已存在")
        else:
            print(f"  [FAIL] {e}")

    # 插入默认 qmt-service 配置
    insert_default_sql = """
    INSERT INTO t_mcp_config (service_name, service_url, enabled, description)
    VALUES ('qmt-service', 'http://localhost:8009', TRUE, 'QMT量化交易服务')
    ON DUPLICATE KEY UPDATE service_url = 'http://localhost:8009'
    """

    print("\n插入默认 MCP 配置:")
    try:
        await conn.execute_query(insert_default_sql)
        print("  [OK] qmt-service 默认配置已插入/更新")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # 关闭数据库连接
    await Tortoise.close_connections()

    print("\n迁移完成!")
    print("=" * 50)
    print("新增字段: qmt_account_id, qmt_account_name, qmt_client_path,")
    print("          qmt_session_id, qmt_api_key, qmt_enabled")
    print("新增表: t_mcp_config")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(migrate())