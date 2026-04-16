"""
指标 REST API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict

from app.models.indicator_models import IndicatorCalculateRequest, IndicatorBatchRequest
from app.services.indicator_service import indicator_service

router = APIRouter()


@router.post("/calculate")
async def calculate_indicators(request: IndicatorCalculateRequest):
    """计算单只股票的技术指标"""
    result = await indicator_service.calculate_indicators(
        stock_code=request.stock_code,
        indicators=request.indicators,
        period=request.period,
        start_date=request.start_date,
        end_date=request.end_date
    )
    return result.model_dump()


@router.post("/batch")
async def batch_calculate(request: IndicatorBatchRequest):
    """批量计算多只股票的指标"""
    result = await indicator_service.batch_calculate(
        stock_codes=request.stock_codes,
        indicators=request.indicators,
        date=request.date
    )
    return result.model_dump()


@router.get("/list")
async def get_indicator_list():
    """获取支持的指标列表"""
    return indicator_service.get_indicator_list()