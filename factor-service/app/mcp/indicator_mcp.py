"""
指标 MCP 类

封装指标服务的 MCP 接口
"""
from typing import Dict, List, Optional
from app.services.indicator_service import indicator_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class IndicatorMCP:
    """指标 MCP 类"""

    async def calculate(
        self,
        stock_code: str,
        indicators: List[str],
        period: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        计算单只股票的技术指标

        Args:
            stock_code: 股票代码
            indicators: 指标列表
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            kline_data: K线数据

        Returns:
            指标计算结果
        """
        logger.info(f"MCP计算指标: {stock_code}, indicators={indicators}")
        result = await indicator_service.calculate_indicators(
            stock_code=stock_code,
            indicators=indicators,
            period=period,
            start_date=start_date,
            end_date=end_date,
            kline_data=kline_data
        )
        return result.model_dump()

    async def batch(
        self,
        stock_codes: List[str],
        indicators: List[str],
        date: Optional[str] = None,
        kline_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        批量计算多只股票的指标

        Args:
            stock_codes: 股票代码列表
            indicators: 指标列表
            date: 日期
            kline_data_map: 各股票K线数据映射

        Returns:
            批量计算结果
        """
        logger.info(f"MCP批量计算指标: {len(stock_codes)}只股票")
        result = await indicator_service.batch_calculate(
            stock_codes=stock_codes,
            indicators=indicators,
            date=date,
            kline_data_map=kline_data_map
        )
        return result.model_dump()

    async def list_indicators(self) -> List[Dict]:
        """
        获取支持的指标列表

        Returns:
            指标定义列表
        """
        logger.info("MCP获取指标列表")
        return indicator_service.get_indicator_list()


# 单例
indicator_mcp = IndicatorMCP()