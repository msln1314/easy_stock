"""
AI Provider 管理器
"""
from typing import Dict, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.core.providers.base_provider import BaseAIProvider
from app.core.providers.claude_provider import ClaudeProvider
from app.core.providers.openai_provider import OpenAIProvider
from app.core.providers.ollama_provider import OllamaProvider

logger = get_logger(__name__)


class AIProviderManager:
    """AI Provider 管理器"""

    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {
            "claude": ClaudeProvider(),
            "openai": OpenAIProvider(),
            "ollama": OllamaProvider()
        }
        self.current_provider = settings.AI_PROVIDER
        logger.info(f"AI Provider Manager 初始化，默认 Provider: {self.current_provider}")

    def get_provider(self, provider_name: Optional[str] = None) -> BaseAIProvider:
        """
        获取指定的 Provider

        Args:
            provider_name: Provider 名称，默认使用配置的 Provider

        Returns:
            AI Provider 实例
        """
        name = provider_name or self.current_provider
        if name not in self.providers:
            logger.warning(f"未知的 Provider: {name}, 使用默认 Provider")
            name = self.current_provider

        return self.providers[name]

    def switch_provider(self, provider_name: str) -> bool:
        """
        切换 Provider

        Args:
            provider_name: Provider 名称

        Returns:
            是否切换成功
        """
        if provider_name not in self.providers:
            logger.error(f"未知的 Provider: {provider_name}")
            return False

        self.current_provider = provider_name
        logger.info(f"切换 Provider: {provider_name}")
        return True

    def get_all_providers(self) -> Dict[str, BaseAIProvider]:
        """获取所有 Provider"""
        return self.providers

    def check_availability(self) -> Dict[str, bool]:
        """
        检查所有 Provider 的可用性

        Returns:
            Provider 可用性映射
        """
        return {
            name: provider.is_available()
            for name, provider in self.providers.items()
        }


# 单例
ai_provider_manager = AIProviderManager()