"""
RSRS择时指标计算

阻力支撑相对强度 (Resistance Support Relative Strength):

核心算法:
1. 对 (low, high) 做线性回归: high = β × low + α
2. 计算斜率 β（阻力支撑相对强度）
3. 对 β 做M日Z-score标准化: Z = (β - mean) / std
4. 信号判断:
   - Z > 0.7: 买入信号（突破阻力区）
   - Z < -0.7: 卖出信号（跌破支撑区）
   - 其他: 中性区间
"""
import numpy as np
from typing import List, Dict, Optional
from scipy import stats


class RSRSCalculator:
    """RSRS择时指标计算器"""

    def __init__(self, period: int = 18, z_window: int = 100):
        """
        Args:
            period: 回归窗口周期，默认18日
            z_window: Z-score标准化窗口，默认100日
        """
        self.period = period
        self.z_window = z_window

    def calculate(
        self,
        highs: List[float],
        lows: List[float],
        beta_history: Optional[List[float]] = None
    ) -> Dict:
        """
        计算RSRS指标

        Args:
            highs: 最高价序列
            lows: 最低价序列
            beta_history: 历史beta序列（用于Z-score计算）

        Returns:
            {
                'beta': 当期斜率β（阻力支撑相对强度）,
                'z_score': Z-score标准化值,
                'signal': buy/sell/neutral
            }
        """
        if len(highs) < self.period or len(lows) < self.period:
            return {'beta': None, 'z_score': None, 'signal': 'neutral'}

        # 取最近N日数据
        h = np.array(highs[-self.period:])
        l = np.array(lows[-self.period:])

        # 线性回归: high = beta * low + alpha
        beta, alpha, r_value, p_value, std_err = stats.linregress(l, h)

        # Z-score标准化
        if beta_history and len(beta_history) >= self.z_window:
            recent_betas = np.array(beta_history[-self.z_window:])
            mean_beta = np.mean(recent_betas)
            std_beta = np.std(recent_betas)
            z_score = (beta - mean_beta) / std_beta if std_beta > 0 else 0
        else:
            z_score = 0  # 数据不足时为中性

        # 信号判断
        if z_score > 0.7:
            signal = 'buy'
        elif z_score < -0.7:
            signal = 'sell'
        else:
            signal = 'neutral'

        return {
            'beta': round(beta, 6),
            'z_score': round(z_score, 6),
            'signal': signal
        }