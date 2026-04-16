"""
factor-service 配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """factor-service 配置"""

    # 服务配置
    PROJECT_NAME: str = "因子分析与评分计算服务"
    API_V1_STR: str = "/api/v1"
    SERVICE_PORT: int = 8010
    SERVICE_HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # CORS设置
    ORIGINS: List[str] = ["*"]

    # stock-service MCP 地址
    STOCK_SERVICE_URL: str = "http://localhost:8008"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()