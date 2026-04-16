"""
投资建议 REST API 路由
"""
from fastapi import APIRouter
from typing import List, Optional

from app.models.advice_models import (
    AdviceRequest,
    BatchAdviceRequest,
    ReportRequest,
)
from app.services.advice_service import advice_service

router = APIRouter()


@router.post("/generate")
async def generate_advice(request: AdviceRequest):
    """生成投资建议"""
    result = await advice_service.generate_advice(
        stock_code=request.stock_code,
        advice_type=request.advice_type,
        include_backtest=request.include_backtest,
        model=request.model
    )
    return result.model_dump()


@router.post("/batch")
async def batch_advice(request: BatchAdviceRequest):
    """批量投资建议"""
    result = await advice_service.batch_generate_advice(
        stock_codes=request.stock_codes,
        advice_type=request.advice_type,
        model=request.model
    )
    return result.model_dump()


@router.post("/report")
async def generate_report(request: ReportRequest):
    """生成分析报告"""
    result = await advice_service.generate_report(
        stock_codes=request.stock_codes,
        report_type=request.report_type,
        model=request.model
    )
    return result.model_dump()