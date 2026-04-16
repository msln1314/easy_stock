"""
MCP Server - FastMCP implementation for factor-service

提供 MCP 协议支持，使用 SSE (Server-Sent Events) 传输
"""
from fastmcp import FastMCP

from app.mcp.indicator_mcp import indicator_mcp
from app.mcp.factor_mcp import factor_mcp
from app.mcp.backtest_mcp import backtest_mcp

# Create FastMCP server
mcp = FastMCP("factor-service")


# ==================== Indicator Tools ====================

@mcp.tool()
async def indicator_calculate(
    stock_code: str,
    indicators: list,
    period: str = "1d",
    start_date: str = None,
    end_date: str = None,
    kline_data: list = None
) -> dict:
    """计算单只股票的技术指标

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        indicators: 指标列表，如 ["MA5", "MA10", "RSI14", "MACD_DIF"]
        period: 周期，可选 1d/1w/1m/5m/15m/30m/60m
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        kline_data: K线数据（可选，不传则需从 stock-service 获取）

    Returns:
        包含指标计算结果的字典
    """
    return await indicator_mcp.calculate(
        stock_code=stock_code,
        indicators=indicators,
        period=period,
        start_date=start_date,
        end_date=end_date,
        kline_data=kline_data
    )


@mcp.tool()
async def indicator_batch(
    stock_codes: list,
    indicators: list,
    date: str = None,
    kline_data_map: dict = None
) -> dict:
    """批量计算多只股票的指标

    Args:
        stock_codes: 股票代码列表
        indicators: 指标列表
        date: 日期 YYYYMMDD
        kline_data_map: 各股票K线数据映射 {stock_code: [kline_data]}

    Returns:
        批量计算结果
    """
    return await indicator_mcp.batch(
        stock_codes=stock_codes,
        indicators=indicators,
        date=date,
        kline_data_map=kline_data_map
    )


@mcp.tool()
async def indicator_list() -> list:
    """获取支持的指标列表

    Returns:
        指标定义列表，包含 indicator_id, indicator_name, category, description 等
    """
    return await indicator_mcp.list_indicators()


# ==================== Factor Tools ====================

@mcp.tool()
async def factor_screen(
    conditions: list,
    stock_pool: list = None,
    date: str = None,
    limit: int = 50,
    stock_data_map: dict = None
) -> dict:
    """因子选股

    Args:
        conditions: 筛选条件列表，每个条件包含 factor_id, operator, value
            operator 可选：gt(大于)/lt(小于)/ge(大于等于)/le(小于等于)/eq(等于)/between
        stock_pool: 股票池（可选，默认全A股）
        date: 日期 YYYYMMDD
        limit: 返回数量限制
        stock_data_map: 各股票K线数据映射

    Returns:
        选股结果，包含筛选出的股票列表及各因子值
    """
    return await factor_mcp.screen(
        conditions=conditions,
        stock_pool=stock_pool,
        date=date,
        limit=limit,
        stock_data_map=stock_data_map
    )


@mcp.tool()
async def factor_score(
    stock_codes: list,
    weights: list,
    date: str = None,
    stock_data_map: dict = None
) -> dict:
    """综合评分计算

    Args:
        stock_codes: 股票代码列表
        weights: 评分权重配置，每个包含 factor_id, weight(0-1), direction(high/low)
        date: 日期 YYYYMMDD
        stock_data_map: 各股票K线数据映射

    Returns:
        评分结果，包含各股票综合评分和排名
    """
    return await factor_mcp.score(
        stock_codes=stock_codes,
        weights=weights,
        date=date,
        stock_data_map=stock_data_map
    )


@mcp.tool()
async def factor_value(
    stock_code: str,
    factor_id: str,
    date: str = None,
    kline_data: list = None
) -> dict:
    """获取单只股票因子值

    Args:
        stock_code: 股票代码
        factor_id: 因子ID，如 RSI14, MA5_MA10
        date: 日期 YYYYMMDD
        kline_data: K线数据

    Returns:
        因子值结果
    """
    return await factor_mcp.value(
        stock_code=stock_code,
        factor_id=factor_id,
        date=date,
        kline_data=kline_data
    )


# ==================== Backtest Tools ====================

@mcp.tool()
async def backtest_run(
    conditions: list,
    start_date: str,
    end_date: str,
    weights: list = None,
    rebalance_freq: str = "daily",
    top_n: int = 10,
    benchmark: str = "000300.SH",
    historical_data: dict = None
) -> dict:
    """执行完整回测

    Args:
        conditions: 筛选条件列表
        weights: 评分权重（可选）
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        rebalance_freq: 调仓频率 daily/weekly/monthly
        top_n: 持仓数量
        benchmark: 基准指数代码
        historical_data: 历史K线数据

    Returns:
        回测报告，包含累计收益、最大回撤、胜率、夏普比率等
    """
    return await backtest_mcp.run(
        conditions=conditions,
        weights=weights,
        start_date=start_date,
        end_date=end_date,
        rebalance_freq=rebalance_freq,
        top_n=top_n,
        benchmark=benchmark,
        historical_data=historical_data
    )


@mcp.tool()
async def backtest_ic(
    factor_id: str,
    start_date: str,
    end_date: str,
    forward_period: int = 5,
    factor_data: dict = None,
    return_data: dict = None
) -> dict:
    """IC分析 - 因子值与未来收益相关性

    Args:
        factor_id: 因子ID
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        forward_period: 预测周期（天）
        factor_data: 因子数据 {date: {stock_code: value}}
        return_data: 收益数据 {date: {stock_code: return}}

    Returns:
        IC分析结果，包含 ic_mean, ic_std, icir, ic_series
    """
    return await backtest_mcp.ic(
        factor_id=factor_id,
        start_date=start_date,
        end_date=end_date,
        forward_period=forward_period,
        factor_data=factor_data,
        return_data=return_data
    )


@mcp.tool()
async def backtest_group(
    factor_id: str,
    start_date: str,
    end_date: str,
    num_groups: int = 5,
    factor_data: dict = None,
    return_data: dict = None
) -> dict:
    """分组收益对比 - 按因子值分组比较各组收益

    Args:
        factor_id: 因子ID
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        num_groups: 分组数量（默认5组）
        factor_data: 因子数据 {stock_code: value}
        return_data: 收益数据 {stock_code: return}

    Returns:
        分组收益结果，包含各组收益和最高/最低组差值
    """
    return await backtest_mcp.group(
        factor_id=factor_id,
        start_date=start_date,
        end_date=end_date,
        num_groups=num_groups,
        factor_data=factor_data,
        return_data=return_data
    )


@mcp.tool()
async def backtest_sensitivity(
    conditions: list,
    param_ranges: dict,
    start_date: str,
    end_date: str,
    historical_data: dict = None
) -> dict:
    """敏感性测试 - 不同参数组合的回测对比

    Args:
        conditions: 筛选条件
        param_ranges: 参数变化范围 {param_name: [values]}
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        historical_data: 历史数据

    Returns:
        敏感性测试结果，包含各参数组合的回测结果和最佳参数
    """
    return await backtest_mcp.sensitivity(
        conditions=conditions,
        param_ranges=param_ranges,
        start_date=start_date,
        end_date=end_date,
        historical_data=historical_data
    )


# Export for use in main.py
mcp_server = mcp