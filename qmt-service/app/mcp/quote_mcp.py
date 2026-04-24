# backend/qmt-service/app/mcp/quote_mcp.py
"""
行情MCP接口

提供行情查询、K线数据、分时数据等行情功能的MCP封装
"""
import logging
from typing import Dict, List, Optional

from app.services.quote_service import quote_service

logger = logging.getLogger(__name__)


class QuoteMCP:
    """
    行情MCP接口

    提供行情数据查询功能，包括实时行情、K线数据、分时数据、深度数据等。

    使用示例:
        quote_mcp = QuoteMCP()
        quote = await quote_mcp.get_quote("000001.SZ")
        kline = await quote_mcp.get_kline("000001.SZ", "1d", 100)
    """

    async def get_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取单只股票实时行情（十档）

        Args:
            stock_code: 股票代码，如 "000001.SZ"

        Returns:
            Dict: 行情数据
                - stock_code: 股票代码
                - stock_name: 票名称
                - price: 当前价格
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - pre_close: 昨收价
                - volume: 成交量
                - amount: 成交额
                - bid_price1~10: 买价1-10档
                - bid_volume1~10: 买量1-10档
                - ask_price1~10: 卖价1-10档
                - ask_volume1~10: 卖量1-10档
                - updated_time: 更新时间

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取实时行情: {stock_code}")
        try:
            result = await quote_service.get_l2_quote(stock_code)
            if result:
                return result.model_dump()
            return None
        except Exception as e:
            logger.error(f"获取实时行情失败: {str(e)}")
            raise Exception(f"获取实时行情失败: {str(e)}")

    async def get_quotes(self, stock_codes: List[str]) -> Dict:
        """
        批量获取实时行情

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 批量行情数据
                - quotes: 行情列表
                - count: 数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP批量获取行情: {stock_codes}")
        try:
            result = await quote_service.get_l2_quotes(stock_codes)
            return result.model_dump()
        except Exception as e:
            logger.error(f"批量获取行情失败: {str(e)}")
            raise Exception(f"批量获取行情失败: {str(e)}")

    async def get_kline(
        self,
        stock_code: str,
        period: str = "1d",
        count: int = 100,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict:
        """
        获取K线数据

        Args:
            stock_code: 股票代码
            period: 周期
                - "1d": 日线
                - "1w": 周线
                - "1m": 月线
                - "1m": 1分钟线
                - "5m": 5分钟线
                - "15m": 15分钟线
                - "30m": 30分钟线
                - "60m": 60分钟线
            count: 返回条数
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            Dict: K线数据
                - stock_code: 股票代码
                - klines: K线列表，每个包含:
                    - date: 日期/时间
                    - open: 开盘价
                    - high: 最高价
                    - low: 最低价
                    - close: 收盘价
                    - volume: 成交量
                    - amount: 成交额
                - count: 数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取K线: {stock_code}, period={period}, count={count}")
        try:
            result = await quote_service.get_kline(
                stock_code, period, count, start_time, end_time
            )
            return result
        except Exception as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            raise Exception(f"获取K线数据失败: {str(e)}")

    async def get_minute_bars(
        self,
        stock_code: str,
        date: Optional[str] = None
    ) -> Dict:
        """
        获取分时数据

        Args:
            stock_code: 票代码
            date: 日期，格式YYYYMMDD，不传则获取今日

        Returns:
            Dict: 分时数据
                - stock_code: 股票代码
                - date: 日期
                - bars: 分时数据列表
                - count: 数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取分时数据: {stock_code}, date={date}")
        try:
            result = await quote_service.get_minute_bars(stock_code, date)
            return result.model_dump()
        except Exception as e:
            logger.error(f"获取分时数据失败: {str(e)}")
            raise Exception(f"获取分时数据失败: {str(e)}")

    async def get_depth(self, stock_code: str) -> Dict:
        """
        获取订单簿深度

        Args:
            stock_code: 股票代码

        Returns:
            Dict: 深度数据
                - stock_code: 股票代码
                - depth: 订单簿信息
                    - price: 当前价格
                    - bid_levels: 买盘档位列表
                    - ask_levels: 卖盘档位列表
                    - updated_time: 更新时间

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取订单簿深度: {stock_code}")
        try:
            result = await quote_service.get_depth(stock_code)
            return result.model_dump()
        except Exception as e:
            logger.error(f"获取订单簿深度失败: {str(e)}")
            raise Exception(f"获取订单簿深度失败: {str(e)}")

    async def get_ticks(
        self,
        stock_code: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        count: int = 100
    ) -> Dict:
        """
        获取逐笔成交数据

        Args:
            stock_code: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            count: 返回条数

        Returns:
            Dict: 逐笔成交数据
                - stock_code: 票代码
                - ticks: 成交列表
                - count: 数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取逐笔成交: {stock_code}")
        try:
            result = await quote_service.get_ticks(stock_code, start_time, end_time, count)
            return result.model_dump()
        except Exception as e:
            logger.error(f"获取逐笔成交失败: {str(e)}")
            raise Exception(f"获取逐笔成交失败: {str(e)}")

    async def get_index_quotes(
        self,
        index_codes: Optional[List[str]] = None
    ) -> Dict:
        """
        获取主要指数行情

        Args:
            index_codes: 指数代码列表，如 ['sh', 'sz', 'cy', 'hs300']
                        不传则获取所有主要指数

        Returns:
            Dict: 指数行情数据
                - indexes: 指数列表，每个包含:
                    - code: 指数代码
                    - name: 指数名称
                    - price: 当前点位
                    - change: 涨跌幅(%)
                    - change_amount: 涨跌点数
                    - pre_close: 昨日收盘
                    - open: 开盘
                    - high: 最高
                    - low: 最低
                    - volume: 成交量
                    - amount: 成交额
                    - updated_time: 更新时间
                - count: 数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取指数行情: {index_codes}")
        try:
            result = await quote_service.get_index_quotes(index_codes)
            return result.model_dump()
        except Exception as e:
            logger.error(f"获取指数行情失败: {str(e)}")
            raise Exception(f"获取指数行情失败: {str(e)}")

    async def search_stock(self, keyword: str, limit: int = 10) -> Dict:
        """
        根据名称或代码搜索股票

        Args:
            keyword: 搜索关键词（股票名称或代码，如 "九联"、"平安"、"000001"）
            limit: 返回数量限制，默认10

        Returns:
            Dict: 搜索结果
                - stocks: 匹配的股票列表
                    - code: 完整代码（如 000001.SZ）
                    - name: 股票名称
                    - exchange: 交易所（SH/SZ）
                    - code_simple: 简化代码（如 000001）
                - count: 匹配数量
                - keyword: 搜索关键词

        Raises:
            Exception: 当搜索失败时抛出
        """
        logger.info(f"MCP搜索股票: keyword={keyword}, limit={limit}")
        try:
            from app.services.quote_service import stock_search_service
            results = await stock_search_service.search_by_name(keyword, limit)
            return {
                "stocks": results,
                "count": len(results),
                "keyword": keyword
            }
        except Exception as e:
            logger.error(f"搜索股票失败: {str(e)}")
            raise Exception(f"搜索股票失败: {str(e)}")


# 单例
quote_mcp = QuoteMCP()