"""
指标库管理API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from enum import Enum

from core.response import success_response
from models.indicator_library import IndicatorLibrary, IndicatorCategory, IndicatorValueType, INDICATOR_PRESET_DATA

router = APIRouter(prefix="/api/indicators", tags=["指标库管理"])


# ==================== Schemas ====================

class IndicatorCategoryEnum(str, Enum):
    trend = "trend"
    momentum = "momentum"
    oscillator = "oscillator"
    volume = "volume"
    volatility = "volatility"


class IndicatorCreate(BaseModel):
    """创建指标"""
    indicator_key: str
    indicator_name: str
    category: IndicatorCategoryEnum
    description: Optional[str] = None
    value_type: str = "single"
    params: Optional[List[dict]] = None
    output_fields: Optional[List[dict]] = None
    default_output: Optional[str] = None
    usage_guide: Optional[str] = None
    signal_interpretation: Optional[dict] = None


class IndicatorUpdate(BaseModel):
    """更新指标"""
    indicator_name: Optional[str] = None
    description: Optional[str] = None
    params: Optional[List[dict]] = None
    output_fields: Optional[List[dict]] = None
    default_output: Optional[str] = None
    usage_guide: Optional[str] = None
    signal_interpretation: Optional[dict] = None
    is_enabled: Optional[bool] = None
    sort_order: Optional[int] = None


# ==================== API接口 ====================

@router.get("")
async def get_indicators(
    category: Optional[str] = Query(None, description="分类筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """获取指标列表"""
    query = IndicatorLibrary.all()

    if category:
        query = query.filter(category=category)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)
    if keyword:
        query = query.filter(
            indicator_name__contains=keyword
        ) | query.filter(
            indicator_key__contains=keyword.upper()
        )

    indicators = await query.order_by("sort_order", "id")

    return success_response([{
        "id": i.id,
        "indicator_key": i.indicator_key,
        "indicator_name": i.indicator_name,
        "category": i.category,
        "category_name": get_category_name(i.category),
        "description": i.description,
        "value_type": i.value_type,
        "params": i.params,
        "output_fields": i.output_fields,
        "default_output": i.default_output,
        "usage_guide": i.usage_guide,
        "signal_interpretation": i.signal_interpretation,
        "is_builtin": i.is_builtin,
        "is_enabled": i.is_enabled,
        "sort_order": i.sort_order
    } for i in indicators])


@router.get("/categories")
async def get_categories():
    """获取指标分类列表"""
    categories = [
        {"key": "trend", "name": "趋势类", "description": "用于判断趋势方向，如MA、EMA、BOLL等"},
        {"key": "momentum", "name": "动量类", "description": "用于判断动量强弱，如MACD、KDJ等"},
        {"key": "oscillator", "name": "震荡类", "description": "用于判断超买超卖，如RSI、CCI等"},
        {"key": "volume", "name": "成交量类", "description": "用于分析成交量变化，如VOL_MA、OBV等"},
        {"key": "volatility", "name": "波动率类", "description": "用于测量波动程度，如ATR等"}
    ]
    return success_response(categories)


@router.get("/{indicator_key}")
async def get_indicator(indicator_key: str):
    """获取单个指标详情"""
    indicator = await IndicatorLibrary.get_or_none(indicator_key=indicator_key)
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")

    return success_response({
        "id": indicator.id,
        "indicator_key": indicator.indicator_key,
        "indicator_name": indicator.indicator_name,
        "category": indicator.category,
        "category_name": get_category_name(indicator.category),
        "description": indicator.description,
        "value_type": indicator.value_type,
        "params": indicator.params,
        "output_fields": indicator.output_fields,
        "default_output": indicator.default_output,
        "usage_guide": indicator.usage_guide,
        "signal_interpretation": indicator.signal_interpretation,
        "is_builtin": indicator.is_builtin,
        "is_enabled": indicator.is_enabled,
        "sort_order": indicator.sort_order
    })


@router.post("")
async def create_indicator(data: IndicatorCreate):
    """创建自定义指标"""
    existing = await IndicatorLibrary.get_or_none(indicator_key=data.indicator_key)
    if existing:
        raise HTTPException(status_code=400, detail="指标KEY已存在")

    indicator = await IndicatorLibrary.create(
        indicator_key=data.indicator_key,
        indicator_name=data.indicator_name,
        category=data.category,
        description=data.description,
        value_type=data.value_type,
        params=data.params,
        output_fields=data.output_fields,
        default_output=data.default_output,
        usage_guide=data.usage_guide,
        signal_interpretation=data.signal_interpretation,
        is_builtin=False,
        is_enabled=True
    )
    return success_response({"id": indicator.id})


@router.put("/{indicator_id}")
async def update_indicator(indicator_id: int, data: IndicatorUpdate):
    """更新指标"""
    indicator = await IndicatorLibrary.get_or_none(id=indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(indicator, key, value)

    await indicator.save()
    return success_response(message="更新成功")


@router.delete("/{indicator_id}")
async def delete_indicator(indicator_id: int):
    """删除指标"""
    indicator = await IndicatorLibrary.get_or_none(id=indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")

    if indicator.is_builtin:
        raise HTTPException(status_code=400, detail="内置指标不可删除")

    await indicator.delete()
    return success_response(message="删除成功")


@router.post("/init")
async def init_indicators():
    """初始化预置指标数据"""
    count = 0
    for data in INDICATOR_PRESET_DATA:
        existing = await IndicatorLibrary.get_or_none(indicator_key=data["indicator_key"])
        if not existing:
            await IndicatorLibrary.create(**data)
            count += 1
        else:
            # 更新已有数据
            for key, value in data.items():
                if key not in ["indicator_key"]:
                    setattr(existing, key, value)
            await existing.save()

    return success_response(message=f"已初始化 {count} 个指标")


def get_category_name(category: str) -> str:
    """获取分类名称"""
    names = {
        "trend": "趋势类",
        "momentum": "动量类",
        "oscillator": "震荡类",
        "volume": "成交量类",
        "volatility": "波动率类"
    }
    return names.get(category, category)