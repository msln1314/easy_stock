"""
技术指标数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class IndicatorValue(BaseModel):
    """单个指标值"""
    indicator_id: str = Field(..., description="指标ID，如 MA5, RSI14")
    indicator_name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    date: Optional[str] = Field(None, description="日期 YYYYMMDD")
    signal: Optional[str] = Field(None, description="信号判断：支撑/压力/中性等")


class IndicatorCalculateRequest(BaseModel):
    """指标计算请求"""
    stock_code: str = Field(..., description="股票代码")
    indicators: List[str] = Field(..., description="指标列表，如 ['MA5', 'MA10', 'RSI14']")
    period: str = Field(default="1d", description="周期：1d/1w/1m/5m/15m/30m/60m")
    start_date: Optional[str] = Field(None, description="开始日期 YYYYMMDD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYYMMDD")


class IndicatorCalculateResponse(BaseModel):
    """指标计算响应"""
    stock_code: str
    period: str
    indicators: List[IndicatorValue]
    raw_data: Optional[List[Dict]] = Field(None, description="原始K线数据")
    count: int = Field(default=0, description="数据点数量")


class IndicatorBatchRequest(BaseModel):
    """批量指标计算请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    indicators: List[str] = Field(..., description="指标列表")
    date: Optional[str] = Field(None, description="日期 YYYYMMDD")


class IndicatorBatchResponse(BaseModel):
    """批量指标计算响应"""
    date: str
    results: Dict[str, List[IndicatorValue]] = Field(default_factory=dict, description="各股票指标结果")
    count: int = Field(default=0, description="股票数量")


class IndicatorDefinition(BaseModel):
    """指标定义"""
    indicator_id: str = Field(..., description="指标ID")
    indicator_name: str = Field(..., description="指标名称")
    category: str = Field(..., description="指标类别：trend/momentum/volatility/volume/price")
    description: str = Field(default="", description="指标描述")
    formula: str = Field(default="", description="计算公式")
    params: Optional[List[Dict]] = Field(None, description="参数列表")
    unit: str = Field(default="", description="单位")


class IndicatorListResponse(BaseModel):
    """指标列表响应"""
    indicators: List[IndicatorDefinition]
    count: int


# 预定义指标列表
PRESET_INDICATORS = [
    # 趋势指标
    IndicatorDefinition(indicator_id="MA5", indicator_name="5日均线", category="trend", description="5日移动平均线", formula="MA(close, 5)", params=[{"key": "period", "default": 5}], unit="元"),
    IndicatorDefinition(indicator_id="MA10", indicator_name="10日均线", category="trend", description="10日移动平均线", formula="MA(close, 10)", params=[{"key": "period", "default": 10}], unit="元"),
    IndicatorDefinition(indicator_id="MA20", indicator_name="20日均线", category="trend", description="20日移动平均线", formula="MA(close, 20)", params=[{"key": "period", "default": 20}], unit="元"),
    IndicatorDefinition(indicator_id="MA60", indicator_name="60日均线", category="trend", description="60日移动平均线", formula="MA(close, 60)", params=[{"key": "period", "default": 60}], unit="元"),
    IndicatorDefinition(indicator_id="EMA12", indicator_name="12日指数均线", category="trend", description="12日指数移动平均线", formula="EMA(close, 12)", unit="元"),
    IndicatorDefinition(indicator_id="EMA26", indicator_name="26日指数均线", category="trend", description="26日指数移动平均线", formula="EMA(close, 26)", unit="元"),
    # 动量指标
    IndicatorDefinition(indicator_id="RSI6", indicator_name="6日RSI", category="momentum", description="6日相对强弱指标", formula="RSI(close, 6)", params=[{"key": "period", "default": 6}], unit="%"),
    IndicatorDefinition(indicator_id="RSI14", indicator_name="14日RSI", category="momentum", description="14日相对强弱指标", formula="RSI(close, 14)", params=[{"key": "period", "default": 14}], unit="%"),
    IndicatorDefinition(indicator_id="KDJ_K", indicator_name="KDJ-K值", category="momentum", description="KDJ指标的K值", formula="KDJ(high, low, close, 9, 3, 3).K"),
    IndicatorDefinition(indicator_id="KDJ_D", indicator_name="KDJ-D值", category="momentum", description="KDJ指标的D值", formula="KDJ(high, low, close, 9, 3, 3).D"),
    IndicatorDefinition(indicator_id="KDJ_J", indicator_name="KDJ-J值", category="momentum", description="KDJ指标的J值", formula="KDJ(high, low, close, 9, 3, 3).J"),
    IndicatorDefinition(indicator_id="MACD_DIF", indicator_name="MACD-DIF", category="momentum", description="MACD的DIF值", formula="MACD(close, 12, 26, 9).DIF"),
    IndicatorDefinition(indicator_id="MACD_DEA", indicator_name="MACD-DEA", category="momentum", description="MACD的DEA值", formula="MACD(close, 12, 26, 9).DEA"),
    IndicatorDefinition(indicator_id="MACD_HIST", indicator_name="MACD柱", category="momentum", description="MACD柱状图", formula="MACD(close, 12, 26, 9).MACD"),
    IndicatorDefinition(indicator_id="MOM10", indicator_name="10日动量", category="momentum", description="10日价格动量", formula="close - close_10", unit="元"),
    IndicatorDefinition(indicator_id="ROC10", indicator_name="10日变动率", category="momentum", description="10日价格变动率", formula="(close - close_10) / close_10 * 100", unit="%"),
    # 波动指标
    IndicatorDefinition(indicator_id="ATR14", indicator_name="14日ATR", category="volatility", description="14日平均真实波幅", formula="ATR(high, low, close, 14)", unit="元"),
    IndicatorDefinition(indicator_id="STD20", indicator_name="20日标准差", category="volatility", description="20日收益率标准差", formula="STD(close, 20)", unit="元"),
    IndicatorDefinition(indicator_id="BOLL_UP", indicator_name="布林上轨", category="volatility", description="布林带上轨", formula="BOLL(close, 20, 2).upper", unit="元"),
    IndicatorDefinition(indicator_id="BOLL_MID", indicator_name="布林中轨", category="volatility", description="布林带中轨", formula="BOLL(close, 20, 2).middle", unit="元"),
    IndicatorDefinition(indicator_id="BOLL_LOW", indicator_name="布林下轨", category="volatility", description="布林带下轨", formula="BOLL(close, 20, 2).lower", unit="元"),
    # 成交量指标
    IndicatorDefinition(indicator_id="VOL_MA5", indicator_name="5日均量", category="volume", description="5日成交量均值", formula="MA(volume, 5)", unit="手"),
    IndicatorDefinition(indicator_id="VOL_MA10", indicator_name="10日均量", category="volume", description="10日成交量均值", formula="MA(volume, 10)", unit="手"),
    IndicatorDefinition(indicator_id="VOL_RATIO", indicator_name="量比", category="volume", description="当日成交量/5日均量", formula="volume / MA(volume, 5)", unit="倍"),
    IndicatorDefinition(indicator_id="OBV", indicator_name="OBV", category="volume", description="能量潮指标", formula="OBV(close, volume)"),
    IndicatorDefinition(indicator_id="VWAP", indicator_name="VWAP", category="volume", description="成交量加权平均价", formula="SUM(amount) / SUM(volume)", unit="元"),
    # 价格指标
    IndicatorDefinition(indicator_id="AMP", indicator_name="振幅", category="price", description="当日振幅", formula="(high - low) / pre_close * 100", unit="%"),
    IndicatorDefinition(indicator_id="PRICE_POS", indicator_name="价格位置", category="price", description="当前价格在布林带中的位置", formula="(close - BOLL_LOW) / (BOLL_UP - BOLL_LOW)", unit="%"),
]