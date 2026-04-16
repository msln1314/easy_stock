"""
风险评估数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class VolatilityMetrics(BaseModel):
    """波动率指标"""
    daily_volatility: float = Field(default=0, description="日波动率")
    annual_volatility: float = Field(default=0, description="年化波动率")
    atr_ratio: float = Field(default=0, description="ATR比率")


class DrawdownMetrics(BaseModel):
    """回撤指标"""
    max_drawdown: float = Field(default=0, description="最大回撤")
    avg_drawdown: float = Field(default=0, description="平均回撤")
    drawdown_duration: int = Field(default=0, description="回撤持续时间")


class TailRisk(BaseModel):
    """尾部风险"""
    var_95: float = Field(default=0, description="95% VaR")
    cvar_95: float = Field(default=0, description="95% CVaR")
    extreme_loss_prob: float = Field(default=0, description="极端损失概率")


class BacktestRisk(BaseModel):
    """回测风险"""
    win_rate: float = Field(default=0, description="胜率")
    loss_streak_max: int = Field(default=0, description="最大连续亏损次数")
    avg_loss: float = Field(default=0, description="平均亏损")


class RiskFactor(BaseModel):
    """风险因素"""
    factor: str = Field(..., description="风险因素名称")
    impact: str = Field(..., description="影响程度: low/medium/high")
    description: str = Field(default="", description="描述")


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    stock_code: str = Field(..., description="股票代码")
    assessment_type: str = Field(default="comprehensive", description="评估类型")
    model: Optional[str] = Field(default=None, description="AI模型")


class RiskAssessmentResult(BaseModel):
    """风险评估结果"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    assessment_date: str = Field(..., description="评估日期")
    risk_level: str = Field(..., description="风险等级: low/medium/high/extreme")
    risk_score: int = Field(..., ge=0, le=100, description="风险评分 0-100")
    volatility_metrics: VolatilityMetrics = Field(default_factory=VolatilityMetrics, description="波动率指标")
    drawdown_metrics: DrawdownMetrics = Field(default_factory=DrawdownMetrics, description="回撤指标")
    tail_risk: TailRisk = Field(default_factory=TailRisk, description="尾部风险")
    backtest_risk: BacktestRisk = Field(default_factory=BacktestRisk, description="回测风险")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="风险因素列表")
    analysis_text: str = Field(default="", description="AI生成的分析文本")
    risk_mitigation: List[str] = Field(default_factory=list, description="风险缓解建议")


class PortfolioRiskRequest(BaseModel):
    """组合风险评估请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    weights: Optional[List[float]] = Field(default=None, description="权重列表")
    model: Optional[str] = Field(default=None, description="AI模型")


class PortfolioRiskResult(BaseModel):
    """组合风险评估结果"""
    assessment_date: str = Field(..., description="评估日期")
    portfolio_risk_level: str = Field(..., description="组合风险等级")
    portfolio_risk_score: int = Field(..., description="组合风险评分")
    individual_risks: List[RiskAssessmentResult] = Field(default_factory=list, description="个股风险")
    diversification_score: float = Field(default=0, description="分散化得分")
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="相关性矩阵")
    analysis_text: str = Field(default="", description="分析文本")


class CompareRiskRequest(BaseModel):
    """风险对比请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    model: Optional[str] = Field(default=None, description="AI模型")


class CompareRiskResult(BaseModel):
    """风险对比结果"""
    assessment_date: str = Field(..., description="评估日期")
    comparisons: List[RiskAssessmentResult] = Field(default_factory=list, description="风险评估结果")
    ranking: List[str] = Field(default_factory=list, description="风险排名（从低到高）")
    summary: str = Field(default="", description="对比摘要")