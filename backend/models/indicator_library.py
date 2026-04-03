"""
指标库数据模型
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class IndicatorCategory(str, Enum):
    """指标分类"""
    TREND = "trend"           # 趋势类指标 (MA, EMA, BOLL, etc.)
    MOMENTUM = "momentum"     # 动量类指标
    OSCILLATOR = "oscillator" # 震荡类指标
    VOLUME = "volume"         # 成交量类指标 (VOL_MA, OBV, etc.)
    VOLATILITY = "volatility" # 波动率类指标


class IndicatorValueType(str, Enum):
    """指标值类型"""
    SINGLE = "single"         # 单值 (RSI, ATR, etc.)
    MULTI = "multi"           # 多值 (BOLL: upper/middle/lower, KDJ: k/d/j)
    SERIES = "series"         # 序列值


class IndicatorLibrary(Model):
    """指标库表"""
    id = fields.IntField(pk=True)
    indicator_key = fields.CharField(max_length=50, unique=True, description="指标KEY")
    indicator_name = fields.CharField(max_length=100, description="指标名称")
    category = fields.CharEnumField(IndicatorCategory, description="指标分类")
    description = fields.TextField(null=True, description="指标说明")
    value_type = fields.CharEnumField(IndicatorValueType, default=IndicatorValueType.SINGLE, description="值类型")

    # 参数定义
    params = fields.JSONField(null=True, description="参数定义列表")

    # 输出定义
    output_fields = fields.JSONField(null=True, description="输出字段定义")
    default_output = fields.CharField(max_length=50, null=True, description="默认输出字段")

    # 使用说明
    usage_guide = fields.TextField(null=True, description="使用说明")
    signal_interpretation = fields.JSONField(null=True, description="信号解读规则")

    # 状态
    is_builtin = fields.BooleanField(default=True, description="是否内置指标")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    sort_order = fields.IntField(default=0, description="排序")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "indicator_library"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.indicator_key} - {self.indicator_name}"


# 预置指标数据 - pandas_ta 支持的常用指标
INDICATOR_PRESET_DATA = [
    # ========== 趋势类指标 ==========
    {
        "indicator_key": "SMA",
        "indicator_name": "简单移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "简单移动平均线，计算一段时间内价格的算术平均值。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500, "desc": "计算周期"},
            {"key": "offset", "name": "偏移", "type": "int", "default": 0, "min": 0, "max": 100, "desc": "数据偏移量"}
        ],
        "output_fields": [
            {"key": "values", "name": "SMA值", "type": "float", "desc": "SMA序列"}
        ],
        "usage_guide": "最基础的移动平均线，用于判断趋势方向和支撑阻力位。",
        "sort_order": 1
    },
    {
        "indicator_key": "EMA",
        "indicator_name": "指数移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "指数移动平均线，对近期价格赋予更大权重，反应更快。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500},
            {"key": "offset", "name": "偏移", "type": "int", "default": 0, "min": 0, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "EMA值", "type": "float"}
        ],
        "usage_guide": "比SMA更敏感，常用周期：EMA12、EMA26（MACD使用）。",
        "sort_order": 2
    },
    {
        "indicator_key": "WMA",
        "indicator_name": "加权移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "加权移动平均线，对近期数据赋予更大权重。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "WMA值", "type": "float"}
        ],
        "sort_order": 3
    },
    {
        "indicator_key": "HMA",
        "indicator_name": "赫尔移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Hull Moving Average，旨在减少滞后同时保持平滑。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "HMA值", "type": "float"}
        ],
        "usage_guide": "HMA反应更快，适合捕捉趋势转折点。",
        "sort_order": 4
    },
    {
        "indicator_key": "TEMA",
        "indicator_name": "三重指数移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Triple EMA，三重平滑的EMA，进一步减少滞后。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "TEMA值", "type": "float"}
        ],
        "sort_order": 5
    },
    {
        "indicator_key": "DEMA",
        "indicator_name": "双重指数移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Double EMA，双重平滑的EMA，减少滞后。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "DEMA值", "type": "float"}
        ],
        "sort_order": 6
    },
    {
        "indicator_key": "KAMA",
        "indicator_name": "考夫曼自适应移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Kaufman's Adaptive Moving Average，根据市场波动自动调整平滑度。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 10, "min": 1, "max": 100},
            {"key": "fast", "name": "快周期", "type": "int", "default": 2, "min": 1, "max": 20},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 30, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "KAMA值", "type": "float"}
        ],
        "usage_guide": "KAMA在震荡市场更平滑，趋势市场更快速。",
        "sort_order": 7
    },
    {
        "indicator_key": "ZLEMA",
        "indicator_name": "零滞后指数移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Zero Lag EMA，通过重新计算减少EMA的滞后。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "ZLEMA值", "type": "float"}
        ],
        "sort_order": 8
    },
    {
        "indicator_key": "T3",
        "indicator_name": "T3移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Tillson T3 Moving Average，使用序列平滑减少滞后。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 10, "min": 1, "max": 200},
            {"key": "a", "name": "体积因子", "type": "float", "default": 0.7, "min": 0, "max": 1}
        ],
        "output_fields": [
            {"key": "values", "name": "T3值", "type": "float"}
        ],
        "sort_order": 9
    },
    {
        "indicator_key": "VWMA",
        "indicator_name": "成交量加权移动平均线",
        "category": IndicatorCategory.TREND,
        "description": "Volume Weighted Moving Average，用成交量加权的移动平均。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 500}
        ],
        "output_fields": [
            {"key": "values", "name": "VWMA值", "type": "float"}
        ],
        "usage_guide": "成交量大的K线权重更高，更能反映资金流向。",
        "sort_order": 10
    },
    {
        "indicator_key": "BOLL",
        "indicator_name": "布林带",
        "category": IndicatorCategory.TREND,
        "description": "Bollinger Bands，由中轨、上轨、下轨组成的价格通道。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200},
            {"key": "std", "name": "标准差倍数", "type": "float", "default": 2.0, "min": 0.1, "max": 5.0}
        ],
        "output_fields": [
            {"key": "BBL", "name": "下轨", "type": "float", "desc": "Lower Band"},
            {"key": "BBM", "name": "中轨", "type": "float", "desc": "Middle Band"},
            {"key": "BBU", "name": "上轨", "type": "float", "desc": "Upper Band"},
            {"key": "BBB", "name": "带宽", "type": "float", "desc": "Bandwidth"},
            {"key": "BBP", "name": "百分比", "type": "float", "desc": "Percent B"}
        ],
        "default_output": "BBM",
        "usage_guide": "价格触及上轨可能超买，触及下轨可能超卖。带宽收窄可能即将突破。",
        "signal_interpretation": {
            "upper_touch": "价格触及上轨，可能超买",
            "lower_touch": "价格触及下轨，可能超卖",
            "squeeze": "带宽收窄，波动减小",
            "expansion": "带宽扩张，波动增大"
        },
        "sort_order": 20
    },
    {
        "indicator_key": "KC",
        "indicator_name": "肯特纳通道",
        "category": IndicatorCategory.TREND,
        "description": "Keltner Channels，使用ATR构建的价格通道。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200},
            {"key": "scalar", "name": "ATR倍数", "type": "float", "default": 2.0, "min": 0.1, "max": 5.0}
        ],
        "output_fields": [
            {"key": "KCL", "name": "下轨", "type": "float"},
            {"key": "KCB", "name": "中轨", "type": "float"},
            {"key": "KCU", "name": "上轨", "type": "float"}
        ],
        "sort_order": 21
    },
    {
        "indicator_key": "DC",
        "indicator_name": "唐奇安通道",
        "category": IndicatorCategory.TREND,
        "description": "Donchian Channels，由最高价和最低价构成的通道。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "lower_length", "name": "下轨周期", "type": "int", "default": 20, "min": 1, "max": 200},
            {"key": "upper_length", "name": "上轨周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "DCL", "name": "下轨", "type": "float", "desc": "最低价的最高值"},
            {"key": "DCM", "name": "中轨", "type": "float", "desc": "上下轨均值"},
            {"key": "DCU", "name": "上轨", "type": "float", "desc": "最高价的最高值"}
        ],
        "usage_guide": "突破上轨买入，跌破下轨卖出。海龟交易法则常用指标。",
        "sort_order": 22
    },
    {
        "indicator_key": "PSAR",
        "indicator_name": "抛物线指标",
        "category": IndicatorCategory.TREND,
        "description": "Parabolic SAR，用于判断趋势反转点。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "step", "name": "步长", "type": "float", "default": 0.02, "min": 0.001, "max": 0.5},
            {"key": "max_step", "name": "最大步长", "type": "float", "default": 0.2, "min": 0.01, "max": 1.0}
        ],
        "output_fields": [
            {"key": "values", "name": "PSAR值", "type": "float"}
        ],
        "usage_guide": "价格在PSAR上方为多头，下方为空头。PSAR点是止损位。",
        "signal_interpretation": {
            "above_psar": "价格在PSAR上方，多头趋势",
            "below_psar": "价格在PSAR下方，空头趋势",
            "reversal": "价格穿越PSAR，趋势反转"
        },
        "sort_order": 23
    },
    {
        "indicator_key": "TRIX",
        "indicator_name": "三重指数平滑平均线",
        "category": IndicatorCategory.TREND,
        "description": "TRIX是TEMA的变化率，用于过滤价格波动。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 30, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "TRIX值", "type": "float"}
        ],
        "sort_order": 24
    },
    {
        "indicator_key": "VORTEX",
        "indicator_name": "漩涡指标",
        "category": IndicatorCategory.TREND,
        "description": "Vortex Indicator，用于识别趋势的开始和方向。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "VIP", "name": "正向漩涡", "type": "float", "desc": "Positive Vortex"},
            {"key": "VIM", "name": "负向漩涡", "type": "float", "desc": "Negative Vortex"}
        ],
        "usage_guide": "VIP>VIM为多头，VIP<VIM为空头。交叉为转折信号。",
        "sort_order": 25
    },
    {
        "indicator_key": "AROON",
        "indicator_name": "阿隆指标",
        "category": IndicatorCategory.TREND,
        "description": "Aroon Indicator，衡量趋势的强度和方向。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "AROOND", "name": "Aroon Down", "type": "float"},
            {"key": "AROONU", "name": "Aroon Up", "type": "float"},
            {"key": "AROONOSC", "name": "Aroon Oscillator", "type": "float"}
        ],
        "usage_guide": "Aroon Up高表示强势上涨，Aroon Down高表示强势下跌。",
        "sort_order": 26
    },

    # ========== 动量类指标 ==========
    {
        "indicator_key": "MACD",
        "indicator_name": "MACD指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Moving Average Convergence Divergence，指数平滑异同移动平均线。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "fast", "name": "快线周期", "type": "int", "default": 12, "min": 1, "max": 100},
            {"key": "slow", "name": "慢线周期", "type": "int", "default": 26, "min": 1, "max": 200},
            {"key": "signal", "name": "信号线周期", "type": "int", "default": 9, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "MACD_12_26_9", "name": "DIF线", "type": "float", "desc": "快慢线差值"},
            {"key": "MACDs_12_26_9", "name": "DEA线", "type": "float", "desc": "信号线"},
            {"key": "MACDh_12_26_9", "name": "MACD柱", "type": "float", "desc": "柱状图"}
        ],
        "usage_guide": "金叉买入，死叉卖出。零轴上方为多头市场。",
        "signal_interpretation": {
            "golden_cross": "DIF上穿DEA，金叉买入",
            "death_cross": "DIF下穿DEA，死叉卖出",
            "above_zero": "零轴上方，多头市场",
            "below_zero": "零轴下方，空头市场"
        },
        "sort_order": 50
    },
    {
        "indicator_key": "RSI",
        "indicator_name": "相对强弱指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Relative Strength Index，测量价格变动速度和幅度。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "RSI值", "type": "float", "desc": "范围0-100"}
        ],
        "usage_guide": "RSI>70超买，<30超卖。背离是重要反转信号。",
        "signal_interpretation": {
            "overbought": "RSI>70超买",
            "oversold": "RSI<30超卖",
            "bullish_divergence": "价格新低RSI不新低，看涨背离",
            "bearish_divergence": "价格新高RSI不新高，看跌背离"
        },
        "sort_order": 51
    },
    {
        "indicator_key": "STOCH",
        "indicator_name": "随机指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Stochastic Oscillator，衡量收盘价在价格区间中的位置。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "k", "name": "K周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "d", "name": "D周期", "type": "int", "default": 3, "min": 1, "max": 20},
            {"key": "smooth_k", "name": "K平滑", "type": "int", "default": 3, "min": 1, "max": 20}
        ],
        "output_fields": [
            {"key": "STOCHk", "name": "K值", "type": "float", "desc": "快线"},
            {"key": "STOCHd", "name": "D值", "type": "float", "desc": "慢线"}
        ],
        "usage_guide": "K>80超买，K<20超卖。K上穿D买入，K下穿D卖出。",
        "sort_order": 52
    },
    {
        "indicator_key": "STOCHRSI",
        "indicator_name": "随机RSI",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Stochastic RSI，对RSI应用随机指标计算。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "RSI周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "rsi_length", "name": "RSI长度", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "k", "name": "K周期", "type": "int", "default": 3, "min": 1, "max": 20},
            {"key": "d", "name": "D周期", "type": "int", "default": 3, "min": 1, "max": 20}
        ],
        "output_fields": [
            {"key": "STOCHRSIk", "name": "K值", "type": "float"},
            {"key": "STOCHRSId", "name": "D值", "type": "float"}
        ],
        "sort_order": 53
    },
    {
        "indicator_key": "WILLR",
        "indicator_name": "威廉指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Williams %R，衡量超买超卖水平。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "WILLR值", "type": "float", "desc": "范围0到-100"}
        ],
        "usage_guide": "WILLR>-20超买，<-80超卖。注意是负数。",
        "sort_order": 54
    },
    {
        "indicator_key": "MOM",
        "indicator_name": "动量指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Momentum，当前价格与N周期前价格的差值。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 10, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "MOM值", "type": "float"}
        ],
        "sort_order": 55
    },
    {
        "indicator_key": "ROC",
        "indicator_name": "变动率指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Rate of Change，价格变化百分比。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 10, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "ROC值", "type": "float", "desc": "百分比"}
        ],
        "sort_order": 56
    },
    {
        "indicator_key": "CMO",
        "indicator_name": "钱德动量摆动指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Chande Momentum Oscillator，测量动量强度。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "CMO值", "type": "float", "desc": "范围-100到100"}
        ],
        "usage_guide": "CMO>50超买，<-50超卖。",
        "sort_order": 57
    },
    {
        "indicator_key": "UO",
        "indicator_name": "终极指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Ultimate Oscillator，综合三个周期的动量。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 7, "min": 1, "max": 50},
            {"key": "medium", "name": "中周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 28, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "UO值", "type": "float", "desc": "范围0-100"}
        ],
        "usage_guide": "UO>70超买，<30超卖。背离信号更可靠。",
        "sort_order": 58
    },
    {
        "indicator_key": "AO",
        "indicator_name": "动量震荡指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Awesome Oscillator，Bill Williams开发的动量指标。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 5, "min": 1, "max": 50},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 34, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "AO值", "type": "float"}
        ],
        "usage_guide": "AO零轴上方为多头，下方为空头。蝶形信号。",
        "sort_order": 59
    },
    {
        "indicator_key": "APO",
        "indicator_name": "绝对价格震荡指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Absolute Price Oscillator，快慢EMA的差值。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 12, "min": 1, "max": 100},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 26, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "APO值", "type": "float"}
        ],
        "sort_order": 60
    },
    {
        "indicator_key": "PPO",
        "indicator_name": "百分比价格震荡指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Percentage Price Oscillator，类似于MACD但用百分比表示。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 12, "min": 1, "max": 100},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 26, "min": 1, "max": 200},
            {"key": "signal", "name": "信号周期", "type": "int", "default": 9, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "PPO", "name": "PPO值", "type": "float"},
            {"key": "PPOs", "name": "信号线", "type": "float"},
            {"key": "PPOh", "name": "PPO柱", "type": "float"}
        ],
        "sort_order": 61
    },
    {
        "indicator_key": "KST",
        "indicator_name": "确知指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Know Sure Thing，综合多个ROC的动量指标。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "roc1", "name": "ROC1周期", "type": "int", "default": 10, "min": 1, "max": 50},
            {"key": "roc2", "name": "ROC2周期", "type": "int", "default": 15, "min": 1, "max": 50},
            {"key": "roc3", "name": "ROC3周期", "type": "int", "default": 20, "min": 1, "max": 100},
            {"key": "roc4", "name": "ROC4周期", "type": "int", "default": 30, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "KST", "name": "KST线", "type": "float"},
            {"key": "KSTs", "name": "信号线", "type": "float"}
        ],
        "sort_order": 62
    },
    {
        "indicator_key": "TSI",
        "indicator_name": "真实强度指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "True Strength Index，双重平滑动量指标。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 13, "min": 1, "max": 100},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 25, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "TSI值", "type": "float"}
        ],
        "sort_order": 63
    },
    {
        "indicator_key": "DPO",
        "indicator_name": "非趋势价格震荡指标",
        "category": IndicatorCategory.MOMENTUM,
        "description": "Detrended Price Oscillator，去除趋势的价格震荡。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "DPO值", "type": "float"}
        ],
        "sort_order": 64
    },

    # ========== 震荡类指标 ==========
    {
        "indicator_key": "CCI",
        "indicator_name": "顺势指标",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Commodity Channel Index，测量价格与统计平均值的偏差。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "CCI值", "type": "float"}
        ],
        "usage_guide": "CCI>100超买，<-100超卖。",
        "sort_order": 80
    },
    {
        "indicator_key": "MFI",
        "indicator_name": "资金流量指标",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Money Flow Index，结合价格和成交量的RSI。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "MFI值", "type": "float", "desc": "范围0-100"}
        ],
        "usage_guide": "MFI>80超买，<20超卖。与RSI配合使用。",
        "sort_order": 81
    },
    {
        "indicator_key": "BOP",
        "indicator_name": "均衡力量指标",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Balance of Power，测量买卖双方力量。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "BOP值", "type": "float"}
        ],
        "usage_guide": "正值表示买方力量强，负值表示卖方力量强。",
        "sort_order": 82
    },
    {
        "indicator_key": "EFI",
        "indicator_name": "艾尔德力指数",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Elder's Force Index，结合价格变化和成交量。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 13, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "EFI值", "type": "float"}
        ],
        "sort_order": 83
    },
    {
        "indicator_key": "RVI",
        "indicator_name": "相对活力指数",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Relative Vigor Index，衡量收盘价在日内区间的位置。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "RVI", "name": "RVI值", "type": "float"},
            {"key": "RVIs", "name": "信号线", "type": "float"}
        ],
        "sort_order": 84
    },
    {
        "indicator_key": "WMAVE",
        "indicator_name": "波浪指标",
        "category": IndicatorCategory.OSCILLATOR,
        "description": "Wave Trend Oscillator，结合RSI和移动平均。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "channel_length", "name": "通道周期", "type": "int", "default": 10, "min": 1, "max": 100},
            {"key": "avg_length", "name": "平均周期", "type": "int", "default": 21, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "WAVE", "name": "Wave值", "type": "float"},
            {"key": "WAVEs", "name": "信号线", "type": "float"}
        ],
        "sort_order": 85
    },

    # ========== 成交量类指标 ==========
    {
        "indicator_key": "OBV",
        "indicator_name": "能量潮",
        "category": IndicatorCategory.VOLUME,
        "description": "On Balance Volume，根据价格涨跌累积成交量。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "OBV值", "type": "float"}
        ],
        "usage_guide": "OBV上升资金流入，下降资金流出。背离是重要信号。",
        "sort_order": 100
    },
    {
        "indicator_key": "AD",
        "indicator_name": "累积派发线",
        "category": IndicatorCategory.VOLUME,
        "description": "Accumulation/Distribution Line，衡量资金流向。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "AD值", "type": "float"}
        ],
        "sort_order": 101
    },
    {
        "indicator_key": "ADOSC",
        "indicator_name": "累积派发震荡指标",
        "category": IndicatorCategory.VOLUME,
        "description": "Chaikin A/D Oscillator，AD的快慢EMA差值。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 3, "min": 1, "max": 50},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 10, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "ADOSC值", "type": "float"}
        ],
        "sort_order": 102
    },
    {
        "indicator_key": "CMF",
        "indicator_name": "蔡金资金流量",
        "category": IndicatorCategory.VOLUME,
        "description": "Chaikin Money Flow，AD的标准化版本。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "CMF值", "type": "float", "desc": "范围-1到1"}
        ],
        "usage_guide": "CMF>0资金流入，<0资金流出。",
        "sort_order": 103
    },
    {
        "indicator_key": "VWAP",
        "indicator_name": "成交量加权平均价",
        "category": IndicatorCategory.VOLUME,
        "description": "Volume Weighted Average Price，日内成交量加权均价。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "VWAP值", "type": "float"}
        ],
        "usage_guide": "价格在VWAP上方为多头，下方为空头。机构常用。",
        "sort_order": 104
    },
    {
        "indicator_key": "EVWMA",
        "indicator_name": "弹性成交量加权移动平均",
        "category": IndicatorCategory.VOLUME,
        "description": "Elastic Volume Weighted Moving Average。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "EVWMA值", "type": "float"}
        ],
        "sort_order": 105
    },
    {
        "indicator_key": "EOM",
        "indicator_name": "简易波动指标",
        "category": IndicatorCategory.VOLUME,
        "description": "Ease of Movement，衡量价格变动与成交量的关系。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "divisor", "name": "除数", "type": "int", "default": 10000, "min": 1, "max": 100000}
        ],
        "output_fields": [
            {"key": "values", "name": "EOM值", "type": "float"}
        ],
        "sort_order": 106
    },
    {
        "indicator_key": "FI",
        "indicator_name": "力度指数",
        "category": IndicatorCategory.VOLUME,
        "description": "Force Index，价格变化乘以成交量。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 13, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "FI值", "type": "float"}
        ],
        "sort_order": 107
    },
    {
        "indicator_key": "NVI",
        "indicator_name": "负成交量指数",
        "category": IndicatorCategory.VOLUME,
        "description": "Negative Volume Index，成交量减少日的价格累积。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "NVI值", "type": "float"}
        ],
        "sort_order": 108
    },
    {
        "indicator_key": "PVI",
        "indicator_name": "正成交量指数",
        "category": IndicatorCategory.VOLUME,
        "description": "Positive Volume Index，成交量增加日的价格累积。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "PVI值", "type": "float"}
        ],
        "sort_order": 109
    },
    {
        "indicator_key": "PVO",
        "indicator_name": "成交量百分比震荡指标",
        "category": IndicatorCategory.VOLUME,
        "description": "Percentage Volume Oscillator，成交量的百分比震荡。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 12, "min": 1, "max": 100},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 26, "min": 1, "max": 200},
            {"key": "signal", "name": "信号周期", "type": "int", "default": 9, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "PVO", "name": "PVO值", "type": "float"},
            {"key": "PVOs", "name": "信号线", "type": "float"},
            {"key": "PVOh", "name": "PVO柱", "type": "float"}
        ],
        "sort_order": 110
    },
    {
        "indicator_key": "VP",
        "indicator_name": "成交量分布",
        "category": IndicatorCategory.VOLUME,
        "description": "Volume Profile，显示不同价格区间的成交量分布。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "VP值", "type": "float"}
        ],
        "sort_order": 111
    },

    # ========== 波动率类指标 ==========
    {
        "indicator_key": "ATR",
        "indicator_name": "平均真实波幅",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Average True Range，测量市场波动程度。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "ATR值", "type": "float"}
        ],
        "usage_guide": "用于设置止损和判断波动。ATR高波动大，低波动小。",
        "sort_order": 130
    },
    {
        "indicator_key": "NATR",
        "indicator_name": "归一化平均真实波幅",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Normalized ATR，ATR相对于价格的百分比。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "NATR值", "type": "float", "desc": "百分比"}
        ],
        "sort_order": 131
    },
    {
        "indicator_key": "TR",
        "indicator_name": "真实波幅",
        "category": IndicatorCategory.VOLATILITY,
        "description": "True Range，单根K线的真实波幅。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "TR值", "type": "float"}
        ],
        "sort_order": 132
    },
    {
        "indicator_key": "RANGE",
        "indicator_name": "价格区间",
        "category": IndicatorCategory.VOLATILITY,
        "description": "High - Low，最高价与最低价的差。",
        "value_type": IndicatorValueType.SERIES,
        "params": [],
        "output_fields": [
            {"key": "values", "name": "RANGE值", "type": "float"}
        ],
        "sort_order": 133
    },
    {
        "indicator_key": "HV",
        "indicator_name": "历史波动率",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Historical Volatility，收益率的标准差。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 20, "min": 1, "max": 200}
        ],
        "output_fields": [
            {"key": "values", "name": "HV值", "type": "float"}
        ],
        "sort_order": 134
    },
    {
        "indicator_key": "UI",
        "indicator_name": "溃疡指数",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Ulcer Index，衡量下行风险和回撤。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "UI值", "type": "float"}
        ],
        "sort_order": 135
    },
    {
        "indicator_key": "MASS",
        "indicator_name": "梅斯指数",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Mass Index，识别趋势反转。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "fast", "name": "快周期", "type": "int", "default": 9, "min": 1, "max": 50},
            {"key": "slow", "name": "慢周期", "type": "int", "default": 25, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "MASS值", "type": "float"}
        ],
        "usage_guide": "MASS>27预示反转可能。",
        "sort_order": 136
    },
    {
        "indicator_key": "CHOP",
        "indicator_name": "萧普指数",
        "category": IndicatorCategory.VOLATILITY,
        "description": "Choppiness Index，衡量市场是否处于震荡。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "CHOP值", "type": "float", "desc": "范围0-100"}
        ],
        "usage_guide": "CHOP>61.8震荡市，<38.2趋势市。",
        "sort_order": 137
    },

    # ========== 趋势强度指标 ==========
    {
        "indicator_key": "ADX",
        "indicator_name": "平均趋向指数",
        "category": IndicatorCategory.TREND,
        "description": "Average Directional Index，衡量趋势强度。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "lensig", "name": "信号周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "ADX_14", "name": "ADX值", "type": "float"},
            {"key": "DMP_14", "name": "+DI", "type": "float"},
            {"key": "DMN_14", "name": "-DI", "type": "float"}
        ],
        "usage_guide": "ADX>25强趋势，<20无趋势。+DI>-DI多头，反之空头。",
        "signal_interpretation": {
            "strong_trend": "ADX>25强趋势",
            "weak_trend": "ADX<20无趋势或震荡",
            "bullish": "+DI>-DI多头趋势",
            "bearish": "+DI<-DI空头趋势"
        },
        "sort_order": 30
    },
    {
        "indicator_key": "DMP",
        "indicator_name": "正向动向指标",
        "category": IndicatorCategory.TREND,
        "description": "Positive Directional Movement，+DI。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "DMP值", "type": "float"}
        ],
        "sort_order": 31
    },
    {
        "indicator_key": "DMN",
        "indicator_name": "负向动向指标",
        "category": IndicatorCategory.TREND,
        "description": "Negative Directional Movement，-DI。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 14, "min": 1, "max": 100}
        ],
        "output_fields": [
            {"key": "values", "name": "DMN值", "type": "float"}
        ],
        "sort_order": 32
    },
    {
        "indicator_key": "QQE",
        "indicator_name": "量化定性估计",
        "category": IndicatorCategory.TREND,
        "description": "Quantitative Qualitative Estimation，基于RSI的趋势指标。",
        "value_type": IndicatorValueType.MULTI,
        "params": [
            {"key": "length", "name": "RSI周期", "type": "int", "default": 14, "min": 1, "max": 100},
            {"key": "smooth", "name": "平滑周期", "type": "int", "default": 5, "min": 1, "max": 50},
            {"key": "factor", "name": "因子", "type": "float", "default": 4.236, "min": 0.1, "max": 10}
        ],
        "output_fields": [
            {"key": "QQE", "name": "QQE线", "type": "float"},
            {"key": "QQEs", "name": "信号线", "type": "float"}
        ],
        "sort_order": 33
    },
    {
        "indicator_key": "TTM_TREND",
        "indicator_name": "TTM趋势",
        "category": IndicatorCategory.TREND,
        "description": "TTM Trend，John Carter的趋势指标。",
        "value_type": IndicatorValueType.SERIES,
        "params": [
            {"key": "length", "name": "周期", "type": "int", "default": 6, "min": 1, "max": 50}
        ],
        "output_fields": [
            {"key": "values", "name": "TTM值", "type": "float"}
        ],
        "sort_order": 34
    }
]