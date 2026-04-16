"""
趋势分析 REST API 路由
"""
from fastapi import APIRouter
from typing import List, Optional, Dict

from app.models.trend_models import (
    TrendAnalysisRequest,
    BatchTrendRequest,
)
from app.services.trend_service import trend_service

router = APIRouter()


@router.post("/analyze")
async def analyze_trend(request: TrendAnalysisRequest):
    """单只股票趋势分析"""
    result = await trend_service.analyze_trend(
        stock_code=request.stock_code,
        analysis_type=request.analysis_type,
        include_indicators=request.include_indicators,
        model=request.model
    )
    return result.model_dump()


@router.post("/batch")
async def batch_analyze(request: BatchTrendRequest):
    """批量趋势分析"""
    result = await trend_service.batch_analyze_trends(
        stock_codes=request.stock_codes,
        analysis_type=request.analysis_type,
        model=request.model
    )
    return result.model_dump()