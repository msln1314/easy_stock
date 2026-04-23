"""
组合条件管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from core.response import success_response, error_response
from models.condition_group import WarningConditionGroup, GroupConditionItem
from models.warning import WarningCondition
from schemas.condition_group import (
    ConditionGroupCreate, ConditionGroupUpdate,
    ConditionItemCreate
)

router = APIRouter(prefix="/api/v1/warning/groups", tags=["组合条件管理"])


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
                        "item_id": item.id,
                        "condition_id": cond.id,
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
    """获取单个组合条件详情（包含子分组）"""
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

    # 获取子分组及其条件
    subgroups_list = await WarningConditionGroup.filter(parent_id=group_id).all()
    subgroups = []
    for sub in subgroups_list:
        sub_items = await GroupConditionItem.filter(group_id=sub.id).order_by("sort_order").all()
        sub_conditions = []
        for item in sub_items:
            cond = await WarningCondition.get_or_none(id=item.condition_id)
            if cond:
                sub_conditions.append({
                    "item_id": item.id,
                    "condition_id": cond.id,
                    "condition_key": cond.condition_key,
                    "condition_name": cond.condition_name,
                    "priority": cond.priority
                })
        subgroups.append({
            "id": sub.id,
            "group_key": sub.group_key,
            "group_name": sub.group_name,
            "logic_type": sub.logic_type,
            "priority": sub.priority,
            "is_enabled": sub.is_enabled,
            "description": sub.description,
            "conditions": sub_conditions
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
        "subgroups": subgroups,
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