"""
回测 REST API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict

from app.models.backtest_models import (
    BacktestRequest,
    ICAnalysisRequest,
    GroupReturnsRequest,
    SensitivityTestRequest,
)
from app.services.backtest_service import backtest_service

router = APIRouter()


@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """执行完整回测"""
    result = await backtest_service.run_backtest(
        conditions=request.conditions,
        weights=request.weights,
        start_date=request.start_date,
        end_date=request.end_date,
        rebalance_freq=request.rebalance_freq,
        top_n=request.top_n,
        benchmark=request.benchmark
    )
    return result.model_dump()


@router.post("/ic")
async def calculate_ic(request: ICAnalysisRequest):
    """IC分析"""
    result = await backtest_service.calculate_ic(
        factor_id=request.factor_id,
        start_date=request.start_date,
        end_date=request.end_date,
        forward_period=request.forward_period
    )
    return result.model_dump()


@router.post("/group")
async def group_returns(request: GroupReturnsRequest):
    """分组收益对比"""
    result = await backtest_service.group_returns(
        factor_id=request.factor_id,
        start_date=request.start_date,
        end_date=request.end_date,
        num_groups=request.num_groups
    )
    return result.model_dump()


@router.post("/sensitivity")
async def sensitivity_test(request: SensitivityTestRequest):
    """敏感性测试"""
    result = await backtest_service.sensitivity_test(
        conditions=request.conditions,
        param_ranges=request.param_ranges,
        start_date=request.start_date,
        end_date=request.end_date
    )
    return result.model_dump()