"""
回测数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class BacktestRequest(BaseModel):
    """回测请求"""
    conditions: List[Dict] = Field(..., description="筛选条件")
    weights: Optional[List[Dict]] = Field(None, description="评分权重（可选）")
    start_date: str = Field(..., description="开始日期 YYYYMMDD")
    end_date: str = Field(..., description="结束日期 YYYYMMDD")
    rebalance_freq: str = Field(default="daily", description="调仓频率：daily/weekly/monthly")
    top_n: int = Field(default=10, description="持仓数量")
    benchmark: str = Field(default="000300.SH", description="基准指数")


class BacktestSummary(BaseModel):
    """回测摘要"""
    total_return: float = Field(..., description="累计收益率 %")
    annual_return: float = Field(..., description="年化收益率 %")
    max_drawdown: float = Field(..., description="最大回撤 %")
    win_rate: float = Field(..., description="胜率 %")
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    benchmark_return: float = Field(..., description="基准收益 %")
    excess_return: float = Field(..., description="超额收益 %")
    total_trades: int = Field(default=0, description="总交易次数")


class DailyReturn(BaseModel):
    """每日收益"""
    date: str
    return_value: float
    benchmark_return: float
    excess_return: float
    positions: List[str] = Field(default_factory=list)


class TradeLog(BaseModel):
    """交易记录"""
    date: str
    action: str  # buy/sell
    stock_code: str
    stock_name: str = ""
    price: float
    quantity: int
    amount: float


class BacktestResult(BaseModel):
    """回测结果"""
    request: BacktestRequest
    summary: BacktestSummary
    daily_returns: List[DailyReturn] = Field(default_factory=list)
    positions_history: List[Dict] = Field(default_factory=list)
    trade_log: List[TradeLog] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class ICAnalysisRequest(BaseModel):
    """IC分析请求"""
    factor_id: str = Field(..., description="因子ID")
    start_date: str = Field(..., description="开始日期 YYYYMMDD")
    end_date: str = Field(..., description="结束日期 YYYYMMDD")
    forward_period: int = Field(default=5, description="预测周期（天）")


class ICValue(BaseModel):
    """IC值"""
    date: str
    ic: float


class ICAnalysisResult(BaseModel):
    """IC分析结果"""
    factor_id: str
    period: str
    ic_mean: float = Field(..., description="平均IC")
    ic_std: float = Field(..., description="IC标准差")
    icir: float = Field(..., description="ICIR = IC均值/IC标准差")
    ic_positive_ratio: float = Field(..., description="IC正值占比")
    ic_series: List[ICValue] = Field(default_factory=list)


class GroupReturnsRequest(BaseModel):
    """分组收益请求"""
    factor_id: str = Field(..., description="因子ID")
    start_date: str = Field(..., description="开始日期 YYYYMMDD")
    end_date: str = Field(..., description="结束日期 YYYYMMDD")
    num_groups: int = Field(default=5, description="分组数量")


class GroupReturn(BaseModel):
    """分组收益"""
    group_id: int
    group_name: str
    return_value: float
    stocks_count: int


class GroupReturnsResult(BaseModel):
    """分组收益结果"""
    factor_id: str
    period: str
    num_groups: int
    groups: List[GroupReturn]
    spread: float = Field(..., description="最高组与最低组收益差")


class SensitivityTestRequest(BaseModel):
    """敏感性测试请求"""
    conditions: List[Dict] = Field(..., description="基础筛选条件")
    param_ranges: Dict[str, List] = Field(..., description="参数变化范围")
    start_date: str
    end_date: str


class SensitivityTestResult(BaseModel):
    """敏感性测试结果"""
    param_combinations: List[Dict]
    results: List[BacktestSummary]
    best_params: Optional[Dict] = None
    sensitivity_matrix: Optional[Dict] = None