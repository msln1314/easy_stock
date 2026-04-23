# backend/stock-service/app/mcp_server.py
"""
MCP Server - FastMCP implementation for stock-service

提供真正的 MCP 协议支持，使用 SSE (Server-Sent Events) 传输。
"""

from fastmcp import FastMCP

# Import existing MCP classes
from app.mcp.stock_mcp import StockMCP
from app.mcp.index_mcp import IndexMCP
from app.mcp.sector_mcp import SectorMCP
from app.mcp.sentiment_mcp import SentimentMCP
from app.mcp.technical_mcp import TechnicalMCP
from app.mcp.news_mcp import NewsMCP

# Create MCP instances
stock_mcp = StockMCP()
index_mcp = IndexMCP()
sector_mcp = SectorMCP()
sentiment_mcp = SentimentMCP()
technical_mcp = TechnicalMCP()
news_mcp = NewsMCP()

# Create FastMCP server
mcp = FastMCP("stock-service")


# ==================== Stock Tools ====================

@mcp.tool()
async def get_stock_info(stock_code: str) -> dict:
    """获取个股基本信息

    Args:
        stock_code: 股票代码，如"000001"（平安银行）、"600000"（浦发银行）等

    Returns:
        包含个股基本信息：总市值、流通市值、行业、上市时间、股票代码、股票简称等
    """
    return await stock_mcp.get_stock_info(stock_code)


@mcp.tool()
async def get_stock_quote(stock_code: str) -> dict:
    """获取个股实时行情

    Args:
        stock_code: 股票代码，如"000001"

    Returns:
        包含个股实时行情：最新价、开盘价、最高价、最低价、成交量等
    """
    return await stock_mcp.get_stock_quote(stock_code)


@mcp.tool()
async def get_stock_history(
    stock_code: str,
    period: str = "daily",
    start_date: str = None,
    end_date: str = None
) -> list:
    """获取个股历史行情

    Args:
        stock_code: 股票代码
        period: 周期，可选 daily, weekly, monthly
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD

    Returns:
        历史行情数据列表
    """
    return await stock_mcp.get_stock_history(stock_code, period, start_date, end_date)


@mcp.tool()
async def get_stock_financial(stock_code: str) -> dict:
    """获取个股财务信息

    Args:
        stock_code: 股票代码

    Returns:
        财务信息字典
    """
    return await stock_mcp.get_stock_financial(stock_code)


@mcp.tool()
async def get_stock_fund_flow(stock_code: str) -> dict:
    """获取个股资金流向

    Args:
        stock_code: 股票代码

    Returns:
        资金流向数据
    """
    return await stock_mcp.get_stock_fund_flow(stock_code)


@mcp.tool()
async def get_stock_margin(stock_code: str) -> dict:
    """获取个股融资融券信息

    Args:
        stock_code: 股票代码

    Returns:
        融资融券信息
    """
    return await stock_mcp.get_stock_margin(stock_code)


# ==================== Index Tools ====================

@mcp.tool()
async def get_index_quotes(symbol: str = "沪深重要指数") -> list:
    """获取指数实时行情列表

    Args:
        symbol: 指数类型，可选值：
            "沪深重要指数", "上证系列指数", "深证系列指数", "指数成份", "中证系列指数"

    Returns:
        指数实时行情数据列表
    """
    return await index_mcp.get_index_quotes(symbol)


@mcp.tool()
async def get_index_quote(index_code: str) -> dict:
    """获取单个指数的实时行情

    Args:
        index_code: 指数代码，如"000001"（上证指数）

    Returns:
        指数实时行情数据
    """
    return await index_mcp.get_index_quote(index_code)


# ==================== Sector Tools ====================

@mcp.tool()
async def get_concept_boards() -> list:
    """获取概念板块列表及实时行情

    Returns:
        概念板块列表
    """
    return await sector_mcp.get_concept_boards()


@mcp.tool()
async def get_concept_board(board_code: str) -> dict:
    """获取单个概念板块的实时行情

    Args:
        board_code: 板块代码，如"BK0892"

    Returns:
        概念板块数据
    """
    return await sector_mcp.get_concept_board(board_code)


@mcp.tool()
async def get_concept_board_constituents(symbol: str) -> list:
    """获取概念板块成份股

    Args:
        symbol: 板块名称或代码，如"融资融券"或"BK0655"

    Returns:
        概念板块成份股列表
    """
    return await sector_mcp.get_concept_board_constituents(symbol)


@mcp.tool()
async def get_industry_boards() -> list:
    """获取行业板块列表及实时行情

    Returns:
        行业板块列表
    """
    return await sector_mcp.get_industry_boards()


@mcp.tool()
async def get_industry_board(board_code: str) -> dict:
    """获取单个行业板块的实时行情

    Args:
        board_code: 板块代码，如"BK0437"

    Returns:
        行业板块数据
    """
    return await sector_mcp.get_industry_board(board_code)


@mcp.tool()
async def get_industry_board_constituents(symbol: str) -> list:
    """获取行业板块成份股

    Args:
        symbol: 板块名称或代码，如"小金属"或"BK1027"

    Returns:
        行业板块成份股列表
    """
    return await sector_mcp.get_industry_board_constituents(symbol)


# ==================== Sentiment Tools ====================

@mcp.tool()
async def get_margin_details(trade_date: str) -> list:
    """获取融资融券明细数据

    Args:
        trade_date: 交易日期，格式为"YYYYMMDD"，如"20230922"

    Returns:
        融资融券明细数据列表
    """
    return await sentiment_mcp.get_margin_details(trade_date)


@mcp.tool()
async def get_stock_hot_rank() -> list:
    """获取股票热度排名数据

    Returns:
        股票热度排名数据列表
    """
    return await sentiment_mcp.get_stock_hot_rank()


@mcp.tool()
async def get_stock_hot_up_rank() -> list:
    """获取股票飙升榜数据

    Returns:
        股票飙升榜数据列表
    """
    return await sentiment_mcp.get_stock_hot_up_rank()


@mcp.tool()
async def get_stock_hot_keywords(symbol: str) -> list:
    """获取股票热门关键词

    Args:
        symbol: 股票代码，如"SZ000665"

    Returns:
        股票热门关键词数据列表
    """
    return await sentiment_mcp.get_stock_hot_keywords(symbol)


# ==================== Technical Tools ====================

@mcp.tool()
async def get_chip_distribution(symbol: str, adjust: str = "") -> list:
    """获取股票筹码分布数据

    Args:
        symbol: 股票代码，如"000001"
        adjust: 复权类型，可选值为"qfq"(前复权)、"hfq"(后复权)、""(不复权)

    Returns:
        筹码分布数据列表
    """
    return await technical_mcp.get_chip_distribution(symbol, adjust)


# ==================== News Tools ====================

@mcp.tool()
async def get_interactive_questions(symbol: str) -> list:
    """获取互动易提问数据

    Args:
        symbol: 股票代码，如"002594"

    Returns:
        互动易提问数据列表
    """
    return await news_mcp.get_interactive_questions(symbol)


@mcp.tool()
async def get_cls_telegraph(symbol: str = "全部") -> list:
    """获取财联社电报数据

    Args:
        symbol: 类型，可选值为"全部"或"重点"

    Returns:
        财联社电报数据列表
    """
    return await news_mcp.get_cls_telegraph(symbol)


@mcp.tool()
async def get_global_finance_news() -> list:
    """获取全球财经快讯数据

    Returns:
        全球财经快讯数据列表
    """
    return await news_mcp.get_global_finance_news()


# Export for use in main.py
mcp_server = mcp