# backend/qmt-service/app/mcp/trade_mcp.py
"""
交易MCP接口

提供下单、撤单、查询委托等交易功能的MCP封装
"""
import logging
from typing import Dict, List, Optional

from app.services.trade_service import trade_service
from app.models.trade_models import OrderCreate, OrderDirection, OrderType

logger = logging.getLogger(__name__)


class TradeMCP:
    """
    交易MCP接口

    提供股票交易相关功能，包括买入、卖出、撤单、查询委托等。
    所有接口通过调用trade_service实现，共享服务层的数据处理机制。

    使用示例:
        trade_mcp = TradeMCP()
        result = await trade_mcp.buy_stock("000001.SZ", 10.5, 100)
    """

    async def buy_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict:
        """
        买入股票

        Args:
            stock_code: 股票代码，如 "000001.SZ"
            price: 委托价格（市价单可传0）
            quantity: 委托数量，必须为100的整数倍
            order_type: 委托类型，"limit"为限价单，"market"为市价单

        Returns:
            Dict: 包含订单信息的结果
                - order_id: 订单ID
                - stock_code: 股票代码
                - direction: "buy"
                - price: 委托价格
                - quantity: 委托数量
                - status: 订单状态
                - message: 提示信息

        Raises:
            Exception: 当交易失败时抛出
        """
        logger.info(f"MCP买入股票: {stock_code}, 价格: {price}, 数量: {quantity}")
        try:
            order = OrderCreate(
                stock_code=stock_code,
                direction=OrderDirection.BUY,
                price=price,
                quantity=quantity,
                order_type=OrderType.LIMIT if order_type == "limit" else OrderType.MARKET
            )
            result = await trade_service.place_order(order)
            print(result,"buy")
            return result.model_dump()
        except Exception as e:
            logger.error(f"买入股票失败: {str(e)}")
            raise Exception(f"买入股票失败: {str(e)}")

    async def sell_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict:
        """
        卖出股票

        Args:
            stock_code: 股票代码
            price: 委托价格（市价单可传0）
            quantity: 委托数量，必须为100的整数倍
            order_type: 委托类型

        Returns:
            Dict: 包含订单信息的结果

        Raises:
            Exception: 当交易失败时抛出
        """
        logger.info(f"MCP卖出股票: {stock_code}, 价格: {price}, 数量: {quantity}")
        try:
            order = OrderCreate(
                stock_code=stock_code,
                direction=OrderDirection.SELL,
                price=price,
                quantity=quantity,
                order_type=OrderType.LIMIT if order_type == "limit" else OrderType.MARKET
            )
            result = await trade_service.place_order(order)
            return result.model_dump()
        except Exception as e:
            logger.error(f"卖出股票失败: {str(e)}")
            raise Exception(f"卖出股票失败: {str(e)}")

    async def cancel_order(self, order_id: str) -> Dict:
        """
        撤销委托订单

        Args:
            order_id: 订单ID

        Returns:
            Dict: 撤单结果
                - order_id: 订单ID
                - success: 是否成功
                - message: 提示信息

        Raises:
            Exception: 当撤单失败时抛出
        """
        logger.info(f"MCP撤单: {order_id}")
        try:
            result = await trade_service.cancel_order(order_id)
            return result.model_dump()
        except Exception as e:
            logger.error(f"撤单失败: {str(e)}")
            raise Exception(f"撤单失败: {str(e)}")

    async def get_orders(self, status: Optional[str] = None) -> List[Dict]:
        """
        查询委托订单列表

        Args:
            status: 可选的状态筛选，如 "pending", "filled", "cancelled"

        Returns:
            List[Dict]: 委托订单列表

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP查询委托列表")
        try:
            from app.models.trade_models import OrderStatus
            status_filter = None
            if status:
                status_map = {
                    "pending": OrderStatus.PENDING,
                    "filled": OrderStatus.FILLED,
                    "partial": OrderStatus.PARTIAL,
                    "cancelled": OrderStatus.CANCELLED,
                    "rejected": OrderStatus.REJECTED,
                }
                status_filter = status_map.get(status.lower())

            orders = await trade_service.get_orders(status=status_filter)
            return [o.model_dump() for o in orders]
        except Exception as e:
            logger.error(f"查询委托列表失败: {str(e)}")
            raise Exception(f"查询委托列表失败: {str(e)}")

    async def get_order(self, order_id: str) -> Optional[Dict]:
        """
        查询单个委托订单

        Args:
            order_id: 订单ID

        Returns:
            Dict: 订单详情，不存在则返回None

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP查询订单: {order_id}")
        try:
            order = await trade_service.get_order(order_id)
            if order:
                return order.model_dump()
            return None
        except Exception as e:
            logger.error(f"查询订单失败: {str(e)}")
            raise Exception(f"查询订单失败: {str(e)}")


# 单例
trade_mcp = TradeMCP()