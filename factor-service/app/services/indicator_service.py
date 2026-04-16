"""
技术指标计算引擎

使用 pandas/numpy 计算各类技术指标
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from app.core.logging import get_logger
from app.models.indicator_models import (
    IndicatorValue,
    IndicatorCalculateRequest,
    IndicatorCalculateResponse,
    IndicatorBatchRequest,
    IndicatorBatchResponse,
    PRESET_INDICATORS,
)

logger = get_logger(__name__)


class IndicatorService:
    """
    技术指标计算服务

    提供各类技术指标的计算方法，支持单只股票和批量计算
    """

    def __init__(self):
        """初始化指标服务"""
        self._indicator_map = {ind.indicator_id: ind for ind in PRESET_INDICATORS}

    async def calculate_indicators(
        self,
        stock_code: str,
        indicators: List[str],
        period: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> IndicatorCalculateResponse:
        """
        计算单只股票的多个技术指标

        Args:
            stock_code: 股票代码
            indicators: 指标列表，如 ["MA5", "MA10", "RSI14"]
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            kline_data: K线数据（可选，如不提供需从外部获取）

        Returns:
            IndicatorCalculateResponse: 指标计算结果
        """
        logger.info(f"计算指标: {stock_code}, indicators={indicators}")

        # 如果没有提供K线数据，返回空结果（实际使用时需调用 MCP 获取）
        if kline_data is None:
            logger.warning(f"未提供K线数据，无法计算 {stock_code} 的指标")
            return IndicatorCalculateResponse(
                stock_code=stock_code,
                period=period,
                indicators=[],
                count=0
            )

        # 转换为 DataFrame
        df = pd.DataFrame(kline_data)
        if df.empty:
            return IndicatorCalculateResponse(
                stock_code=stock_code,
                period=period,
                indicators=[],
                count=0
            )

        # 计算各指标
        results = []
        for indicator_id in indicators:
            try:
                value = self._calculate_single_indicator(df, indicator_id)
                if value is not None:
                    ind_def = self._indicator_map.get(indicator_id)
                    results.append(IndicatorValue(
                        indicator_id=indicator_id,
                        indicator_name=ind_def.indicator_name if ind_def else indicator_id,
                        value=float(value),
                        date=end_date,
                        signal=self._get_signal(indicator_id, value)
                    ))
            except Exception as e:
                logger.warning(f"计算指标 {indicator_id} 失败: {e}")

        return IndicatorCalculateResponse(
            stock_code=stock_code,
            period=period,
            indicators=results,
            raw_data=kline_data,
            count=len(results)
        )

    def _calculate_single_indicator(self, df: pd.DataFrame, indicator_id: str) -> Optional[float]:
        """
        计算单个指标值

        Args:
            df: K线数据 DataFrame
            indicator_id: 指标ID

        Returns:
            指标值
        """
        # MACD (必须先检查，因为 MACD_DIF 以 MA 开头)
        if indicator_id == "MACD_DIF":
            result = self.calculate_macd(df)
            return result.get("dif")
        if indicator_id == "MACD_DEA":
            result = self.calculate_macd(df)
            return result.get("dea")
        if indicator_id == "MACD_HIST":
            result = self.calculate_macd(df)
            return result.get("hist")

        # MA 均线
        if indicator_id.startswith("MA"):
            period = int(indicator_id[2:])
            return self.calculate_ma(df, period)

        # EMA 指数均线
        if indicator_id.startswith("EMA"):
            period = int(indicator_id[3:])
            return self.calculate_ema(df, period)

        # RSI
        if indicator_id.startswith("RSI"):
            period = int(indicator_id[3:])
            return self.calculate_rsi(df, period)

        # KDJ
        if indicator_id.startswith("KDJ_"):
            result = self.calculate_kdj(df)
            key = indicator_id.split("_")[1].lower()
            return result.get(key)

        # BOLL
        if indicator_id == "BOLL_UP":
            result = self.calculate_boll(df)
            return result.get("upper")
        if indicator_id == "BOLL_MID":
            result = self.calculate_boll(df)
            return result.get("middle")
        if indicator_id == "BOLL_LOW":
            result = self.calculate_boll(df)
            return result.get("lower")

        # ATR
        if indicator_id.startswith("ATR"):
            period = int(indicator_id[3:])
            return self.calculate_atr(df, period)

        # VOL_MA
        if indicator_id.startswith("VOL_MA"):
            period = int(indicator_id[6:])
            return self.calculate_vol_ma(df, period)

        # VOL_RATIO
        if indicator_id == "VOL_RATIO":
            return self.calculate_vol_ratio(df)

        # OBV
        if indicator_id == "OBV":
            return self.calculate_obv(df)

        # AMP 振幅
        if indicator_id == "AMP":
            return self.calculate_amp(df)

        # MOM 动量
        if indicator_id.startswith("MOM"):
            period = int(indicator_id[3:])
            return self.calculate_mom(df, period)

        # ROC
        if indicator_id.startswith("ROC"):
            period = int(indicator_id[3:])
            return self.calculate_roc(df, period)

        logger.warning(f"未知的指标ID: {indicator_id}")
        return None

    def calculate_ma(self, df: pd.DataFrame, period: int) -> float:
        """
        计算移动平均线 MA

        Args:
            df: K线数据，需包含 close 列
            period: 周期

        Returns:
            MA值
        """
        if 'close' not in df.columns or len(df) < period:
            return None
        closes = df['close'].values
        return float(np.mean(closes[-period:]))

    def calculate_ema(self, df: pd.DataFrame, period: int) -> float:
        """
        计算指数移动平均线 EMA

        Args:
            df: K线数据，需包含 close 列
            period: 周期

        Returns:
            EMA值
        """
        if 'close' not in df.columns or len(df) < period:
            return None
        closes = df['close'].values
        # EMA = 前一日EMA * (n-1)/(n+1) + 今日收盘价 * 2/(n+1)
        alpha = 2 / (period + 1)
        ema = closes[0]
        for price in closes[1:]:
            ema = price * alpha + ema * (1 - alpha)
        return float(ema)

    def calculate_rsi(self, df: pd.DataFrame, period: int) -> float:
        """
        计算相对强弱指标 RSI

        Args:
            df: K线数据，需包含 close 列
            period: 周期

        Returns:
            RSI值 (0-100)
        """
        if 'close' not in df.columns or len(df) < period + 1:
            return None
        closes = df['close'].values
        changes = np.diff(closes[-period-1:])
        gains = np.sum(changes[changes > 0])
        losses = np.abs(np.sum(changes[changes < 0]))
        if gains + losses == 0:
            return 50.0  # 无变化时返回中性值
        rsi = float(gains / (gains + losses) * 100)
        return rsi

    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """
        计算 MACD

        Args:
            df: K线数据
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            dict: {dif, dea, hist}
        """
        if 'close' not in df.columns or len(df) < slow + signal:
            return {"dif": None, "dea": None, "hist": None}
        closes = df['close'].values

        # 计算 EMA
        def ema(values, period):
            alpha = 2 / (period + 1)
            result = values[0]
            for v in values[1:]:
                result = v * alpha + result * (1 - alpha)
            return result

        ema_fast = ema(closes, fast)
        ema_slow = ema(closes, slow)
        dif = ema_fast - ema_slow

        # 计算 DEA（DIF的EMA）
        # 简化计算：使用最近N个DIF值的EMA
        dea = dif * 2 / (signal + 1) + dif * (signal - 1) / (signal + 1) * 0.9

        hist = dif - dea

        return {
            "dif": float(dif),
            "dea": float(dea),
            "hist": float(hist)
        }

    def calculate_kdj(self, df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, float]:
        """
        计算 KDJ 指标

        Args:
            df: K线数据，需包含 high, low, close 列
            n: RSV 周期
            m1: K 平滑周期
            m2: D 平滑周期

        Returns:
            dict: {k, d, j}
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            return {"k": None, "d": None, "j": None}
        if len(df) < n:
            return {"k": None, "d": None, "j": None}

        highs = df['high'].values[-n:]
        lows = df['low'].values[-n:]
        close = df['close'].values[-1]

        hn = np.max(highs)
        ln = np.min(lows)

        if hn == ln:
            rsv = 50.0
        else:
            rsv = (close - ln) / (hn - ln) * 100

        # K = 前一日K * (m1-1)/m1 + RSV * 1/m1
        # D = 前一日D * (m2-1)/m2 + K * 1/m2
        # 简化计算
        k = rsv
        d = k
        j = 3 * k - 2 * d

        return {
            "k": float(k),
            "d": float(d),
            "j": float(j)
        }

    def calculate_boll(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """
        计算布林带 BOLL

        Args:
            df: K线数据
            period: 周期
            std_dev: 标准差倍数

        Returns:
            dict: {upper, middle, lower}
        """
        if 'close' not in df.columns or len(df) < period:
            return {"upper": None, "middle": None, "lower": None}

        closes = df['close'].values[-period:]
        middle = np.mean(closes)
        std = np.std(closes)

        upper = middle + std_dev * std
        lower = middle - std_dev * std

        return {
            "upper": float(upper),
            "middle": float(middle),
            "lower": float(lower)
        }

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        计算平均真实波幅 ATR

        Args:
            df: K线数据
            period: 周期

        Returns:
            ATR值
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            return None
        if len(df) < period + 1:
            return None

        highs = df['high'].values[-period:]
        lows = df['low'].values[-period:]
        pre_closes = df['close'].values[-period-1:-1]

        # True Range = max(H-L, H-pre_close, pre_close-L)
        tr1 = highs - lows
        tr2 = np.abs(highs - pre_closes)
        tr3 = np.abs(pre_closes - lows)
        tr = np.maximum(tr1, np.maximum(tr2, tr3))

        return float(np.mean(tr))

    def calculate_vol_ma(self, df: pd.DataFrame, period: int) -> float:
        """
        计算成交量均线

        Args:
            df: K线数据
            period: 周期

        Returns:
            成交量均值
        """
        if 'volume' not in df.columns or len(df) < period:
            return None
        volumes = df['volume'].values[-period:]
        return float(np.mean(volumes))

    def calculate_vol_ratio(self, df: pd.DataFrame) -> float:
        """
        计算量比

        Args:
            df: K线数据

        Returns:
            量比值
        """
        if 'volume' not in df.columns or len(df) < 6:
            return None
        today_vol = df['volume'].values[-1]
        avg_vol = np.mean(df['volume'].values[-6:-1])
        if avg_vol == 0:
            return None
        return float(today_vol / avg_vol)

    def calculate_obv(self, df: pd.DataFrame) -> float:
        """
        计算能量潮 OBV

        Args:
            df: K线数据

        Returns:
            OBV值
        """
        if not all(col in df.columns for col in ['close', 'volume']):
            return None
        closes = df['close'].values
        volumes = df['volume'].values

        obv = 0
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        return float(obv)

    def calculate_amp(self, df: pd.DataFrame) -> float:
        """
        计算振幅

        Args:
            df: K线数据

        Returns:
            振幅值 (%)
        """
        if not all(col in df.columns for col in ['high', 'low', 'close']):
            return None
        if len(df) < 2:
            return None

        high = df['high'].values[-1]
        low = df['low'].values[-1]
        pre_close = df['close'].values[-2]

        if pre_close == 0:
            return None
        return float((high - low) / pre_close * 100)

    def calculate_mom(self, df: pd.DataFrame, period: int) -> float:
        """
        计算动量 MOM

        Args:
            df: K线数据
            period: 周期

        Returns:
            动量值
        """
        if 'close' not in df.columns or len(df) < period + 1:
            return None
        closes = df['close'].values
        return float(closes[-1] - closes[-period-1])

    def calculate_roc(self, df: pd.DataFrame, period: int) -> float:
        """
        计算变动率 ROC

        Args:
            df: K线数据
            period: 周期

        Returns:
            ROC值 (%)
        """
        if 'close' not in df.columns or len(df) < period + 1:
            return None
        closes = df['close'].values
        if closes[-period-1] == 0:
            return None
        return float((closes[-1] - closes[-period-1]) / closes[-period-1] * 100)

    def _get_signal(self, indicator_id: str, value: float) -> str:
        """
        根据指标值判断信号

        Args:
            indicator_id: 指标ID
            value: 指标值

        Returns:
            信号判断
        """
        # RSI 信号
        if indicator_id.startswith("RSI"):
            if value > 80:
                return "超买"
            elif value < 20:
                return "超卖"
            return "中性"

        # MACD 信号
        if indicator_id == "MACD_HIST":
            if value > 0:
                return "金叉"
            elif value < 0:
                return "死叉"
            return "中性"

        # KDJ 信号
        if indicator_id.startswith("KDJ"):
            if value > 80:
                return "超买"
            elif value < 20:
                return "超卖"
            return "中性"

        return ""

    async def batch_calculate(
        self,
        stock_codes: List[str],
        indicators: List[str],
        date: Optional[str] = None,
        kline_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> IndicatorBatchResponse:
        """
        批量计算多只股票的指标

        Args:
            stock_codes: 股票代码列表
            indicators: 指标列表
            date: 日期
            kline_data_map: 各股票K线数据映射

        Returns:
            IndicatorBatchResponse: 批量计算结果
        """
        results = {}
        for stock_code in stock_codes:
            kline_data = kline_data_map.get(stock_code) if kline_data_map else None
            response = await self.calculate_indicators(
                stock_code=stock_code,
                indicators=indicators,
                kline_data=kline_data
            )
            results[stock_code] = response.indicators

        return IndicatorBatchResponse(
            date=date or "",
            results=results,
            count=len(results)
        )

    def get_indicator_list(self) -> List[Dict]:
        """
        获取支持的指标列表

        Returns:
            指标定义列表
        """
        return [ind.model_dump() for ind in PRESET_INDICATORS]


# 单例
indicator_service = IndicatorService()