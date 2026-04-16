"""
MCP 客户端 - 用于调用 stock-service 获取行情数据
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MCPClient:
    """
    MCP 客户端类

    用于通过 HTTP 调用 stock-service 的 MCP 工具接口获取行情数据
    """

    def __init__(self, base_url: str = None):
        """
        初始化 MCP 客户端

        Args:
            base_url: stock-service 的地址，默认从配置读取
        """
        self.base_url = base_url or settings.STOCK_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具返回结果
        """
        url = f"{self.base_url}/api/v1/mcp/call"
        payload = {
            "tool": tool_name,
            "arguments": arguments or {}
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.debug(f"MCP call {tool_name} success: {result}")
            return result
        except httpx.HTTPError as e:
            logger.error(f"MCP call {tool_name} failed: {e}")
            raise RuntimeError(f"调用 stock-service 失败: {e}")

    async def get_stock_history(
        stock_code: str,
        period: str = "daily",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        获取股票历史行情

        Args:
            stock_code: 股票代码，如 "000001"
            period: 周期，daily/weekly/monthly
            start_date: 开始日期，格式 YYYYMMDD
            end_date: 结束日期，格式 YYYYMMDD

        Returns:
            历史行情数据列表
        """
        arguments = {
            "stock_code": stock_code,
            "period": period
        }
        if start_date:
            arguments["start_date"] = start_date
        if end_date:
            arguments["end_date"] = end_date

        return await self.call_tool("get_stock_history", arguments)

    async def get_stock_quote(stock_code: str) -> Dict:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            实时行情数据
        """
        return await self.call_tool("get_stock_quote", {"stock_code": stock_code})

    async def get_stock_info(stock_code: str) -> Dict:
        """
        获取股票基本信息

        Args:
            stock_code: 股票代码

        Returns:
            股票基本信息
        """
        return await self.call_tool("get_stock_info", {"stock_code": stock_code})

    async def get_index_quotes(symbol: str = "沪深重要指数") -> List[Dict]:
        """
        获取指数行情

        Args:
            symbol: 指数类型

        Returns:
            指数行情列表
        """
        return await self.call_tool("get_index_quotes", {"symbol": symbol})

    async def batch_get_quotes(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """
        批量获取股票行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            股票行情字典 {stock_code: quote_data}
        """
        results = {}
        for code in stock_codes:
            try:
                quote = await self.get_stock_quote(code)
                results[code] = quote
            except Exception as e:
                logger.warning(f"获取 {code} 行情失败: {e}")
                results[code] = None
        return results


# 单例客户端
mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """获取 MCP 客户端单例"""
    if mcp_client is None:
        mcp_client = MCPClient()
    return mcp_client


async def close_mcp_client():
    """关闭 MCP 客户端"""
    if mcp_client:
        await mcp_client.close()
        mcp_client = None