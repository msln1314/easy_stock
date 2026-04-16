"""
模型管理数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ModelInfo(BaseModel):
    """模型信息"""
    provider: str = Field(..., description="Provider名称")
    models: List[str] = Field(default_factory=list, description="支持的模型列表")


class CurrentModel(BaseModel):
    """当前模型"""
    provider: str = Field(..., description="当前Provider")
    model: str = Field(..., description="当前模型")


class ProviderStatus(BaseModel):
    """Provider状态"""
    provider: str = Field(..., description="Provider名称")
    available: bool = Field(..., description="是否可用")
    error: Optional[str] = Field(default=None, description="错误信息")


class SwitchModelRequest(BaseModel):
    """切换模型请求"""
    provider: str = Field(..., description="Provider名称")
    model: Optional[str] = Field(default=None, description="模型名称")


class SwitchModelResult(BaseModel):
    """切换模型结果"""
    success: bool = Field(..., description="是否成功")
    provider: str = Field(..., description="Provider名称")
    model: str = Field(..., description="当前模型")
    message: str = Field(default="", description="消息")


class ModelListResponse(BaseModel):
    """模型列表响应"""
    providers: List[ModelInfo] = Field(default_factory=list, description="Provider列表")


class ModelStatusResponse(BaseModel):
    """模型状态响应"""
    statuses: List[ProviderStatus] = Field(default_factory=list, description="状态列表")
    current_provider: str = Field(..., description="当前Provider")