"""
模型管理 MCP 类
"""
from typing import Dict
from app.services.model_service import model_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelMCP:
    """模型管理 MCP 类"""

    def list_models(self) -> Dict:
        """
        获取支持的模型列表

        Returns:
            模型列表
        """
        logger.info("MCP获取模型列表")
        result = model_service.get_available_models()
        return result.model_dump()

    def current_model(self) -> Dict:
        """
        获取当前使用的模型

        Returns:
            当前模型信息
        """
        logger.info("MCP获取当前模型")
        result = model_service.get_current_model()
        return result.model_dump()

    def switch_model(self, provider: str, model: str = None) -> Dict:
        """
        切换模型

        Args:
            provider: Provider名称
            model: 模型名称（可选）

        Returns:
            切换结果
        """
        logger.info(f"MCP切换模型: provider={provider}")
        result = model_service.switch_model(provider, model)
        return result.model_dump()

    def check_status(self) -> Dict:
        """
        检查各 Provider 状态

        Returns:
            状态信息
        """
        logger.info("MCP检查状态")
        result = model_service.check_status()
        return result.model_dump()


# 单例
model_mcp = ModelMCP()