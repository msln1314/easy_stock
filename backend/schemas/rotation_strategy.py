"""
轮动策略Schema定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal


class RotationStrategyCreate(BaseModel):
    """轮动策略创建请求"""
    name: str = Field(..., max_length=100, description="策略名称")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    slope_period: int = Field(default=20, ge=5, le=60, description="斜率计算周期")
    rsrs_period: int = Field(default=18, ge=5, le=30, description="RSRS窗口周期")
    rsrs_z_window: int = Field(default=100, ge=50, le=300, description="Z-score标准化窗口")
    rsrs_buy_threshold: float = Field(default=0.7, ge=0.5, le=1.5, description="RSRS买入阈值")
    rsrs_sell_threshold: float = Field(default=-0.7, ge=-1.5, le=-0.5, description="RSRS卖出阈值")
    ma_period: int = Field(default=20, ge=5, le=60, description="MA过滤周期")
    hold_count: int = Field(default=2, ge=1, le=5, description="持仓数量")
    rebalance_freq: str = Field(default="weekly", description="调仓频率: daily/weekly/monthly")
    execute_mode: str = Field(default="simulate", description="执行模式: simulate/alert")


class RotationStrategyUpdate(BaseModel):
    """轮动策略更新请求"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slope_period: Optional[int] = Field(None, ge=5, le=60)
    rsrs_period: Optional[int] = Field(None, ge=5, le=30)
    status: Optional[str] = Field(None, description="状态: running/paused/stopped")


class RotationStrategyResponse(BaseModel):
    """轮动策略响应"""
    id: int
    name: str
    description: Optional[str]
    slope_period: int
    rsrs_period: int
    rsrs_z_window: int
    rsrs_buy_threshold: float
    rsrs_sell_threshold: float
    ma_period: int
    hold_count: int
    rebalance_freq: str
    execute_mode: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RotationStrategyStatusUpdate(BaseModel):
    """策略状态更新"""
    status: str = Field(..., description="状态: running/paused/stopped")


class EtfScoreResponse(BaseModel):
    """ETF评分响应"""
    etf_code: str
    etf_name: Optional[str]
    momentum_score: Optional[float]
    slope_value: Optional[float]
    r_squared: Optional[float]
    rsrs_z_score: Optional[float]
    close_price: Optional[float]
    ma_value: Optional[float]
    rank_position: Optional[int]

    class Config:
        from_attributes = True


class RotationSignalResponse(BaseModel):
    """轮动信号响应"""
    id: int
    signal_date: date
    signal_type: str
    etf_code: str
    etf_name: Optional[str]
    action: str
    score: Optional[float]
    rsrs_z: Optional[float]
    price: Optional[float]
    reason: Optional[str]
    is_executed: bool
    created_at: datetime

    class Config:
        from_attributes = True