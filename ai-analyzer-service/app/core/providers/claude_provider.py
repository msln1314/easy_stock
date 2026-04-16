"""
Claude API Provider
"""
from typing import Dict, List, Optional, AsyncGenerator
import anthropic
from app.core.config import settings
from app.core.logging import get_logger
from app.core.providers.base_provider import BaseAIProvider

logger = get_logger(__name__)


class ClaudeProvider(BaseAIProvider):
    """Claude API Provider"""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.base_url = settings.ANTHROPIC_BASE_URL
        self.default_model = "claude-sonnet-4-6"
        self.models = [
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "claude-haiku-4-5-20251001"
        ]

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Claude API Key 未配置")

    async def analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """执行分析"""
        if not self.client:
            return "Claude 服务未配置"

        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        try:
            message = self.client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API 调用失败: {e}")
            return f"分析失败: {str(e)}"

    async def stream_analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式执行分析"""
        if not self.client:
            yield "Claude 服务未配置"
            return

        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        try:
            with self.client.messages.stream(
                model=model_name,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Claude 流式 API 调用失败: {e}")
            yield f"分析失败: {str(e)}"

    def get_model_list(self) -> List[str]:
        """获取支持的模型列表"""
        return self.models

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return bool(self.api_key and self.client)