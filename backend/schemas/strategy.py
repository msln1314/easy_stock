"""
策略相关Schema定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# 指标Schema
class IndicatorBase(BaseModel):
    indicator_type: str = Field(..., description="指标类型")
    parameters: dict = Field(..., description="指标参数")


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorResponse(IndicatorBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# 信号Schema
class SignalBase(BaseModel):
    signal_type: str = Field(..., description="信号类型: buy/sell")
    condition_type: str = Field(..., description="条件类型")
    condition_config: dict = Field(..., description="条件配置")
    priority: int = Field(default=0, description="优先级")


class SignalCreate(SignalBase):
    pass


class SignalResponse(SignalBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# 风控Schema
class RiskBase(BaseModel):
    stop_profit_type: Optional[str] = Field(None, description="止盈类型")
    stop_profit_value: Optional[float] = Field(None, description="止盈值")
    stop_loss_type: Optional[str] = Field(None, description="止损类型")
    stop_loss_value: Optional[float] = Field(None, description="止损值")
    max_position: Optional[float] = Field(None, description="最大仓位比例")


class RiskCreate(RiskBase):
    pass


class RiskResponse(RiskBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# 策略Schema
class StrategyBase(BaseModel):
    name: str = Field(..., max_length=100, description="策略名称")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    execute_mode: str = Field(default="simulate", description="执行模式")
    status: str = Field(default="paused", description="状态")


class StrategyCreate(StrategyBase):
    indicators: List[IndicatorCreate] = Field(default=[], description="技术指标配置")
    signals: List[SignalCreate] = Field(default=[], description="买卖信号规则")
    risk: Optional[RiskCreate] = Field(None, description="止盈止损配置")


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    execute_mode: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    indicators: Optional[List[IndicatorCreate]] = Field(None)
    signals: Optional[List[SignalCreate]] = Field(None)
    risk: Optional[RiskCreate] = Field(None)


class StrategyResponse(StrategyBase):
    id: int
    indicators: List[IndicatorResponse] = []
    signals: List[SignalResponse] = []
    risk: Optional[RiskResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    """策略列表响应"""
    id: int
    name: str
    description: Optional[str]
    execute_mode: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StrategyStatusUpdate(BaseModel):
    """状态更新"""
    status: str = Field(..., description="新状态: running/paused/stopped")


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    page_size: int
    items: List[StrategyListResponse]


class StrategyStatsResponse(BaseModel):
    """统计响应"""
    total: int
    by_execute_mode: dict
    by_status: dict