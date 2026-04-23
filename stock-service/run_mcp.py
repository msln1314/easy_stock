#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Service MCP Server Entry Point

Run MCP server independently on a separate port.
"""
import os

# Set environment before importing
os.environ.setdefault("AKSHARE_PATCH_MODE", "direct")

from app.mcp_server import mcp_server

# Run MCP server
if __name__ == "__main__":
    print("=" * 60)
    print("Stock Service MCP Server")
    print("=" * 60)
    print("\nMCP SSE endpoint: http://127.0.0.1:8011/sse")
    print("Use Claude Code or MCP Inspector to connect")
    print("\nAvailable tools: 22")
    print("  - get_stock_info, get_stock_quote, get_stock_history")
    print("  - get_index_quotes, get_index_quote")
    print("  - get_concept_boards, get_industry_boards")
    print("  - get_stock_hot_rank, get_margin_details")
    print("  - and more...")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    mcp_server.run(transport="sse", port=8011)