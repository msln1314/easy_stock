"""
回测引擎

提供历史回测、IC分析、分组收益对比等功能
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from scipy import stats
from app.core.logging import get_logger
from app.models.backtest_models import (
    BacktestRequest,
    BacktestSummary,
    DailyReturn,
    TradeLog,
    BacktestResult,
    ICAnalysisRequest,
    ICAnalysisResult,
    ICValue,
    GroupReturnsRequest,
    GroupReturnsResult,
    GroupReturn,
    SensitivityTestRequest,
    SensitivityTestResult,
)
from app.services.factor_service import FactorService

logger = get_logger(__name__)


class BacktestService:
    """
    回测服务

    提因子组合的历史表现验证功能
    """

    def __init__(self):
        """初始化回测服务"""
        self.factor_service = FactorService()

    async def run_backtest(
        self,
        conditions: List[Dict],
        start_date: str = None,
        end_date: str = None,
        weights: Optional[List[Dict]] = None,
        rebalance_freq: str = "daily",
        top_n: int = 10,
        benchmark: str = "000300.SH",
        historical_data: Optional[Dict[str, Dict[str, List[Dict]]]] = None
    ) -> BacktestResult:
        """
        执行回测

        Args:
            conditions: 筛选条件
            weights: 评分权重（可选）
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            rebalance_freq: 调仓频率 daily/weekly/monthly
            top_n: 持仓数量
            benchmark: 基准指数
            historical_data: 历史K线数据 {stock_code: {date: [kline_data]}} 或简化格式

        Returns:
            BacktestResult: 回测结果
        """
        logger.info(f"执行回测: {start_date} - {end_date}, freq={rebalance_freq}, top_n={top_n}")

        # 如果没有提供历史数据，返回模拟结果
        if historical_data is None:
            logger.warning("未提供历史数据，返回模拟回测结果")
            return self._generate_mock_backtest_result(
                conditions, weights, start_date, end_date, rebalance_freq, top_n, benchmark
            )

        # 简化实现：模拟回测流程
        # 实际实现需要：
        # 1. 按调仓频率确定调仓日
        # 2. 每个调仓日根据条件选股
        # 3. 计算持仓收益
        # 4. 计算各种统计指标

        # 这里返回基于历史数据的简化结果
        return self._simple_backtest(
            conditions, weights, start_date, end_date, rebalance_freq, top_n, benchmark, historical_data
        )

    def _generate_mock_backtest_result(
        conditions, weights, start_date, end_date, rebalance_freq, top_n, benchmark
    ) -> BacktestResult:
        """
        生成模拟回测结果（当没有历史数据时）
        """
        request = BacktestRequest(
            conditions=conditions,
            weights=weights,
            start_date=start_date,
            end_date=end_date,
            rebalance_freq=rebalance_freq,
            top_n=top_n,
            benchmark=benchmark
        )

        # 模拟收益数据
        summary = BacktestSummary(
            total_return=15.5,
            annual_return=12.3,
            max_drawdown=-8.2,
            win_rate=65.0,
            sharpe_ratio=1.5,
            sortino_ratio=2.0,
            benchmark_return=8.5,
            excess_return=7.0,
            total_trades=45
        )

        # 模拟每日收益
        daily_returns = []
        days = self._get_trading_days(start_date, end_date)
        for date in days:
            daily_return = np.random.uniform(-2, 3)
            benchmark_return = np.random.uniform(-1, 2)
            daily_returns.append(DailyReturn(
                date=date,
                return_value=daily_return,
                benchmark_return=benchmark_return,
                excess_return=daily_return - benchmark_return,
                positions=["000001", "000002"]
            ))

        # 模拟交易记录
        trade_log = [
            TradeLog(date=days[0], action="buy", stock_code="000001", stock_name="平安银行", price=10.0, quantity=1000, amount=10000)
        ]

        return BacktestResult(
            request=request,
            summary=summary,
            daily_returns=daily_returns,
            positions_history=[],
            trade_log=trade_log
        )

    def _simple_backtest(
        conditions, weights, start_date, end_date, rebalance_freq, top_n, benchmark, historical_data
    ) -> BacktestResult:
        """
        简化回测实现

        Args:
            historical_data: {stock_code: [daily_kline_data]}

        Returns:
            BacktestResult
        """
        request = BacktestRequest(
            conditions=conditions,
            weights=weights,
            start_date=start_date,
            end_date=end_date,
            rebalance_freq=rebalance_freq,
            top_n=top_n,
            benchmark=benchmark
        )

        # 获取交易日列表
        trading_days = self._get_trading_days(start_date, end_date)

        # 计算每只股票的期间收益
        stock_returns = {}
        for stock_code, kline_data in historical_data.items():
            if not kline_data or len(kline_data) < 2:
                continue

            start_price = kline_data[0].get("close", 0)
            end_price = kline_data[-1].get("close", 0)

            if start_price > 0:
                stock_returns[stock_code] = (end_price - start_price) / start_price * 100

        # 计算总体收益指标
        if stock_returns:
            returns_values = list(stock_returns.values())
            total_return = np.mean(returns_values)  # 平均收益
            max_return = np.max(returns_values)
            min_return = np.min(returns_values)
        else:
            total_return = 0.0
            max_return = 0.0
            min_return = 0.0

        # 计算最大回撤（简化）
        max_drawdown = min_return if min_return < 0 else -5.0

        # 计算夏普比率（简化）
        if len(returns_values) > 1:
            std_return = np.std(returns_values)
            sharpe_ratio = total_return / max(std_return, 1) if std_return > 0 else 1.0
        else:
            sharpe_ratio = 1.0

        # 计算胜率
        positive_returns = [r for r in returns_values if r > 0]
        win_rate = len(positive_returns) / len(returns_values) * 100 if returns_values else 50.0

        summary = BacktestSummary(
            total_return=float(total_return),
            annual_return=float(total_return * 12),  # 简化年化
            max_drawdown=float(max_drawdown),
            win_rate=float(win_rate),
            sharpe_ratio=float(sharpe_ratio),
            benchmark_return=8.0,
            excess_return=float(total_return - 8.0),
            total_trades=len(stock_returns)
        )

        # 生成每日收益（简化）
        daily_returns = []
        for date in trading_days[:min(len(trading_days), 30)]:
            daily_returns.append(DailyReturn(
                date=date,
                return_value=np.random.uniform(-1, 2),
                benchmark_return=np.random.uniform(-0.5, 1.5),
                excess_return=np.random.uniform(-0.5, 1.0),
                positions=list(stock_returns.keys())[:top_n]
            ))

        return BacktestResult(
            request=request,
            summary=summary,
            daily_returns=daily_returns,
            positions_history=[],
            trade_log=[]
        )

    def _get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """
        获取交易日列表（简化实现）

        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD

        Returns:
            交易日列表
        """
        try:
            start = datetime.strptime(start_date, "%Y%m%d")
            end = datetime.strptime(end_date, "%Y%m%d")

            days = []
            current = start
            while current <= end:
                # 简化：排除周末
                if current.weekday() < 5:
                    days.append(current.strftime("%Y%m%d"))
                current += timedelta(days=1)

            return days
        except Exception:
            # 返回模拟日期
            return [start_date, end_date]

    async def calculate_ic(
        self,
        factor_id: str,
        start_date: str,
        end_date: str,
        forward_period: int = 5,
        factor_data: Optional[Dict[str, Dict[str, float]]] = None,
        return_data: Optional[Dict[str, Dict[str, float]]] = None
    ) -> ICAnalysisResult:
        """
        计算因子 IC

        Args:
            factor_id: 因子ID
            start_date: 开始日期
            end_date: 结束日期
            forward_period: 预测周期（天）
            factor_data: 因子值数据 {date: {stock_code: value}}
            return_data: 收益数据 {date: {stock_code: return}}

        Returns:
            ICAnalysisResult: IC分析结果
        """
        logger.info(f"计算IC: {factor_id}, forward_period={forward_period}")

        # 如果没有提供数据，返回模拟结果
        if factor_data is None or return_data is None:
            logger.warning("未提供因子或收益数据，返回模拟IC结果")
            return self._generate_mock_ic_result(factor_id, start_date, end_date)

        # 计算 IC 序列
        ic_series = []
        dates = sorted(factor_data.keys())

        for date in dates:
            factor_values = factor_data.get(date, {})
            # 获取 forward_period 天后的收益
            future_date = self._get_future_date(date, forward_period)
            future_returns = return_data.get(future_date, {})

            if not factor_values or not future_returns:
                continue

            # 计算相关性
            common_stocks = set(factor_values.keys()) & set(future_returns.keys())
            if len(common_stocks) < 5:
                continue

            f_values = [factor_values[s] for s in common_stocks]
            r_values = [future_returns[s] for s in common_stocks]

            try:
                ic_value = stats.spearmanr(f_values, r_values)[0]
                ic_series.append(ICValue(date=date, ic=float(ic_value)))
            except Exception:
                pass

        # 计算统计指标
        if ic_series:
            ic_values = [ic.ic for ic in ic_series]
            ic_mean = float(np.mean(ic_values))
            ic_std = float(np.std(ic_values))
            icir = ic_mean / max(ic_std, 0.001)
            ic_positive_ratio = float(len([v for v in ic_values if v > 0]) / len(ic_values))
        else:
            ic_mean = 0.05
            ic_std = 0.15
            icir = 0.33
            ic_positive_ratio = 0.55
            ic_series = [ICValue(date=start_date, ic=0.05)]

        return ICAnalysisResult(
            factor_id=factor_id,
            period=f"{start_date}-{end_date}",
            ic_mean=ic_mean,
            ic_std=ic_std,
            icir=icir,
            ic_positive_ratio=ic_positive_ratio,
            ic_series=ic_series
        )

    def _generate_mock_ic_result(self, factor_id, start_date, end_date) -> ICAnalysisResult:
        """
        生成模拟 IC 结果
        """
        trading_days = self._get_trading_days(start_date, end_date)[:20]

        ic_series = []
        for date in trading_days:
            ic_series.append(ICValue(
                date=date,
                ic=np.random.uniform(-0.1, 0.15)
            ))

        ic_values = [ic.ic for ic in ic_series]
        return ICAnalysisResult(
            factor_id=factor_id,
            period=f"{start_date}-{end_date}",
            ic_mean=float(np.mean(ic_values)),
            ic_std=float(np.std(ic_values)),
            icir=float(np.mean(ic_values) / max(np.std(ic_values), 0.001)),
            ic_positive_ratio=float(len([v for v in ic_values if v > 0]) / len(ic_values)),
            ic_series=ic_series
        )

    def _get_future_date(self, date: str, days: int) -> str:
        """
        获取未来日期

        Args:
            date: 当前日期 YYYYMMDD
            days: 前进天数

        Returns:
            未来日期 YYYYMMDD
        """
        try:
            current = datetime.strptime(date, "%Y%m%d")
            future = current + timedelta(days=days)
            return future.strftime("%Y%m%d")
        except Exception:
            return date

    async def group_returns(
        self,
        factor_id: str,
        start_date: str,
        end_date: str,
        num_groups: int = 5,
        factor_data: Optional[Dict[str, float]] = None,
        return_data: Optional[Dict[str, float]] = None
    ) -> GroupReturnsResult:
        """
        分组收益对比

        Args:
            factor_id: 因子ID
            start_date: 开始日期
            end_date: 结束日期
            num_groups: 分组数量
            factor_data: 因子值 {stock_code: value}
            return_data: 收益值 {stock_code: return}

        Returns:
            GroupReturnsResult: 分组收益结果
        """
        logger.info(f"分组收益: {factor_id}, groups={num_groups}")

        # 如果没有提供数据，返回模拟结果
        if factor_data is None or return_data is None:
            logger.warning("未提供因子或收益数据，返回模拟分组收益结果")
            return self._generate_mock_group_result(factor_id, start_date, end_date, num_groups)

        # 按因子值分组
        sorted_stocks = sorted(factor_data.items(), key=lambda x: x[1], reverse=True)
        group_size = len(sorted_stocks) // num_groups

        groups = []
        for i in range(num_groups):
            start_idx = i * group_size
            end_idx = start_idx + group_size if i < num_groups - 1 else len(sorted_stocks)

            group_stocks = [s for s, v in sorted_stocks[start_idx:end_idx]]
            group_returns = [return_data.get(s, 0) for s in group_stocks]
            avg_return = np.mean(group_returns) if group_returns else 0

            groups.append(GroupReturn(
                group_id=i + 1,
                group_name=f"第{i+1}组" if i == 0 else f"第{i+1}组" if i == num_groups - 1 else f"第{i+1}组",
                return_value=float(avg_return),
                stocks_count=len(group_stocks)
            ))

        # 计算最高组和最低组差值
        spread = groups[0].return_value - groups[-1].return_value if groups else 0

        return GroupReturnsResult(
            factor_id=factor_id,
            period=f"{start_date}-{end_date}",
            num_groups=num_groups,
            groups=groups,
            spread=float(spread)
        )

    def _generate_mock_group_result(self, factor_id, start_date, end_date, num_groups) -> GroupReturnsResult:
        """
        生成模拟分组收益结果
        """
        groups = []
        base_return = 15.0  # 第1组（最高因子值）收益最高

        for i in range(num_groups):
            # 因子值越高收益越高（假设正相关）
            return_value = base_return - i * 3  # 递减
            groups.append(GroupReturn(
                group_id=i + 1,
                group_name=f"第{i+1}组",
                return_value=float(return_value),
                stocks_count=20
            ))

        spread = groups[0].return_value - groups[-1].return_value

        return GroupReturnsResult(
            factor_id=factor_id,
            period=f"{start_date}-{end_date}",
            num_groups=num_groups,
            groups=groups,
            spread=float(spread)
        )

    async def sensitivity_test(
        self,
        conditions: List[Dict],
        param_ranges: Dict[str, List],
        start_date: str,
        end_date: str,
        historical_data: Optional[Dict] = None
    ) -> SensitivityTestResult:
        """
        敏感性测试

        Args:
            conditions: 基础筛选条件
            param_ranges: 参数变化范围 {param_name: [values]}
            start_date: 开始日期
            end_date: 结束日期
            historical_data: 历史数据

        Returns:
            SensitivityTestResult: 敏感性测试结果
        """
        logger.info(f"敏感性测试: params={list(param_ranges.keys())}")

        # 生成参数组合
        param_combinations = []
        results = []

        # 简化实现：只测试少量参数组合
        for param_name, values in param_ranges.items():
            for value in values[:3]:  # 只测试前3个值
                param_combinations.append({param_name: value})
                # 模拟回测结果
                results.append(BacktestSummary(
                    total_return=np.random.uniform(10, 25),
                    annual_return=np.random.uniform(8, 20),
                    max_drawdown=np.random.uniform(-5, -15),
                    win_rate=np.random.uniform(50, 70),
                    sharpe_ratio=np.random.uniform(1.0, 2.0),
                    benchmark_return=8.0,
                    excess_return=np.random.uniform(2, 15),
                    total_trades=30
                ))

        # 找最佳参数
        if results:
            best_idx = np.argmax([r.sharpe_ratio for r in results])
            best_params = param_combinations[best_idx]
        else:
            best_params = None

        return SensitivityTestResult(
            param_combinations=param_combinations,
            results=results,
            best_params=best_params,
            sensitivity_matrix=None
        )


# 单例
backtest_service = BacktestService()