"""
测试 fixtures 和配置
"""
import pytest


@pytest.fixture
def sample_kline_data():
    """提供模拟K线数据"""
    import numpy as np

    np.random.seed(42)
    base_price = 10.0
    data = []

    for i in range(30):
        change = np.random.uniform(-0.5, 0.5)
        close = base_price + change + i * 0.05
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
def trend_service():
    """提供 TrendService 实例"""
    from app.services.trend_service import TrendService
    return TrendService()


@pytest.fixture
def risk_service():
    """提供 RiskService 实例"""
    from app.services.risk_service import RiskService
    return RiskService()


@pytest.fixture
def advice_service():
    """提供 AdviceService 实例"""
    from app.services.advice_service import AdviceService
    return AdviceService()


@pytest.fixture
def model_service():
    """提供 ModelService 实例"""
    from app.services.model_service import ModelService
    return ModelService()