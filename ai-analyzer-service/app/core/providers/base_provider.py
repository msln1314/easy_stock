"""
AI Provider 基础抽象类
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator


class BaseAIProvider(ABC):
    """AI Provider 基础抽象类"""

    @abstractmethod
    async def analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        执行分析

        Args:
            prompt: 分析提示词
            context: 分析上下文数据
            model: 模型名称（可选）
            temperature: 温度参数
            max_tokens: 最大输出 token 数

        Returns:
            分析结果文本
        """
        pass

    @abstractmethod
    async def stream_analyze(
        self,
        prompt: str,
        context: Dict,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式执行分析

        Args:
            prompt: 分析提示词
            context: 分析上下文数据
            model: 模型名称（可选）

        Returns:
            流式返回分析结果
        """
        pass

    @abstractmethod
    def get_model_list(self) -> List[str]:
        """
        获取支持的模型列表

        Returns:
            模型名称列表
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查服务是否可用

        Returns:
            是否可用
        """
        pass

    def _build_full_prompt(self, prompt: str, context: Dict) -> str:
        """
        构建完整的提示词

        Args:
            prompt: 基础提示词
            context: 上下文数据

        Returns:
            完整提示词
        """
        import json

        context_str = json.dumps(context, indent=2, ensure_ascii=False)
        full_prompt = f"{prompt}\n\n上下文数据：\n{context_str}"
        return full_prompt