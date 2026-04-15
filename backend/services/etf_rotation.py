"""
ETF轮动策略核心服务
"""
from typing import List, Dict, Optional
from datetime import date
from loguru import logger

from services.kline_service import kline_service
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator
from utils.rotation_calculator.rsrs import RSRSCalculator
from utils.rotation_calculator.ma_filter import MAFilter
from models.rotation_strategy import RotationStrategy
from models.etf_pool import EtfPool
from models.etf_score import EtfScore
from models.rotation_signal import RotationSignal
from models.rotation_position import RotationPosition


class EtfRotationService:
    """ETF轮动策略服务"""

    async def calculate_scores(
        self,
        strategy: RotationStrategy,
        trade_date: date
    ) -> List[EtfScore]:
        """
        计算ETF池所有ETF的评分并排序

        Args:
            strategy: 轮动策略配置
            trade_date: 交易日期

        Returns:
            按评分降序排列的ETF评分列表
        """
        # 获取ETF池
        etf_pool = await EtfPool.filter(is_active=True).all()

        if not etf_pool:
            logger.warning("ETF池为空，无法计算评分")
            return []

        scores = []
        slope_calc = SlopeMomentumCalculator(strategy.slope_period)
        rsrs_calc = RSRSCalculator(strategy.rsrs_period, strategy.rsrs_z_window)
        ma_filter = MAFilter(strategy.ma_period)

        # 需要的最大数据长度
        max_length = max(
            strategy.slope_period,
            strategy.rsrs_period,
            strategy.rsrs_z_window
        ) + 10

        for etf in etf_pool:
            try:
                # 获取K线数据
                klines = await kline_service.get_klines(
                    etf.code,
                    limit=max_length
                )

                closes = klines['close']
                highs = klines['high']
                lows = klines['low']

                # 计算各指标
                momentum = slope_calc.calculate(closes)
                rsrs = rsrs_calc.calculate(highs, lows)
                ma_val = ma_filter.calculate(closes)

                score = EtfScore(
                    strategy_id=strategy.id,
                    etf_code=etf.code,
                    trade_date=trade_date,
                    slope_value=momentum['slope'],
                    r_squared=momentum['r_squared'],
                    momentum_score=momentum['score'],
                    rsrs_beta=rsrs['beta'],
                    rsrs_z_score=rsrs['z_score'],
                    ma_value=ma_val,
                    close_price=closes[-1]
                )
                scores.append(score)

            except Exception as e:
                logger.error(f"计算ETF {etf.code} 评分失败: {e}")
                continue

        # 按评分降序排序
        scores.sort(key=lambda x: x.momentum_score or 0, reverse=True)

        # 设置排名
        for i, score in enumerate(scores):
            score.rank_position = i + 1

        logger.info(f"完成 {len(scores)} 只ETF评分计算")
        return scores

    async def generate_signals(
        self,
        strategy: RotationStrategy,
        scores: List[EtfScore]
    ) -> List[RotationSignal]:
        """
        根据评分和RSRS信号生成调仓建议

        Args:
            strategy: 轮动策略配置
            scores: ETF评分列表

        Returns:
            调仓信号列表
        """
        signals = []
        trade_date = scores[0].trade_date if scores else date.today()

        # 获取当前持仓
        holdings = await RotationPosition.filter(
            strategy_id=strategy.id,
            status='holding'
        ).all()

        # 检查卖出信号
        for holding in holdings:
            score = next((s for s in scores if s.etf_code == holding.etf_code), None)
            if score:
                # RSRS跌破阈值 + MA过滤确认
                if score.rsrs_z_score and score.rsrs_z_score < float(strategy.rsrs_sell_threshold):
                    if score.close_price and score.ma_value and score.close_price < score.ma_value:
                        signal = RotationSignal(
                            strategy_id=strategy.id,
                            signal_date=trade_date,
                            signal_type='sell',
                            etf_code=holding.etf_code,
                            etf_name=holding.etf_name,
                            action='sell',
                            score=score.momentum_score,
                            rsrs_z=score.rsrs_z_score,
                            price=score.close_price,
                            reason=f"RSRS Z={score.rsrs_z_score:.2f}<{float(strategy.rsrs_sell_threshold)}, "
                                   f"收盘{score.close_price}<MA{strategy.ma_period}={score.ma_value:.2f}"
                        )
                        signals.append(signal)

        # 检查买入信号
        buy_candidates = []
        for score in scores[:strategy.hold_count + 2]:  # 多看几个候选
            # RSRS突破阈值 + MA过滤确认
            if score.rsrs_z_score and score.rsrs_z_score > float(strategy.rsrs_buy_threshold):
                if score.close_price and score.ma_value and score.close_price > score.ma_value:
                    # 不在持仓中
                    if not any(h.etf_code == score.etf_code for h in holdings):
                        buy_candidates.append(score)

        # 计算可买入数量
        sell_count = len([s for s in signals if s.action == 'sell'])
        buy_count = strategy.hold_count - len(holdings) + sell_count

        # 按评分选择买入候选
        for score in buy_candidates[:buy_count]:
            etf = await EtfPool.filter(code=score.etf_code).first()
            signal = RotationSignal(
                strategy_id=strategy.id,
                signal_date=trade_date,
                signal_type='buy',
                etf_code=score.etf_code,
                etf_name=etf.name if etf else '',
                action='buy',
                score=score.momentum_score,
                rsrs_z=score.rsrs_z_score,
                price=score.close_price,
                reason=f"评分排名#{score.rank_position}, "
                       f"RSRS Z={score.rsrs_z_score:.2f}>{float(strategy.rsrs_buy_threshold)}, "
                       f"收盘{score.close_price}>MA{strategy.ma_period}={score.ma_value:.2f}"
            )
            signals.append(signal)

        logger.info(f"生成 {len(signals)} 个调仓信号")
        return signals

    async def save_scores(self, scores: List[EtfScore]) -> int:
        """保存评分记录"""
        saved_count = 0
        for score in scores:
            # 检查是否已存在
            existing = await EtfScore.filter(
                strategy_id=score.strategy_id,
                etf_code=score.etf_code,
                trade_date=score.trade_date
            ).first()

            if not existing:
                await score.save()
                saved_count += 1

        return saved_count

    async def save_signals(self, signals: List[RotationSignal]) -> int:
        """保存信号记录"""
        for signal in signals:
            await signal.save()
        return len(signals)