"""
系统配置相关Schema定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class SysConfigBase(BaseModel):
    """系统配置基础"""
    key: str = Field(..., max_length=100, description="配置键")
    value: str = Field(..., description="配置值")
    category: str = Field(default="basic", description="类别: basic/security/notification")
    data_type: str = Field(default="plain", description="数据类型: plain/encrypted")
    access_type: str = Field(default="public", description="访问类型: public/private")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class SysConfigCreate(SysConfigBase):
    """系统配置创建"""
    pass


class SysConfigUpdate(BaseModel):
    """系统配置更新"""
    value: Optional[str] = Field(None, description="配置值")
    category: Optional[str] = Field(None, description="类别")
    data_type: Optional[str] = Field(None, description="数据类型")
    access_type: Optional[str] = Field(None, description="访问类型")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class SysConfigResponse(SysConfigBase):
    """系统配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    decrypted_value: Optional[str] = Field(None, description="解密后的值")

    class Config:
        from_attributes = True


class SysConfigListResponse(BaseModel):
    """系统配置列表响应"""
    id: int
    key: str
    value: Optional[str]  # 私有配置不返回value
    category: str
    data_type: str
    access_type: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SysConfigPaginatedResponse(BaseModel):
    """系统配置分页响应"""
    total: int
    page: int
    page_size: int
    items: List[SysConfigListResponse]


class PublicConfigResponse(BaseModel):
    """公开配置响应（无需认证）"""
    key: str
    value: str
    description: Optional[str]