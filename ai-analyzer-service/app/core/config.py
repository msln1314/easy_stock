"""
ai-analyzer-service 配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """ai-analyzer-service 配置"""

    # 服务配置
    PROJECT_NAME: str = "AI 智能分析服务"
    API_V1_STR: str = "/api/v1"
    SERVICE_PORT: int = 8011
    SERVICE_HOST: str = "0.0.0.0"
    DEBUG: bool = False

    # CORS设置
    ORIGINS: List[str] = ["*"]

    # factor-service MCP 地址
    FACTOR_SERVICE_URL: str = "http://localhost:8010"

    # 默认 AI Provider
    AI_PROVIDER: str = "claude"

    # Claude 配置
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"

    # OpenAI 配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Ollama 配置
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2:7b"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()