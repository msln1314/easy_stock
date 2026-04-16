"""
风险评估 MCP 类
"""
from typing import Dict, List, Optional
from app.services.risk_service import risk_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class RiskMCP:
    """风险评估 MCP 类"""

    async def assess(
        self,
        stock_code: str,
        assessment_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None,
        backtest_data: Optional[Dict] = None
    ) -> Dict:
        """
        单只股票风险评估

        Args:
            stock_code: 股票代码
            assessment_type: 评估类型
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据
            backtest_data: 回测数据

        Returns:
            风险评估结果
        """
        logger.info(f"MCP风险评估: {stock_code}")
        result = await risk_service.assess_risk(
            stock_code=stock_code,
            assessment_type=assessment_type,
            model=model,
            stock_name=stock_name,
            kline_data=kline_data,
            backtest_data=backtest_data
        )
        return result.model_dump()

    async def portfolio(
        self,
        stock_codes: List[str],
        weights: Optional[List[float]] = None,
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        组合风险评估

        Args:
            stock_codes: 股票代码列表
            weights: 权重列表
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            组合风险评估结果
        """
        logger.info(f"MCP组合风险评估: {len(stock_codes)}只股票")
        result = await risk_service.portfolio_risk(
            stock_codes=stock_codes,
            weights=weights,
            model=model,
            stock_data_map=stock_data_map
        )
        return result.model_dump()

    async def compare(
        self,
        stock_codes: List[str],
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        多股风险对比

        Args:
            stock_codes: 股票代码列表
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            风险对比结果
        """
        logger.info(f"MCP风险对比: {len(stock_codes)}只股票")
        result = await risk_service.compare_risk(
            stock_codes=stock_codes,
            model=model,
            stock_data_map=stock_data_map
        )
        return result.model_dump()


# 单例
risk_mcp = RiskMCP()