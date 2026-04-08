"""
测试配置文件
"""
import os

# 后端服务地址
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8030")

# 测试账号配置
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASS", "admin123")

USER_USERNAME = os.getenv("TEST_USER_NAME", "test_user")
USER_PASSWORD = os.getenv("TEST_USER_PASS", "test123")

# 超时设置
REQUEST_TIMEOUT = 30

# 报告输出路径
REPORTS_DIR = "backend/tests/reports"
INTERFACE_REPORT = f"{REPORTS_DIR}/interface_report.html"
TEST_REPORT = f"{REPORTS_DIR}/test_report.html"