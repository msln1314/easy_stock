"""
因子库数据模型
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class FactorCategory(str, Enum):
    """因子分类"""
    TREND = "trend"           # 趋势因子
    MOMENTUM = "momentum"     # 动量因子
    VOLATILITY = "volatility" # 波动因子
    VOLUME = "volume"         # 成交量因子
    VALUE = "value"           # 价值因子
    GROWTH = "growth"         # 成长因子
    QUALITY = "quality"       # 质量因子
    SENTIMENT = "sentiment"   # 情绪因子
    CUSTOM = "custom"         # 自定义因子


class FactorDefinition(Model):
    """因子定义表"""
    id = fields.IntField(pk=True)
    factor_id = fields.CharField(max_length=50, unique=True, description="因子ID")
    factor_name = fields.CharField(max_length=100, description="因子名称")
    category = fields.CharEnumField(FactorCategory, description="因子分类")
    description = fields.TextField(null=True, description="因子描述")
    formula = fields.TextField(null=True, description="计算公式")
    params = fields.JSONField(null=True, description="参数配置")
    unit = fields.CharField(max_length=20, null=True, description="单位")
    data_source = fields.CharField(max_length=50, null=True, description="数据来源")
    update_freq = fields.CharField(max_length=20, default="daily", description="更新频率")
    is_builtin = fields.BooleanField(default=True, description="是否内置因子")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "factor_definition"
        ordering = ["id"]

    def __str__(self):
        return f"{self.factor_id} - {self.factor_name}"


class FactorValue(Model):
    """因子值表"""
    id = fields.IntField(pk=True)
    factor_id = fields.CharField(max_length=50, description="因子ID")
    stock_code = fields.CharField(max_length=20, description="股票代码")
    trade_date = fields.CharField(max_length=10, description="交易日期YYYYMMDD")
    value = fields.FloatField(null=True, description="因子值")
    rank = fields.IntField(null=True, description="排名")
    percentile = fields.FloatField(null=True, description="百分位")
    zscore = fields.FloatField(null=True, description="Z-Score")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "factor_value"
        indexes = [
            ("factor_id", "trade_date"),
            ("stock_code", "trade_date"),
        ]

    def __str__(self):
        return f"{self.factor_id} - {self.stock_code} - {self.trade_date}"


class FactorScreenResult(Model):
    """因子选股结果表"""
    id = fields.IntField(pk=True)
    screen_date = fields.CharField(max_length=10, description="筛选日期YYYYMMDD")
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")
    score = fields.FloatField(description="综合得分")
    factor_values = fields.JSONField(description="因子值")
    conditions = fields.JSONField(description="筛选条件")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "factor_screen_result"
        indexes = [
            ("screen_date",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.screen_date}"


# 预置因子数据 - 从QMT同步的常用因子
PRESET_FACTORS = [
    # 趋势因子
    {"factor_id": "MA5", "factor_name": "5日均线", "category": FactorCategory.TREND, "description": "5日移动平均线", "unit": "元"},
    {"factor_id": "MA10", "factor_name": "10日均线", "category": FactorCategory.TREND, "description": "10日移动平均线", "unit": "元"},
    {"factor_id": "MA20", "factor_name": "20日均线", "category": FactorCategory.TREND, "description": "20日移动平均线", "unit": "元"},
    {"factor_id": "MA60", "factor_name": "60日均线", "category": FactorCategory.TREND, "description": "60日移动平均线", "unit": "元"},
    {"factor_id": "EMA12", "factor_name": "12日EMA", "category": FactorCategory.TREND, "description": "12日指数移动平均", "unit": "元"},
    {"factor_id": "EMA26", "factor_name": "26日EMA", "category": FactorCategory.TREND, "description": "26日指数移动平均", "unit": "元"},

    # 动量因子
    {"factor_id": "RSI6", "factor_name": "RSI(6)", "category": FactorCategory.MOMENTUM, "description": "6日相对强弱指标", "unit": ""},
    {"factor_id": "RSI14", "factor_name": "RSI(14)", "category": FactorCategory.MOMENTUM, "description": "14日相对强弱指标", "unit": ""},
    {"factor_id": "MACD", "factor_name": "MACD", "category": FactorCategory.MOMENTUM, "description": "MACD指标", "unit": ""},
    {"factor_id": "KDJ_K", "factor_name": "KDJ-K值", "category": FactorCategory.MOMENTUM, "description": "KDJ指标的K值", "unit": ""},
    {"factor_id": "KDJ_D", "factor_name": "KDJ-D值", "category": FactorCategory.MOMENTUM, "description": "KDJ指标的D值", "unit": ""},

    # 波动因子
    {"factor_id": "ATR", "factor_name": "ATR", "category": FactorCategory.VOLATILITY, "description": "平均真实波幅", "unit": "元"},
    {"factor_id": "BOLL_UP", "factor_name": "布林上轨", "category": FactorCategory.VOLATILITY, "description": "布林带上轨", "unit": "元"},
    {"factor_id": "BOLL_MID", "factor_name": "布林中轨", "category": FactorCategory.VOLATILITY, "description": "布林带中轨", "unit": "元"},
    {"factor_id": "BOLL_LOW", "factor_name": "布林下轨", "category": FactorCategory.VOLATILITY, "description": "布林带下轨", "unit": "元"},

    # 成交量因子
    {"factor_id": "VOL", "factor_name": "成交量", "category": FactorCategory.VOLUME, "description": "当日成交量", "unit": "手"},
    {"factor_id": "AMOUNT", "factor_name": "成交额", "category": FactorCategory.VOLUME, "description": "当日成交金额", "unit": "万元"},
    {"factor_id": "TURNOVER", "factor_name": "换手率", "category": FactorCategory.VOLUME, "description": "当日换手率", "unit": "%"},
    {"factor_id": "VOL_MA5", "factor_name": "5日均量", "category": FactorCategory.VOLUME, "description": "5日成交量均值", "unit": "手"},
    {"factor_id": "VOL_MA10", "factor_name": "10日均量", "category": FactorCategory.VOLUME, "description": "10日成交量均值", "unit": "手"},

    # 价值因子
    {"factor_id": "PE", "factor_name": "市盈率", "category": FactorCategory.VALUE, "description": "股价/每股收益", "unit": "倍"},
    {"factor_id": "PB", "factor_name": "市净率", "category": FactorCategory.VALUE, "description": "股价/每股净资产", "unit": "倍"},
    {"factor_id": "PS", "factor_name": "市销率", "category": FactorCategory.VALUE, "description": "市值/营业收入", "unit": "倍"},
    {"factor_id": "PCF", "factor_name": "市现率", "category": FactorCategory.VALUE, "description": "市值/现金流", "unit": "倍"},
    {"factor_id": "PEG", "factor_name": "PEG", "category": FactorCategory.VALUE, "description": "市盈率/盈利增长率", "unit": "倍"},

    # 成长因子
    {"factor_id": "REVG", "factor_name": "营收增长率", "category": FactorCategory.GROWTH, "description": "营业收入同比增长率", "unit": "%"},
    {"factor_id": "PROFG", "factor_name": "利润增长率", "category": FactorCategory.GROWTH, "description": "净利润同比增长率", "unit": "%"},
    {"factor_id": "EPSG", "factor_name": "EPS增长率", "category": FactorCategory.GROWTH, "description": "每股收益同比增长率", "unit": "%"},

    # 质量因子
    {"factor_id": "ROE", "factor_name": "ROE", "category": FactorCategory.QUALITY, "description": "净资产收益率", "unit": "%"},
    {"factor_id": "ROA", "factor_name": "ROA", "category": FactorCategory.QUALITY, "description": "总资产收益率", "unit": "%"},
    {"factor_id": "GROSSM", "factor_name": "毛利率", "category": FactorCategory.QUALITY, "description": "毛利润/营业收入", "unit": "%"},
    {"factor_id": "NETM", "factor_name": "净利率", "category": FactorCategory.QUALITY, "description": "净利润/营业收入", "unit": "%"},
    {"factor_id": "DEBTR", "factor_name": "资产负债率", "category": FactorCategory.QUALITY, "description": "总负债/总资产", "unit": "%"},
]