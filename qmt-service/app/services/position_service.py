# backend/qmt-service/app/services/position_service.py
"""
持仓管理服务

提供持仓查询、资金余额、成交记录等功能
"""
import logging
from datetime import datetime
from typing import List, Optional

from app.core.qmt_client import QMTClientManager
from app.models.position_models import (
    Position,
    PositionListResponse,
    Balance,
    Trade,
    TradeListResponse,
    Entrust,
    EntrustListResponse,
)

logger = logging.getLogger(__name__)


class PositionService:
    """持仓管理服务"""

    async def get_positions(self) -> PositionListResponse:
        """查询持仓列表"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()  # 获取账号对象

        positions = trader.query_stock_positions(account)

        # 获取所有股票代码，批量查询行情
        stock_codes = [p.stock_code for p in positions if p.volume > 0]

        # 批量获取实时行情
        quotes = await self._get_realtime_quotes(stock_codes)

        result = []
        total_market_value = 0.0
        total_profit = 0.0

        for p in positions:
            if p.volume <= 0:
                continue
            quote = quotes.get(p.stock_code, {})
            position = self._convert_position(p, quote)
            result.append(position)
            total_market_value += position.market_value
            total_profit += position.profit

        return PositionListResponse(
            positions=result,
            total_market_value=total_market_value,
            total_profit=total_profit,
            count=len(result)
        )

    async def _get_realtime_quotes(self, stock_codes: List[str]) -> dict:
        """批量获取实时行情"""
        if not stock_codes:
            return {}

        try:
            from xtquant import xtdata

            # 获取实时行情
            full_tick = xtdata.get_full_tick(stock_codes)

            quotes = {}
            for code in stock_codes:
                if code in full_tick:
                    tick = full_tick[code]

                    # 获取股票名称（从 tick 数据或单独查询）
                    stock_name = tick.get('stock_name', '') or tick.get('symbol', '')

                    # 如果 tick 中没有名称，尝试从证券信息获取
                    if not stock_name:
                        try:
                            instrument = xtdata.get_instrument_detail(code)
                            if instrument:
                                stock_name = instrument.get('InstrumentName', '')
                        except:
                            pass

                    quotes[code] = {
                        'stock_name': stock_name,
                        'price': float(tick.get('lastPrice', 0)),
                        'pre_close': float(tick.get('lastClose', 0)),
                    }
            return quotes
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return {}

    async def get_balance(self) -> Balance:
        """查询资金余额"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()

        asset = trader.query_stock_asset(account)

        # 计算总盈亏（从持仓数据）
        positions = trader.query_stock_positions(account)
        total_profit = 0.0
        for p in positions:
            if hasattr(p, 'market_price') and hasattr(p, 'open_price'):
                total_profit += (p.market_price - p.open_price) * p.volume

        return Balance(
            total_asset=asset.total_asset,
            available_cash=asset.cash,
            market_value=asset.market_value,
            frozen_cash=asset.total_asset - asset.cash - asset.market_value,
            profit_today=0,  # QMT不直接提供今日盈亏
            profit_total=total_profit,
            updated_time=datetime.now()
        )

    async def get_trades(
        self,
        date: Optional[str] = None,
        stock_code: Optional[str] = None
    ) -> TradeListResponse:
        """查询成交记录"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()

        trades = trader.query_stock_trades(account)

        result = []
        for t in trades:
            trade = self._convert_trade(t)
            if stock_code and trade.stock_code != stock_code:
                continue
            result.append(trade)

        return TradeListResponse(
            trades=result,
            total=len(result)
        )

    async def get_today_trades(self) -> TradeListResponse:
        """查询今日成交"""
        today = datetime.now().strftime("%Y%m%d")
        return await self.get_trades(date=today)

    async def get_today_entrusts(self) -> EntrustListResponse:
        """查询今日委托"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        trader = QMTClientManager.get_trader()
        account = QMTClientManager.get_account()

        orders = trader.query_stock_orders(account)

        entrusts = []
        for o in orders:
            entrust = self._convert_entrust(o)
            entrusts.append(entrust)

        return EntrustListResponse(
            entrusts=entrusts,
            total=len(entrusts)
        )

    def _convert_position(self, qmt_position, quote: dict = None) -> Position:
        """转换QMT持仓对象"""
        now = datetime.now()
        quantity = qmt_position.volume
        cost_price = qmt_position.open_price

        # 优先使用实时行情价格，否则使用持仓的市场价或成本价
        if quote and quote.get('price', 0) > 0:
            current_price = quote['price']
            stock_name = quote.get('stock_name', '')
        else:
            current_price = qmt_position.market_price if hasattr(qmt_position, 'market_price') and qmt_position.market_price > 0 else cost_price
            # 尝试从持仓对象获取名称
            stock_name = ""
            if hasattr(qmt_position, 'stock_name'):
                stock_name = qmt_position.stock_name or ""
            elif hasattr(qmt_position, 'symbol'):
                stock_name = qmt_position.symbol or ""

        profit = (current_price - cost_price) * quantity
        profit_rate = ((current_price - cost_price) / cost_price * 100) if cost_price > 0 else 0

        return Position(
            stock_code=qmt_position.stock_code,
            stock_name=stock_name,
            quantity=quantity,
            available=qmt_position.can_use_volume if hasattr(qmt_position, 'can_use_volume') else quantity,
            cost_price=cost_price,
            current_price=current_price,
            profit=profit,
            profit_rate=round(profit_rate, 2),
            market_value=current_price * quantity,
            updated_time=now
        )

    def _convert_trade(self, qmt_trade) -> Trade:
        """转换QMT成交对象"""
        # stock_name 可能在不同位置
        stock_name = ""
        if hasattr(qmt_trade, 'stock_name'):
            stock_name = qmt_trade.stock_name or ""
        elif hasattr(qmt_trade, 'symbol'):
            stock_name = qmt_trade.symbol or ""

        return Trade(
            trade_id=str(qmt_trade.order_id),
            order_id=str(qmt_trade.order_id),
            stock_code=qmt_trade.stock_code,
            stock_name=stock_name,
            direction="buy" if qmt_trade.order_type == 23 else "sell",
            price=qmt_trade.traded_price,
            quantity=qmt_trade.traded_volume,
            trade_time=datetime.now(),
            commission=qmt_trade.commission if hasattr(qmt_trade, 'commission') else 0
        )

    def _convert_entrust(self, qmt_order) -> Entrust:
        """转换QMT委托对象"""
        direction = "buy"
        if hasattr(qmt_order, 'order_type'):
            if qmt_order.order_type == 24:
                direction = "sell"
            elif hasattr(qmt_order, 'offset_flag') and qmt_order.offset_flag == 24:
                direction = "sell"

        status_map = {
            48: "pending",    # 未报
            49: "pending",    # 待报
            50: "submitted",  # 已报
            51: "partial",    # 部成
            52: "filled",     # 全成
            53: "cancelled",  # 已撤
            54: "cancelled",  # 已撤
            55: "rejected",   # 废单
        }
        status = status_map.get(getattr(qmt_order, 'order_status', 0), "pending")

        # stock_name 可能在不同位置
        stock_name = ""
        if hasattr(qmt_order, 'stock_name'):
            stock_name = qmt_order.stock_name or ""
        elif hasattr(qmt_order, 'symbol'):
            stock_name = qmt_order.symbol or ""

        return Entrust(
            order_id=str(qmt_order.order_id),
            stock_code=qmt_order.stock_code,
            stock_name=stock_name,
            direction=direction,
            price=qmt_order.price if hasattr(qmt_order, 'price') else 0,
            quantity=qmt_order.order_volume if hasattr(qmt_order, 'order_volume') else 0,
            traded_quantity=qmt_order.traded_volume if hasattr(qmt_order, 'traded_volume') else 0,
            status=status,
            entrust_time=datetime.now()
        )


# 单例
position_service = PositionService()