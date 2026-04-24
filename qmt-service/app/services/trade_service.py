# backend/qmt-service/app/services/trade_service.py
"""
交易执行服务

提供下单、撤单、查询委托等功能
参考: https://github.com/guangxiangdebizi/QMT-MCP
"""
import logging
from datetime import datetime
from typing import Optional, List

from app.core.qmt_client import QMTClientManager
from app.models.trade_models import (
    OrderCreate,
    OrderResponse,
    OrderDirection,
    OrderType,
    OrderStatus,
    CancelOrderResponse,
)

logger = logging.getLogger(__name__)

# 尝试导入xtconstant常量
try:
    from xtquant import xtconstant
    XTCONSTANT_AVAILABLE = True
except ImportError:
    XTCONSTANT_AVAILABLE = False
    logger.warning("xtconstant未安装，使用硬编码常量")


class TradeService:
    """交易执行服务"""

    # 使用xtconstant常量（推荐）或硬编码值
    if XTCONSTANT_AVAILABLE:
        ORDER_BUY = xtconstant.STOCK_BUY      # 买入
        ORDER_SELL = xtconstant.STOCK_SELL    # 卖出
        ORDER_LIMIT = xtconstant.FIX_PRICE    # 限价单
        ORDER_MARKET = xtconstant.LATEST_PRICE  # 市价单（使用最新价）
    else:
        ORDER_BUY = 23      # 买入
        ORDER_SELL = 24     # 卖出
        ORDER_LIMIT = 23    # 限价单
        ORDER_MARKET = 24   # 市价单

    # 方向映射
    DIRECTION_MAP = {
        OrderDirection.BUY: ORDER_BUY,
        OrderDirection.SELL: ORDER_SELL,
    }

    # 订单类型映射
    ORDER_TYPE_MAP = {
        OrderType.LIMIT: ORDER_LIMIT,
        OrderType.MARKET: ORDER_MARKET,
    }

    # 状态映射（QMT状态 -> 系统状态）
    STATUS_MAP = {
        48: OrderStatus.PENDING,    # 未报
        49: OrderStatus.PENDING,    # 待报
        50: OrderStatus.PENDING,    # 已报
        51: OrderStatus.PARTIAL,    # 部成
        52: OrderStatus.FILLED,     # 全成
        53: OrderStatus.CANCELLED,  # 已撤
        54: OrderStatus.CANCELLED,  # 已撤
        55: OrderStatus.REJECTED,   # 废单
    }

    async def place_order(self, order: OrderCreate) -> OrderResponse:
        """下单

        参数顺序（参考QMT-MCP）：
        order_stock(account, stock_code, direction, quantity, order_type, price, strategy_name, remark)
        """
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()

        logger.info(f"下单请求: {order.stock_code} {order.direction} {order.quantity}股 @{order.price}")

        # 下单 - 使用正确的参数顺序
        order_id = trader.order_stock(
            account,                             # 账户
            order.stock_code,                    # 股票代码
            self.DIRECTION_MAP[order.direction], # 买卖方向
            order.quantity,                      # 数量
            self.ORDER_TYPE_MAP[order.order_type], # 订单类型(限价/市价)
            order.price or 0,                    # 价格（市价单传0）
            "AI交易",                            # 策略名称
            "Auto_Order"                         # 备注
        )

        if order_id <= 0:
            logger.error(f"下单失败，返回order_id: {order_id}")
            raise Exception(f"下单失败，错误代码: {order_id}")

        logger.info(f"下单成功，订单号: {order_id}")

        now = datetime.now()
        return OrderResponse(
            order_id=str(order_id),
            stock_code=order.stock_code,
            stock_name="",  # 需要额外查询
            direction=order.direction,
            price=order.price or 0,
            quantity=order.quantity,
            order_type=order.order_type,
            status=OrderStatus.PENDING,
            filled_quantity=0,
            filled_price=0,
            created_time=now,
            updated_time=now,
            message="下单成功"
        )

    async def cancel_order(self, order_id: str) -> CancelOrderResponse:
        """撤单"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()

        logger.info(f"撤单请求: order_id={order_id}")

        # 撤单 - 需要传入account参数
        result = trader.cancel_order_stock(account, int(order_id))

        success = result == 0
        logger.info(f"撤单结果: order_id={order_id}, success={success}")

        return CancelOrderResponse(
            order_id=order_id,
            success=success,
            message="撤单成功" if success else "撤单失败"
        )

    async def get_orders(
        self,
        status: Optional[OrderStatus] = None,
        date: Optional[str] = None
    ) -> List[OrderResponse]:
        """查询委托列表"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()

        orders = trader.query_stock_orders()

        result = []
        for o in orders:
            order_response = self._convert_order(o)
            if status and order_response.status != status:
                continue
            result.append(order_response)

        return result

    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """查询单个委托"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()

        order = trader.query_stock_order(int(order_id))
        if order:
            return self._convert_order(order)
        return None

    def _convert_order(self, qmt_order) -> OrderResponse:
        """转换QMT订单对象"""
        now = datetime.now()
        return OrderResponse(
            order_id=str(qmt_order.order_id),
            stock_code=qmt_order.stock_code,
            stock_name=qmt_order.stock_name or "",
            direction=OrderDirection.BUY if qmt_order.order_type == 23 else OrderDirection.SELL,
            price=qmt_order.price,
            quantity=qmt_order.order_volume,
            order_type=OrderType.LIMIT,
            status=self.STATUS_MAP.get(qmt_order.order_status, OrderStatus.PENDING),
            filled_quantity=qmt_order.traded_volume or 0,
            filled_price=qmt_order.traded_price or 0,
            created_time=now,
            updated_time=now,
        )


# 单例
trade_service = TradeService()