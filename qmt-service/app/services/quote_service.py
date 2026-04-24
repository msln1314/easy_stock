# backend/qmt-service/app/services/quote_service.py
"""
L2行情服务

提供十档行情、逐笔成交、分时数据等L2级别行情功能
"""
import logging
from datetime import datetime
from typing import List, Optional
import asyncio

from app.core.qmt_client import QMTClientManager
from app.models.quote_models import (
    L2Quote,
    L2QuoteListResponse,
    Tick,
    TickListResponse,
    MinuteBar,
    MinuteBarListResponse,
    OrderBook,
    DepthResponse,
    QuoteStatus,
    IndexQuote,
    IndexQuoteListResponse,
)

logger = logging.getLogger(__name__)


# 主要指数代码映射
INDEX_CODES = {
    "sh": "000001.SH",  # 上证指数
    "sz": "399001.SZ",  # 深证成指
    "cy": "399006.SZ",  # 创业板指
    "hs300": "000300.SH",  # 沪深300
    "zz500": "000905.SH",  # 中证500
    "sz50": "000016.SH",  # 上证50
}


class QuoteService:
    """L2行情服务"""

    # 缓存行情数据
    _quote_cache: dict = {}
    _subscribed_codes: set = set()
    _l2_enabled: bool = False

    async def get_kline(
        self,
        stock_code: str,
        period: str = "1d",
        count: int = 100,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> dict:
        """
        获取K线数据

        Args:
            stock_code: 股票代码，如 000001.SZ
            period: 周期 1d-日线, 1w-周线, 1m-月线, 1m-1分钟, 5m-5分钟
            count: 返回条数
            start_time: 开始时间
            end_time: 结束时间
        """
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 先下载历史数据
        xtdata.download_history_data(stock_code, period=period, start_time=start_time or '', end_time=end_time or '')

        # 获取K线数据
        kline_data = xtdata.get_market_data_ex(
            stock_list=[stock_code],
            period=period,
            count=count,
            start_time=start_time or '',
            end_time=end_time or ''
        )

        if not kline_data or stock_code not in kline_data:
            return {"stock_code": stock_code, "klines": [], "count": 0}

        df = kline_data[stock_code]
        if df.empty:
            return {"stock_code": stock_code, "klines": [], "count": 0}

        klines = []
        for idx, row in df.iterrows():
            kline = {
                "date": row.get('time', str(idx)) if isinstance(row.get('time'), str) else str(idx),
                "open": float(row.get('open', 0)),
                "high": float(row.get('high', 0)),
                "low": float(row.get('low', 0)),
                "close": float(row.get('close', 0)),
                "volume": float(row.get('volume', 0)),
                "amount": float(row.get('amount', 0)),
            }
            klines.append(kline)

        return {"stock_code": stock_code, "klines": klines, "count": len(klines)}

    async def get_l2_quote(self, stock_code: str) -> Optional[L2Quote]:
        """获取单只股票L2十档行情"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 获取完整行情数据
        full_tick = xtdata.get_full_tick([stock_code])
        if not full_tick or stock_code not in full_tick:
            logger.warning(f"未获取到 {stock_code} 的行情数据")
            return None

        tick_data = full_tick[stock_code]
        return self._convert_l2_quote(stock_code, tick_data)

    async def get_l2_quotes(self, stock_codes: List[str]) -> L2QuoteListResponse:
        """批量获取L2十档行情"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        full_tick = xtdata.get_full_tick(stock_codes)
        quotes = []

        for code in stock_codes:
            if code in full_tick:
                quotes.append(self._convert_l2_quote(code, full_tick[code]))

        return L2QuoteListResponse(quotes=quotes, count=len(quotes))

    async def get_ticks(
        self,
        stock_code: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        count: int = 100
    ) -> TickListResponse:
        """获取逐笔成交数据"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 获取逐笔成交
        ticks_data = xtdata.get_market_data(
            stock_list=[stock_code],
            period='tick',
            start_time=start_time or '',
            end_time=end_time or '',
            count=count
        )

        if ticks_data is None or ticks_data.empty:
            return TickListResponse(stock_code=stock_code, ticks=[], count=0)

        ticks = []
        for idx, row in ticks_data.iterrows():
            tick = Tick(
                tick_id=f"{stock_code}_{idx.timestamp()}",
                stock_code=stock_code,
                price=float(row.get('lastPrice', 0)),
                volume=int(row.get('lastVolume', 0)),
                direction=self._get_tick_direction(row),
                trade_time=idx.to_pydatetime(),
                order_type=self._get_order_type(row)
            )
            ticks.append(tick)

        return TickListResponse(stock_code=stock_code, ticks=ticks, count=len(ticks))

    async def get_minute_bars(
        self,
        stock_code: str,
        date: Optional[str] = None
    ) -> MinuteBarListResponse:
        """获取分时数据"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 获取分时数据
        if date:
            start_time = f"{date} 09:30:00"
            end_time = f"{date} 15:00:00"
        else:
            today = datetime.now().strftime("%Y%m%d")
            start_time = f"{today} 09:30:00"
            end_time = f"{today} 15:00:00"

        data = xtdata.get_market_data(
            stock_list=[stock_code],
            period='1m',
            start_time=start_time,
            end_time=end_time
        )

        if data is None or data.empty:
            return MinuteBarListResponse(
                stock_code=stock_code,
                date=date or datetime.now().strftime("%Y%m%d"),
                bars=[],
                count=0
            )

        bars = []
        for idx, row in data.iterrows():
            bar = MinuteBar(
                stock_code=stock_code,
                time=idx.to_pydatetime(),
                price=float(row.get('close', 0)),
                volume=int(row.get('volume', 0)),
                amount=float(row.get('amount', 0)),
                avg_price=float(row.get('amount', 0)) / max(int(row.get('volume', 1)), 1),
                open=float(row.get('open', 0)),
                high=float(row.get('high', 0)),
                low=float(row.get('low', 0))
            )
            bars.append(bar)

        return MinuteBarListResponse(
            stock_code=stock_code,
            date=date or datetime.now().strftime("%Y%m%d"),
            bars=bars,
            count=len(bars)
        )

    async def get_depth(self, stock_code: str) -> DepthResponse:
        """获取订单簿深度"""
        quote = await self.get_l2_quote(stock_code)
        if not quote:
            raise RuntimeError(f"无法获取 {stock_code} 的行情数据")

        bid_levels = [
            {"price": quote.bid_price1, "volume": quote.bid_volume1},
            {"price": quote.bid_price2, "volume": quote.bid_volume2},
            {"price": quote.bid_price3, "volume": quote.bid_volume3},
            {"price": quote.bid_price4, "volume": quote.bid_volume4},
            {"price": quote.bid_price5, "volume": quote.bid_volume5},
            {"price": quote.bid_price6, "volume": quote.bid_volume6},
            {"price": quote.bid_price7, "volume": quote.bid_volume7},
            {"price": quote.bid_price8, "volume": quote.bid_volume8},
            {"price": quote.bid_price9, "volume": quote.bid_volume9},
            {"price": quote.bid_price10, "volume": quote.bid_volume10},
        ]

        ask_levels = [
            {"price": quote.ask_price1, "volume": quote.ask_volume1},
            {"price": quote.ask_price2, "volume": quote.ask_volume2},
            {"price": quote.ask_price3, "volume": quote.ask_volume3},
            {"price": quote.ask_price4, "volume": quote.ask_volume4},
            {"price": quote.ask_price5, "volume": quote.ask_volume5},
            {"price": quote.ask_price6, "volume": quote.ask_volume6},
            {"price": quote.ask_price7, "volume": quote.ask_volume7},
            {"price": quote.ask_price8, "volume": quote.ask_volume8},
            {"price": quote.ask_price9, "volume": quote.ask_volume9},
            {"price": quote.ask_price10, "volume": quote.ask_volume10},
        ]

        order_book = OrderBook(
            stock_code=stock_code,
            price=quote.price,
            bid_levels=[l for l in bid_levels if l["price"] > 0],
            ask_levels=[l for l in ask_levels if l["price"] > 0],
            updated_time=quote.updated_time
        )

        return DepthResponse(stock_code=stock_code, depth=order_book)

    async def subscribe_quotes(self, stock_codes: List[str]) -> QuoteStatus:
        """订阅行情"""
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 订阅行情
        for code in stock_codes:
            xtdata.subscribe_quote(
                stock_code=code,
                callback=self._quote_callback
            )
            self._subscribed_codes.add(code)

        self._l2_enabled = True

        return QuoteStatus(
            subscribed=True,
            stock_codes=list(self._subscribed_codes),
            l2_enabled=self._l2_enabled,
            message=f"已订阅 {len(stock_codes)} 只股票行情"
        )

    async def unsubscribe_quotes(self, stock_codes: List[str] = None) -> QuoteStatus:
        """取消订阅"""
        if stock_codes:
            self._subscribed_codes -= set(stock_codes)
        else:
            self._subscribed_codes.clear()

        return QuoteStatus(
            subscribed=len(self._subscribed_codes) > 0,
            stock_codes=list(self._subscribed_codes),
            l2_enabled=self._l2_enabled,
            message="取消订阅成功"
        )

    def get_subscription_status(self) -> QuoteStatus:
        """获取订阅状态"""
        return QuoteStatus(
            subscribed=len(self._subscribed_codes) > 0,
            stock_codes=list(self._subscribed_codes),
            l2_enabled=self._l2_enabled,
            message="订阅状态正常" if self._subscribed_codes else "未订阅任何股票"
        )

    def _quote_callback(self, data):
        """行情回调"""
        try:
            if data and 'stock_code' in data:
                self._quote_cache[data['stock_code']] = data
        except Exception as e:
            logger.error(f"行情回调处理失败: {e}")

    def _convert_l2_quote(self, stock_code: str, tick_data) -> L2Quote:
        """转换L2行情数据"""
        now = datetime.now()

        return L2Quote(
            stock_code=stock_code,
            stock_name=tick_data.get('stock_name', ''),
            price=float(tick_data.get('lastPrice', 0)),
            open=float(tick_data.get('open', 0)),
            high=float(tick_data.get('high', 0)),
            low=float(tick_data.get('low', 0)),
            pre_close=float(tick_data.get('lastClose', 0)),
            volume=int(tick_data.get('volume', 0)),
            amount=float(tick_data.get('amount', 0)),

            # 买盘
            bid_price1=float(tick_data.get('bidPrice1', 0)),
            bid_volume1=int(tick_data.get('bidVol1', 0)),
            bid_price2=float(tick_data.get('bidPrice2', 0)),
            bid_volume2=int(tick_data.get('bidVol2', 0)),
            bid_price3=float(tick_data.get('bidPrice3', 0)),
            bid_volume3=int(tick_data.get('bidVol3', 0)),
            bid_price4=float(tick_data.get('bidPrice4', 0)),
            bid_volume4=int(tick_data.get('bidVol4', 0)),
            bid_price5=float(tick_data.get('bidPrice5', 0)),
            bid_volume5=int(tick_data.get('bidVol5', 0)),

            # 卖盘
            ask_price1=float(tick_data.get('askPrice1', 0)),
            ask_volume1=int(tick_data.get('askVol1', 0)),
            ask_price2=float(tick_data.get('askPrice2', 0)),
            ask_volume2=int(tick_data.get('askVol2', 0)),
            ask_price3=float(tick_data.get('askPrice3', 0)),
            ask_volume3=int(tick_data.get('askVol3', 0)),
            ask_price4=float(tick_data.get('askPrice4', 0)),
            ask_volume4=int(tick_data.get('askVol4', 0)),
            ask_price5=float(tick_data.get('askPrice5', 0)),
            ask_volume5=int(tick_data.get('askVol5', 0)),

            # L2扩展档位 (需要L2权限)
            bid_price6=float(tick_data.get('bidPrice6', 0)),
            bid_volume6=int(tick_data.get('bidVol6', 0)),
            bid_price7=float(tick_data.get('bidPrice7', 0)),
            bid_volume7=int(tick_data.get('bidVol7', 0)),
            bid_price8=float(tick_data.get('bidPrice8', 0)),
            bid_volume8=int(tick_data.get('bidVol8', 0)),
            bid_price9=float(tick_data.get('bidPrice9', 0)),
            bid_volume9=int(tick_data.get('bidVol9', 0)),
            bid_price10=float(tick_data.get('bidPrice10', 0)),
            bid_volume10=int(tick_data.get('bidVol10', 0)),

            ask_price6=float(tick_data.get('askPrice6', 0)),
            ask_volume6=int(tick_data.get('askVol6', 0)),
            ask_price7=float(tick_data.get('askPrice7', 0)),
            ask_volume7=int(tick_data.get('askVol7', 0)),
            ask_price8=float(tick_data.get('askPrice8', 0)),
            ask_volume8=int(tick_data.get('askVol8', 0)),
            ask_price9=float(tick_data.get('askPrice9', 0)),
            ask_volume9=int(tick_data.get('askVol9', 0)),
            ask_price10=float(tick_data.get('askPrice10', 0)),
            ask_volume10=int(tick_data.get('askVol10', 0)),

            updated_time=now
        )

    def _get_tick_direction(self, row) -> str:
        """判断逐笔成交方向"""
        # 根据成交价与买卖价判断
        last_price = row.get('lastPrice', 0)
        bid_price = row.get('bidPrice1', 0)
        ask_price = row.get('askPrice1', 0)

        if bid_price and ask_price:
            mid_price = (bid_price + ask_price) / 2
            if last_price >= mid_price:
                return "buy"
            else:
                return "sell"
        return "neutral"

    def _get_order_type(self, row) -> str:
        """判断订单类型"""
        volume = row.get('lastVolume', 0)
        # 简单判断：大于10万股为大单
        if volume >= 100000:
            return "block"
        elif volume >= 10000:
            return "large"
        return "normal"

    async def get_index_quotes(self, index_codes: Optional[List[str]] = None) -> IndexQuoteListResponse:
        """
        获取主要指数行情

        Args:
            index_codes: 指数代码列表，如 ['sh', 'sz', 'cy', 'hs300']，为空则获取所有主要指数
        """
        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 确定要获取的指数
        if index_codes:
            codes_to_fetch = [INDEX_CODES.get(code, code) for code in index_codes if code in INDEX_CODES or '.' in code]
        else:
            codes_to_fetch = list(INDEX_CODES.values())

        # 获取行情数据
        full_tick = xtdata.get_full_tick(codes_to_fetch)

        indexes = []
        for short_code, full_code in INDEX_CODES.items():
            if full_code in full_tick:
                tick_data = full_tick[full_code]
                index_quote = self._convert_index_quote(short_code, full_code, tick_data)
                indexes.append(index_quote)

        return IndexQuoteListResponse(indexes=indexes, count=len(indexes))

    def _convert_index_quote(self, short_code: str, full_code: str, tick_data) -> IndexQuote:
        """转换指数行情数据"""
        now = datetime.now()

        last_price = float(tick_data.get('lastPrice', 0))
        pre_close = float(tick_data.get('lastClose', 0))

        # 计算涨跌幅
        if pre_close > 0:
            change = (last_price - pre_close) / pre_close * 100
            change_amount = last_price - pre_close
        else:
            change = 0.0
            change_amount = 0.0

        # 指数名称映射
        index_names = {
            "sh": "上证指数",
            "sz": "深证成指",
            "cy": "创业板指",
            "hs300": "沪深300",
            "zz500": "中证500",
            "sz50": "上证50",
        }

        return IndexQuote(
            code=short_code,
            name=index_names.get(short_code, tick_data.get('stock_name', full_code)),
            price=last_price,
            change=change,
            change_amount=change_amount,
            pre_close=pre_close,
            open=float(tick_data.get('open', 0)),
            high=float(tick_data.get('high', 0)),
            low=float(tick_data.get('low', 0)),
            volume=int(tick_data.get('volume', 0)),
            amount=float(tick_data.get('amount', 0)),
            updated_time=now
        )


# 单例
quote_service = QuoteService()


class StockSearchResult:
    """股票搜索结果"""
    code: str
    name: str
    exchange: str

    def __init__(self, code: str, name: str, exchange: str):
        self.code = code
        self.name = name
        self.exchange = exchange

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "exchange": self.exchange
        }


class StockSearchService:
    """股票搜索服务"""

    _stock_list_cache: List[dict] = []
    _cache_loaded: bool = False

    async def _load_stock_list(self) -> List[dict]:
        """加载股票列表（从QMT获取）"""
        if self._cache_loaded:
            return self._stock_list_cache

        if not QMTClientManager.is_connected():
            raise RuntimeError("QMT未连接，请先启动QMT客户端并登录账号")

        from xtquant import xtdata

        # 获取沪深A股列表
        stock_codes = xtdata.get_stock_list_in_sector("沪深A股")

        stocks = []
        for code in stock_codes:
            try:
                # 获取股票详情
                detail = xtdata.get_instrument_detail(code)
                if detail:
                    name = detail.get('InstrumentName', '')
                    exchange = 'SH' if code.endswith('.SH') else 'SZ'
                    stocks.append({
                        "code": code,
                        "name": name,
                        "exchange": exchange,
                        "code_simple": code.split('.')[0]  # 去掉后缀的代码
                    })
            except Exception as e:
                logger.warning(f"获取股票 {code} 详情失败: {e}")

        self._stock_list_cache = stocks
        self._cache_loaded = True
        logger.info(f"已加载 {len(stocks)} 只股票信息")

        return stocks

    async def search_by_name(self, keyword: str, limit: int = 10) -> List[dict]:
        """
        根据名称搜索股票

        Args:
            keyword: 搜索关键词（股票名称或代码）
            limit: 返回数量限制

        Returns:
            匹配的股票列表
        """
        stocks = await self._load_stock_list()
        keyword_upper = keyword.upper()

        results = []
        for stock in stocks:
            # 匹配名称或代码
            name = stock.get('name', '').upper()
            code = stock.get('code_simple', '').upper()
            full_code = stock.get('code', '').upper()

            if keyword_upper in name or name in keyword_upper or keyword_upper in code or keyword_upper in full_code:
                results.append(stock)

            if len(results) >= limit:
                break

        return results

    async def get_stock_code_by_name(self, name: str) -> Optional[str]:
        """
        根据名称获取股票代码

        Args:
            name: 股票名称

        Returns:
            股票代码（如 000001.SZ），找不到返回 None
        """
        results = await self.search_by_name(name, limit=1)
        if results:
            return results[0].get('code')
        return None

    def clear_cache(self):
        """清除缓存"""
        self._stock_list_cache = []
        self._cache_loaded = False


# 单例
stock_search_service = StockSearchService()