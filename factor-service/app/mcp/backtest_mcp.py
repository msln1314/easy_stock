"""
回测 MCP 类

封装回测服务的 MCP 接口
"""
from typing import Dict, List, Optional
from app.services.backtest_service import backtest_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class BacktestMCP:
    """回测 MCP 类"""

    async def run(
        self,
        conditions: List[Dict],
        start_date: str,
        end_date: str,
        weights: Optional[List[Dict]] = None,
        rebalance_freq: str = "daily",
        top_n: int = 10,
        benchmark: str = "000300.SH",
        historical_data: Optional[Dict] = None
    ) -> Dict:
        """
        执行完整回测

        Args:
            conditions: 筛选条件
            weights: 评分权重（可选）
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            rebalance_freq: 调仓频率 daily/weekly/monthly
            top_n: 持仓数量
            benchmark: 基准指数
            historical_data: 历史数据

        Returns:
            回测结果
        """
        logger.info(f"MCP执行回测: {start_date}-{end_date}")
        result = await backtest_service.run_backtest(
            conditions=conditions,
            weights=weights,
            start_date=start_date,
            end_date=end_date,
            rebalance_freq=rebalance_freq,
            top_n=top_n,
            benchmark=benchmark,
            historical_data=historical_data
        )
        return result.model_dump()

    async def ic(
        self,
        factor_id: str,
        start_date: str,
        end_date: str,
        forward_period: int = 5,
        factor_data: Optional[Dict] = None,
        return_data: Optional[Dict] = None
    ) -> Dict:
        """
        IC分析

        Args:
            factor_id: 因子ID
            start_date: 开始日期
            end_date: 结束日期
            forward_period: 预测周期（天）
            factor_data: 因子数据
            return_data: 收益数据

        Returns:
            IC分析结果
        """
        logger.info(f"MCP IC分析: {factor_id}")
        result = await backtest_service.calculate_ic(
            factor_id=factor_id,
            start_date=start_date,
            end_date=end_date,
            forward_period=forward_period,
            factor_data=factor_data,
            return_data=return_data
        )
        return result.model_dump()

    async def group(
        self,
        factor_id: str,
        start_date: str,
        end_date: str,
        num_groups: int = 5,
        factor_data: Optional[Dict] = None,
        return_data: Optional[Dict] = None
    ) -> Dict:
        """
        分组收益对比

        Args:
            factor_id: 因子ID
            start_date: 开始日期
            end_date: 结束日期
            num_groups: 分组数量
            factor_data: 因子数据
            return_data: 收益数据

        Returns:
            分组收益结果
        """
        logger.info(f"MCP分组收益: {factor_id}, groups={num_groups}")
        result = await backtest_service.group_returns(
            factor_id=factor_id,
            start_date=start_date,
            end_date=end_date,
            num_groups=num_groups,
            factor_data=factor_data,
            return_data=return_data
        )
        return result.model_dump()

    async def sensitivity(
        self,
        conditions: List[Dict],
        param_ranges: Dict[str, List],
        start_date: str,
        end_date: str,
        historical_data: Optional[Dict] = None
    ) -> Dict:
        """
        敏感性测试

        Args:
            conditions: 筛选条件
            param_ranges: 参数变化范围
            start_date: 开始日期
            end_date: 结束日期
            historical_data: 历史数据

        Returns:
            敏感性测试结果
        """
        logger.info(f"MCP敏感性测试: params={list(param_ranges.keys())}")
        result = await backtest_service.sensitivity_test(
            conditions=conditions,
            param_ranges=param_ranges,
            start_date=start_date,
            end_date=end_date,
            historical_data=historical_data
        )
        return result.model_dump()


# 单例
backtest_mcp = BacktestMCP()