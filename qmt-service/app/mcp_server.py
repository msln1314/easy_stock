# backend/qmt-service/app/mcp_server.py
"""
MCP Server - FastMCP implementation for qmt-service

提供真正的 MCP 协议支持，使用 SSE (Server-Sent Events) 传输。
"""

from fastmcp import FastMCP

# 导入现有 MCP 单例实例
from app.mcp.trade_mcp import trade_mcp
from app.mcp.position_mcp import position_mcp
from app.mcp.quote_mcp import quote_mcp
from app.mcp.factor_mcp import factor_mcp

# Create FastMCP server
mcp = FastMCP("qmt-service")


# ==================== Trade Tools ====================

@mcp.tool()
async def trade_buy(
    stock_code: str,
    price: float,
    quantity: int,
    order_type: str = "limit"
) -> dict:
    """买入股票

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        price: 委托价格（市价单可传0）
        quantity: 委托数量，必须为100的整数倍
        order_type: 委托类型，"limit"为限价单，"market"为市价单

    Returns:
        包含订单信息的结果字典，包括order_id、stock_code、status等
    """
    return await trade_mcp.buy_stock(stock_code, price, quantity, order_type)


@mcp.tool()
async def trade_sell(
    stock_code: str,
    price: float,
    quantity: int,
    order_type: str = "limit"
) -> dict:
    """卖出股票

    Args:
        stock_code: 股票代码
        price: 委托价格（市价单可传0）
        quantity: 委托数量，必须为100的整数倍
        order_type: 委托类型，"limit"或"market"

    Returns:
        包含订单信息的结果字典
    """
    return await trade_mcp.sell_stock(stock_code, price, quantity, order_type)


@mcp.tool()
async def trade_cancel(order_id: str) -> dict:
    """撤销委托订单

    Args:
        order_id: 订单ID

    Returns:
        撤单结果，包含order_id、success、message
    """
    return await trade_mcp.cancel_order(order_id)


@mcp.tool()
async def trade_get_orders(status: str = None) -> list:
    """查询委托订单列表

    Args:
        status: 可选的状态筛选，如 "pending", "filled", "cancelled"

    Returns:
        委托订单列表
    """
    return await trade_mcp.get_orders(status)


@mcp.tool()
async def trade_get_order(order_id: str) -> dict:
    """查询单个委托订单

    Args:
        order_id: 订单ID

    Returns:
        订单详情，不存在则返回null
    """
    result = await trade_mcp.get_order(order_id)
    return result if result else None


# ==================== Position Tools ====================

@mcp.tool()
async def position_list() -> dict:
    """查询持仓列表

    Returns:
        持仓信息，包含positions列表、total_market_value、total_profit等
    """
    return await position_mcp.get_positions()


@mcp.tool()
async def position_balance() -> dict:
    """查询资金余额

    Returns:
        资金信息，包含total_asset、available_cash、market_value等
    """
    return await position_mcp.get_balance()


@mcp.tool()
async def position_trades(
    date: str = None,
    stock_code: str = None
) -> dict:
    """查询成交记录

    Args:
        date: 日期筛选，格式YYYYMMDD
        stock_code: 股票代码筛选

    Returns:
        成交记录列表
    """
    return await position_mcp.get_trades(date, stock_code)


@mcp.tool()
async def position_today_trades() -> dict:
    """查询今日成交记录

    Returns:
        今日成交记录列表
    """
    return await position_mcp.get_today_trades()


@mcp.tool()
async def position_today_entrusts() -> dict:
    """查询今日委托

    Returns:
        今日委托记录列表
    """
    return await position_mcp.get_today_entrusts()


# ==================== Quote Tools ====================

@mcp.tool()
async def quote_get(stock_code: str) -> dict:
    """获取单只股票实时行情

    Args:
        stock_code: 股票代码，如 "000001.SZ"

    Returns:
        实时行情数据，包含price、open、high、low、volume等
    """
    result = await quote_mcp.get_quote(stock_code)
    return result if result else {"error": "未找到行情数据"}


@mcp.tool()
async def quote_batch(stock_codes: list) -> dict:
    """批量获取实时行情

    Args:
        stock_codes: 股票代码列表

    Returns:
        批量行情数据，包含quotes列表和count
    """
    return await quote_mcp.get_quotes(stock_codes)


@mcp.tool()
async def quote_kline(
    stock_code: str,
    period: str = "1d",
    count: int = 100,
    start_time: str = None,
    end_time: str = None
) -> dict:
    """获取K线数据

    Args:
        stock_code: 股票代码
        period: 周期，可选 1d/1w/1m/5m/15m/30m/60m
        count: 返回条数
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        K线数据，包含klines列表
    """
    return await quote_mcp.get_kline(stock_code, period, count, start_time, end_time)


@mcp.tool()
async def quote_minute(
    stock_code: str,
    date: str = None
) -> dict:
    """获取分时数据

    Args:
        stock_code: 股票代码
        date: 日期，格式YYYYMMDD，不传则获取今日

    Returns:
        分时数据列表
    """
    return await quote_mcp.get_minute_bars(stock_code, date)


@mcp.tool()
async def quote_depth(stock_code: str) -> dict:
    """获取订单簿深度

    Args:
        stock_code: 股票代码

    Returns:
        订单簿深度数据，包含bid_levels和ask_levels
    """
    return await quote_mcp.get_depth(stock_code)


@mcp.tool()
async def quote_ticks(
    stock_code: str,
    start_time: str = None,
    end_time: str = None,
    count: int = 100
) -> dict:
    """获取逐笔成交数据

    Args:
        stock_code: 股票代码
        start_time: 开始时间
        end_time: 结束时间
        count: 返回条数

    Returns:
        逐笔成交数据列表
    """
    return await quote_mcp.get_ticks(stock_code, start_time, end_time, count)


@mcp.tool()
async def quote_indexes(index_codes: list = None) -> dict:
    """获取主要指数行情

    Args:
        index_codes: 指数代码列表，如 ['sh', 'sz', 'cy', 'hs300']，不传则获取所有主要指数

    Returns:
        指数行情数据列表
    """
    return await quote_mcp.get_index_quotes(index_codes)


# ==================== Factor Tools ====================

@mcp.tool()
async def factor_list(
    category: str = None,
    keyword: str = None
) -> dict:
    """获取因子列表

    Args:
        category: 因子类别筛选，如 "trend", "momentum", "volatility"
        keyword: 关键词搜索

    Returns:
        因子列表，包含factors和total
    """
    return await factor_mcp.get_factor_list(category, keyword)


@mcp.tool()
async def factor_screen(
    factors: list,
    date: str = None,
    limit: int = 50
) -> dict:
    """因子选股

    Args:
        factors: 筛选条件列表，每个包含factor_id、op、value
        date: 日期，格式YYYYMMDD，不传则使用今日
        limit: 返回数量限制

    Returns:
        选股结果，包含stocks列表
    """
    return await factor_mcp.screen_stocks(factors, date, limit)


@mcp.tool()
async def factor_get_info(factor_id: str) -> dict:
    """获取因子详情

    Args:
        factor_id: 因子ID，如 "MA5", "PE", "RSI6"

    Returns:
        因子详情字典，不存在则返回null
    """
    result = await factor_mcp.get_factor_info(factor_id)
    return result if result else None


# Export for use in main.py
mcp_server = mcp