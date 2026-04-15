"""
回测Schema定义
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import date, datetime


class BacktestRequest(BaseModel):
    """回测请求"""
    start_date: date = Field(..., description="回测开始日期")
    end_date: date = Field(..., description="回测结束日期")
    initial_capital: float = Field(default=100000, ge=10000, description="初始资金")


class BacktestResponse(BaseModel):
    """回测结果响应"""
    id: int
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: Optional[float]
    total_return: Optional[float]
    annual_return: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    trade_count: Optional[int]
    sharpe_ratio: Optional[float]
    calmar_ratio: Optional[float]
    benchmark_return: Optional[float]
    excess_return: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class BacktestCurvePoint(BaseModel):
    """收益曲线点"""
    date: date
    equity: float
    benchmark: Optional[float]


class BacktestCurveResponse(BaseModel):
    """收益曲线响应"""
    strategy_curve: List[BacktestCurvePoint]
    benchmark_curve: List[BacktestCurvePoint]