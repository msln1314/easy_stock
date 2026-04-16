"""
因子选股与评分数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class FactorCondition(BaseModel):
    """因子筛选条件"""
    factor_id: str = Field(..., description="因子ID，如 RSI14, MA5_MA10")
    operator: str = Field(..., description="操作符：gt/lt/ge/le/eq/between")
    value: float = Field(..., description="阈值")
    value2: Optional[float] = Field(None, description="between操作符的第二阈值")


class ScoreWeight(BaseModel):
    """评分权重配置"""
    factor_id: str = Field(..., description="因子ID")
    weight: float = Field(..., description="权重，0-1之间")
    direction: str = Field(default="high", description="方向：high表示高值更好，low表示低值更好")


class FactorScreenRequest(BaseModel):
    """因子选股请求"""
    conditions: List[FactorCondition] = Field(..., description="筛选条件列表")
    stock_pool: Optional[List[str]] = Field(None, description="股票池，默认全A股")
    date: Optional[str] = Field(None, description="日期 YYYYMMDD，默认今日")
    limit: int = Field(default=50, description="返回数量限制")


class StockScoreResult(BaseModel):
    """股票评分结果"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(default="", description="股票名称")
    score: float = Field(..., description="综合评分")
    rank: int = Field(default=0, description="排名")
    factor_values: Dict[str, float] = Field(default_factory=dict, description="各因子值")
    factor_scores: Optional[Dict[str, float]] = Field(None, description="各因子得分")


class FactorScreenResponse(BaseModel):
    """因子选股响应"""
    date: str = Field(..., description="日期")
    stocks: List[StockScoreResult] = Field(default_factory=list, description="筛选结果")
    count: int = Field(default=0, description="结果数量")


class ScoreCalculateRequest(BaseModel):
    """评分计算请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    weights: List[ScoreWeight] = Field(..., description="评分权重配置")
    date: Optional[str] = Field(None, description="日期 YYYYMMDD")


class ScoreCalculateResponse(BaseModel):
    """评分计算响应"""
    date: str
    stocks: List[StockScoreResult]
    weights_summary: Dict[str, float] = Field(default_factory=dict, description="权重汇总")


class FactorValueRequest(BaseModel):
    """获取因子值请求"""
    stock_code: str = Field(..., description="股票代码")
    factor_id: str = Field(..., description="因子ID")
    date: Optional[str] = Field(None, description="日期 YYYYMMDD")


class FactorValueResponse(BaseModel):
    """获取因子值响应"""
    stock_code: str
    factor_id: str
    factor_name: str
    value: float
    date: str
    percentile: Optional[float] = Field(None, description="百分位排名")


class FactorDefinition(BaseModel):
    """因子定义"""
    factor_id: str
    factor_name: str
    category: str
    description: str = ""
    is_custom: bool = False


class FactorListResponse(BaseModel):
    """因子列表响应"""
    factors: List[FactorDefinition]
    count: int