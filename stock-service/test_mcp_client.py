#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Service MCP Test Script

Test MCP protocol connection using mcp library
"""
import asyncio
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_mcp():
    """Test MCP SSE connection"""
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    server_url = "http://127.0.0.1:8011/sse"

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
                print("   Session initialized!")

                # List tools
                print("\n[2] Listing tools...")
                tools = await session.list_tools()
                print(f"   Found {len(tools.tools)} tools:")
                for t in tools.tools[:10]:
                    print(f"   - {t.name}")
                if len(tools.tools) > 10:
                    print(f"   ... and {len(tools.tools) - 10} more")

                # Test tool call
                print("\n[3] Testing get_index_quotes...")
                result = await session.call_tool("get_index_quotes", {"symbol": "沪深重要指数"})
                print("   Tool call successful!")
                if result.content:
                    for item in result.content:
                        if hasattr(item, 'text'):
                            text = item.text[:300] if len(item.text) > 300 else item.text
                            print(f"   Result: {text}...")

                print("\n" + "=" * 60)
                print("MCP Test Complete!")
                print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp())