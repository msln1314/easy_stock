"""
回测引擎测试
"""
import pytest
import numpy as np
from app.services.backtest_service import BacktestService, backtest_service


class TestBacktestService:
    """BacktestService 测试类"""

    @pytest.mark.asyncio
    async def test_run_backtest_mock(self, backtest_service):
        """测试模拟回测（无历史数据）"""
        conditions = [
            {"factor_id": "RSI14", "operator": "lt", "value": 70}
        ]

        result = await backtest_service.run_backtest(
            conditions=conditions,
            start_date="20240101",
            end_date="20240331",
            rebalance_freq="daily",
            top_n=10
        )

        assert result.request.start_date == "20240101"
        assert result.request.end_date == "20240331"
        assert result.summary.total_return is not None
        assert result.summary.sharpe_ratio is not None
        assert len(result.daily_returns) > 0

    @pytest.mark.asyncio
    async def test_run_backtest_with_data(self, backtest_service, sample_kline_data):
        """测试带数据的回测"""
        conditions = [
            {"factor_id": "MA5", "operator": "gt", "value": 0}
        ]

        # 构造历史数据
        historical_data = {
            "000001": sample_kline_data,
            "000002": sample_kline_data,
            "000003": sample_kline_data
        }

        result = await backtest_service.run_backtest(
            conditions=conditions,
            start_date="20240101",
            end_date="20240131",
            rebalance_freq="daily",
            top_n=5,
            historical_data=historical_data
        )

        assert result.summary.total_return is not None
        assert result.summary.win_rate >= 0
        assert result.summary.win_rate <= 100

    @pytest.mark.asyncio
    async def test_run_backtest_weekly_rebalance(self, backtest_service):
        """测试周调仓频率"""
        conditions = [{"factor_id": "RSI14", "operator": "lt", "value": 80}]

        result = await backtest_service.run_backtest(
            conditions=conditions,
            start_date="20240101",
            end_date="20240331",
            rebalance_freq="weekly",
            top_n=10
        )

        assert result.request.rebalance_freq == "weekly"

    @pytest.mark.asyncio
    async def test_run_backtest_monthly_rebalance(self, backtest_service):
        """测试月调仓频率"""
        conditions = [{"factor_id": "RSI14", "operator": "lt", "value": 80}]

        result = await backtest_service.run_backtest(
            conditions=conditions,
            start_date="20240101",
            end_date="20240630",
            rebalance_freq="monthly",
            top_n=10
        )

        assert result.request.rebalance_freq == "monthly"

    @pytest.mark.asyncio
    async def test_calculate_ic_mock(self, backtest_service):
        """测试 IC 计算（模拟数据）"""
        result = await backtest_service.calculate_ic(
            factor_id="RSI14",
            start_date="20240101",
            end_date="20240331",
            forward_period=5
        )

        assert result.factor_id == "RSI14"
        assert result.ic_mean is not None
        assert result.ic_std is not None
        assert result.icir is not None
        assert result.ic_positive_ratio >= 0
        assert result.ic_positive_ratio <= 1
        assert len(result.ic_series) > 0

    @pytest.mark.asyncio
    async def test_calculate_ic_with_data(self, backtest_service):
        """测试带数据的 IC 计算"""
        # 构造因子数据
        factor_data = {
            "20240101": {"000001": 65, "000002": 45, "000003": 55},
            "20240102": {"000001": 60, "000002": 50, "000003": 58}
        }

        # 构造收益数据
        return_data = {
            "20240106": {"000001": 2.0, "000002": -1.0, "000003": 1.5},
            "20240107": {"000001": 1.8, "000002": -0.5, "000003": 1.2}
        }

        result = await backtest_service.calculate_ic(
            factor_id="RSI14",
            start_date="20240101",
            end_date="20240131",
            forward_period=5,
            factor_data=factor_data,
            return_data=return_data
        )

        assert result.factor_id == "RSI14"
        assert len(result.ic_series) > 0

    @pytest.mark.asyncio
    async def test_group_returns_mock(self, backtest_service):
        """测试分组收益（模拟数据）"""
        result = await backtest_service.group_returns(
            factor_id="RSI14",
            start_date="20240101",
            end_date="20240331",
            num_groups=5
        )

        assert result.factor_id == "RSI14"
        assert result.num_groups == 5
        assert len(result.groups) == 5
        assert result.spread is not None

        # 验证分组顺序（第1组收益应最高）
        for i, group in enumerate(result.groups):
            assert group.group_id == i + 1
            assert group.stocks_count > 0

    @pytest.mark.asyncio
    async def test_group_returns_with_data(self, backtest_service):
        """测试带数据的分组收益"""
        factor_data = {
            "000001": 65,
            "000002": 45,
            "000003": 55,
            "000004": 70,
            "000005": 40,
            "000006": 60,
            "000007": 50,
            "000008": 75,
            "000009": 35,
            "000010": 80
        }

        return_data = {
            "000001": 2.0,
            "000002": -1.0,
            "000003": 1.5,
            "000004": 3.0,
            "000005": -2.0,
            "000006": 2.5,
            "000007": 0.5,
            "000008": 4.0,
            "000009": -3.0,
            "000010": 5.0
        }

        result = await backtest_service.group_returns(
            factor_id="RSI14",
            start_date="20240101",
            end_date="20240131",
            num_groups=5,
            factor_data=factor_data,
            return_data=return_data
        )

        assert len(result.groups) == 5
        # 第1组（因子值最高）应该收益最高
        assert result.groups[0].return_value > result.groups[-1].return_value

    @pytest.mark.asyncio
    async def test_group_returns_different_num_groups(self, backtest_service):
        """测试不同分组数量"""
        for num_groups in [3, 5, 10]:
            result = await backtest_service.group_returns(
                factor_id="RSI14",
                start_date="20240101",
                end_date="20240331",
                num_groups=num_groups
            )

            assert len(result.groups) == num_groups

    @pytest.mark.asyncio
    async def test_sensitivity_test(self, backtest_service):
        """测试敏感性分析"""
        conditions = [{"factor_id": "RSI14", "operator": "lt", "value": 70}]

        param_ranges = {
            "value": [60, 70, 80]
        }

        result = await backtest_service.sensitivity_test(
            conditions=conditions,
            param_ranges=param_ranges,
            start_date="20240101",
            end_date="20240331"
        )

        assert len(result.param_combinations) > 0
        assert len(result.results) > 0
        assert result.best_params is not None

    @pytest.mark.asyncio
    async def test_sensitivity_test_multiple_params(self, backtest_service):
        """测试多参数敏感性分析"""
        conditions = [{"factor_id": "RSI14", "operator": "lt", "value": 70}]

        param_ranges = {
            "value": [60, 70, 80],
            "top_n": [5, 10, 15]
        }

        result = await backtest_service.sensitivity_test(
            conditions=conditions,
            param_ranges=param_ranges,
            start_date="20240101",
            end_date="20240331"
        )

        assert len(result.results) > 0

    def test_get_trading_days(self, backtest_service):
        """测试获取交易日"""
        days = backtest_service._get_trading_days("20240101", "20240110")

        assert len(days) > 0
        assert days[0] == "20240101"
        # 应排除周末
        assert len(days) <= 10

    def test_get_future_date(self, backtest_service):
        """测试获取未来日期"""
        future = backtest_service._get_future_date("20240101", 5)
        assert future == "20240106"

        future = backtest_service._get_future_date("20240101", 10)
        assert future == "20240111"

    @pytest.mark.asyncio
    async def test_backtest_summary_metrics(self, backtest_service):
        """测试回测摘要指标完整性"""
        conditions = [{"factor_id": "RSI14", "operator": "lt", "value": 70}]

        result = await backtest_service.run_backtest(
            conditions=conditions,
            start_date="20240101",
            end_date="20240331"
        )

        summary = result.summary

        # 验证所有关键指标存在
        assert summary.total_return is not None
        assert summary.annual_return is not None
        assert summary.max_drawdown is not None
        assert summary.win_rate is not None
        assert summary.sharpe_ratio is not None
        assert summary.benchmark_return is not None
        assert summary.excess_return is not None

        # 验证指标范围合理
        assert summary.win_rate >= 0 and summary.win_rate <= 100
        assert summary.sharpe_ratio >= -5 and summary.sharpe_ratio <= 5