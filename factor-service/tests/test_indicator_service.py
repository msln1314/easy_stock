"""
技术指标计算引擎测试
"""
import pytest
import numpy as np
from app.services.indicator_service import IndicatorService


class TestIndicatorService:
    """IndicatorService 测试类"""

    @pytest.mark.asyncio
    async def test_calculate_ma(self, indicator_service, sample_kline_data):
        """测试 MA 均线计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["MA5", "MA10", "MA20"],
            kline_data=sample_kline_data
        )

        assert result.stock_code == "000001"
        assert len(result.indicators) == 3

        # 验证 MA5 存在且有值
        ma5 = next((i for i in result.indicators if i.indicator_id == "MA5"), None)
        assert ma5 is not None
        assert ma5.value > 0

        # 验证 MA 值在合理范围内
        closes = [d["close"] for d in sample_kline_data[-5:]]
        expected_ma5 = sum(closes) / len(closes)
        assert abs(ma5.value - expected_ma5) < 0.01

    @pytest.mark.asyncio
    async def test_calculate_rsi(self, indicator_service, sample_kline_data):
        """测试 RSI 计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["RSI6", "RSI14"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 2

        rsi6 = next((i for i in result.indicators if i.indicator_id == "RSI6"), None)
        assert rsi6 is not None
        assert 0 <= rsi6.value <= 100  # RSI 在 0-100 范围内

    @pytest.mark.asyncio
    async def test_calculate_macd(self, indicator_service, sample_kline_data):
        """测试 MACD 计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["MACD_DIF", "MACD_DEA", "MACD_HIST"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 3

        dif = next((i for i in result.indicators if i.indicator_id == "MACD_DIF"), None)
        dea = next((i for i in result.indicators if i.indicator_id == "MACD_DEA"), None)
        hist = next((i for i in result.indicators if i.indicator_id == "MACD_HIST"), None)

        assert dif is not None
        assert dea is not None
        assert hist is not None

        # HIST = DIF - DEA
        assert abs(hist.value - (dif.value - dea.value)) < 0.01

    @pytest.mark.asyncio
    async def test_calculate_kdj(self, indicator_service, sample_kline_data):
        """测试 KDJ 计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["KDJ_K", "KDJ_D", "KDJ_J"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 3

        k = next((i for i in result.indicators if i.indicator_id == "KDJ_K"), None)
        d = next((i for i in result.indicators if i.indicator_id == "KDJ_D"), None)
        j = next((i for i in result.indicators if i.indicator_id == "KDJ_J"), None)

        assert k is not None
        assert d is not None
        assert j is not None

        # J = 3K - 2D
        expected_j = 3 * k.value - 2 * d.value
        assert abs(j.value - expected_j) < 0.01

    @pytest.mark.asyncio
    async def test_calculate_boll(self, indicator_service, sample_kline_data):
        """测试布林带计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["BOLL_UP", "BOLL_MID", "BOLL_LOW"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 3

        upper = next((i for i in result.indicators if i.indicator_id == "BOLL_UP"), None)
        middle = next((i for i in result.indicators if i.indicator_id == "BOLL_MID"), None)
        lower = next((i for i in result.indicators if i.indicator_id == "BOLL_LOW"), None)

        assert upper is not None
        assert middle is not None
        assert lower is not None

        # 布林带顺序：上轨 > 中轨 > 下轨
        assert upper.value > middle.value
        assert middle.value > lower.value

    @pytest.mark.asyncio
    async def test_calculate_volume_indicators(self, indicator_service, sample_kline_data):
        """测试成交量相关指标"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["VOL_MA5", "VOL_RATIO"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 2

        vol_ma5 = next((i for i in result.indicators if i.indicator_id == "VOL_MA5"), None)
        vol_ratio = next((i for i in result.indicators if i.indicator_id == "VOL_RATIO"), None)

        assert vol_ma5 is not None
        assert vol_ma5.value > 0

        assert vol_ratio is not None
        assert vol_ratio.value > 0

    @pytest.mark.asyncio
    async def test_calculate_amp(self, indicator_service, sample_kline_data):
        """测试振幅计算"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["AMP"],
            kline_data=sample_kline_data
        )

        assert len(result.indicators) == 1

        amp = result.indicators[0]
        assert amp is not None
        assert amp.value > 0  # 振幅应为正数

    @pytest.mark.asyncio
    async def test_empty_kline_data(self, indicator_service):
        """测试空K线数据的处理"""
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["MA5"],
            kline_data=[]
        )

        assert result.stock_code == "000001"
        assert len(result.indicators) == 0
        assert result.count == 0

    @pytest.mark.asyncio
    async def test_get_indicator_list(self, indicator_service):
        """测试获取指标列表"""
        indicators = indicator_service.get_indicator_list()

        assert len(indicators) > 0
        # 验证包含基本指标
        indicator_ids = [i["indicator_id"] for i in indicators]
        assert "MA5" in indicator_ids
        assert "RSI14" in indicator_ids
        assert "MACD_DIF" in indicator_ids

    @pytest.mark.asyncio
    async def test_rsi_signal_detection(self, indicator_service, sample_kline_data):
        """测试 RSI 信号判断"""
        # 正常范围的 RSI
        result = await indicator_service.calculate_indicators(
            stock_code="000001",
            indicators=["RSI14"],
            kline_data=sample_kline_data
        )

        rsi = result.indicators[0]
        assert rsi.signal in ["超买", "超卖", "中性", ""]

    def test_direct_calculate_ma(self, indicator_service, sample_kline_df):
        """直接测试 calculate_ma 方法"""
        ma5 = indicator_service.calculate_ma(sample_kline_df, 5)
        assert ma5 is not None
        assert ma5 > 0

        ma10 = indicator_service.calculate_ma(sample_kline_df, 10)
        assert ma10 is not None

    def test_direct_calculate_rsi(self, indicator_service, sample_kline_df):
        """直接测试 calculate_rsi 方法"""
        rsi14 = indicator_service.calculate_rsi(sample_kline_df, 14)
        assert rsi14 is not None
        assert 0 <= rsi14 <= 100

    def test_direct_calculate_macd(self, indicator_service, sample_kline_df):
        """直接测试 calculate_macd 方法"""
        macd = indicator_service.calculate_macd(sample_kline_df)
        assert macd["dif"] is not None
        assert macd["dea"] is not None
        assert macd["hist"] is not None

    def test_direct_calculate_kdj(self, indicator_service, sample_kline_df):
        """直接测试 calculate_kdj 方法"""
        kdj = indicator_service.calculate_kdj(sample_kline_df)
        assert kdj["k"] is not None
        assert kdj["d"] is not None
        assert kdj["j"] is not None

    def test_direct_calculate_boll(self, indicator_service, sample_kline_df):
        """直接测试 calculate_boll 方法"""
        boll = indicator_service.calculate_boll(sample_kline_df)
        assert boll["upper"] is not None
        assert boll["middle"] is not None
        assert boll["lower"] is not None
        assert boll["upper"] > boll["middle"] > boll["lower"]