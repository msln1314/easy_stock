"""
因子 REST API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict

from app.models.factor_models import (
    FactorScreenRequest,
    ScoreCalculateRequest,
    FactorValueRequest,
    FactorCondition,
    ScoreWeight,
)
from app.services.factor_service import factor_service

router = APIRouter()


@router.post("/screen")
async def screen_stocks(request: FactorScreenRequest):
    """因子选股"""
    result = await factor_service.screen_stocks(
        conditions=request.conditions,
        stock_pool=request.stock_pool,
        date=request.date,
        limit=request.limit
    )
    return result.model_dump()


@router.post("/score")
async def calculate_score(request: ScoreCalculateRequest):
    """综合评分计算"""
    result = await factor_service.calculate_score(
        stock_codes=request.stock_codes,
        weights=request.weights,
        date=request.date
    )
    return result.model_dump()


@router.get("/value/{stock_code}")
async def get_factor_value(
    stock_code: str,
    factor_id: str,
    date: Optional[str] = None
):
    """获取单只股票的因子值"""
    result = await factor_service.get_factor_value(
        stock_code=stock_code,
        factor_id=factor_id,
        date=date
    )
    return result.model_dump()


@router.get("/list")
async def get_factor_list():
    """获取支持的因子列表"""
    return factor_service.get_available_factors().model_dump()