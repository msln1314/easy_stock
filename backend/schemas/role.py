"""
角色相关Schema定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础"""
    name: str = Field(..., max_length=50, description="角色名称")
    code: str = Field(..., max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=200, description="描述")
    status: str = Field(default="active", description="状态")


class RoleCreate(RoleBase):
    """角色创建"""
    menu_ids: List[int] = Field(default=[], description="菜单ID列表")


class RoleUpdate(BaseModel):
    """角色更新"""
    name: Optional[str] = Field(None, max_length=50, description="角色名称")
    code: Optional[str] = Field(None, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=200, description="描述")
    status: Optional[str] = Field(None, description="状态")


class RoleResponse(RoleBase):
    """角色响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """角色列表响应"""
    id: int
    name: str
    code: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoleWithMenusResponse(RoleBase):
    """角色详情响应（含菜单）"""
    id: int
    menu_ids: List[int] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignMenusRequest(BaseModel):
    """分配菜单请求"""
    menu_ids: List[int] = Field(..., description="菜单ID列表")