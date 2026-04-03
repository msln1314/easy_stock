"""
预警相关API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.response import success_response, error_response
from models.warning import WarningCondition, WarningStockPool, IndicatorLibrary
from utils.warning_evaluator import WARNING_CONDITIONS_PRESET

router = APIRouter(prefix="/api/warning", tags=["预警管理"])


# ==================== Schemas ====================

class WarningConditionCreate(BaseModel):
    """创建预警条件"""
    condition_key: str
    condition_name: str
    indicator_key: str
    indicator_key2: Optional[str] = None
    period: str
    condition_rule: str
    priority: str = "warning"
    description: Optional[str] = None


class WarningConditionUpdate(BaseModel):
    """更新预警条件"""
    is_enabled: Optional[bool] = None
    priority: Optional[str] = None


class HandleWarning(BaseModel):
    """处理预警"""
    action: str  # IGNORE/SELL/WATCH


class CustomConditionCreate(BaseModel):
    """创建自定义预警条件"""
    condition_name: str
    description: Optional[str] = None
    priority: str = "warning"
    rule_type: str  # cross/break/threshold
    indicator_key: str
    indicator_params: dict = {}
    rule_config: dict  # 具体规则配置


# ==================== 指标库接口 ====================

@router.get("/indicators")
async def get_indicators():
    """获取指标库列表"""
    indicators = await IndicatorLibrary.all()
    return success_response([{
        "id": i.id,
        "indicator_key": i.indicator_key,
        "indicator_name": i.indicator_name,
        "category": i.category,
        "parameters": i.parameters,
        "output_fields": i.output_fields,
        "is_builtin": i.is_builtin
    } for i in indicators])


# ==================== 预警条件接口 ====================

@router.get("/conditions")
async def get_conditions():
    """获取预警条件列表"""
    conditions = await WarningCondition.all()
    return success_response([{
        "id": c.id,
        "condition_key": c.condition_key,
        "condition_name": c.condition_name,
        "indicator_key": c.indicator_key,
        "indicator_key2": c.indicator_key2,
        "period": c.period,
        "condition_rule": c.condition_rule,
        "priority": c.priority,
        "is_enabled": c.is_enabled,
        "description": c.description
    } for c in conditions])


@router.post("/conditions")
async def create_condition(data: WarningConditionCreate):
    """创建预警条件"""
    condition = await WarningCondition.create(
        condition_key=data.condition_key,
        condition_name=data.condition_name,
        indicator_key=data.indicator_key,
        indicator_key2=data.indicator_key2,
        period=data.period,
        condition_rule=data.condition_rule,
        priority=data.priority,
        description=data.description
    )
    return success_response({"id": condition.id})


@router.put("/conditions/{condition_id}")
async def update_condition(condition_id: int, data: WarningConditionUpdate):
    """更新预警条件"""
    condition = await WarningCondition.get_or_none(id=condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="预警条件不存在")

    if data.is_enabled is not None:
        condition.is_enabled = data.is_enabled
    if data.priority:
        condition.priority = data.priority

    await condition.save()
    return success_response(message="更新成功")


@router.post("/conditions/custom")
async def create_custom_condition(data: CustomConditionCreate):
    """创建自定义预警条件"""
    import json

    condition_rule = {
        "rule_type": data.rule_type,
        **data.rule_config
    }

    condition = await WarningCondition.create(
        condition_key=f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        condition_name=data.condition_name,
        indicator_key=data.indicator_key,
        indicator_key2=None,
        period="daily",
        condition_rule=json.dumps(condition_rule),
        priority=data.priority,
        description=data.description,
        is_enabled=True
    )
    return success_response({"id": condition.id})


@router.post("/conditions/init")
async def init_conditions():
    """初始化预置预警条件"""
    import json

    count = 0
    for preset in WARNING_CONDITIONS_PRESET:
        existing = await WarningCondition.get_or_none(condition_key=preset['condition_key'])
        if not existing:
            await WarningCondition.create(**preset)
            count += 1

    return success_response(message=f"已初始化 {count} 条预警条件")


# ==================== 预警股票池接口 ====================

@router.get("/stocks")
async def get_warning_stocks(
    level: Optional[str] = Query(None, description="预警级别筛选"),
    handled: Optional[bool] = Query(None, description="是否已处理"),
    limit: int = Query(50, description="返回数量")
):
    """获取预警股票池"""
    query = WarningStockPool.all()

    if level:
        levels = level.split(",")
        query = query.filter(warning_level__in=levels)
    if handled is not None:
        query = query.filter(is_handled=handled)

    stocks = await query.order_by("-trigger_time").limit(limit)

    return success_response([{
        "id": s.id,
        "stock_code": s.stock_code,
        "stock_name": s.stock_name,
        "price": float(s.price) if s.price else None,
        "change_percent": float(s.change_percent) if s.change_percent else None,
        "condition_name": s.condition_name,
        "warning_level": s.warning_level,
        "trigger_time": s.trigger_time.isoformat() if s.trigger_time else None,
        "trigger_value": s.trigger_value,
        "is_handled": s.is_handled,
        "handle_action": s.handle_action
    } for s in stocks])


@router.put("/stocks/{stock_id}/handle")
async def handle_warning_stock(stock_id: int, data: HandleWarning):
    """处理预警股票"""
    stock = await WarningStockPool.get_or_none(id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="预警记录不存在")

    stock.is_handled = True
    stock.handle_action = data.action
    stock.handled_at = datetime.now()
    await stock.save()

    return success_response(message="处理成功")


@router.delete("/stocks/{stock_id}")
async def delete_warning_stock(stock_id: int):
    """删除预警记录"""
    stock = await WarningStockPool.get_or_none(id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="预警记录不存在")

    await stock.delete()
    return success_response(message="删除成功")


@router.delete("/stocks")
async def clear_handled_stocks():
    """清理已处理的预警记录"""
    deleted = await WarningStockPool.filter(is_handled=True).delete()
    return success_response(message=f"已清理 {deleted} 条记录")