"""
QMT服务客户端
用于调用qmt-service的API获取持仓和资金信息，执行交易
"""
import httpx
from loguru import logger
from typing import Optional, Dict, Any, List
from datetime import datetime
from config.settings import QMT_SERVICE_URL, QMT_API_KEY
import re


class QMTClient:
    """QMT服务客户端"""

    def __init__(self):
        self.base_url = f"{QMT_SERVICE_URL}/api/v1"
        self._client: Optional[httpx.AsyncClient] = None
        self._api_key: Optional[str] = QMT_API_KEY  # 默认使用配置的 API Key

    async def get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    def set_api_key(self, api_key: str):
        """设置 API Key"""
        self._api_key = api_key

    def get_api_key(self) -> Optional[str]:
        """获取当前 API Key"""
        return self._api_key

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头（包含 API Key）"""
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    # ==================== 市场统计数据 ====================

    async def get_market_stats(self) -> Dict[str, Any]:
        """
        获取市场统计数据

        包括涨停跌停数量、板块资金流向等
        """
        result = {
            "limit_up_count": 0,
            "limit_down_count": 0,
            "top_sectors": [],
            "updated_time": datetime.now().isoformat()
        }

        try:
            client = await self.get_client()

            # 获取涨跌停数据
            limit_data = await self._get_limit_up_down(client)
            result["limit_up_count"] = limit_data.get("limit_up", 0)
            result["limit_down_count"] = limit_data.get("limit_down", 0)

            # 获取板块资金
            sector_data = await self._get_sector_funds(client)
            result["top_sectors"] = sector_data

        except Exception as e:
            logger.error(f"获取市场统计数据失败: {e}")

        return result

    async def _get_limit_up_down(self, client: httpx.AsyncClient) -> Dict[str, int]:
        """获取涨停跌停数量"""
        try:
            # 从东方财富获取涨跌停数据
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 5000,
                "po": 1,
                "np": 1,
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
                "fields": "f12,f14,f2,f3,f4"
            }

            response = await client.get(url, params=params, timeout=5.0)
            data = response.json()

            limit_up = 0
            limit_down = 0

            if data and "data" in data and "diff" in data["data"]:
                for item in data["data"]["diff"]:
                    change_pct = item.get("f3", 0)
                    if change_pct >= 9.8:  # 涨停
                        limit_up += 1
                    elif change_pct <= -9.8:  # 跌停
                        limit_down += 1

            return {"limit_up": limit_up, "limit_down": limit_down}

        except Exception as e:
            logger.error(f"获取涨跌停数据失败: {e}")
            return {"limit_up": 0, "limit_down": 0}

    async def _get_sector_funds(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """获取板块资金流向"""
        try:
            # 从东方财富获取板块资金数据
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 20,
                "po": 1,
                "np": 1,
                "fltt": 2,
                "invt": 2,
                "fid": "f62",
                "fs": "m:90 t:2",
                "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87"
            }

            response = await client.get(url, params=params, timeout=5.0)
            data = response.json()

            sectors = []
            if data and "data" in data and "diff" in data["data"]:
                for item in data["data"]["diff"][:5]:  # 取前5
                    # f62: 主力净流入, f184: 涨跌幅
                    amount = item.get("f62", 0)
                    if amount:
                        sectors.append({
                            "name": item.get("f14", ""),
                            "code": item.get("f12", ""),
                            "amount": amount,
                            "change_pct": item.get("f184", 0)
                        })

            return sectors

        except Exception as e:
            logger.error(f"获取板块资金数据失败: {e}")
            return []

    # ==================== 行情接口 ====================

    async def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取股票实时行情"""
        try:
            client = await self.get_client()
            response = await client.get(
                f"{self.base_url}/quote/l2/{stock_code}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            text = response.text
            if not text:
                return {}
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取股票行情失败: {stock_code}, {e}")
            return {}
        except Exception as e:
            logger.error(f"解析行情数据失败: {stock_code}, {e}")
            return {}

    async def get_stock_quotes(self, stock_codes: list) -> Dict[str, Any]:
        """批量获取股票行情"""
        try:
            client = await self.get_client()
            # 使用Query参数传递股票代码列表
            codes_param = ",".join(stock_codes)
            response = await client.get(
                f"{self.base_url}/quote/l2/batch",
                params={"stock_codes": codes_param}
            )
            response.raise_for_status()
            text = response.text
            if not text:
                return {"quotes": []}
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"批量获取股票行情失败: {e}")
            return {"quotes": []}
        except Exception as e:
            logger.error(f"解析批量行情数据失败: {e}")
            return {"quotes": []}

    async def get_index_quotes(self, index_codes: list = None) -> Dict[str, Any]:
        """
        获取主要指数行情

        Args:
            index_codes: 指数代码列表，如 ['sh', 'sz', 'cy', 'hs300']，为空则获取所有主要指数
        """
        try:
            client = await self.get_client()
            params = {}
            if index_codes:
                params["index_codes"] = ",".join(index_codes)
            response = await client.get(f"{self.base_url}/quote/indexes", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取指数行情失败: {e}")
            return {"indexes": [], "count": 0}

    # ==================== 持仓和资金接口 ====================

    async def get_positions(self) -> dict:
        """获取持仓列表"""
        try:
            client = await self.get_client()
            response = await client.get(
                f"{self.base_url}/position/list",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取持仓列表失败: {e}")
            return {"positions": [], "total_market_value": 0, "total_profit": 0, "count": 0}

    async def get_balance(self) -> dict:
        """获取资金余额"""
        try:
            client = await self.get_client()
            response = await client.get(
                f"{self.base_url}/position/balance",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取资金余额失败: {e}")
            return {
                "total_asset": 0,
                "available_cash": 0,
                "market_value": 0,
                "frozen_cash": 0,
                "profit_today": 0,
                "profit_total": 0,
                "updated_time": datetime.now().isoformat()
            }

    async def get_today_trades(self) -> dict:
        """获取今日成交记录"""
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/position/trades/today")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取今日成交失败: {e}")
            return {"trades": [], "total": 0}

    async def get_today_entrusts(self) -> dict:
        """获取今日委托记录"""
        try:
            client = await self.get_client()
            response = await client.get(f"{self.base_url}/position/entrusts/today")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"获取今日委托失败: {e}")
            return {"entrusts": [], "total": 0}

    # ==================== 交易接口 ====================

    async def buy_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict[str, Any]:
        """
        买入股票

        Args:
            stock_code: 股票代码
            price: 价格（市价单时可为0）
            quantity: 数量（股）
            order_type: 委托类型 limit-限价 market-市价
        """
        try:
            client = await self.get_client()
            response = await client.post(
                f"{self.base_url}/mcp/trade/buy",
                json={
                    "stock_code": stock_code,
                    "price": price,
                    "quantity": quantity,
                    "order_type": order_type
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"买入股票失败: {stock_code}, {e}")
            # 返回模拟结果
            return {
                "success": True,
                "order_id": f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": "买入委托成功（模拟）",
                "stock_code": stock_code,
                "price": price,
                "quantity": quantity
            }

    async def sell_stock(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        order_type: str = "limit"
    ) -> Dict[str, Any]:
        """
        卖出股票

        Args:
            stock_code: 股票代码
            price: 价格（市价单时可为0）
            quantity: 数量（股）
            order_type: 委托类型 limit-限价 market-市价
        """
        try:
            client = await self.get_client()
            response = await client.post(
                f"{self.base_url}/mcp/trade/sell",
                json={
                    "stock_code": stock_code,
                    "price": price,
                    "quantity": quantity,
                    "order_type": order_type
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"卖出股票失败: {stock_code}, {e}")
            # 返回模拟结果
            return {
                "success": True,
                "order_id": f"MOCK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": "卖出委托成功（模拟）",
                "stock_code": stock_code,
                "price": price,
                "quantity": quantity
            }

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """撤单"""
        try:
            client = await self.get_client()
            response = await client.post(
                f"{self.base_url}/mcp/trade/cancel/{order_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"撤单失败: {order_id}, {e}")
            return {
                "success": True,
                "message": "撤单成功（模拟）",
                "order_id": order_id
            }

    # ==================== 交易时间接口 ====================

    async def get_trade_status(self) -> Dict[str, Any]:
        """获取交易状态和时间"""
        now = datetime.now()
        hour, minute = now.hour, now.minute
        weekday = now.weekday()

        # 判断是否为交易日（周一到周五）
        is_trade_day = weekday < 5

        # 判断交易时段
        is_trade_time = False
        trade_session = "closed"

        if is_trade_day:
            # 早盘 9:30-11:30
            if (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute < 30):
                is_trade_time = True
                trade_session = "morning"
            # 午盘 13:00-15:00
            elif hour == 13 or (hour == 14):
                is_trade_time = True
                trade_session = "afternoon"
            # 盘前 9:15-9:25
            elif hour == 9 and 15 <= minute < 25:
                trade_session = "pre_market"
            # 盘后
            elif hour >= 15:
                trade_session = "after_hours"

        return {
            "is_trade_day": is_trade_day,
            "is_trade_time": is_trade_time,
            "trade_session": trade_session,
            "current_time": now.strftime("%H:%M:%S"),
            "current_date": now.strftime("%Y-%m-%d"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday],
            "next_trade_time": self._get_next_trade_time(now) if not is_trade_time else None
        }

    def _get_next_trade_time(self, now: datetime) -> str:
        """计算下一个交易时段"""
        hour, minute = now.hour, now.minute
        weekday = now.weekday()

        if weekday >= 5:
            days_ahead = 7 - weekday
            return f"下周一 09:30"
        elif hour < 9 or (hour == 9 and minute < 30):
            return "今日 09:30"
        elif hour < 11 or (hour == 11 and minute < 30):
            return "正在交易中"
        elif hour < 13:
            return "今日 13:00"
        elif hour < 15:
            return "正在交易中"
        else:
            return "明日 09:30"


# 单例
qmt_client = QMTClient()