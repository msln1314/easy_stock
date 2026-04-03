"""
指标计算工具

基于 pandas-ta 库计算技术指标

K线数据格式（标准数组格式）:
[
    {'open': 10.0, 'close': 10.2, 'high': 10.5, 'low': 9.8, 'volume': 100000},
    {'open': 10.5, 'close': 10.8, 'high': 11.0, 'low': 10.2, 'volume': 120000},
    ...
]
"""
from typing import Dict, List
import pandas as pd

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False


class IndicatorCalculator:
    """
    指标计算工具（基于 pandas-ta）

    使用方式:
        calculator = IndicatorCalculator()
        result = calculator.calculate('MA', klines, {'period': 5})
    """

    # 指标默认参数
    _DEFAULT_PARAMS = {
        'MA': {'period': 5},
        'EMA': {'period': 12},
        'EXPMA': {'period': 12},
        'BOLL': {'period': 20, 'std_dev': 2.0},
        'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
        'KDJ': {'n': 9, 'm1': 3, 'm2': 3},
        'RSI': {'period': 6},
        'CCI': {'period': 14},
        'VOL_MA': {'period': 5},
        'VOL_RATIO': {'period': 5},
        'ATR': {'period': 14},
        'OBV': {},
        'WILLR': {'period': 14},
    }

    def __init__(self):
        self._register_calculators()

    def _register_calculators(self):
        """注册所有指标计算函数"""
        self._CALCULATORS = {
            'MA': self._calc_ma,
            'EMA': self._calc_ema,
            'EXPMA': self._calc_expma,
            'BOLL': self._calc_boll,
            'MACD': self._calc_macd,
            'KDJ': self._calc_kdj,
            'RSI': self._calc_rsi,
            'CCI': self._calc_cci,
            'VOL_MA': self._calc_vol_ma,
            'VOL_RATIO': self._calc_vol_ratio,
            'ATR': self._calc_atr,
            'OBV': self._calc_obv,
            'WILLR': self._calc_willr,
        }

    def calculate(self, indicator_key: str, klines: List[Dict], params: Dict = None) -> Dict:
        """
        计算指标值

        Args:
            indicator_key: 指标KEY，如 'MA', 'MACD', 'KDJ'
            klines: K线数据列表
            params: 指标参数

        Returns:
            指标计算结果字典
        """
        if indicator_key not in self._CALCULATORS:
            raise ValueError(f"不支持的指标: {indicator_key}")

        calc_func = self._CALCULATORS[indicator_key]

        final_params = self._DEFAULT_PARAMS.get(indicator_key, {}).copy()
        if params:
            final_params.update(params)

        return calc_func(klines, **final_params)

    def list_indicators(self) -> List[str]:
        """列出所有支持的指标"""
        return list(self._CALCULATORS.keys())

    def _to_dataframe(self, klines: List[Dict]) -> pd.DataFrame:
        """将K线列表转换为DataFrame"""
        df = pd.DataFrame(klines)
        # 确保列名小写
        df.columns = df.columns.str.lower()
        return df

    # ==================== 指标计算函数 ====================

    def _calc_ma(self, klines: List[Dict], period: int = 5) -> Dict:
        """计算移动平均线 MA"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            ma = ta.sma(df['close'], length=period)
            values = ma.tolist()
        else:
            # 回退到手动计算
            values = df['close'].rolling(window=period).mean().tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_ema(self, klines: List[Dict], period: int = 12) -> Dict:
        """计算指数移动平均 EMA"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            ema = ta.ema(df['close'], length=period)
            values = ema.tolist()
        else:
            values = df['close'].ewm(span=period, adjust=False).mean().tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_expma(self, klines: List[Dict], period: int = 12) -> Dict:
        """计算 EXPMA（与EMA相同）"""
        return self._calc_ema(klines, period)

    def _calc_boll(self, klines: List[Dict], period: int = 20, std_dev: float = 2.0) -> Dict:
        """计算布林带 BOLL"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            boll = ta.bbands(df['close'], length=period, std=std_dev)
            lower = boll[f'BBL_{period}_{std_dev}'].tolist()
            middle = boll[f'BBM_{period}_{std_dev}'].tolist()
            upper = boll[f'BBU_{period}_{std_dev}'].tolist()
        else:
            middle = df['close'].rolling(window=period).mean().tolist()
            std = df['close'].rolling(window=period).std().tolist()
            upper = [m + std_dev * s if m and s else None for m, s in zip(middle, std)]
            lower = [m - std_dev * s if m and s else None for m, s in zip(middle, std)]

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'latest': {
                'upper': upper[-1],
                'middle': middle[-1],
                'lower': lower[-1]
            }
        }

    def _calc_macd(self, klines: List[Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """计算 MACD 指标"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            dif = macd[f'MACD_{fast}_{slow}_{signal}'].tolist()
            dea = macd[f'MACDs_{fast}_{slow}_{signal}'].tolist()
            macd_bar = macd[f'MACDh_{fast}_{slow}_{signal}'].tolist()
        else:
            ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
            dif = (ema_fast - ema_slow).tolist()
            dea = pd.Series(dif).ewm(span=signal, adjust=False).mean().tolist()
            macd_bar = [(d - de) * 2 for d, de in zip(dif, dea)]

        return {
            'dif': dif,
            'dea': dea,
            'macd_bar': macd_bar,
            'latest': {
                'dif': dif[-1],
                'dea': dea[-1],
                'macd_bar': macd_bar[-1]
            }
        }

    def _calc_kdj(self, klines: List[Dict], n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """计算 KDJ 指标"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            stoch = ta.stoch(df['high'], df['low'], df['close'], k=n, d=m1)
            k_values = stoch[f'STOK_{n}_{m1}_{m2}'].tolist()
            d_values = stoch[f'STOKD_{n}_{m1}_{m2}'].tolist()
            # pandas-ta的stoch和kdj略有不同，这里手动计算j
            j_values = [3 * k - 2 * d if k and d else None for k, d in zip(k_values, d_values)]
        else:
            # 手动计算
            low_n = df['low'].rolling(window=n).min()
            high_n = df['high'].rolling(window=n).max()
            rsv = (df['close'] - low_n) / (high_n - low_n) * 100
            k_values = rsv.ewm(alpha=1/m1, adjust=False).mean().tolist()
            d_values = pd.Series(k_values).ewm(alpha=1/m2, adjust=False).mean().tolist()
            j_values = [3 * k - 2 * d if k and d else None for k, d in zip(k_values, d_values)]

        return {
            'k': k_values,
            'd': d_values,
            'j': j_values,
            'latest': {
                'k': k_values[-1],
                'd': d_values[-1],
                'j': j_values[-1]
            }
        }

    def _calc_rsi(self, klines: List[Dict], period: int = 6) -> Dict:
        """计算 RSI 指标"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            rsi = ta.rsi(df['close'], length=period)
            values = rsi.tolist()
        else:
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            values = (100 - 100 / (1 + rs)).tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_cci(self, klines: List[Dict], period: int = 14) -> Dict:
        """计算 CCI 指标"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            cci = ta.cci(df['high'], df['low'], df['close'], length=period)
            values = cci.tolist()
        else:
            tp = (df['high'] + df['low'] + df['close']) / 3
            ma_tp = tp.rolling(window=period).mean()
            md = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
            values = ((tp - ma_tp) / (0.015 * md)).tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_vol_ma(self, klines: List[Dict], period: int = 5) -> Dict:
        """计算成交量均线"""
        df = self._to_dataframe(klines)
        values = df['volume'].rolling(window=period).mean().tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_vol_ratio(self, klines: List[Dict], period: int = 5) -> Dict:
        """计算量比"""
        df = self._to_dataframe(klines)

        if len(df) < period:
            return {'value': None}

        avg_volume = df['volume'].iloc[-period:].mean()
        current_volume = df['volume'].iloc[-1]
        ratio = current_volume / avg_volume

        return {
            'value': ratio
        }

    def _calc_atr(self, klines: List[Dict], period: int = 14) -> Dict:
        """计算 ATR（平均真实波幅）"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            atr = ta.atr(df['high'], df['low'], df['close'], length=period)
            values = atr.tolist()
        else:
            high = df['high']
            low = df['low']
            close = df['close']
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            values = tr.rolling(window=period).mean().tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_obv(self, klines: List[Dict]) -> Dict:
        """计算 OBV（能量潮）"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            obv = ta.obv(df['close'], df['volume'])
            values = obv.tolist()
        else:
            direction = df['close'].diff().apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
            values = (direction * df['volume']).cumsum().tolist()

        return {
            'values': values,
            'latest': values[-1]
        }

    def _calc_willr(self, klines: List[Dict], period: int = 14) -> Dict:
        """计算 Williams %R"""
        df = self._to_dataframe(klines)

        if HAS_PANDAS_TA:
            willr = ta.willr(df['high'], df['low'], df['close'], length=period)
            values = willr.tolist()
        else:
            high_n = df['high'].rolling(window=period).max()
            low_n = df['low'].rolling(window=period).min()
            values = ((high_n - df['close']) / (high_n - low_n) * -100).tolist()

        return {
            'values': values,
            'latest': values[-1]
        }


# 单例实例
calculator = IndicatorCalculator()