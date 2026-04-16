"""
投资建议 MCP 类
"""
from typing import Dict, List, Optional
from app.services.advice_service import advice_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class AdviceMCP:
    """投资建议 MCP 类"""

    async def generate(
        self,
        stock_code: str,
        advice_type: str = "comprehensive",
        include_backtest: bool = True,
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        生成投资建议

        Args:
            stock_code: 股票代码
            advice_type: 建议类型
            include_backtest: 包含回测
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据

        Returns:
            投资建议结果
        """
        logger.info(f"MCP投资建议: {stock_code}")
        result = await advice_service.generate_advice(
            stock_code=stock_code,
            advice_type=advice_type,
            include_backtest=include_backtest,
            model=model,
            stock_name=stock_name,
            kline_data=kline_data
        )
        return result.model_dump()

    async def batch(
        self,
        stock_codes: List[str],
        advice_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        批量投资建议

        Args:
            stock_codes: 股票代码列表
            advice_type: 建议类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            批量投资建议结果
        """
        logger.info(f"MCP批量投资建议: {len(stock_codes)}只股票")
        result = await advice_service.batch_generate_advice(
            stock_codes=stock_codes,
            advice_type=advice_type,
            model=model,
            stock_data_map=stock_data_map
        )
        return result.model_dump()

    async def report(
        self,
        stock_codes: List[str],
        report_type: str = "portfolio",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        生成分析报告

        Args:
            stock_codes: 股票代码列表
            report_type: 报告类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            报告结果
        """
        logger.info(f"MCP生成报告: {len(stock_codes)}只股票")
        result = await advice_service.generate_report(
            stock_codes=stock_codes,
            report_type=report_type,
            model=model,
            stock_data_map=stock_data_map
        )
        return result.model_dump()


# 单例
advice_mcp = AdviceMCP()