# backend/qmt-service/tests/test_mcp_tools.py
"""
MCP 工具测试

验证 MCP 工具函数的返回格式正确。
"""
import pytest
import asyncio

from app.mcp_server import mcp


class TestMCPToolsRegistration:
    """测试 MCP 工具是否正确注册"""

    def test_mcp_server_created(self):
        """验证 MCP server 实例创建成功"""
        assert mcp is not None
        assert mcp.name == "qmt-service"

    @pytest.mark.asyncio
    async def test_trade_tools_registered(self):
        """验证交易工具注册"""
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        expected_trade_tools = [
            "trade_buy", "trade_sell", "trade_cancel",
            "trade_get_orders", "trade_get_order"
        ]
        for tool_name in expected_trade_tools:
            assert tool_name in tool_names, f"工具 {tool_name} 未注册"

    @pytest.mark.asyncio
    async def test_position_tools_registered(self):
        """验证持仓工具注册"""
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        expected_position_tools = [
            "position_list", "position_balance", "position_trades",
            "position_today_trades", "position_today_entrusts"
        ]
        for tool_name in expected_position_tools:
            assert tool_name in tool_names, f"工具 {tool_name} 未注册"

    @pytest.mark.asyncio
    async def test_quote_tools_registered(self):
        """验证行情工具注册"""
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        expected_quote_tools = [
            "quote_get", "quote_batch", "quote_kline",
            "quote_minute", "quote_depth", "quote_ticks", "quote_indexes"
        ]
        for tool_name in expected_quote_tools:
            assert tool_name in tool_names, f"工具 {tool_name} 未注册"

    @pytest.mark.asyncio
    async def test_factor_tools_registered(self):
        """验证因子工具注册"""
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        expected_factor_tools = [
            "factor_list", "factor_screen", "factor_get_info"
        ]
        for tool_name in expected_factor_tools:
            assert tool_name in tool_names, f"工具 {tool_name} 未注册"


class TestFactorMCPTools:
    """测试因子 MCP 工具"""

    @pytest.mark.asyncio
    async def test_factor_list(self):
        """测试获取因子列表"""
        # 需要先初始化因子库
        from app.services.factor_service import factor_service
        await factor_service.init_factors()

        result = await factor_mcp.get_factor_list()
        assert "factors" in result
        assert "total" in result
        assert result["total"] > 0

    @pytest.mark.asyncio
    async def test_factor_get_info(self):
        """测试获取因子详情"""
        from app.services.factor_service import factor_service
        await factor_service.init_factors()

        result = await factor_mcp.get_factor_info("MA5")
        assert result is not None
        assert result["factor_id"] == "MA5"
        assert result["factor_name"] == "5日均线"


# 导入用于测试
from app.mcp.factor_mcp import factor_mcp