# 卖出预警组合条件功能实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现卖出预警组合条件功能，支持多条件AND/OR混合逻辑组合，任意层级嵌套，表单式层级配置界面。

**Architecture:** 后端采用嵌套分组模型（WarningConditionGroup + GroupConditionItem）支持递归组合，评估器扩展支持阈值类指标和组合条件递归评估，前端新增组合条件管理页面。

**Tech Stack:** Python/FastAPI/TortoiseORM (后端), Vue3/NaiveUI/TypeScript (前端)

---

## Task 1: 数据模型 - 新增组合条件表

**Files:**
- Create: `backend/models/condition_group.py`
- Modify: `backend/models/__init__.py`

- [ ] **Step 1: 创建组合条件组模型**

```python
# backend/models/condition_group.py
"""
组合条件数据模型
"""
from tortoise import fields
from tortoise.models import Model


class WarningConditionGroup(Model):
    """组合条件组表"""
    id = fields.IntField(pk=True)
    group_key = fields.CharField(max_length=50, unique=True, description="组合唯一标识")
    group_name = fields.CharField(max_length=100, description="组合名称")
    logic_type = fields.CharField(max_length=10, default="AND", description="逻辑类型: AND/OR")
    parent_id = fields.IntField(null=True, description="父分组ID，支持嵌套")
    priority = fields.CharField(max_length=20, default="warning", description="优先级")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    description = fields.TextField(null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_condition_groups"
        indexes = [("parent_id",), ("group_key",)]

    def __str__(self):
        return f"{self.group_key} - {self.group_name}"


class GroupConditionItem(Model):
    """组合条件项表 - 关联具体预警条件到分组"""
    id = fields.IntField(pk=True)
    group_id = fields.IntField(description="所属分组ID")
    condition_id = fields.IntField(description="关联的预警条件ID")
    sort_order = fields.IntField(default=0, description="排序")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "group_condition_items"
        indexes = [("group_id",), ("condition_id",)]

    def __str__(self):
        return f"Group {self.group_id} - Condition {self.condition_id}"
```

- [ ] **Step 2: 更新模型导入**

```python
# backend/models/__init__.py 添加导入
from .condition_group import WarningConditionGroup, GroupConditionItem
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/models/condition_group.py backend/models/__init__.py
git commit -m "feat: 添加组合条件数据模型"
```

---

## Task 2: 数据模型 - 修改预警股票池表

**Files:**
- Modify: `backend/models/warning.py`

- [ ] **Step 1: 修改 WarningStockPool 模型**

在 `WarningStockPool` 类中添加新字段：

```python
# 在 WarningStockPool 类中添加以下字段（在现有字段之后）
    group_key = fields.CharField(max_length=50, null=True, description="触发组合KEY")
    is_group = fields.BooleanField(default=False, description="是否组合预警")
    triggered_conditions = fields.JSONField(null=True, description="满足的条件列表")
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/models/warning.py
git commit -m "feat: 预警股票池表新增组合条件字段"
```

---

## Task 3: 数据模型 - 扩展指标库表

**Files:**
- Modify: `backend/models/indicator_library.py`

- [ ] **Step 1: 添加指标类型枚举**

在 `IndicatorCategory` 枚举后添加：

```python
class IndicatorCategory(str, Enum):
    """指标分类"""
    TREND = "trend"           # 趋势类指标 (MA, EMA, BOLL, etc.)
    MOMENTUM = "momentum"     # 动量类指标
    OSCILLATOR = "oscillator" # 震荡类指标
    VOLUME = "volume"         # 成交量类指标 (VOL_MA, OBV, etc.)
    VOLATILITY = "volatility" # 波动率类指标
    QUOTE = "quote"           # 行情类指标（新增）
    FUNDAMENTAL = "fundamental"  # 基本面类指标（新增）


class IndicatorType(str, Enum):
    """指标类型"""
    CALCULATED = "calculated"  # 需要计算的指标
    THRESHOLD = "threshold"    # 阈值类指标
```

- [ ] **Step 2: 修改 IndicatorLibrary 模型**

在模型中添加 `indicator_type` 字段：

```python
# 在 IndicatorLibrary 类中添加字段（在 category 字段之后）
    indicator_type = fields.CharEnumField(IndicatorType, default=IndicatorType.CALCULATED, description="指标类型")
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/models/indicator_library.py
git commit -m "feat: 指标库表新增指标类型字段"
```

---

## Task 4: 新增阈值类指标数据

**Files:**
- Modify: `backend/models/indicator_library.py`

- [ ] **Step 1: 在 INDICATOR_PRESET_DATA 末尾添加阈值类指标**

```python
# 在 INDICATOR_PRESET_DATA 列表末尾添加以下数据
    # ========== 行情阈值类指标 ==========
    {
        "indicator_key": "THRESHOLD_CHANGE",
        "indicator_name": "涨跌幅阈值",
        "category": IndicatorCategory.QUOTE,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "从指定日期开始计算涨跌幅，判断是否达到阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "start_date", "name": "起始日期", "type": "date", "required": True, "desc": "从该日期开始计算涨跌幅"},
            {"key": "threshold_percent", "name": "阈值涨跌幅%", "type": "float", "default": 5, "min": -100, "max": 1000, "desc": "目标涨跌幅百分比"},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "gt", "options": ["gt", "lt", "ge", "le"], "desc": "gt:大于, lt:小于, ge:大于等于, le:小于等于"}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_change_percent", "name": "实际涨跌幅%", "type": "float"},
            {"key": "threshold_percent", "name": "阈值%", "type": "float"},
            {"key": "start_price", "name": "起始价", "type": "float"},
            {"key": "current_price", "name": "当前价", "type": "float"}
        ],
        "usage_guide": "用于判断从某日起的涨跌幅是否达到目标值。正值表示涨幅，负值表示跌幅。",
        "sort_order": 200
    },
    {
        "indicator_key": "THRESHOLD_TURNOVER",
        "indicator_name": "换手率阈值",
        "category": IndicatorCategory.QUOTE,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断换手率是否达到指定阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "换手率阈值%", "type": "float", "default": 10, "min": 0, "max": 100, "desc": "换手率百分比"},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "gt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_turnover", "name": "实际换手率%", "type": "float"},
            {"key": "threshold", "name": "阈值%", "type": "float"}
        ],
        "usage_guide": "换手率高表示交易活跃，低表示交易清淡。",
        "sort_order": 201
    },
    {
        "indicator_key": "THRESHOLD_VOLUME_RATIO",
        "indicator_name": "量比阈值",
        "category": IndicatorCategory.QUOTE,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断量比是否达到指定阈值。量比 = 当日成交量 / 5日平均成交量。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "量比阈值", "type": "float", "default": 2, "min": 0, "max": 100, "desc": "量比值"},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "gt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_volume_ratio", "name": "实际量比", "type": "float"},
            {"key": "threshold", "name": "阈值", "type": "float"}
        ],
        "usage_guide": "量比>1表示放量，<1表示缩量。量比>2为明显放量。",
        "sort_order": 202
    },
    {
        "indicator_key": "THRESHOLD_AMOUNT",
        "indicator_name": "成交额阈值",
        "category": IndicatorCategory.QUOTE,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断成交额是否达到指定阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "成交额阈值", "type": "float", "default": 1, "min": 0, "desc": "成交额数值"},
            {"key": "unit", "name": "单位", "type": "select", "default": "亿", "options": ["亿", "万"]},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "gt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_amount", "name": "实际成交额", "type": "float"},
            {"key": "threshold", "name": "阈值", "type": "float"},
            {"key": "unit", "name": "单位", "type": "string"}
        ],
        "usage_guide": "成交额反映市场活跃度和资金参与程度。",
        "sort_order": 203
    },

    # ========== 基本面阈值类指标 ==========
    {
        "indicator_key": "THRESHOLD_MARKET_VALUE",
        "indicator_name": "市值阈值",
        "category": IndicatorCategory.FUNDAMENTAL,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断股票市值是否达到指定阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "市值阈值", "type": "float", "default": 50, "min": 0, "desc": "市值数值"},
            {"key": "unit", "name": "单位", "type": "select", "default": "亿", "options": ["亿", "万"]},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "lt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_value", "name": "实际市值", "type": "float"},
            {"key": "threshold", "name": "阈值", "type": "float"},
            {"key": "unit", "name": "单位", "type": "string"}
        ],
        "usage_guide": "小市值股票波动大，大市值股票相对稳定。常用50亿区分大小盘。",
        "sort_order": 220
    },
    {
        "indicator_key": "THRESHOLD_PE",
        "indicator_name": "市盈率阈值",
        "category": IndicatorCategory.FUNDAMENTAL,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断市盈率(PE)是否达到指定阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "PE阈值", "type": "float", "default": 30, "min": 0, "desc": "市盈率数值"},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "lt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_pe", "name": "实际PE", "type": "float"},
            {"key": "threshold", "name": "阈值", "type": "float"}
        ],
        "usage_guide": "PE低可能被低估，高可能被高估。负PE表示亏损。",
        "sort_order": 221
    },
    {
        "indicator_key": "THRESHOLD_PB",
        "indicator_name": "市净率阈值",
        "category": IndicatorCategory.FUNDAMENTAL,
        "indicator_type": IndicatorType.THRESHOLD,
        "description": "判断市净率(PB)是否达到指定阈值。",
        "value_type": IndicatorValueType.SINGLE,
        "params": [
            {"key": "threshold", "name": "PB阈值", "type": "float", "default": 3, "min": 0, "desc": "市净率数值"},
            {"key": "compare_op", "name": "比较方式", "type": "select", "default": "lt", "options": ["gt", "lt", "ge", "le"]}
        ],
        "output_fields": [
            {"key": "triggered", "name": "是否触发", "type": "boolean"},
            {"key": "actual_pb", "name": "实际PB", "type": "float"},
            {"key": "threshold", "name": "阈值", "type": "float"}
        ],
        "usage_guide": "PB<1可能破净，PB低可能被低估。",
        "sort_order": 222
    },
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/models/indicator_library.py
git commit -m "feat: 添加行情和基本面阈值类指标"
```

---

## Task 5: 后端 Schema 定义

**Files:**
- Create: `backend/schemas/condition_group.py`

- [ ] **Step 1: 创建 Schema 定义**

```python
# backend/schemas/condition_group.py
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
```

- [ ] **Step 2: 提交代码**

```bash
git add backend/schemas/condition_group.py
git commit -m "feat: 添加组合条件 Schema 定义"
```

---

## Task 6: 后端 API - 组合条件管理

**Files:**
- Create: `backend/api/v1/condition_group.py`

- [ ] **Step 1: 创建组合条件 API**

```python
# backend/api/v1/condition_group.py
"""
组合条件管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import json

from core.response import success_response, error_response
from models.condition_group import WarningConditionGroup, GroupConditionItem
from models.warning import WarningCondition
from schemas.condition_group import (
    ConditionGroupCreate, ConditionGroupUpdate, 
    ConditionItemCreate, ConditionGroupTreeNode
)

router = APIRouter(prefix="/api/warning/groups", tags=["组合条件管理"])


# ==================== 组合条件组接口 ====================

@router.get("")
async def get_condition_groups(parent_id: Optional[int] = Query(None, description="父分组ID，不传则返回根分组")):
    """获取组合条件列表"""
    groups = await WarningConditionGroup.filter(parent_id=parent_id).all()
    
    result = []
    for g in groups:
        # 统计条件数量
        condition_count = await GroupConditionItem.filter(group_id=g.id).count()
        # 统计子分组数量
        subgroup_count = await WarningConditionGroup.filter(parent_id=g.id).count()
        
        result.append({
            "id": g.id,
            "group_key": g.group_key,
            "group_name": g.group_name,
            "logic_type": g.logic_type,
            "priority": g.priority,
            "is_enabled": g.is_enabled,
            "parent_id": g.parent_id,
            "description": g.description,
            "condition_count": condition_count,
            "subgroup_count": subgroup_count,
            "created_at": g.created_at.isoformat() if g.created_at else None,
            "updated_at": g.updated_at.isoformat() if g.updated_at else None
        })
    
    return success_response(result)


@router.get("/tree")
async def get_condition_group_tree():
    """获取组合条件树形结构"""
    async def build_tree(parent_id: Optional[int] = None) -> List[dict]:
        groups = await WarningConditionGroup.filter(parent_id=parent_id).all()
        result = []
        
        for g in groups:
            # 获取条件列表
            items = await GroupConditionItem.filter(group_id=g.id).order_by("sort_order").all()
            conditions = []
            for item in items:
                cond = await WarningCondition.get_or_none(id=item.condition_id)
                if cond:
                    conditions.append({
                        "id": cond.id,
                        "condition_key": cond.condition_key,
                        "condition_name": cond.condition_name,
                        "priority": cond.priority
                    })
            
            # 递归获取子分组
            subgroups = await build_tree(g.id)
            
            result.append({
                "id": g.id,
                "group_key": g.group_key,
                "group_name": g.group_name,
                "logic_type": g.logic_type,
                "priority": g.priority,
                "is_enabled": g.is_enabled,
                "description": g.description,
                "conditions": conditions,
                "subgroups": subgroups
            })
        
        return result
    
    tree = await build_tree()
    return success_response(tree)


@router.post("")
async def create_condition_group(data: ConditionGroupCreate):
    """创建组合条件组"""
    # 生成唯一标识
    group_key = f"GROUP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    group = await WarningConditionGroup.create(
        group_key=group_key,
        group_name=data.group_name,
        logic_type=data.logic_type,
        parent_id=data.parent_id,
        priority=data.priority,
        description=data.description,
        is_enabled=True
    )
    
    # 关联条件
    for idx, cond_id in enumerate(data.condition_ids):
        condition = await WarningCondition.get_or_none(id=cond_id)
        if condition:
            await GroupConditionItem.create(
                group_id=group.id,
                condition_id=cond_id,
                sort_order=idx
            )
    
    return success_response({"id": group.id, "group_key": group_key})


@router.get("/{group_id}")
async def get_condition_group(group_id: int):
    """获取单个组合条件详情"""
    group = await WarningConditionGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="组合条件不存在")
    
    # 获取关联的条件
    items = await GroupConditionItem.filter(group_id=group_id).order_by("sort_order").all()
    conditions = []
    for item in items:
        cond = await WarningCondition.get_or_none(id=item.condition_id)
        if cond:
            conditions.append({
                "item_id": item.id,
                "condition_id": cond.id,
                "condition_key": cond.condition_key,
                "condition_name": cond.condition_name,
                "priority": cond.priority,
                "sort_order": item.sort_order
            })
    
    return success_response({
        "id": group.id,
        "group_key": group.group_key,
        "group_name": group.group_name,
        "logic_type": group.logic_type,
        "priority": group.priority,
        "is_enabled": group.is_enabled,
        "parent_id": group.parent_id,
        "description": group.description,
        "conditions": conditions,
        "created_at": group.created_at.isoformat() if group.created_at else None,
        "updated_at": group.updated_at.isoformat() if group.updated_at else None
    })


@router.put("/{group_id}")
async def update_condition_group(group_id: int, data: ConditionGroupUpdate):
    """更新组合条件组"""
    group = await WarningConditionGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="组合条件不存在")
    
    if data.group_name is not None:
        group.group_name = data.group_name
    if data.logic_type is not None:
        group.logic_type = data.logic_type
    if data.priority is not None:
        group.priority = data.priority
    if data.is_enabled is not None:
        group.is_enabled = data.is_enabled
    if data.description is not None:
        group.description = data.description
    
    await group.save()
    return success_response(message="更新成功")


@router.delete("/{group_id}")
async def delete_condition_group(group_id: int):
    """删除组合条件组（递归删除子分组和条件项）"""
    group = await WarningConditionGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="组合条件不存在")
    
    # 递归删除子分组
    async def delete_recursive(gid: int):
        # 删除子分组
        subgroups = await WarningConditionGroup.filter(parent_id=gid).all()
        for sub in subgroups:
            await delete_recursive(sub.id)
        
        # 删除条件项
        await GroupConditionItem.filter(group_id=gid).delete()
        
        # 删除分组本身
        await WarningConditionGroup.filter(id=gid).delete()
    
    await delete_recursive(group_id)
    return success_response(message="删除成功")


# ==================== 条件项接口 ====================

@router.post("/{group_id}/items")
async def add_condition_item(group_id: int, data: ConditionItemCreate):
    """向分组添加条件项"""
    group = await WarningConditionGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="组合条件不存在")
    
    condition = await WarningCondition.get_or_none(id=data.condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="预警条件不存在")
    
    # 检查是否已存在
    existing = await GroupConditionItem.filter(
        group_id=group_id, 
        condition_id=data.condition_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该条件已在组合中")
    
    item = await GroupConditionItem.create(
        group_id=group_id,
        condition_id=data.condition_id,
        sort_order=data.sort_order
    )
    
    return success_response({"id": item.id})


@router.delete("/{group_id}/items/{item_id}")
async def remove_condition_item(group_id: int, item_id: int):
    """移除条件项"""
    item = await GroupConditionItem.get_or_none(id=item_id, group_id=group_id)
    if not item:
        raise HTTPException(status_code=404, detail="条件项不存在")
    
    await item.delete()
    return success_response(message="移除成功")


@router.put("/{group_id}/items/reorder")
async def reorder_condition_items(group_id: int, item_ids: List[int]):
    """重新排序条件项"""
    for idx, item_id in enumerate(item_ids):
        item = await GroupConditionItem.get_or_none(id=item_id, group_id=group_id)
        if item:
            item.sort_order = idx
            await item.save()
    
    return success_response(message="排序更新成功")


# ==================== 子分组接口 ====================

@router.post("/{group_id}/subgroups")
async def create_subgroup(group_id: int, data: ConditionGroupCreate):
    """创建子分组"""
    parent = await WarningConditionGroup.get_or_none(id=group_id)
    if not parent:
        raise HTTPException(status_code=404, detail="父分组不存在")
    
    # 设置父ID
    create_data = data.model_dump()
    create_data["parent_id"] = group_id
    
    group_key = f"GROUP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    group = await WarningConditionGroup.create(
        group_key=group_key,
        group_name=data.group_name,
        logic_type=data.logic_type,
        parent_id=group_id,
        priority=data.priority,
        description=data.description,
        is_enabled=True
    )
    
    # 关联条件
    for idx, cond_id in enumerate(data.condition_ids):
        condition = await WarningCondition.get_or_none(id=cond_id)
        if condition:
            await GroupConditionItem.create(
                group_id=group.id,
                condition_id=cond_id,
                sort_order=idx
            )
    
    return success_response({"id": group.id, "group_key": group_key})
```

- [ ] **Step 2: 注册路由**

在 `backend/main.py` 中注册新路由：

```python
# 在路由注册部分添加
from api.v1 import condition_group
app.include_router(condition_group.router, prefix="/api/v1")
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/api/v1/condition_group.py backend/main.py
git commit -m "feat: 添加组合条件管理 API"
```

---

## Task 7: 扩展预警评估器

**Files:**
- Modify: `backend/utils/warning_evaluator.py`

- [ ] **Step 1: 扩展 evaluate 方法**

修改 `evaluate` 方法签名，增加 `quote` 参数，并添加阈值评估分支：

```python
def evaluate(self, klines: List[Dict], condition: Dict, quote: Dict = None) -> Tuple[bool, Dict]:
    """
    评估预警条件
    
    Args:
        klines: K线数据列表
        condition: 预警条件配置
        quote: 实时行情数据（阈值指标判断用）
    """
    rule = json.loads(condition['condition_rule'])
    rule_type = rule.get('rule_type')
    
    # 技术指标类（需要K线计算）
    if rule_type in ['cross', 'break', 'threshold']:
        if rule_type == 'cross':
            return self._evaluate_cross(klines, condition, rule)
        elif rule_type == 'break':
            return self._evaluate_break(klines, condition, rule)
        elif rule_type == 'threshold':
            return self._evaluate_threshold(klines, condition, rule)
    
    # 行情/基本面阈值类
    elif rule_type == 'quote_threshold':
        return self._evaluate_quote_threshold(quote or {}, condition, rule)
    
    return False, {}
```

- [ ] **Step 2: 添加阈值评估方法**

在 `WarningEvaluator` 类中添加以下方法：

```python
def _evaluate_quote_threshold(self, quote: Dict, condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
    """评估行情/基本面阈值类条件"""
    indicator_key = rule.get('indicator_key')
    params = rule.get('params', {})
    
    if indicator_key == 'THRESHOLD_CHANGE':
        return self._eval_change_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_TURNOVER':
        return self._eval_turnover_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_VOLUME_RATIO':
        return self._eval_volume_ratio_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_AMOUNT':
        return self._eval_amount_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_MARKET_VALUE':
        return self._eval_market_value_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_PE':
        return self._eval_pe_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_PB':
        return self._eval_pb_threshold(quote, params)
    
    return False, {}

def _eval_change_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估涨跌幅阈值"""
    start_date = params.get('start_date')
    threshold_percent = params.get('threshold_percent', 5)
    compare_op = params.get('compare_op', 'gt')
    
    start_price = quote.get('history_prices', {}).get(start_date)
    current_price = quote.get('price')
    
    if start_price is None or current_price is None or start_price == 0:
        return False, {}
    
    actual_change = (current_price - start_price) / start_price * 100
    
    ops = {
        'gt': lambda v, t: v > t,
        'lt': lambda v, t: v < t,
        'ge': lambda v, t: v >= t,
        'le': lambda v, t: v <= t,
    }
    
    triggered = ops.get(compare_op, ops['gt'])(actual_change, threshold_percent)
    
    return triggered, {
        'triggered': triggered,
        'actual_change_percent': round(actual_change, 4),
        'threshold_percent': threshold_percent,
        'start_price': round(start_price, 4),
        'current_price': round(current_price, 4),
        'start_date': start_date
    }

def _eval_turnover_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估换手率阈值"""
    threshold = params.get('threshold', 10)
    compare_op = params.get('compare_op', 'gt')
    
    actual_turnover = quote.get('turnover_rate')
    if actual_turnover is None:
        return False, {}
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['gt'])(actual_turnover, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_turnover': round(actual_turnover, 4),
        'threshold': threshold
    }

def _eval_volume_ratio_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估量比阈值"""
    threshold = params.get('threshold', 2)
    compare_op = params.get('compare_op', 'gt')
    
    actual_ratio = quote.get('volume_ratio')
    if actual_ratio is None:
        return False, {}
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['gt'])(actual_ratio, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_volume_ratio': round(actual_ratio, 4),
        'threshold': threshold
    }

def _eval_amount_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估成交额阈值"""
    threshold = params.get('threshold', 1)
    unit = params.get('unit', '亿')
    compare_op = params.get('compare_op', 'gt')
    
    actual_amount = quote.get('amount', 0)
    # 转换单位
    if unit == '亿':
        actual_amount = actual_amount / 100000000
    elif unit == '万':
        actual_amount = actual_amount / 10000
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['gt'])(actual_amount, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_amount': round(actual_amount, 4),
        'threshold': threshold,
        'unit': unit
    }

def _eval_market_value_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估市值阈值"""
    threshold = params.get('threshold', 50)
    unit = params.get('unit', '亿')
    compare_op = params.get('compare_op', 'lt')
    
    actual_value = quote.get('market_value', 0)
    if unit == '亿':
        actual_value = actual_value / 100000000
    elif unit == '万':
        actual_value = actual_value / 10000
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['lt'])(actual_value, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_value': round(actual_value, 4),
        'threshold': threshold,
        'unit': unit
    }

def _eval_pe_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估市盈率阈值"""
    threshold = params.get('threshold', 30)
    compare_op = params.get('compare_op', 'lt')
    
    actual_pe = quote.get('pe')
    if actual_pe is None:
        return False, {}
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['lt'])(actual_pe, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_pe': round(actual_pe, 4),
        'threshold': threshold
    }

def _eval_pb_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估市净率阈值"""
    threshold = params.get('threshold', 3)
    compare_op = params.get('compare_op', 'lt')
    
    actual_pb = quote.get('pb')
    if actual_pb is None:
        return False, {}
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops.get(compare_op, ops['lt'])(actual_pb, threshold)
    
    return triggered, {
        'triggered': triggered,
        'actual_pb': round(actual_pb, 4),
        'threshold': threshold
    }
```

- [ ] **Step 3: 添加组合条件评估方法**

在 `WarningEvaluator` 类中添加：

```python
def evaluate_group(self, klines: List[Dict], quote: Dict, group: Dict) -> Tuple[bool, Dict]:
    """
    评估组合条件组（支持嵌套）
    
    Args:
        klines: K线数据
        quote: 实时行情数据
        group: 组合条件组（包含 conditions 和 subgroups）
    
    Returns:
        (是否触发, 触发详情)
    """
    logic_type = group.get('logic_type', 'AND')
    
    # 评估当前组的所有条件项
    condition_results = []
    for item in group.get('conditions', []):
        condition = {
            'indicator_key': item.get('indicator_key'),
            'indicator_key2': item.get('indicator_key2'),
            'condition_rule': item.get('condition_rule'),
            'condition_key': item.get('condition_key'),
            'condition_name': item.get('condition_name'),
        }
        triggered, value = self.evaluate(klines, condition, quote)
        condition_results.append({
            'condition_key': item.get('condition_key'),
            'condition_name': item.get('condition_name'),
            'triggered': triggered,
            'trigger_value': value
        })
    
    # 递归评估子分组
    subgroup_results = []
    for subgroup in group.get('subgroups', []):
        triggered, sub_detail = self.evaluate_group(klines, quote, subgroup)
        subgroup_results.append({
            'group_key': subgroup.get('group_key'),
            'group_name': subgroup.get('group_name'),
            'triggered': triggered,
            'details': sub_detail
        })
    
    # 合并结果，按逻辑类型判断
    all_results = condition_results + subgroup_results
    triggered_flags = [r['triggered'] for r in all_results]
    
    if not triggered_flags:
        return False, {}
    
    if logic_type == 'AND':
        group_triggered = all(triggered_flags)
    else:
        group_triggered = any(triggered_flags)
    
    return group_triggered, {
        'group_name': group.get('group_name'),
        'logic_type': logic_type,
        'condition_results': condition_results,
        'subgroup_results': subgroup_results,
        'triggered_count': sum(triggered_flags),
        'total_count': len(all_results)
    }
```

- [ ] **Step 4: 提交代码**

```bash
git add backend/utils/warning_evaluator.py
git commit -m "feat: 扩展预警评估器支持阈值指标和组合条件"
```

---

## Task 8: 修改预警检测任务

**Files:**
- Modify: `backend/jobs/warning_detector.py`

- [ ] **Step 1: 扩展行情数据获取函数**

添加扩展行情数据获取函数：

```python
async def get_extended_quote(stock_code: str, start_date: str = None) -> Dict:
    """
    获取扩展行情数据
    
    Args:
        stock_code: 股票代码
        start_date: 起始日期（用于计算涨跌幅）
    """
    # 获取基础实时行情
    quote = await get_realtime_quote(stock_code)
    if not quote:
        return {}
    
    result = {
        **quote,
        'history_prices': {},
        'turnover_rate': None,
        'volume_ratio': None,
        'market_value': None,
        'amount': None,
        'pe': None,
        'pb': None,
    }
    
    try:
        # 转换股票代码格式
        if '.' not in stock_code:
            if stock_code.startswith('6'):
                stock_code = f"{stock_code}.SH"
            else:
                stock_code = f"{stock_code}.SZ"
        
        async with httpx.AsyncClient(timeout=10) as client:
            # 获取历史价格（如果需要）
            if start_date:
                url = f"{QMT_SERVICE_URL}/api/v1/quote/kline/{stock_code}"
                params = {"period": "1d", "count": 100}
                response = await client.get(url, params=params)
                response.raise_for_status()
                kline_data = response.json()
                
                for kline in kline_data.get('klines', []):
                    if kline.get('date', '').startswith(start_date):
                        result['history_prices'][start_date] = kline.get('close')
                        break
            
            # 获取扩展行情数据
            try:
                url = f"{QMT_SERVICE_URL}/api/v1/quote/extended/{stock_code}"
                response = await client.get(url)
                if response.status_code == 200:
                    extended = response.json()
                    result['turnover_rate'] = extended.get('turnover_rate')
                    result['volume_ratio'] = extended.get('volume_ratio')
                    result['market_value'] = extended.get('market_value')
                    result['amount'] = extended.get('amount')
                    result['pe'] = extended.get('pe')
                    result['pb'] = extended.get('pb')
            except:
                pass  # 扩展接口可能不存在，忽略错误
    
    except Exception as e:
        logger.error(f"获取扩展行情失败: {stock_code}, 错误: {str(e)}")
    
    return result


async def build_group_tree(group) -> Dict:
    """构建组合条件树结构"""
    # 获取关联的条件
    items = await GroupConditionItem.filter(group_id=group.id).order_by("sort_order").all()
    conditions = []
    for item in items:
        cond = await WarningCondition.get_or_none(id=item.condition_id)
        if cond:
            conditions.append({
                'condition_key': cond.condition_key,
                'condition_name': cond.condition_name,
                'indicator_key': cond.indicator_key,
                'indicator_key2': cond.indicator_key2,
                'condition_rule': cond.condition_rule,
            })
    
    # 获取子分组
    subgroups = await WarningConditionGroup.filter(parent_id=group.id).all()
    subgroup_list = []
    for sub in subgroups:
        subgroup_dict = await build_group_tree(sub)
        subgroup_list.append(subgroup_dict)
    
    return {
        'group_key': group.group_key,
        'group_name': group.group_name,
        'logic_type': group.logic_type,
        'conditions': conditions,
        'subgroups': subgroup_list
    }


def extract_triggered_conditions(detail: Dict) -> List[Dict]:
    """从评估详情中提取触发的条件列表"""
    result = []
    
    for cond in detail.get('condition_results', []):
        result.append({
            'condition_key': cond.get('condition_key'),
            'condition_name': cond.get('condition_name'),
            'triggered': cond.get('triggered', False)
        })
    
    for sub in detail.get('subgroup_results', []):
        sub_conditions = extract_triggered_conditions(sub.get('details', {}))
        result.extend(sub_conditions)
    
    return result
```

- [ ] **Step 2: 修改 detect_warnings 函数**

在 `detect_warnings` 函数中添加组合条件检测逻辑：

```python
# 在 detect_warnings 函数中添加（在检查普通条件之后）

from models.condition_group import WarningConditionGroup, GroupConditionItem

async def detect_warnings():
    """预警检测主任务"""
    logger.info(f"[{datetime.now()}] 开始预警检测...")
    
    try:
        # 1. 获取启用的监控股票
        monitor_stocks = await MonitorStock.filter(is_active=True).all()
        
        if not monitor_stocks:
            logger.info("没有启用的监控股票")
            return {"success": True, "checked": 0, "triggered": 0}
        
        # 2. 获取启用的预警条件
        conditions = await WarningCondition.filter(is_enabled=True).all()
        
        # 3. 获取启用的组合条件（根分组）
        groups = await WarningConditionGroup.filter(is_enabled=True, parent_id=None).all()
        
        if not conditions and not groups:
            logger.info("没有启用的预警条件或组合条件")
            return {"success": True, "checked": 0, "triggered": 0}
        
        checked_count = 0
        triggered_count = 0
        
        for stock in monitor_stocks:
            # 获取K线数据
            klines = await get_kline_from_stock_service(stock.stock_code, period="d", days=100)
            
            if not klines or len(klines) < 30:
                logger.warning(f"股票 {stock.stock_code} K线数据不足，跳过检测")
                continue
            
            checked_count += 1
            
            # 获取扩展行情数据
            quote = await get_extended_quote(stock.stock_code)
            
            if quote:
                stock.last_price = quote.get('price')
                stock.change_percent = quote.get('change_percent')
                stock.last_check_time = datetime.now()
                await stock.save()
            
            # 检查普通条件（保持原有逻辑）
            stock_conditions = []
            if stock.conditions:
                condition_keys = stock.conditions if isinstance(stock.conditions, list) else []
                stock_conditions = [c for c in conditions if c.condition_key in condition_keys]
            if not stock_conditions:
                stock_conditions = conditions
            
            for condition in stock_conditions:
                try:
                    condition_dict = {
                        "indicator_key": condition.indicator_key,
                        "indicator_key2": condition.indicator_key2,
                        "condition_rule": condition.condition_rule,
                    }
                    
                    triggered, trigger_value = warning_evaluator.evaluate(klines, condition_dict, quote)
                    
                    if triggered:
                        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        existing = await WarningStockPool.filter(
                            stock_code=stock.stock_code,
                            condition_key=condition.condition_key,
                            trigger_time__gte=today_start
                        ).first()
                        
                        if existing:
                            continue
                        
                        await WarningStockPool.create(
                            stock_code=stock.stock_code,
                            stock_name=stock.stock_name,
                            price=stock.last_price,
                            change_percent=stock.change_percent,
                            condition_key=condition.condition_key,
                            condition_name=condition.condition_name,
                            warning_level=condition.priority,
                            trigger_time=datetime.now(),
                            trigger_value=trigger_value,
                            is_group=False,
                            is_handled=False
                        )
                        
                        triggered_count += 1
                        logger.info(f"触发预警: {stock.stock_code} - {condition.condition_name}")
                
                except Exception as e:
                    logger.error(f"评估预警条件失败: {condition.condition_key}, 错误: {str(e)}")
            
            # 检查组合条件
            for group in groups:
                try:
                    group_dict = await build_group_tree(group)
                    triggered, detail = warning_evaluator.evaluate_group(klines, quote, group_dict)
                    
                    if triggered:
                        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        existing = await WarningStockPool.filter(
                            stock_code=stock.stock_code,
                            group_key=group.group_key,
                            trigger_time__gte=today_start
                        ).first()
                        
                        if existing:
                            continue
                        
                        triggered_conditions = extract_triggered_conditions(detail)
                        
                        await WarningStockPool.create(
                            stock_code=stock.stock_code,
                            stock_name=stock.stock_name,
                            price=stock.last_price,
                            change_percent=stock.change_percent,
                            condition_key=group.group_key,
                            condition_name=group.group_name,
                            warning_level=group.priority,
                            trigger_time=datetime.now(),
                            trigger_value=detail,
                            triggered_conditions=triggered_conditions,
                            is_group=True,
                            group_key=group.group_key,
                            is_handled=False
                        )
                        
                        triggered_count += 1
                        logger.info(f"触发组合预警: {stock.stock_code} - {group.group_name}")
                
                except Exception as e:
                    logger.error(f"评估组合条件失败: {group.group_key}, 错误: {str(e)}")
        
        logger.info(f"预警检测完成: 检查 {checked_count} 只股票, 触发 {triggered_count} 条预警")
        
        return {
            "success": True,
            "checked": checked_count,
            "triggered": triggered_count,
            "message": f"检测完成: 检查 {checked_count} 只股票, 触发 {triggered_count} 条预警"
        }
    
    except Exception as e:
        logger.error(f"预警检测失败: {str(e)}")
        return {"success": False, "error": str(e)}
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/jobs/warning_detector.py
git commit -m "feat: 预警检测任务支持组合条件"
```

---

## Task 9: 前端 API - 组合条件

**Files:**
- Create: `frontend/src/api/conditionGroup.ts`

- [ ] **Step 1: 创建前端 API 文件**

```typescript
// frontend/src/api/conditionGroup.ts
/**
 * 组合条件 API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface ConditionGroup {
  id: number
  group_key: string
  group_name: string
  logic_type: 'AND' | 'OR'
  priority: string
  is_enabled: boolean
  parent_id: number | null
  description: string | null
  condition_count: number
  subgroup_count: number
  created_at: string
  updated_at: string
}

export interface ConditionGroupTreeNode {
  id: number
  group_key: string
  group_name: string
  logic_type: 'AND' | 'OR'
  priority: string
  is_enabled: boolean
  description: string | null
  conditions: ConditionItem[]
  subgroups: ConditionGroupTreeNode[]
}

export interface ConditionItem {
  item_id?: number
  condition_id: number
  condition_key: string
  condition_name: string
  priority: string
  sort_order?: number
}

export interface CreateGroupParams {
  group_name: string
  logic_type: 'AND' | 'OR'
  parent_id?: number
  priority?: string
  description?: string
  condition_ids?: number[]
}

export interface UpdateGroupParams {
  group_name?: string
  logic_type?: 'AND' | 'OR'
  priority?: string
  is_enabled?: boolean
  description?: string
}

// ==================== API 函数 ====================

/** 获取组合条件列表 */
export async function fetchConditionGroups(parentId?: number): Promise<ConditionGroup[]> {
  const params = parentId !== undefined ? { parent_id: parentId } : {}
  return request.get('/warning/groups', { params })
}

/** 获取组合条件树 */
export async function fetchConditionGroupTree(): Promise<ConditionGroupTreeNode[]> {
  return request.get('/warning/groups/tree')
}

/** 获取单个组合条件详情 */
export async function fetchConditionGroup(id: number): Promise<ConditionGroupTreeNode> {
  return request.get(`/warning/groups/${id}`)
}

/** 创建组合条件 */
export async function createConditionGroup(data: CreateGroupParams): Promise<{ id: number; group_key: string }> {
  return request.post('/warning/groups', data)
}

/** 更新组合条件 */
export async function updateConditionGroup(id: number, data: UpdateGroupParams): Promise<void> {
  return request.put(`/warning/groups/${id}`, data)
}

/** 删除组合条件 */
export async function deleteConditionGroup(id: number): Promise<void> {
  return request.delete(`/warning/groups/${id}`)
}

/** 添加条件项 */
export async function addConditionItem(groupId: number, conditionId: number, sortOrder?: number): Promise<{ id: number }> {
  return request.post(`/warning/groups/${groupId}/items`, { condition_id: conditionId, sort_order: sortOrder })
}

/** 移除条件项 */
export async function removeConditionItem(groupId: number, itemId: number): Promise<void> {
  return request.delete(`/warning/groups/${groupId}/items/${itemId}`)
}

/** 创建子分组 */
export async function createSubgroup(parentId: number, data: CreateGroupParams): Promise<{ id: number; group_key: string }> {
  return request.post(`/warning/groups/${parentId}/subgroups`, data)
}
```

- [ ] **Step 2: 提交代码**

```bash
git add frontend/src/api/conditionGroup.ts
git commit -m "feat: 添加组合条件前端 API"
```

---

## Task 10: 前端页面 - 组合条件管理

**Files:**
- Create: `frontend/src/views/warning/ConditionGroup.vue`
- Create: `frontend/src/views/warning/components/GroupTree.vue`
- Create: `frontend/src/views/warning/components/GroupEditor.vue`

- [ ] **Step 1: 创建主页面**

```vue
<!-- frontend/src/views/warning/ConditionGroup.vue -->
<template>
  <div class="condition-group-page">
    <div class="page-header">
      <h2>组合条件管理</h2>
      <n-space>
        <n-button type="primary" @click="handleCreateRoot">
          <template #icon><n-icon><AddOutline /></n-icon></template>
          新增组合
        </n-button>
        <n-button @click="loadTree" :loading="loading">刷新</n-button>
      </n-space>
    </div>

    <div class="main-content">
      <div class="tree-panel">
        <n-spin :show="loading">
          <GroupTree
            :tree-data="groupTree"
            :selected-key="selectedGroupId"
            @select="handleSelect"
            @add-subgroup="handleAddSubgroup"
            @delete="handleDelete"
          />
        </n-spin>
      </div>

      <div class="editor-panel">
        <GroupEditor
          v-if="selectedGroup"
          :group="selectedGroup"
          :mode="editorMode"
          @save="handleSave"
          @cancel="handleCancel"
        />
        <n-empty v-else description="请选择组合条件" />
      </div>
    </div>

    <!-- 创建弹窗 -->
    <n-modal v-model:show="showCreateModal" preset="card" title="新建组合条件" style="width: 500px">
      <n-form ref="createFormRef" :model="createForm" label-placement="left" label-width="80">
        <n-form-item label="组合名称" path="group_name">
          <n-input v-model:value="createForm.group_name" placeholder="请输入组合名称" />
        </n-form-item>
        <n-form-item label="逻辑类型" path="logic_type">
          <n-radio-group v-model:value="createForm.logic_type">
            <n-radio-button value="AND">AND（全部满足）</n-radio-button>
            <n-radio-button value="OR">OR（任一满足）</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="优先级" path="priority">
          <n-select v-model:value="createForm.priority" :options="priorityOptions" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="createForm.description" type="textarea" placeholder="可选描述" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateSubmit" :loading="creating">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NSpace, NIcon, NSpin, NEmpty, NModal, NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSelect, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import GroupTree from './components/GroupTree.vue'
import GroupEditor from './components/GroupEditor.vue'
import {
  fetchConditionGroupTree,
  fetchConditionGroup,
  createConditionGroup,
  deleteConditionGroup,
  type ConditionGroupTreeNode
} from '@/api/conditionGroup'

const message = useMessage()

const loading = ref(false)
const groupTree = ref<ConditionGroupTreeNode[]>([])
const selectedGroupId = ref<number | null>(null)
const selectedGroup = ref<ConditionGroupTreeNode | null>(null)
const editorMode = ref<'view' | 'edit'>('view')

const showCreateModal = ref(false)
const creating = ref(false)
const createParentId = ref<number | null>(null)
const createForm = ref({
  group_name: '',
  logic_type: 'AND' as 'AND' | 'OR',
  priority: 'warning',
  description: ''
})

const priorityOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

async function loadTree() {
  loading.value = true
  try {
    groupTree.value = await fetchConditionGroupTree()
  } catch (error) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleSelect(id: number) {
  selectedGroupId.value = id
  try {
    selectedGroup.value = await fetchConditionGroup(id)
    editorMode.value = 'view'
  } catch (error) {
    message.error('加载详情失败')
  }
}

function handleCreateRoot() {
  createParentId.value = null
  createForm.value = { group_name: '', logic_type: 'AND', priority: 'warning', description: '' }
  showCreateModal.value = true
}

function handleAddSubgroup(parentId: number) {
  createParentId.value = parentId
  createForm.value = { group_name: '', logic_type: 'AND', priority: 'warning', description: '' }
  showCreateModal.value = true
}

async function handleCreateSubmit() {
  if (!createForm.value.group_name) {
    message.warning('请输入组合名称')
    return
  }

  creating.value = true
  try {
    if (createParentId.value) {
      await createConditionGroup({ ...createForm.value, parent_id: createParentId.value })
    } else {
      await createConditionGroup(createForm.value)
    }
    message.success('创建成功')
    showCreateModal.value = false
    loadTree()
  } catch (error) {
    message.error('创建失败')
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteConditionGroup(id)
    message.success('删除成功')
    if (selectedGroupId.value === id) {
      selectedGroupId.value = null
      selectedGroup.value = null
    }
    loadTree()
  } catch (error) {
    message.error('删除失败')
  }
}

function handleSave() {
  loadTree()
}

function handleCancel() {
  editorMode.value = 'view'
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped lang="scss">
.condition-group-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.tree-panel {
  width: 320px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}

.editor-panel {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}
</style>
```

- [ ] **Step 2: 创建树组件**

```vue
<!-- frontend/src/views/warning/components/GroupTree.vue -->
<template>
  <div class="group-tree">
    <n-tree
      :data="treeData"
      :selected-keys="selectedKeys"
      :render-label="renderLabel"
      :render-suffix="renderSuffix"
      block-line
      @update:selected-keys="handleSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { NTree, NButton, NTag, NSpace, NIcon } from 'naive-ui'
import { FolderOutline, AddOutline, TrashOutline } from '@vicons/ionicons5'
import type { ConditionGroupTreeNode } from '@/api/conditionGroup'

const props = defineProps<{
  treeData: ConditionGroupTreeNode[]
  selectedKey: number | null
}>()

const emit = defineEmits<{
  select: [id: number]
  addSubgroup: [id: number]
  delete: [id: number]
}>()

const selectedKeys = computed(() => props.selectedKey ? [props.selectedKey] : [])

interface TreeOption {
  key: number
  label: string
  children?: TreeOption[]
  raw: ConditionGroupTreeNode
}

function transformData(data: ConditionGroupTreeNode[]): TreeOption[] {
  return data.map(item => ({
    key: item.id,
    label: item.group_name,
    children: item.subgroups?.length ? transformData(item.subgroups) : undefined,
    raw: item
  }))
}

const treeData = computed(() => transformData(props.treeData))

function handleSelect(keys: number[]) {
  if (keys.length > 0) {
    emit('select', keys[0])
  }
}

function renderLabel({ option }: { option: TreeOption }) {
  const raw = option.raw
  return h('div', { class: 'tree-node-label' }, [
    h(NIcon, { size: 16, style: 'margin-right: 4px' }, { default: () => h(FolderOutline) }),
    h('span', raw.group_name),
    h(NTag, { 
      size: 'small', 
      type: raw.logic_type === 'AND' ? 'info' : 'warning',
      style: 'margin-left: 8px'
    }, { default: () => raw.logic_type })
  ])
}

function renderSuffix({ option }: { option: TreeOption }) {
  const raw = option.raw
  return h(NSpace, { size: 4 }, {
    default: () => [
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        onClick: (e: Event) => {
          e.stopPropagation()
          emit('addSubgroup', raw.id)
        }
      }, { icon: () => h(NIcon, null, { default: () => h(AddOutline) }) }),
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        type: 'error',
        onClick: (e: Event) => {
          e.stopPropagation()
          emit('delete', raw.id)
        }
      }, { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) })
    ]
  })
}
</script>

<style scoped lang="scss">
.group-tree {
  :deep(.tree-node-label) {
    display: flex;
    align-items: center;
  }
}
</style>
```

- [ ] **Step 3: 创建编辑器组件**

```vue
<!-- frontend/src/views/warning/components/GroupEditor.vue -->
<template>
  <div class="group-editor">
    <div class="editor-header">
      <h3>{{ group.group_name }}</h3>
      <n-space>
        <n-button v-if="mode === 'view'" type="primary" @click="mode = 'edit'">编辑</n-button>
        <n-button v-if="mode === 'edit'" type="primary" @click="handleSave" :loading="saving">保存</n-button>
        <n-button v-if="mode === 'edit'" @click="handleCancel">取消</n-button>
      </n-space>
    </div>

    <n-divider />

    <!-- 基本信息 -->
    <n-form :model="formData" label-placement="left" label-width="80">
      <n-form-item label="组合名称">
        <n-input v-if="mode === 'edit'" v-model:value="formData.group_name" />
        <span v-else>{{ group.group_name }}</span>
      </n-form-item>
      <n-form-item label="逻辑类型">
        <n-radio-group v-if="mode === 'edit'" v-model:value="formData.logic_type">
          <n-radio-button value="AND">AND（全部满足）</n-radio-button>
          <n-radio-button value="OR">OR（任一满足）</n-radio-button>
        </n-radio-group>
        <n-tag v-else :type="group.logic_type === 'AND' ? 'info' : 'warning'">
          {{ group.logic_type }}
        </n-tag>
      </n-form-item>
      <n-form-item label="优先级">
        <n-select v-if="mode === 'edit'" v-model:value="formData.priority" :options="priorityOptions" />
        <n-tag v-else :type="getPriorityType(group.priority)">{{ getPriorityLabel(group.priority) }}</n-tag>
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-if="mode === 'edit'" v-model:value="formData.description" type="textarea" />
        <span v-else>{{ group.description || '--' }}</span>
      </n-form-item>
    </n-form>

    <n-divider />

    <!-- 条件列表 -->
    <div class="section-title">
      <span>条件列表</span>
      <n-button v-if="mode === 'edit'" size="small" @click="showAddCondition = true">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        添加条件
      </n-button>
    </div>

    <div class="condition-list">
      <n-empty v-if="!group.conditions?.length" description="暂无条件" />
      <div v-else class="condition-items">
        <div v-for="(cond, idx) in group.conditions" :key="cond.condition_id" class="condition-item">
          <n-tag type="info">{{ cond.condition_name }}</n-tag>
          <n-button v-if="mode === 'edit'" size="tiny" quaternary type="error" @click="handleRemoveCondition(cond)">
            移除
          </n-button>
        </div>
      </div>
    </div>

    <!-- 子分组 -->
    <n-divider />

    <div class="section-title">
      <span>子分组</span>
    </div>

    <div class="subgroup-list">
      <n-empty v-if="!group.subgroups?.length" description="暂无子分组" />
      <div v-else class="subgroup-items">
        <n-card v-for="sub in group.subgroups" :key="sub.id" size="small" :title="sub.group_name">
          <template #header-extra>
            <n-tag :type="sub.logic_type === 'AND' ? 'info' : 'warning'" size="small">
              {{ sub.logic_type }}
            </n-tag>
          </template>
          <div class="subgroup-conditions">
            <n-tag v-for="cond in sub.conditions" :key="cond.condition_id" size="small" style="margin: 2px">
              {{ cond.condition_name }}
            </n-tag>
          </div>
        </n-card>
      </div>
    </div>

    <!-- 添加条件弹窗 -->
    <n-modal v-model:show="showAddCondition" preset="card" title="添加条件" style="width: 500px">
      <n-select
        v-model:value="selectedConditionId"
        :options="conditionOptions"
        filterable
        placeholder="选择预警条件"
      />
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddCondition = false">取消</n-button>
          <n-button type="primary" @click="handleAddCondition" :disabled="!selectedConditionId">添加</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSelect, NTag, NButton, NSpace, NDivider, NEmpty, NCard, NModal, NIcon, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import {
  updateConditionGroup,
  addConditionItem,
  removeConditionItem,
  type ConditionGroupTreeNode
} from '@/api/conditionGroup'
import { fetchWarningConditions, type WarningCondition } from '@/api/warning'

const props = defineProps<{
  group: ConditionGroupTreeNode
  mode: 'view' | 'edit'
}>()

const emit = defineEmits<{
  save: []
  cancel: []
}>()

const message = useMessage()

const mode = ref(props.mode)
const saving = ref(false)
const formData = ref({
  group_name: '',
  logic_type: 'AND' as 'AND' | 'OR',
  priority: 'warning',
  description: ''
})

const showAddCondition = ref(false)
const selectedConditionId = ref<number | null>(null)
const allConditions = ref<WarningCondition[]>([])

const priorityOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

const conditionOptions = computed(() =>
  allConditions.value.map(c => ({
    label: c.condition_name,
    value: c.id
  }))
)

function getPriorityType(priority: string): 'error' | 'warning' | 'info' {
  if (priority === 'critical') return 'error'
  if (priority === 'warning') return 'warning'
  return 'info'
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = { critical: '严重', warning: '警告', info: '提示' }
  return labels[priority] || priority
}

watch(() => props.group, (val) => {
  formData.value = {
    group_name: val.group_name,
    logic_type: val.logic_type,
    priority: val.priority,
    description: val.description || ''
  }
}, { immediate: true })

async function loadConditions() {
  try {
    allConditions.value = await fetchWarningConditions()
  } catch (error) {
    console.error('加载条件失败', error)
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateConditionGroup(props.group.id, formData.value)
    message.success('保存成功')
    mode.value = 'view'
    emit('save')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  mode.value = 'view'
  emit('cancel')
}

async function handleAddCondition() {
  if (!selectedConditionId.value) return
  
  try {
    await addConditionItem(props.group.id, selectedConditionId.value)
    message.success('添加成功')
    showAddCondition.value = false
    selectedConditionId.value = null
    emit('save')
  } catch (error) {
    message.error('添加失败')
  }
}

async function handleRemoveCondition(cond: { item_id?: number; condition_id: number }) {
  if (!cond.item_id) return
  
  try {
    await removeConditionItem(props.group.id, cond.item_id)
    message.success('移除成功')
    emit('save')
  } catch (error) {
    message.error('移除失败')
  }
}

loadConditions()
</script>

<style scoped lang="scss">
.group-editor {
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
    }
  }

  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .condition-list {
    min-height: 60px;
  }

  .condition-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .condition-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .subgroup-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .subgroup-conditions {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style>
```

- [ ] **Step 4: 提交代码**

```bash
git add frontend/src/views/warning/ConditionGroup.vue frontend/src/views/warning/components/GroupTree.vue frontend/src/views/warning/components/GroupEditor.vue
git commit -m "feat: 添加组合条件管理前端页面"
```

---

## Task 11: 修改预警列表页面

**Files:**
- Modify: `frontend/src/views/signal/index.vue`

- [ ] **Step 1: 修改触发条件列渲染**

找到 `signalColumns` 中的触发条件列，修改渲染逻辑：

```typescript
{
  title: '触发条件',
  key: 'condition_name',
  width: 180,
  render: (row: SignalRecord) => {
    if (row.is_group && row.triggered_conditions) {
      // 组合条件：显示组合名 + 满足的条件标签
      const tags = row.triggered_conditions.map((c: any) =>
        h(NTag, {
          type: c.triggered ? 'success' : 'default',
          size: 'small',
          bordered: false,
          style: 'margin: 2px'
        }, { default: () => c.condition_name })
      )
      
      return h(NSpace, { vertical: false, size: 2, wrap: true }, {
        default: () => [
          h(NText, { strong: true }, { default: () => row.condition_name }),
          h(NText, { depth: 3 }, { default: () => ' (' }),
          ...tags,
          h(NText, { depth: 3 }, { default: () => ')' })
        ]
      })
    }
    
    // 普通条件
    return h(NTag, {
      type: getLevelType(row.warning_level),
      size: 'small'
    }, { default: () => row.condition_name })
  }
}
```

- [ ] **Step 2: 更新类型定义**

在 `SignalRecord` 接口中添加新字段：

```typescript
interface SignalRecord extends WarningStock {
  handled_at?: string
  is_group?: boolean
  triggered_conditions?: Array<{
    condition_key: string
    condition_name: string
    triggered: boolean
  }>
}
```

- [ ] **Step 3: 提交代码**

```bash
git add frontend/src/views/signal/index.vue
git commit -m "feat: 预警列表支持显示组合条件"
```

---

## Task 12: 添加菜单入口

**Files:**
- (通过数据库或管理后台添加菜单)

- [ ] **Step 1: 创建菜单初始化脚本**

```python
# backend/scripts/init_condition_group_menu.py
"""
初始化组合条件菜单
"""
import asyncio
from models.menu import Menu
from models.role_menu import RoleMenu

async def init_menu():
    # 查找预警管理父菜单
    parent = await Menu.filter(menu_key="warning").first()
    if not parent:
        print("未找到预警管理父菜单")
        return
    
    # 检查是否已存在
    existing = await Menu.filter(menu_key="condition_group").first()
    if existing:
        print("组合条件菜单已存在")
        return
    
    # 创建菜单
    menu = await Menu.create(
        menu_key="condition_group",
        menu_name="组合条件",
        parent_id=parent.id,
        path="/warning/condition-group",
        component="views/warning/ConditionGroup",
        icon="git-branch-outline",
        sort_order=20,
        is_visible=True
    )
    
    print(f"创建菜单成功: {menu.menu_name}")

if __name__ == "__main__":
    asyncio.run(init_menu())
```

- [ ] **Step 2: 运行脚本**

```bash
cd backend && python -m scripts.init_condition_group_menu
```

- [ ] **Step 3: 提交代码**

```bash
git add backend/scripts/init_condition_group_menu.py
git commit -m "feat: 添加组合条件菜单初始化脚本"
```

---

## Task 13: 数据库迁移

**Files:**
- (执行数据库迁移)

- [ ] **Step 1: 生成迁移文件（如果使用 aerich）**

```bash
cd backend && aerich migrate --name add_condition_group
```

- [ ] **Step 2: 执行迁移**

```bash
cd backend && aerich upgrade
```

或者直接让 Tortoise ORM 自动创建表（开发环境）。

---

## 实施检查清单

- [ ] Task 1: 数据模型 - 组合条件表
- [ ] Task 2: 数据模型 - 修改预警股票池表
- [ ] Task 3: 数据模型 - 扩展指标库表
- [ ] Task 4: 新增阈值类指标数据
- [ ] Task 5: 后端 Schema 定义
- [ ] Task 6: 后端 API - 组合条件管理
- [ ] Task 7: 扩展预警评估器
- [ ] Task 8: 修改预警检测任务
- [ ] Task 9: 前端 API - 组合条件
- [ ] Task 10: 前端页面 - 组合条件管理
- [ ] Task 11: 修改预警列表页面
- [ ] Task 12: 添加菜单入口
- [ ] Task 13: 数据库迁移