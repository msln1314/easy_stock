"""
MCP配置Schema
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class McpConfigBase(BaseModel):
    """MCP配置基础"""
    service_name: str = Field(..., description="服务名称", max_length=50)
    service_url: str = Field(..., description="服务地址", max_length=200)
    api_key: Optional[str] = Field(None, description="API Key", max_length=100)
    enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述", max_length=500)


class McpConfigCreate(McpConfigBase):
    """创建MCP配置"""
    pass


class McpConfigUpdate(BaseModel):
    """更新MCP配置"""
    service_name: Optional[str] = Field(None, description="服务名称", max_length=50)
    service_url: Optional[str] = Field(None, description="服务地址", max_length=200)
    api_key: Optional[str] = Field(None, description="API Key", max_length=100)
    enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述", max_length=500)


class McpConfigResponse(McpConfigBase):
    """MCP配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class McpConfigListResponse(BaseModel):
    """MCP配置列表响应"""
    total: int
    items: list[McpConfigResponse]