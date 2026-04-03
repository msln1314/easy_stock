"""
创建MySQL数据库
"""
import pymysql

# 连接MySQL服务器（不指定数据库）
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='1qaz2wsx',
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS stock_policy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database stock_policy created successfully")
finally:
    conn.close()