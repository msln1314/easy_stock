"""
MA均线过滤计算

用于二次确认买卖信号:
- 买入确认: 收盘价 > MA
- 卖出确认: 收盘价 < MA
"""
from typing import List


class MAFilter:
    """MA均线计算器"""

    def __init__(self, period: int = 20):
        """
        Args:
            period: 均线周期，默认20日
        """
        self.period = period

    def calculate(self, closes: List[float]) -> float:
        """
        计算MA均线值

        Args:
            closes: 收盘价序列

        Returns:
            MA均线值（最近period日的平均值）
        """
        if len(closes) < self.period:
            # 数据不足时返回全部数据的平均值
            return sum(closes) / len(closes) if closes else 0

        # 取最近N日收盘价计算平均值
        recent_closes = closes[-self.period:]
        return sum(recent_closes) / self.period