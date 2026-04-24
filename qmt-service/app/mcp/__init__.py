# backend/qmt-service/app/mcp/__init__.py
"""
MCP接口模块

提供QMT交易、持仓、行情等功能的MCP封装接口
"""

from app.mcp.router import mcp_router
from app.mcp.trade_mcp import TradeMCP, trade_mcp
from app.mcp.position_mcp import PositionMCP, position_mcp
from app.mcp.quote_mcp import QuoteMCP, quote_mcp

__all__ = [
    "mcp_router",
    "TradeMCP",
    "trade_mcp",
    "PositionMCP",
    "position_mcp",
    "QuoteMCP",
    "quote_mcp",
]