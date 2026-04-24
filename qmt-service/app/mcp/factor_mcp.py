# backend/qmt-service/app/mcp/factor_mcp.py
"""
因子选股MCP接口

提供因子列表、因子选股等功能的MCP封装
"""
import logging
from typing import Dict, List, Optional

from app.services.factor_service import factor_service

logger = logging.getLogger(__name__)


class FactorMCP:
    """
    因子选股MCP接口

    提供因子查询和选股功能。

    使用示例:
        factor_mcp = FactorMCP()
        factors = await factor_mcp.get_factor_list()
    """

    async def get_factor_list(
        self,
        category: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict:
        """
        获取因子列表

        Args:
            category: 因子类别筛选，如 "trend", "momentum", "volatility" 等
            keyword: 关键词搜索

        Returns:
            Dict: 因子列表
                - factors: 因子定义列表，每个包含:
                    - factor_id: 因子ID
                    - factor_name: 因子名称
                    - category: 类别
                    - description: 描述
                    - formula: 公式
                    - unit: 单位
                - total: 总数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取因子列表, category={category}, keyword={keyword}")
        try:
            result = await factor_service.get_factor_definitions(
                category=category,
                keyword=keyword
            )
            return {
                "factors": [f.model_dump() for f in result.factors],
                "total": result.total
            }
        except Exception as e:
            logger.error(f"获取因子列表失败: {str(e)}")
            raise Exception(f"获取因子列表失败: {str(e)}")

    async def get_factor_info(self, factor_id: str) -> Optional[Dict]:
        """
        获取单个因子详情

        Args:
            factor_id: 因子ID，如 "MA5", "PE", "RSI6" 等

        Returns:
            Dict: 因子详情，不存在则返回None

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取因子详情: {factor_id}")
        try:
            factor = await factor_service.get_factor_definition(factor_id)
            if factor:
                return factor.model_dump()
            return None
        except Exception as e:
            logger.error(f"获取因子详情失败: {str(e)}")
            raise Exception(f"获取因子详情失败: {str(e)}")

    async def screen_stocks(
        self,
        factors: List[Dict],
        date: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """
        因子选股

        Args:
            factors: 筛选条件列表，每个条件包含:
                - factor_id: 因子ID
                - op: 操作符，可选 gt(大于), lt(小于), ge(大于等于), le(小于等于), eq(等于)
                - value: 阈值
            date: 日期，格式YYYYMMDD，不传则使用今日
            limit: 返回数量限制

        Returns:
            Dict: 选股结果
                - date: 日期
                - stocks: 股票列表，每个包含:
                    - stock_code: 股票代码
                    - stock_name: 股票名称
                    - score: 综合得分
                    - factor_values: 各因子值
                - count: 数量

        Raises:
            Exception: 当选股失败时抛出
        """
        logger.info(f"MCP因子选股, factors={len(factors)}, date={date}")
        try:
            from app.models.factor_models import FactorScreenRequest
            request = FactorScreenRequest(
                factors=factors,
                date=date,
                limit=limit
            )
            result = await factor_service.screen_stocks(request)
            return {
                "date": result.date,
                "stocks": [s.model_dump() for s in result.stocks],
                "count": result.count
            }
        except Exception as e:
            logger.error(f"因子选股失败: {str(e)}")
            raise Exception(f"因子选股失败: {str(e)}")


# 单例
factor_mcp = FactorMCP()