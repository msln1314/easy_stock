"""
趋势分析 MCP 类
"""
from typing import Dict, List, Optional
from app.services.trend_service import trend_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class TrendMCP:
    """趋势分析 MCP 类"""

    async def analyze(
        self,
        stock_code: str,
        analysis_type: str = "comprehensive",
        include_indicators: Optional[List[str]] = None,
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        分析单只股票趋势

        Args:
            stock_code: 股票代码
            analysis_type: 分析类型
            include_indicators: 包含的指标
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据

        Returns:
            趋势分析结果
        """
        logger.info(f"MCP趋势分析: {stock_code}")
        result = await trend_service.analyze_trend(
            stock_code=stock_code,
            analysis_type=analysis_type,
            include_indicators=include_indicators,
            model=model,
            stock_name=stock_name,
            kline_data=kline_data
        )
        return result.model_dump()

    async def batch(
        self,
        stock_codes: List[str],
        analysis_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        批量趋势分析

        Args:
            stock_codes: 股票代码列表
            analysis_type: 分析类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            批量趋势分析结果
        """
        logger.info(f"MCP批量趋势分析: {len(stock_codes)}只股票")
        result = await trend_service.batch_analyze_trends(
            stock_codes=stock_codes,
            analysis_type=analysis_type,
            model=model,
            stock_data_map=stock_data_map
        )
        return result.model_dump()


# 单例
trend_mcp = TrendMCP()