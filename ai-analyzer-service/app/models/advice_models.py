"""
投资建议数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ActionSuggestion(BaseModel):
    """行动建议"""
    action: str = Field(..., description="建议操作: 买入/卖出/持有/观望")
    position_size: str = Field(default="中等仓位", description="仓位建议")
    entry_strategy: str = Field(default="分批建仓", description="入场策略")
    target_price: Optional[float] = Field(default=None, description="目标价位")
    stop_loss: Optional[float] = Field(default=None, description="止损价位")


class Reasoning(BaseModel):
    """建议理由"""
    trend_reason: str = Field(default="", description="趋势理由")
    score_reason: str = Field(default="", description="评分理由")
    risk_reason: str = Field(default="", description="风险理由")


class TimeHorizon(BaseModel):
    """时间维度"""
    short_term: str = Field(default="中性", description="短期看法")
    mid_term: str = Field(default="中性", description="中期看法")
    long_term: str = Field(default="中性", description="长期看法")


class AdviceRequest(BaseModel):
    """投资建议请求"""
    stock_code: str = Field(..., description="股票代码")
    advice_type: str = Field(default="comprehensive", description="建议类型")
    include_backtest: bool = Field(default=True, description="包含回测数据")
    model: Optional[str] = Field(default=None, description="AI模型")


class AdviceResult(BaseModel):
    """投资建议结果"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    advice_date: str = Field(..., description="建议日期")
    recommendation: str = Field(..., description="建议: buy/sell/hold/watch")
    confidence: float = Field(..., ge=0, le=1, description="置信度 0-1")
    action_suggestion: ActionSuggestion = Field(default_factory=ActionSuggestion, description="行动建议")
    reasoning: Reasoning = Field(default_factory=Reasoning, description="建议理由")
    time_horizon: TimeHorizon = Field(default_factory=TimeHorizon, description="时间维度")
    analysis_summary: str = Field(default="", description="分析摘要")
    key_catalysts: List[str] = Field(default_factory=list, description="关键催化剂")
    risk_warnings: List[str] = Field(default_factory=list, description="风险警示")
    related_stocks: List[str] = Field(default_factory=list, description="相关股票")


class BatchAdviceRequest(BaseModel):
    """批量投资建议请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    advice_type: str = Field(default="comprehensive", description="建议类型")
    model: Optional[str] = Field(default=None, description="AI模型")


class BatchAdviceResponse(BaseModel):
    """批量投资建议响应"""
    advice_date: str = Field(..., description="建议日期")
    results: List[AdviceResult] = Field(default_factory=list, description="建议结果")
    count: int = Field(default=0, description="结果数量")


class ReportRequest(BaseModel):
    """报告生成请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    report_type: str = Field(default="portfolio", description="报告类型")
    model: Optional[str] = Field(default=None, description="AI模型")


class ReportResult(BaseModel):
    """报告结果"""
    report_date: str = Field(..., description="报告日期")
    report_type: str = Field(..., description="报告类型")
    title: str = Field(..., description="报告标题")
    summary: str = Field(default="", description="报告摘要")
    sections: List[str] = Field(default_factory=list, description="报告章节")
    recommendations: List[str] = Field(default_factory=list, description="主要建议")
    risk_summary: str = Field(default="", description="风险摘要")
    opportunities: List[str] = Field(default_factory=list, description="机会列表")