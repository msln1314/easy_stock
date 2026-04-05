"""
组合条件 Schema 定义
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ConditionGroupCreate(BaseModel):
    """创建组合条件组"""
    group_name: str
    logic_type: str = "AND"  # AND 或 OR
    parent_id: Optional[int] = None
    priority: str = "warning"
    description: Optional[str] = None
    condition_ids: List[int] = []  # 创建时直接关联条件


class ConditionGroupUpdate(BaseModel):
    """更新组合条件组"""
    group_name: Optional[str] = None
    logic_type: Optional[str] = None
    priority: Optional[str] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None


class ConditionItemCreate(BaseModel):
    """添加条件项"""
    condition_id: int
    sort_order: int = 0


class ConditionGroupTreeNode(BaseModel):
    """组合条件树节点"""
    id: int
    group_key: str
    group_name: str
    logic_type: str
    priority: str
    is_enabled: bool
    description: Optional[str] = None
    conditions: List[dict] = []  # 包含的条件列表
    subgroups: List['ConditionGroupTreeNode'] = []  # 子分组

    class Config:
        from_attributes = True


class ConditionGroupList(BaseModel):
    """组合条件列表项"""
    id: int
    group_key: str
    group_name: str
    logic_type: str
    priority: str
    is_enabled: bool
    parent_id: Optional[int] = None
    description: Optional[str] = None
    condition_count: int = 0
    subgroup_count: int = 0
    created_at: datetime
    updated_at: datetime