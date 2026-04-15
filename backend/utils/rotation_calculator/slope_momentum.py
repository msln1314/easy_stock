"""
斜率动量评分计算

核心算法:
动量评分 = slope × R² × 10000

其中:
- slope: 线性回归斜率，反映趋势方向和强度
- R²: 拟合优度，反映趋势稳定性和可信度
"""
import numpy as np
from typing import List, Dict
from scipy import stats


class SlopeMomentumCalculator:
    """斜率动量评分计算器"""

    def __init__(self, period: int = 20):
        """
        Args:
            period: 回归计算窗口周期，默认20日
        """
        self.period = period

    def calculate(self, closes: List[float]) -> Dict:
        """
        计算斜率动量评分

        Args:
            closes: 收盘价序列

        Returns:
            {
                'slope': 斜率值（正为上涨，负为下跌）,
                'r_squared': R²拟合优度（0-1，越接近1越稳定）,
                'score': 动量评分 = slope × R² × 10000
            }
        """
        if len(closes) < self.period:
            return {'slope': None, 'r_squared': None, 'score': None}

        # 取最近N日收盘价
        y = np.array(closes[-self.period:])
        x = np.arange(self.period)

        # 线性回归: y = slope * x + intercept
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2

        # 动量评分 = slope × R² × 10000
        # 放大稳定上涨趋势的得分，过滤不稳定波动
        score = slope * r_squared * 10000

        return {
            'slope': round(slope, 6),
            'r_squared': round(r_squared, 6),
            'score': round(score, 4)
        }