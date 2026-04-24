#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QMT MCP客户端测试脚本

测试qmt-service的MCP接口调用
"""
import asyncio
import httpx
import json
from typing import Dict, List, Optional


class QMTMCPClient:
    """
    QMT MCP客户端

    封装qmt-service的MCP接口调用，提供简洁的API
    """

    def __init__(self, base_url: str = "http://localhost:8009"):
        """
        初始化客户端

        Args:
            base_url: qmt-service服务地址
        """
        self.base_url = base_url
        self.mcp_prefix = "/api/v1/mcp"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def _get(self, path: str, params: dict = None) -> Dict:
        """GET请求"""
        url = f"{self.base_url}{self.mcp_prefix}{path}"
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, data: dict = None) -> Dict:
        """POST请求"""
        url = f"{self.base_url}{self.mcp_prefix}{path}"
        response = await self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    # ==================== 持仓接口 ====================

    async def get_positions(self) -> Dict:
        """
        查询持仓列表

        Returns:
            持仓信息，包含positions、total_market_value、total_profit、count
        """
        return await self._get("/position/list")

    async def get_balance(self) -> Dict:
        """
        查询资金余额

        Returns:
            资金信息，包含total_asset、available_cash、market_value等
        """
        return await self._get("/position/balance")

    async def get_today_trades(self) -> Dict:
        """
        查询今日成交记录

        Returns:
            今日成交列表
        """
        return await self._get("/position/trades/today")

    async def get_today_entrusts(self) -> Dict:
        """
        查询今日委托

        Returns:
            今日委托列表
        """
        return await self._get("/position/entrusts/today")

    # ==================== 行情接口 ====================

    async def get_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取单只股票实时行情

        Args:
            stock_code: 股票代码，如 "000001.SZ"

        Returns:
            十档行情数据
        """
        return await self._get(f"/quote/{stock_code}")

    async def get_quotes(self, stock_codes: List[str]) -> Dict:
        """
        批量获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            批量行情数据
        """
        return await self._post("/quote/batch", stock_codes)

    async def get_kline(
        self,
        stock_code: str,
        period: str = "1d",
        count: int = 100,
        start_time: str = None,
        end_time: str = None
    ) -> Dict:
        """
        获取K线数据

        Args:
            stock_code: 股票代码
            period: 周期 (1d/1w/1m/5m/15m/30m/60m)
            count: 返回条数
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            K线数据列表
        """
        params = {"period": period, "count": count}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return await self._get(f"/quote/kline/{stock_code}", params)

    async def get_minute_bars(self, stock_code: str, date: str = None) -> Dict:
        """
        获取分时数据

        Args:
            stock_code: 股票代码
            date: 日期（可选）

        Returns:
            分时数据列表
        """
        params = {}
        if date:
            params["date"] = date
        return await self._get(f"/quote/minute/{stock_code}", params)

    async def get_index_quotes(self, index_codes: List[str] = None) -> Dict:
        """
        获取主要指数行情

        Args:
            index_codes: 指数代码列表，如 ['sh', 'sz', 'cy']

        Returns:
            指数行情列表
        """
        params = {}
        if index_codes:
            params["index_codes"] = index_codes
        return await self._get("/quote/indexes", params)

    # ==================== 交易接口 ====================

    async def buy_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict:
        """
        买入股票

        Args:
            stock_code: 股票代码
            price: 委托价格
            quantity: 委托数量（100的整数倍）
            order_type: 委托类型 limit/market

        Returns:
            订单信息
        """
        data = {
            "stock_code": stock_code,
            "price": price,
            "quantity": quantity,
            "order_type": order_type
        }
        return await self._post("/trade/buy", data)

    async def sell_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict:
        """
        卖出股票

        Args:
            stock_code: 股票代码
            price: 委托价格
            quantity: 委托数量
            order_type: 委托类型

        Returns:
            订单信息
        """
        data = {
            "stock_code": stock_code,
            "price": price,
            "quantity": quantity,
            "order_type": order_type
        }
        return await self._post("/trade/sell", data)

    async def cancel_order(self, order_id: str) -> Dict:
        """
        撤销委托

        Args:
            order_id: 订单ID

        Returns:
            撤单结果
        """
        return await self._post(f"/trade/cancel/{order_id}")

    async def get_orders(self, status: str = None) -> List[Dict]:
        """
        查询委托列表

        Args:
            status: 状态筛选（可选）

        Returns:
            委托列表
        """
        params = {}
        if status:
            params["status"] = status
        return await self._get("/trade/orders", params)


async def test_qmt_mcp():
    """
    测试QMT MCP接口
    """
    print("=" * 60)
    print("QMT MCP 接口测试")
    print("=" * 60)

    async with QMTMCPClient() as client:
        # 1. 测试健康检查
        print("\n[1] 检查服务状态...")
        try:
            response = await client._client.get(f"{client.base_url}/health")
            print(f"服务状态: {response.json()}")
        except Exception as e:
            print(f"服务连接失败: {e}")
            return

        # 2. 测试持仓查询
        print("\n[2] 测试持仓查询...")
        try:
            positions = await client.get_positions()
            print(f"持仓数量: {positions.get('count', 0)}")
            print(f"总市值: {positions.get('total_market_value', 0)}")
            print(f"总盈亏: {positions.get('total_profit', 0)}")
            if positions.get('positions'):
                for p in positions['positions'][:3]:
                    print(f"  - {p['stock_code']} {p['stock_name']}: "
                          f"{p['quantity']}股, 盈亏{p['profit']:.2f}元")
        except Exception as e:
            print(f"持仓查询失败: {e}")

        # 3. 测试资金查询
        print("\n[3] 测试资金查询...")
        try:
            balance = await client.get_balance()
            print(f"总资产: {balance.get('total_asset', 0)}")
            print(f"可用资金: {balance.get('available_cash', 0)}")
            print(f"持仓市值: {balance.get('market_value', 0)}")
        except Exception as e:
            print(f"资金查询失败: {e}")

        # 4. 测试指数行情
        print("\n[4] 测试指数行情...")
        try:
            indexes = await client.get_index_quotes(['sh', 'sz', 'cy'])
            print(f"指数数量: {indexes.get('count', 0)}")
            if indexes.get('indexes'):
                for idx in indexes['indexes']:
                    print(f"  - {idx['name']}: {idx['price']:.2f}, "
                          f"涨跌{idx['change']:.2f}%")
        except Exception as e:
            print(f"指数行情查询失败: {e}")

        # 5. 测试单只股票行情
        print("\n[5] 测试单只股票行情...")
        try:
            quote = await client.get_quote("000001.SZ")
            if quote:
                print(f"股票代码: {quote.get('stock_code')}")
                print(f"股票名称: {quote.get('stock_name')}")
                print(f"当前价格: {quote.get('price')}")
                print(f"昨收价: {quote.get('pre_close')}")
        except Exception as e:
            print(f"行情查询失败: {e}")

        # 6. 测试K线数据
        print("\n[6] 测试K线数据...")
        try:
            kline = await client.get_kline("000001.SZ", "1d", 10)
            print(f"K线数量: {kline.get('count', 0)}")
            if kline.get('klines'):
                for k in kline['klines'][:3]:
                    print(f"  - {k['date']}: 开{k['open']:.2f}, "
                          f"高{k['high']:.2f}, 低{k['low']:.2f}, 收{k['close']:.2f}")
        except Exception as e:
            print(f"K线查询失败: {e}")

        # 7. 测试今日委托
        print("\n[7] 测试今日委托...")
        try:
            entrusts = await client.get_today_entrusts()
            print(f"今日委托数量: {entrusts.get('total', 0)}")
        except Exception as e:
            print(f"委托查询失败: {e}")

        # 8. 测试今日成交
        print("\n[8] 测试今日成交...")
        try:
            trades = await client.get_today_trades()
            print(f"今日成交数量: {trades.get('total', 0)}")
        except Exception as e:
            print(f"成交查询失败: {e}")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


async def test_trade_operations():
    """
    测试交易操作（仅演示，不实际执行）
    """
    print("\n" + "=" * 60)
    print("交易操作演示（模拟）")
    print("=" * 60)

    async with QMTMCPClient() as client:
        # 注意：以下操作需要QMT连接且在交易时间才能成功

        print("\n[演示] 买入股票参数:")
        print("  股票代码: 000001.SZ")
        print("  价格: 10.50")
        print("  数量: 100")
        print("  类型: limit")

        # 实际调用（需要交易时间和QMT连接）
        # result = await client.buy_stock("000001.SZ", 10.50, 100)
        # print(f"下单结果: {result}")

        print("\n[演示] 撤单参数:")
        print("  订单ID: 需从下单结果获取")

        # result = await client.cancel_order("order_id")
        # print(f"撤单结果: {result}")

        print("\n提示: 实际交易需要:")
        print("  1. QMT客户端已启动并登录")
        print("  2. 在交易时间（9:30-15:00）")
        print("  3. 资金充足")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_qmt_mcp())

    # 交易操作演示
    # asyncio.run(test_trade_operations())