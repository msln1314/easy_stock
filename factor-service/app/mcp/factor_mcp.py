"""
因子 MCP 类

封装因子服务的 MCP 接口
"""
from typing import Dict, List, Optional
from app.services.factor_service import factor_service
from app.models.factor_models import FactorCondition, ScoreWeight
from app.core.logging import get_logger

logger = get_logger(__name__)


class FactorMCP:
    """因子 MCP 类"""

    async def screen(
        self,
        conditions: List[Dict],
        stock_pool: Optional[List[str]] = None,
        date: Optional[str] = None,
        limit: int = 50,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        因子选股

        Args:
            conditions: 筛选条件列表
            stock_pool: 股票池
            date: 日期
            limit: 返回数量限制
            stock_data_map: 各股票K线数据映射

        Returns:
            选股结果
        """
        logger.info(f"MCP因子选股: conditions={len(conditions)}")

        # 转换条件格式
        factor_conditions = [
            FactorCondition(
                factor_id=c.get("factor_id"),
                operator=c.get("operator"),
                value=c.get("value"),
                value2=c.get("value2")
            )
            for c in conditions
        ]

        result = await factor_service.screen_stocks(
            conditions=factor_conditions,
            stock_pool=stock_pool,
            date=date,
            limit=limit,
            stock_data_map=stock_data_map
        )
        return result.model_dump()

    async def score(
        self,
        stock_codes: List[str],
        weights: List[Dict],
        date: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> Dict:
        """
        综合评分计算

        Args:
            stock_codes: 股票代码列表
            weights: 评分权重配置
            date: 日期
            stock_data_map: 各股票K线数据映射

        Returns:
            评分结果
        """
        logger.info(f"MCP评分计算: {len(stock_codes)}只股票")

        # 转换权重格式
        score_weights = [
            ScoreWeight(
                factor_id=w.get("factor_id"),
                weight=w.get("weight"),
                direction=w.get("direction", "high")
            )
            for w in weights
        ]

        result = await factor_service.calculate_score(
            stock_codes=stock_codes,
            weights=score_weights,
            date=date,
            stock_data_map=stock_data_map
        )
        return result.model_dump()

    async def value(
        self,
        stock_code: str,
        factor_id: str,
        date: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> Dict:
        """
        获取单只股票因子值

        Args:
            stock_code: 股票代码
            factor_id: 因子ID
            date: 日期
            kline_data: K线数据

        Returns:
            因子值结果
        """
        logger.info(f"MCP获取因子值: {stock_code}, factor={factor_id}")
        result = await factor_service.get_factor_value(
            stock_code=stock_code,
            factor_id=factor_id,
            date=date,
            kline_data=kline_data
        )
        return result.model_dump()

    async def list_factors(self) -> Dict:
        """
        获取支持的因子列表

        Returns:
            因子定义列表
        """
        logger.info("MCP获取因子列表")
        result = factor_service.get_available_factors()
        return result.model_dump()


# 单例
factor_mcp = FactorMCP()