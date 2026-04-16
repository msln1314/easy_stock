"""
OpenAI API Provider
"""
from typing import Dict, List, Optional, AsyncGenerator
from openai import OpenAI, AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.core.providers.base_provider import BaseAIProvider

logger = get_logger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI API Provider"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.default_model = "gpt-4o-mini"
        self.models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ]

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
            self.async_client = None
            logger.warning("OpenAI API Key 未配置")

    async def analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """执行分析"""
        if not self.async_client:
            return "OpenAI 服务未配置"

        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        try:
            response = await self.async_client.chat.completions.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}")
            return f"分析失败: {str(e)}"

    async def stream_analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式执行分析"""
        if not self.async_client:
            yield "OpenAI 服务未配置"
            return

        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        try:
            stream = await self.async_client.chat.completions.create(
                model=model_name,
                max_tokens=2000,
                stream=True,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI 流式 API 调用失败: {e}")
            yield f"分析失败: {str(e)}"

    def get_model_list(self) -> List[str]:
        """获取支持的模型列表"""
        return self.models

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return bool(self.api_key and self.client)