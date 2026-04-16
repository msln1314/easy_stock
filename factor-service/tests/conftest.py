"""
测试 fixtures 和配置
"""
import pytest
import pandas as pd
import numpy as np
from typing import List, Dict


@pytest.fixture
def sample_kline_data() -> List[Dict]:
    """
    提供模拟K线数据用于测试

    生成30天的模拟K线数据
    """
    # 生成模拟数据：收盘价从10元开始，每天波动
    np.random.seed(42)
    base_price = 10.0
    data = []

    for i in range(30):
        change = np.random.uniform(-0.5, 0.5)
        close = base_price + change + i * 0.05  # 轻微上升趋势
        open_price = close - np.random.uniform(0, 0.3)
        high = close + np.random.uniform(0, 0.5)
        low = close - np.random.uniform(0, 0.5)
        volume = np.random.randint(100000, 500000)

        data.append({
            "date": f"202401{i+1:02d}",
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": volume,
            "amount": volume * close
        })
        base_price = close

    return data


@pytest.fixture
def sample_kline_df(sample_kline_data) -> pd.DataFrame:
    """
    提供模拟K线DataFrame用于测试
    """
    return pd.DataFrame(sample_kline_data)


@pytest.fixture
def indicator_service():
    """
    提供IndicatorService实例
    """
    from app.services.indicator_service import IndicatorService
    return IndicatorService()


@pytest.fixture
def factor_service():
    """
    提供FactorService实例
    """
    from app.services.factor_service import FactorService
    return FactorService()


@pytest.fixture
def backtest_service():
    """
    提供BacktestService实例
    """
    from app.services.backtest_service import BacktestService
    return BacktestService()