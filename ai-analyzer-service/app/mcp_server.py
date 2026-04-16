"""
MCP Server - FastMCP implementation for ai-analyzer-service

提供 MCP 协议支持，使用 SSE (Server-Sent Events) 传输
"""
from fastmcp import FastMCP

from app.mcp.trend_mcp import trend_mcp
from app.mcp.risk_mcp import risk_mcp
from app.mcp.advice_mcp import advice_mcp
from app.mcp.model_mcp import model_mcp

# Create FastMCP server
mcp = FastMCP("ai-analyzer-service")


# ==================== Trend Tools ====================

@mcp.tool()
async def ai_trend_analyze(
    stock_code: str,
    analysis_type: str = "comprehensive",
    include_indicators: list = None,
    model: str = None,
    stock_name: str = None,
    kline_data: list = None
) -> dict:
    """分析单只股票趋势

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        analysis_type: 分析类型 comprehensive/short_term/mid_term/long_term
        include_indicators: 包含的指标列表
        model: AI模型名称
        stock_name: 股票名称
        kline_data: K线数据

    Returns:
        包含趋势分析结果的字典
    """
    return await trend_mcp.analyze(
        stock_code=stock_code,
        analysis_type=analysis_type,
        include_indicators=include_indicators,
        model=model,
        stock_name=stock_name,
        kline_data=kline_data
    )


@mcp.tool()
async def ai_trend_batch(
    stock_codes: list,
    analysis_type: str = "comprehensive",
    model: str = None,
    stock_data_map: dict = None
) -> dict:
    """批量趋势分析

    Args:
        stock_codes: 股票代码列表
        analysis_type: 分析类型
        model: AI模型名称
        stock_data_map: 各股票K线数据映射

    Returns:
        批量趋势分析结果
    """
    return await trend_mcp.batch(
        stock_codes=stock_codes,
        analysis_type=analysis_type,
        model=model,
        stock_data_map=stock_data_map
    )


# ==================== Risk Tools ====================

@mcp.tool()
async def ai_risk_assess(
    stock_code: str,
    assessment_type: str = "comprehensive",
    model: str = None,
    stock_name: str = None,
    kline_data: list = None,
    backtest_data: dict = None
) -> dict:
    """单只股票风险评估

    Args:
        stock_code: 股票代码
        assessment_type: 评估类型 comprehensive/volatility/drawdown/liquidity
        model: AI模型名称
        stock_name: 股票名称
        kline_data: K线数据
        backtest_data: 回测数据

    Returns:
        风险评估结果
    """
    return await risk_mcp.assess(
        stock_code=stock_code,
        assessment_type=assessment_type,
        model=model,
        stock_name=stock_name,
        kline_data=kline_data,
        backtest_data=backtest_data
    )


@mcp.tool()
async def ai_risk_portfolio(
    stock_codes: list,
    weights: list = None,
    model: str = None,
    stock_data_map: dict = None
) -> dict:
    """组合风险评估

    Args:
        stock_codes: 股票代码列表
        weights: 权重列表
        model: AI模型名称
        stock_data_map: 各股票K线数据映射

    Returns:
        组合风险评估结果
    """
    return await risk_mcp.portfolio(
        stock_codes=stock_codes,
        weights=weights,
        model=model,
        stock_data_map=stock_data_map
    )


@mcp.tool()
async def ai_risk_compare(
    stock_codes: list,
    model: str = None,
    stock_data_map: dict = None
) -> dict:
    """多股风险对比

    Args:
        stock_codes: 股票代码列表
        model: AI模型名称
        stock_data_map: 各股票K线数据映射

    Returns:
        风险对比结果
    """
    return await risk_mcp.compare(
        stock_codes=stock_codes,
        model=model,
        stock_data_map=stock_data_map
    )


# ==================== Advice Tools ====================

@mcp.tool()
async def ai_advice_generate(
    stock_code: str,
    advice_type: str = "comprehensive",
    include_backtest: bool = True,
    model: str = None,
    stock_name: str = None,
    kline_data: list = None
) -> dict:
    """生成投资建议

    Args:
        stock_code: 股票代码
        advice_type: 建议类型 comprehensive/buy/sell/hold
        include_backtest: 是否包含回测数据
        model: AI模型名称
        stock_name: 股票名称
        kline_data: K线数据

    Returns:
        投资建议结果
    """
    return await advice_mcp.generate(
        stock_code=stock_code,
        advice_type=advice_type,
        include_backtest=include_backtest,
        model=model,
        stock_name=stock_name,
        kline_data=kline_data
    )


@mcp.tool()
async def ai_advice_batch(
    stock_codes: list,
    advice_type: str = "comprehensive",
    model: str = None,
    stock_data_map: dict = None
) -> dict:
    """批量投资建议

    Args:
        stock_codes: 股票代码列表
        advice_type: 建议类型
        model: AI模型名称
        stock_data_map: 各股票K线数据映射

    Returns:
        批量投资建议结果
    """
    return await advice_mcp.batch(
        stock_codes=stock_codes,
        advice_type=advice_type,
        model=model,
        stock_data_map=stock_data_map
    )


@mcp.tool()
async def ai_advice_report(
    stock_codes: list,
    report_type: str = "portfolio",
    model: str = None,
    stock_data_map: dict = None
) -> dict:
    """生成分析报告

    Args:
        stock_codes: 股票代码列表
        report_type: 报告类型 portfolio/watchlist/custom
        model: AI模型名称
        stock_data_map: 各股票K线数据映射

    Returns:
        分析报告结果
    """
    return await advice_mcp.report(
        stock_codes=stock_codes,
        report_type=report_type,
        model=model,
        stock_data_map=stock_data_map
    )


# ==================== Model Tools ====================

@mcp.tool()
def ai_model_list() -> dict:
    """获取支持的模型列表

    Returns:
        模型列表，包含各 Provider 支持的模型
    """
    return model_mcp.list_models()


@mcp.tool()
def ai_model_current() -> dict:
    """获取当前使用的模型

    Returns:
        当前模型信息
    """
    return model_mcp.current_model()


@mcp.tool()
def ai_model_switch(
    provider: str,
    model: str = None
) -> dict:
    """切换模型

    Args:
        provider: Provider名称 claude/openai/ollama
        model: 模型名称（可选）

    Returns:
        切换结果
    """
    return model_mcp.switch_model(provider, model)


@mcp.tool()
def ai_model_status() -> dict:
    """检查各 Provider 状态

    Returns:
        各 Provider 的可用状态
    """
    return model_mcp.check_status()


# Export for use in main.py
mcp_server = mcp