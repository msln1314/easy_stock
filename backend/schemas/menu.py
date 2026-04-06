"""
菜单相关Schema定义
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class MenuBase(BaseModel):
    """菜单基础"""
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    name: str = Field(..., max_length=50, description="菜单名称")
    path: str = Field(..., max_length=100, description="路由路径")
    component: Optional[str] = Field(None, max_length=100, description="组件路径")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    sort: int = Field(default=0, description="排序")
    visible: bool = Field(default=True, description="是否显示")
    status: str = Field(default="active", description="状态")
    menu_type: str = Field(..., max_length=10, description="类型: directory/menu/button")
    permission: Optional[str] = Field(None, max_length=100, description="权限标识")


class MenuCreate(MenuBase):
    """菜单创建"""
    pass


class MenuUpdate(BaseModel):
    """菜单更新"""
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    name: Optional[str] = Field(None, max_length=50, description="菜单名称")
    path: Optional[str] = Field(None, max_length=100, description="路由路径")
    component: Optional[str] = Field(None, max_length=100, description="组件路径")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    sort: Optional[int] = Field(None, description="排序")
    visible: Optional[bool] = Field(None, description="是否显示")
    status: Optional[str] = Field(None, description="状态")
    menu_type: Optional[str] = Field(None, max_length=10, description="类型")
    permission: Optional[str] = Field(None, max_length=100, description="权限标识")


class MenuResponse(MenuBase):
    """菜单响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuTreeResponse(MenuBase):
    """菜单树形响应"""
    id: int
    children: List[MenuTreeResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuListResponse(BaseModel):
    """菜单列表响应（扁平）"""
    id: int
    parent_id: Optional[int]
    name: str
    path: str
    icon: Optional[str]
    sort: int
    visible: bool
    status: str
    menu_type: str
    permission: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserMenuResponse(BaseModel):
    """用户菜单响应（用于前端路由）"""
    id: int
    parent_id: Optional[int]
    name: str
    path: str
    icon: Optional[str]
    sort: int
    menu_type: str
    children: List[UserMenuResponse] = []