"""
Ollama Provider (本地模型)
"""
from typing import Dict, List, Optional, AsyncGenerator
import httpx
import json
from app.core.config import settings
from app.core.logging import get_logger
from app.core.providers.base_provider import BaseAIProvider

logger = get_logger(__name__)


class OllamaProvider(BaseAIProvider):
    """Ollama Provider (本地模型)"""

    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.default_model = settings.OLLAMA_MODEL
        self.models = ["llama3", "llama3:8b", "qwen2:7b", "qwen2:14b"]
        self.timeout = 60.0

    async def analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """执行分析"""
        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        url = f"{self.host}/api/generate"
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama API 调用失败: {e}")
            return f"分析失败: {str(e)}"

    async def stream_analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """流式执行分析"""
        full_prompt = self._build_full_prompt(prompt, context)
        model_name = model or self.default_model

        url = f"{self.host}/api/generate"
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Ollama 流式 API 调用失败: {e}")
            yield f"分析失败: {str(e)}"

    def get_model_list(self) -> List[str]:
        """获取支持的模型列表"""
        return self.models

    def is_available(self) -> bool:
        """检查服务是否可用"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False