# backend/qmt-service/app/mcp/router.py
"""
MCP路由注册

将所有MCP接口注册到统一的路由器
"""
from fastapi import APIRouter, Body, Depends

from app.mcp.trade_mcp import trade_mcp
from app.mcp.position_mcp import position_mcp
from app.mcp.quote_mcp import quote_mcp
from app.core.auth import verify_api_key

mcp_router = APIRouter(prefix="/mcp", tags=["MCP接口"], dependencies=[Depends(verify_api_key)])

# ==================== 交易MCP路由 ====================

@mcp_router.post("/trade/buy")
async def mcp_buy_stock(
    stock_code: str = Body(...),
    price: float = Body(...),
    quantity: int = Body(...),
    order_type: str = Body(default="limit")
):
    """
    MCP买入股票

    Args:
        stock_code: 股票代码
        price: 委托价格
        quantity: 委托数量
        order_type: 委托类型 limit/market
    """
    return await trade_mcp.buy_stock(stock_code, price, quantity, order_type)


@mcp_router.post("/trade/sell")
async def mcp_sell_stock(
    stock_code: str = Body(...),
    price: float = Body(...),
    quantity: int = Body(...),
    order_type: str = Body(default="limit")
):
    """
    MCP卖出股票
    """
    return await trade_mcp.sell_stock(stock_code, price, quantity, order_type)


@mcp_router.post("/trade/cancel/{order_id}")
async def mcp_cancel_order(order_id: str):
    """
    MCP撤销委托
    """
    return await trade_mcp.cancel_order(order_id)


@mcp_router.get("/trade/orders")
async def mcp_get_orders(status: str = None):
    """
    MCP查询委托列表
    """
    return await trade_mcp.get_orders(status)


@mcp_router.get("/trade/order/{order_id}")
async def mcp_get_order(order_id: str):
    """
    MCP查询单个委托
    """
    return await trade_mcp.get_order(order_id)


# ==================== 持仓MCP路由 ====================

@mcp_router.get("/position/list")
async def mcp_get_positions():
    """
    MCP查询持仓列表
    """
    return await position_mcp.get_positions()


@mcp_router.get("/position/balance")
async def mcp_get_balance():
    """
    MCP查询资金余额
    """
    return await position_mcp.get_balance()


@mcp_router.get("/position/trades")
async def mcp_get_trades(date: str = None, stock_code: str = None):
    """
    MCP查询成交记录
    """
    return await position_mcp.get_trades(date, stock_code)


@mcp_router.get("/position/trades/today")
async def mcp_get_today_trades():
    """
    MCP查询今日成交
    """
    return await position_mcp.get_today_trades()


@mcp_router.get("/position/entrusts/today")
async def mcp_get_today_entrusts():
    """
    MCP查询今日委托
    """
    return await position_mcp.get_today_entrusts()


# ==================== 行情MCP路由 ====================

@mcp_router.get("/quote/{stock_code}")
async def mcp_get_quote(stock_code: str):
    """
    MCP获取单只股票实时行情
    """
    return await quote_mcp.get_quote(stock_code)


@mcp_router.post("/quote/batch")
async def mcp_get_quotes(stock_codes: list):
    """
    MCP批量获取实时行情
    """
    return await quote_mcp.get_quotes(stock_codes)


@mcp_router.get("/quote/kline/{stock_code}")
async def mcp_get_kline(
    stock_code: str,
    period: str = "1d",
    count: int = 100,
    start_time: str = None,
    end_time: str = None
):
    """
    MCP获取K线数据

    Args:
        stock_code: 票代码
        period: 周期 (1d/1w/1m/5m/15m/30m/60m)
        count: 返回条数
        start_time: 开始时间
        end_time: 结束时间
    """
    return await quote_mcp.get_kline(stock_code, period, count, start_time, end_time)


@mcp_router.get("/quote/minute/{stock_code}")
async def mcp_get_minute_bars(stock_code: str, date: str = None):
    """
    MCP获取分时数据
    """
    return await quote_mcp.get_minute_bars(stock_code, date)


@mcp_router.get("/quote/depth/{stock_code}")
async def mcp_get_depth(stock_code: str):
    """
    MCP获取订单簿深度
    """
    return await quote_mcp.get_depth(stock_code)


@mcp_router.get("/quote/ticks/{stock_code}")
async def mcp_get_ticks(
    stock_code: str,
    start_time: str = None,
    end_time: str = None,
    count: int = 100
):
    """
    MCP获取逐笔成交
    """
    return await quote_mcp.get_ticks(stock_code, start_time, end_time, count)


@mcp_router.get("/quote/indexes")
async def mcp_get_index_quotes(index_codes: list = None):
    """
    MCP获取主要指数行情
    """
    return await quote_mcp.get_index_quotes(index_codes)


@mcp_router.get("/quote/search")
async def mcp_search_stock(keyword: str, limit: int = 10):
    """
    MCP搜索股票（根据名称或代码）

    Args:
        keyword: 搜索关键词（股票名称或代码，如 "九联"、"平安"、"000001"）
        limit: 返回数量限制，默认10

    Returns:
        匹配的股票列表，包含代码、名称、交易所等信息
    """
    return await quote_mcp.search_stock(keyword, limit)