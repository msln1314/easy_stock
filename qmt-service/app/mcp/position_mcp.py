# backend/qmt-service/app/mcp/position_mcp.py
"""
持仓MCP接口

提供持仓查询、资金余额、成交记录等功能的MCP封装
"""
import logging
from typing import Dict, List, Optional

from app.services.position_service import position_service

logger = logging.getLogger(__name__)


class PositionMCP:
    """
    持仓MCP接口

    提供持仓和资金相关查询功能，包括持仓列表、资金余额、成交记录等。

    使用示例:
        position_mcp = PositionMCP()
        positions = await position_mcp.get_positions()
        balance = await position_mcp.get_balance()
    """

    async def get_positions(self) -> Dict:
        """
        查询持仓列表

        Returns:
            Dict: 持仓信息
                - positions: 持仓列表，每个包含:
                    - stock_code: 股票代码
                    - stock_name: 票名称
                    - quantity: 持仓数量
                    - available: 可卖数量
                    - cost_price: 成本价
                    - current_price: 现价
                    - profit: 盈亏金额
                    - profit_rate: 盈亏比例(%)
                    - market_value: 市值
                    - updated_time: 更新时间
                - total_market_value: 总市值
                - total_profit: 总盈亏
                - count: 持仓数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info("MCP查询持仓列表")
        try:
            result = await position_service.get_positions()
            return result.model_dump()
        except Exception as e:
            logger.error(f"查询持仓列表失败: {str(e)}")
            raise Exception(f"查询持仓列表失败: {str(e)}")

    async def get_balance(self) -> Dict:
        """
        查询资金余额

        Returns:
            Dict: 资金信息
                - total_asset: 总资产
                - available_cash: 可用资金
                - market_value: 持仓市值
                - frozen_cash: 冻结资金
                - profit_today: 今日盈亏
                - profit_total: 总盈亏
                - updated_time: 更新时间

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info("MCP查询资金余额")
        try:
            result = await position_service.get_balance()
            return result.model_dump()
        except Exception as e:
            logger.error(f"查询资金余额失败: {str(e)}")
            raise Exception(f"查询资金余额失败: {str(e)}")

    async def get_trades(
        self,
        date: Optional[str] = None,
        stock_code: Optional[str] = None
    ) -> Dict:
        """
        查询成交记录

        Args:
            date: 日期筛选，格式YYYYMMDD
            stock_code: 股票代码筛选

        Returns:
            Dict: 成交记录
                - trades: 成交列表，每个包含:
                    - trade_id: 成交ID
                    - order_id: 原委托ID
                    - stock_code: 股票代码
                    - stock_name: 票名称
                    - direction: 买卖方向
                    - price: 成交价格
                    - quantity: 成交数量
                    - trade_time: 成交时间
                    - commission: 手续费
                - total: 总数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP查询成交记录, date={date}, stock_code={stock_code}")
        try:
            result = await position_service.get_trades(date=date, stock_code=stock_code)
            return result.model_dump()
        except Exception as e:
            logger.error(f"查询成交记录失败: {str(e)}")
            raise Exception(f"查询成交记录失败: {str(e)}")

    async def get_today_trades(self) -> Dict:
        """
        查询今日成交记录

        Returns:
            Dict: 今日成交记录

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info("MCP查询今日成交")
        try:
            result = await position_service.get_today_trades()
            return result.model_dump()
        except Exception as e:
            logger.error(f"查询今日成交失败: {str(e)}")
            raise Exception(f"查询今日成交失败: {str(e)}")

    async def get_today_entrusts(self) -> Dict:
        """
        查询今日委托

        Returns:
            Dict: 今日委托记录
                - entrusts: 委托列表，每个包含:
                    - order_id: 委托ID
                    - stock_code: 股票代码
                    - stock_name: 股票名称
                    - direction: 买卖方向
                    - price: 委托价格
                    - quantity: 委托数量
                    - traded_quantity: 已成交数量
                    - status: 委托状态
                    - entrust_time: 委托时间
                - total: 总数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info("MCP查询今日委托")
        try:
            result = await position_service.get_today_entrusts()
            return result.model_dump()
        except Exception as e:
            logger.error(f"查询今日委托失败: {str(e)}")
            raise Exception(f"查询今日委托失败: {str(e)}")


# 单例
position_mcp = PositionMCP()