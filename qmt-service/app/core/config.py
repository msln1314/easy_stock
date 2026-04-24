# backend/qmt-service/app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """QMT服务配置"""

    # 服务配置
    PROJECT_NAME: str = "QMT量化交易服务"
    API_V1_STR: str = "/api/v1"
    SERVICE_PORT: int = 8009
    SERVICE_HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # Backend 配置（用于 API Key 验证）
    BACKEND_URL: str = "http://localhost:8030"

    # CORS设置
    ORIGINS: list = ["*"]

    # QMT客户端配置
    QMT_CLIENT_PATH: str = ""  # QMT客户端路径，如: E:\Program Files\国金QMT交易端模拟
    QMT_ACCOUNT: str = ""      # QMT账号（需先在客户端登录）
    QMT_SESSION_ID: int = 123456  # 会话ID，任意整数

    # 日志配置
    LOG_LEVEL: str = "INFO"

    # API Key 认证配置
    INTERNAL_SYNC_KEY: str = "internal_sync_key_2024"  # 内部同步 Key
    API_KEYS: str = ""  # API Keys（逗号分隔，如: "key1,key2,key3")
    DEBUG_SKIP_AUTH: bool = False  # 开发模式下跳过认证

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()