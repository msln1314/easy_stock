"""
ETF池Schema定义
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EtfPoolCreate(BaseModel):
    """ETF池创建请求"""
    name: str = Field(..., max_length=100, description="ETF名称")
    code: str = Field(..., max_length=20, description="ETF代码")
    sector: str = Field(..., max_length=50, description="所属行业板块")
    is_active: bool = Field(default=True, description="是否启用")


class EtfPoolUpdate(BaseModel):
    """ETF池更新请求"""
    name: Optional[str] = Field(None, max_length=100, description="ETF名称")
    sector: Optional[str] = Field(None, max_length=50, description="所属行业板块")
    is_active: Optional[bool] = Field(None, description="是否启用")


class EtfPoolResponse(BaseModel):
    """ETF池响应"""
    id: int
    name: str
    code: str
    sector: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True