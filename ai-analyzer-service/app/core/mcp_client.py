"""
MCP 客户端 - 调用 factor-service
"""
import httpx
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MCPClient:
    """MCP 客户端，用于调用 factor-service"""

    def __init__(self):
        self.base_url = settings.FACTOR_SERVICE_URL
        self.timeout = 30.0

    async def get_indicator_data(
        self,
        stock_code: str,
        indicators: List[str],
        date: Optional[str] = None
    ) -> Dict:
        """
        获取技术指标数据

        Args:
            stock_code: 股票代码
            indicators: 指标列表
            date: 日期

        Returns:
            指标数据
        """
        url = f"{self.base_url}/api/v1/indicator/calculate"

        payload = {
            "stock_code": stock_code,
            "indicators": indicators,
            "date": date
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取指标数据失败: {e}")
            return {}

    async def get_score_data(
        self,
        stock_codes: List[str],
        weights: List[Dict],
        date: Optional[str] = None
    ) -> Dict:
        """
        获取评分数据

        Args:
            stock_codes: 股票代码列表
            weights: 权重配置
            date: 日期

        Returns:
            评分数据
        """
        url = f"{self.base_url}/api/v1/factor/score"

        payload = {
            "stock_codes": stock_codes,
            "weights": weights,
            "date": date
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取评分数据失败: {e}")
            return {}

    async def get_backtest_data(
        self,
        conditions: List[Dict],
        start_date: str,
        end_date: str,
        top_n: int = 10
    ) -> Dict:
        """
        获取回测数据

        Args:
            conditions: 筛选条件
            start_date: 开始日期
            end_date: 结束日期
            top_n: 持仓数量

        Returns:
            回测数据
        """
        url = f"{self.base_url}/api/v1/backtest/run"

        payload = {
            "conditions": conditions,
            "start_date": start_date,
            "end_date": end_date,
            "top_n": top_n
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取回测数据失败: {e}")
            return {}


# 单例
mcp_client = MCPClient()