"""
趋势分析数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class KeyIndicator(BaseModel):
    """关键指标"""
    value: float = Field(..., description="指标值")
    signal: str = Field(default="中性", description="信号判断")


class ScoreSummary(BaseModel):
    """评分摘要"""
    composite_score: float = Field(..., description="综合评分")
    rank: Optional[int] = Field(default=None, description="排名")


class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""
    stock_code: str = Field(..., description="股票代码")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    include_indicators: Optional[List[str]] = Field(default=None, description="包含的指标")
    model: Optional[str] = Field(default=None, description="AI模型")


class TrendAnalysisResult(BaseModel):
    """趋势分析结果"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    analysis_date: str = Field(..., description="分析日期")
    trend_direction: str = Field(..., description="趋势方向: upward/downward/sideways")
    trend_strength: float = Field(..., ge=0, le=1, description="趋势强度 0-1")
    confidence: float = Field(..., ge=0, le=1, description="分析置信度 0-1")
    key_indicators: Dict[str, KeyIndicator] = Field(default_factory=dict, description="关键指标")
    score_summary: Optional[ScoreSummary] = Field(default=None, description="评分摘要")
    analysis_text: str = Field(default="", description="AI生成的分析文本")
    key_points: List[str] = Field(default_factory=list, description="关键点")
    warnings: List[str] = Field(default_factory=list, description="风险提示")


class BatchTrendRequest(BaseModel):
    """批量趋势分析请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    analysis_type: str = Field(default="comprehensive", description="分析类型")
    model: Optional[str] = Field(default=None, description="AI模型")


class BatchTrendResponse(BaseModel):
    """批量趋势分析响应"""
    analysis_date: str = Field(..., description="分析日期")
    results: List[TrendAnalysisResult] = Field(default_factory=list, description="分析结果")
    count: int = Field(default=0, description="结果数量")