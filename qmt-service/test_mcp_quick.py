#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QMT MCP Quick Test Script

Test MCP interfaces are working properly
"""
import asyncio
import httpx
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def quick_test():
    """Quick test for MCP interfaces"""
    base_url = "http://localhost:8009"
    mcp_prefix = "/api/v1/mcp"

    print("QMT MCP Quick Test")
    print("-" * 40)

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Health check
        print("\n1. Health Check...")
        try:
            resp = await client.get(f"{base_url}/health")
            data = resp.json()
            print(f"   Status: {data.get('status')}")
            qmt_info = data.get('qmt', {})
            print(f"   QMT Connected: {qmt_info.get('connected', False)}")
            if qmt_info.get('connected'):
                print(f"   Account: {qmt_info.get('account')}")
        except Exception as e:
            print(f"   Error: {e}")
            return

        # Position query
        print("\n2. Position Query...")
        try:
            resp = await client.get(f"{base_url}{mcp_prefix}/position/list")
            data = resp.json()
            print(f"   Position Count: {data.get('count', 0)}")
            print(f"   Total Market Value: {data.get('total_market_value', 0):.2f}")
            print(f"   Total Profit: {data.get('total_profit', 0):.2f}")
            for p in data.get('positions', [])[:3]:
                print(f"   - {p['stock_code']} {p['stock_name']}: {p['quantity']} shares, profit {p['profit']:.2f}")
        except Exception as e:
            print(f"   Error: {e}")

        # Balance query
        print("\n3. Balance Query...")
        try:
            resp = await client.get(f"{base_url}{mcp_prefix}/position/balance")
            data = resp.json()
            print(f"   Total Asset: {data.get('total_asset', 0):.2f}")
            print(f"   Available: {data.get('available_cash', 0):.2f}")
        except Exception as e:
            print(f"   Error: {e}")

        # Index quotes
        print("\n4. Index Quotes...")
        try:
            resp = await client.get(f"{base_url}{mcp_prefix}/quote/indexes")
            data = resp.json()
            for idx in data.get('indexes', [])[:3]:
                print(f"   {idx['name']}: {idx['price']:.2f} ({idx['change']:+.2f}%)")
        except Exception as e:
            print(f"   Error: {e}")

    print("\n" + "-" * 40)
    print("Test Complete")


if __name__ == "__main__":
    asyncio.run(quick_test())