#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Service MCP Test Script

Test MCP protocol connection and tool calls for stock-service.
"""
import asyncio
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_mcp_connection():
    """Test MCP SSE connection using httpx-sse"""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    server_url = "http://localhost:8008/mcp"

    print("=" * 60)
    print("Stock Service MCP Protocol Test")
    print("=" * 60)
    print(f"\nConnecting to: {server_url}")

    try:
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize connection
                print("\n[1] Initializing MCP session...")
                await session.initialize()
                print("   Session initialized successfully!")

                # List available tools
                print("\n[2] Listing available tools...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"   Found {len(tools)} tools:")
                for tool in tools[:10]:  # Show first 10
                    print(f"   - {tool.name}")
                if len(tools) > 10:
                    print(f"   ... and {len(tools) - 10} more tools")

                # Test calling a tool
                print("\n[3] Testing tool call: get_index_quotes...")
                try:
                    result = await session.call_tool("get_index_quotes", {"symbol": "沪深重要指数"})
                    print(f"   Tool call successful!")
                    content = result.content
                    if content:
                        for item in content:
                            if hasattr(item, 'text'):
                                print(f"   Result preview: {item.text[:200]}...")
                except Exception as e:
                    print(f"   Tool call error: {e}")

                # Test another tool
                print("\n[4] Testing tool call: get_stock_info...")
                try:
                    result = await session.call_tool("get_stock_info", {"stock_code": "000001"})
                    print(f"   Tool call successful!")
                    content = result.content
                    if content:
                        for item in content:
                            if hasattr(item, 'text'):
                                print(f"   Result preview: {item.text[:200]}...")
                except Exception as e:
                    print(f"   Tool call error: {e}")

                print("\n" + "=" * 60)
                print("MCP Protocol Test Complete!")
                print("=" * 60)

    except Exception as e:
        print(f"\nConnection error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure stock-service is running: python run.py")
        print("  2. Check the server URL: http://localhost:8008/mcp")
        print("  3. Verify fastmcp is installed: pip install fastmcp")


async def test_mcp_simple():
    """Simple test using httpx"""
    print("=" * 60)
    print("Simple MCP Endpoint Test")
    print("=" * 60)

    try:
        import httpx

        print("\n[1] Testing health endpoint...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_resp = await client.get("http://localhost:8008/health")
            print(f"   Health: {health_resp.json()}")

            print("\n[2] Testing MCP endpoint availability...")
            # SSE endpoint requires proper headers
            try:
                response = await client.get(
                    "http://localhost:8008/mcp",
                    headers={"Accept": "text/event-stream"},
                    timeout=5.0
                )
                print(f"   MCP endpoint status: {response.status_code}")
            except Exception as e:
                print(f"   MCP endpoint response: {type(e).__name__}")

        print("\nMCP endpoint is available. Use Claude Code or MCP Inspector for full testing.")

    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure stock-service is running on port 8008")


if __name__ == "__main__":
    print("\nChoose test mode:")
    print("  1. Full MCP protocol test (requires mcp package)")
    print("  2. Simple endpoint test")

    mode = input("\nEnter choice (1 or 2): ").strip()

    if mode == "1":
        asyncio.run(test_mcp_connection())
    else:
        asyncio.run(test_mcp_simple())