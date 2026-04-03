"""
字典相关Schema定义
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# 字典类型Schema
class DictTypeBase(BaseModel):
    """字典类型基础"""
    code: str = Field(..., max_length=50, description="类型编码")
    name: str = Field(..., max_length=100, description="类型名称")
    category: str = Field(default="system", description="类别: system/custom/config")
    access_type: str = Field(default="public", description="访问类型: public/private")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    sort: int = Field(default=0, description="排序")
    status: str = Field(default="active", description="状态")


class DictTypeCreate(DictTypeBase):
    """字典类型创建"""
    pass


class DictTypeUpdate(BaseModel):
    """字典类型更新"""
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None)
    access_type: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=500)
    sort: Optional[int] = Field(None)
    status: Optional[str] = Field(None)


class DictTypeResponse(DictTypeBase):
    """字典类型响应"""
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DictTypeListResponse(BaseModel):
    """字典类型列表响应"""
    id: int
    code: str
    name: str
    category: str
    access_type: str
    sort: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# 字典项Schema
class DictItemBase(BaseModel):
    """字典项基础"""
    type_id: int = Field(..., description="字典类型ID")
    code: str = Field(..., max_length=50, description="项编码")
    name: str = Field(..., max_length=100, description="项名称")
    value: Optional[str] = Field(None, description="项值")
    data_type: str = Field(default="plain", description="数据类型: plain/encrypted")
    parent_id: Optional[int] = Field(None, description="父级ID")
    sort: int = Field(default=0, description="排序")
    status: str = Field(default="active", description="状态")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class DictItemCreate(DictItemBase):
    """字典项创建"""
    pass


class DictItemUpdate(BaseModel):
    """字典项更新"""
    name: Optional[str] = Field(None, max_length=100)
    value: Optional[str] = Field(None)
    data_type: Optional[str] = Field(None)
    parent_id: Optional[int] = Field(None)
    sort: Optional[int] = Field(None)
    status: Optional[str] = Field(None)
    remark: Optional[str] = Field(None, max_length=500)


class DictItemResponse(DictItemBase):
    """字典项响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    # 解密后的值（仅返回给有权限的用户）
    decrypted_value: Optional[str] = Field(None, description="解密后的值")

    class Config:
        from_attributes = True


class DictItemListResponse(BaseModel):
    """字典项列表响应"""
    id: int
    type_id: int
    code: str
    name: str
    value: Optional[str]
    data_type: str
    parent_id: Optional[int]
    sort: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DictItemTreeResponse(BaseModel):
    """字典项树形响应"""
    id: int
    type_id: int
    code: str
    name: str
    value: Optional[str]
    data_type: str
    parent_id: Optional[int]
    sort: int
    status: str
    children: List[DictItemTreeResponse] = []

    class Config:
        from_attributes = True


# 分页响应
class DictTypePaginatedResponse(BaseModel):
    """字典类型分页响应"""
    total: int
    page: int
    page_size: int
    items: List[DictTypeListResponse]


class DictItemPaginatedResponse(BaseModel):
    """字典项分页响应"""
    total: int
    page: int
    page_size: int
    items: List[DictItemListResponse]