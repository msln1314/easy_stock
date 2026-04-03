"""
K线数据获取服务

从数据库或外部API获取K线数据，供指标计算使用
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio


class KLineService:
    """
    K线数据获取服务

    支持从多种数据源获取K线数据：
    1. 本地数据库（如果有存储）
    2. 外部行情API（如东方财富、新浪等）
    """

    def __init__(self):
        # TODO: 配置数据源
        self.data_source = "local"  # local / api

    async def get_klines(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "daily",
        limit: int = 100
    ) -> Dict[str, List]:
        """
        获取K线数据

        Args:
            stock_code: 股票代码，如 '000001'
            start_date: 开始日期，如 '2026-01-01'
            end_date: 结束日期，如 '2026-04-03'
            period: 周期 - daily/60min/30min/15min/5min
            limit: 返回数量限制

        Returns:
            K线数据字典:
            {
                'dates': ['2026-01-01', '2026-01-02', ...],
                'open': [10.0, 10.5, ...],
                'close': [10.2, 10.8, ...],
                'high': [10.5, 11.0, ...],
                'low': [9.8, 10.2, ...],
                'volume': [100000, 120000, ...]
            }
        """
        # 如果没有指定日期范围，默认获取最近N条
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            # 根据周期计算需要的起始日期
            days = self._calculate_days_needed(period, limit)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 从数据源获取
        if self.data_source == "local":
            return await self._get_from_local(stock_code, start_date, end_date, period)
        else:
            return await self._get_from_api(stock_code, start_date, end_date, period)

    async def _get_from_local(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str
    ) -> Dict[str, List]:
        """从本地数据库获取K线数据"""
        # TODO: 实现从数据库获取
        # 这里返回模拟数据用于测试
        return self._get_mock_data()

    async def _get_from_api(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        period: str
    ) -> Dict[str, List]:
        """从外部API获取K线数据"""
        # TODO: 实现从行情API获取
        # 例如调用东方财富、新浪等接口
        return self._get_mock_data()

    def _calculate_days_needed(self, period: str, limit: int) -> int:
        """根据周期和数量计算需要的天数"""
        multipliers = {
            "daily": 1.5,  # 日线，考虑节假日
            "60min": 3,
            "30min": 5,
            "15min": 8,
            "5min": 20,
        }
        return int(limit * multipliers.get(period, 1.5))

    def _get_mock_data(self) -> Dict[str, List]:
        """返回模拟数据（用于测试）"""
        import random

        base_price = 12.0
        count = 50

        dates = []
        opens = []
        closes = []
        highs = []
        lows = []
        volumes = []

        current_date = datetime.now() - timedelta(days=count)
        current_price = base_price

        for i in range(count):
            # 跳过周末
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue

            # 随机波动
            change = random.uniform(-0.03, 0.03)
            open_price = current_price
            close_price = current_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = random.randint(500000, 2000000)

            dates.append(current_date.strftime("%Y-%m-%d"))
            opens.append(round(open_price, 2))
            closes.append(round(close_price, 2))
            highs.append(round(high_price, 2))
            lows.append(round(low_price, 2))
            volumes.append(volume)

            current_price = close_price
            current_date += timedelta(days=1)

        return {
            "dates": dates,
            "open": opens,
            "close": closes,
            "high": highs,
            "low": lows,
            "volume": volumes
        }

    async def get_latest_price(self, stock_code: str) -> Optional[float]:
        """获取最新价格"""
        klines = await self.get_klines(stock_code, limit=1)
        if klines["close"]:
            return klines["close"][-1]
        return None


# 单例实例
kline_service = KLineService()