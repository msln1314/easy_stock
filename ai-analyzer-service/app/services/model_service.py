"""
模型管理服务
"""
from typing import Dict, List
from app.core.logging import get_logger
from app.core.ai_provider import ai_provider_manager
from app.models.model_models import (
    ModelInfo,
    CurrentModel,
    ProviderStatus,
    ModelListResponse,
    ModelStatusResponse,
    SwitchModelResult
)

logger = get_logger(__name__)


class ModelService:
    """模型管理服务"""

    def __init__(self):
        self.manager = ai_provider_manager

    def get_available_models(self) -> ModelListResponse:
        """
        获取支持的模型列表

        Returns:
            模型列表响应
        """
        providers = self.manager.get_all_providers()
        model_infos = []

        for name, provider in providers.items():
            model_infos.append(ModelInfo(
                provider=name,
                models=provider.get_model_list()
            ))

        return ModelListResponse(providers=model_infos)

    def get_current_model(self) -> CurrentModel:
        """
        获取当前使用的模型

        Returns:
            当前模型信息
        """
        provider = self.manager.get_provider()
        provider_name = self.manager.current_provider

        # 获取默认模型
        models = provider.get_model_list()
        default_model = models[0] if models else "unknown"

        return CurrentModel(
            provider=provider_name,
            model=default_model
        )

    def switch_model(self, provider: str, model: str = None) -> SwitchModelResult:
        """
        切换模型

        Args:
            provider: Provider名称
            model: 模型名称（可选）

        Returns:
            切换结果
        """
        success = self.manager.switch_provider(provider)

        if success:
            logger.info(f"切换成功: provider={provider}")
            return SwitchModelResult(
                success=True,
                provider=provider,
                model=model or self.get_current_model().model,
                message=f"成功切换到 {provider}"
            )
        else:
            logger.warning(f"切换失败: provider={provider}")
            return SwitchModelResult(
                success=False,
                provider=self.manager.current_provider,
                model=self.get_current_model().model,
                message=f"切换失败，未知的 Provider: {provider}"
            )

    def check_status(self) -> ModelStatusResponse:
        """
        检查各 Provider 状态

        Returns:
            状态响应
        """
        availability = self.manager.check_availability()
        statuses = []

        for name, available in availability.items():
            error = None if available else "服务不可用或未配置"
            statuses.append(ProviderStatus(
                provider=name,
                available=available,
                error=error
            ))

        return ModelStatusResponse(
            statuses=statuses,
            current_provider=self.manager.current_provider
        )


# 单例
model_service = ModelService()