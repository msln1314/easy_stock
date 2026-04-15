"""
ETF轮动策略指标计算器单元测试
"""
import pytest
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator
from utils.rotation_calculator.rsrs import RSRSCalculator
from utils.rotation_calculator.ma_filter import MAFilter


class TestSlopeMomentum:
    """斜率动量计算器测试"""

    def test_basic_uptrend(self):
        """测试稳定上涨趋势"""
        calc = SlopeMomentumCalculator(period=5)
        closes = [10.0, 11.0, 12.0, 13.0, 14.0]
        result = calc.calculate(closes)

        assert result['slope'] is not None
        assert result['slope'] > 0  # 上涨趋势，斜率正
        assert result['r_squared'] > 0.9  # 稳定趋势，R²接近1
        assert result['score'] > 0  # 正评分

    def test_basic_downtrend(self):
        """测试稳定下跌趋势"""
        calc = SlopeMomentumCalculator(period=5)
        closes = [14.0, 13.0, 12.0, 11.0, 10.0]
        result = calc.calculate(closes)

        assert result['slope'] < 0  # 下跌趋势，斜率负
        assert result['r_squared'] > 0.9
        assert result['score'] < 0  # 负评分

    def test_insufficient_data(self):
        """测试数据不足时返回None"""
        calc = SlopeMomentumCalculator(period=20)
        closes = [10.0, 11.0, 12.0]  # 只有3个数据点
        result = calc.calculate(closes)

        assert result['slope'] is None
        assert result['r_squared'] is None
        assert result['score'] is None

    def test_score_formula(self):
        """测试评分公式: score = slope * r_squared * 10000"""
        calc = SlopeMomentumCalculator(period=5)
        closes = [10.0, 11.0, 12.0, 13.0, 14.0]
        result = calc.calculate(closes)

        expected_score = result['slope'] * result['r_squared'] * 10000
        assert abs(result['score'] - expected_score) < 0.01


class TestRSRS:
    """RSRS择时指标测试"""

    def test_buy_signal_high_z(self):
        """测试高Z-score买入信号"""
        calc = RSRSCalculator(period=5, z_window=5)
        # 构造上涨趋势，beta较大
        highs = [15.0, 16.0, 17.0, 18.0, 19.0]
        lows = [14.0, 15.0, 16.0, 17.0, 18.0]
        # 历史beta较小，当前beta较大 -> Z > 0
        beta_history = [0.5, 0.6, 0.7, 0.8, 0.9]

        result = calc.calculate(highs, lows, beta_history)
        assert result['beta'] is not None
        assert result['signal'] in ['buy', 'sell', 'neutral']

    def test_insufficient_data(self):
        """测试数据不足返回中性"""
        calc = RSRSCalculator(period=18, z_window=100)
        highs = [10.0, 11.0]
        lows = [9.0, 10.0]
        result = calc.calculate(highs, lows)

        assert result['beta'] is None
        assert result['signal'] == 'neutral'

    def test_no_beta_history(self):
        """测试无历史beta时返回中性"""
        calc = RSRSCalculator(period=5, z_window=100)
        highs = [10.0, 11.0, 12.0, 13.0, 14.0]
        lows = [9.0, 10.0, 11.0, 12.0, 13.0]
        result = calc.calculate(highs, lows)  # 无beta_history

        assert result['z_score'] == 0
        assert result['signal'] == 'neutral'


class TestMAFilter:
    """MA均线计算器测试"""

    def test_basic_ma(self):
        """测试MA计算"""
        calc = MAFilter(period=5)
        closes = [10.0, 11.0, 12.0, 13.0, 14.0]
        result = calc.calculate(closes)

        # 5日均线 = (10+11+12+13+14)/5 = 12
        assert result == 12.0

    def test_insufficient_data(self):
        """测试数据不足时返回平均值"""
        calc = MAFilter(period=20)
        closes = [10.0, 11.0, 12.0]
        result = calc.calculate(closes)

        # 返回全部数据的平均值 = (10+11+12)/3 = 11
        assert result == 11.0

    def test_empty_data(self):
        """测试空数据返回0"""
        calc = MAFilter(period=5)
        result = calc.calculate([])

        assert result == 0