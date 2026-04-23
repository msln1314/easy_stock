"""
股票筛选服务

支持多指标组合选股
"""
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from loguru import logger

from models.stock_pick import StockPickStrategy, StrategyTrackPool
from models.indicator_library import IndicatorLibrary
from utils.indicator_calculator import calculator
from services.kline_service import kline_service
from core.qmt_client import qmt_client


class StockScreeningService:
    """股票筛选服务"""

    def __init__(self):
        self.calculator = calculator
        self.kline_service = kline_service

    async def screen_stocks(
        self,
        strategy_config: Dict[str, Any],
        stock_pool: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        根据策略配置筛选股票

        Args:
            strategy_config: 策略配置
                {
                    "indicators": [
                        {
                            "indicator_key": "RSI",
                            "params": {"length": 14},
                            "output_field": "values",
                            "conditions": [
                                {"operator": "<", "value": 30}
                            ]
                        }
                    ],
                    "condition_groups": [
                        {
                            "group_id": "group1",
                            "logic": "AND",  # AND 或 OR
                            "condition_ids": ["cond1", "cond2"]
                        }
                    ],
                    "logic": "AND"  # 全局逻辑
                }
            stock_pool: 股票池，为None则使用全市场

        Returns:
            筛选结果列表
        """
        # 获取股票池
        if stock_pool is None:
            stock_pool = await self._get_all_stocks()

        # 并行筛选
        results = []
        batch_size = 50

        for i in range(0, len(stock_pool), batch_size):
            batch = stock_pool[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self._evaluate_stock(stock_code, strategy_config) for stock_code in batch],
                return_exceptions=True
            )

            for stock_code, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.warning(f"筛选股票 {stock_code} 失败: {result}")
                    continue
                if result and result.get("passed"):
                    results.append(result)

        # 按置信度排序
        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return results

    async def _get_all_stocks(self) -> List[str]:
        """获取全市场股票列表"""
        try:
            # 从东方财富获取A股列表
            async with httpx.AsyncClient(timeout=10.0) as client:
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
                response = await client.get(url, params=params)
                data = response.json()

                stocks = []
                if data and "data" in data and "diff" in data["data"]:
                    for item in data["data"]["diff"]:
                        code = item.get("f12", "")
                        # 过滤ST和退市股
                        name = item.get("f14", "")
                        if "ST" not in name and "退" not in name and code:
                            stocks.append(code)

                logger.info(f"获取股票列表成功，共 {len(stocks)} 只")
                return stocks
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    async def _evaluate_stock(
        self,
        stock_code: str,
        strategy_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        评估单只股票是否满足策略条件

        Returns:
            {
                "stock_code": str,
                "stock_name": str,
                "passed": bool,
                "confidence": float,
                "matched_conditions": list,
                "indicator_values": dict,
                "current_price": float,
                "change_percent": float
            }
        """
        try:
            # 获取K线数据
            klines = await self._get_klines(stock_code, days=120)
            if not klines or len(klines) < 30:
                return None

            # 获取实时行情
            quote = await self._get_quote(stock_code)

            # 计算所有指标
            indicator_values = {}
            indicators_config = strategy_config.get("indicators", [])

            for indicator in indicators_config:
                indicator_key = indicator.get("indicator_key")
                params = indicator.get("params", {})

                try:
                    result = self.calculator.calculate(indicator_key, klines, params)
                    indicator_values[indicator_key] = result
                except Exception as e:
                    logger.warning(f"计算指标 {indicator_key} 失败: {stock_code}, {e}")
                    indicator_values[indicator_key] = None

            # 评估条件
            conditions = strategy_config.get("conditions", [])
            condition_results = []

            for cond in conditions:
                cond_result = self._evaluate_condition(cond, indicator_values, quote)
                condition_results.append(cond_result)

            # 根据逻辑组合条件结果
            global_logic = strategy_config.get("logic", "AND")
            passed = self._combine_results(condition_results, global_logic)

            # 计算置信度
            matched_count = sum(1 for r in condition_results if r.get("passed"))
            total_count = len(condition_results)
            confidence = (matched_count / total_count * 100) if total_count > 0 else 0

            # 只返回通过的股票
            if not passed:
                return None

            return {
                "stock_code": stock_code,
                "stock_name": quote.get("stock_name", ""),
                "passed": True,
                "confidence": confidence,
                "matched_conditions": [r for r in condition_results if r.get("passed")],
                "indicator_values": indicator_values,
                "current_price": quote.get("lastPrice", 0),
                "change_percent": quote.get("changePercent", 0),
            }

        except Exception as e:
            logger.error(f"评估股票 {stock_code} 失败: {e}")
            return None

    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        indicator_values: Dict[str, Any],
        quote: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        评估单个条件

        condition: {
            "id": "cond1",
            "type": "indicator",  # indicator, quote, threshold
            "indicator_key": "RSI",
            "output_field": "values",  # 指标输出字段
            "operator": "<",  # >, <, >=, <=, ==, !=, cross_up, cross_down
            "value": 30,  # 比较值，可以是数字或另一个指标
            "value_type": "number",  # number, indicator, quote_field
            "value_indicator_key": None,  # 如果value_type是indicator
        }
        """
        cond_id = condition.get("id", "")
        cond_type = condition.get("type", "indicator")

        try:
            # 获取左值
            left_value = None
            if cond_type == "indicator":
                indicator_key = condition.get("indicator_key")
                output_field = condition.get("output_field", "values")
                indicator_data = indicator_values.get(indicator_key)
                if indicator_data:
                    if output_field == "values":
                        left_value = indicator_data.get("latest", indicator_data.get("values", [None])[-1])
                    elif output_field == "latest":
                        left_value = indicator_data.get("latest")
                    else:
                        # 多值指标如MACD的DIF
                        latest = indicator_data.get("latest", {})
                        left_value = latest.get(output_field)
            elif cond_type == "quote":
                field = condition.get("field", "lastPrice")
                left_value = quote.get(field)
            elif cond_type == "threshold":
                # 阈值类条件（如涨跌幅阈值）
                left_value = self._calculate_threshold(condition, quote)

            # 获取右值
            right_value = None
            value_type = condition.get("value_type", "number")

            if value_type == "number":
                right_value = condition.get("value")
            elif value_type == "indicator":
                # 比较另一个指标值
                other_indicator_key = condition.get("value_indicator_key")
                other_output_field = condition.get("value_output_field", "values")
                other_data = indicator_values.get(other_indicator_key)
                if other_data:
                    if other_output_field == "values":
                        right_value = other_data.get("latest", other_data.get("values", [None])[-1])
                    elif other_output_field == "latest":
                        right_value = other_data.get("latest")
                    else:
                        latest = other_data.get("latest", {})
                        right_value = latest.get(other_output_field)
            elif value_type == "quote_field":
                right_value = quote.get(condition.get("value_field"))

            # 执行比较
            operator = condition.get("operator", ">")
            passed = self._compare(left_value, right_value, operator)

            return {
                "id": cond_id,
                "type": cond_type,
                "left_value": left_value,
                "right_value": right_value,
                "operator": operator,
                "passed": passed
            }

        except Exception as e:
            logger.error(f"评估条件 {cond_id} 失败: {e}")
            return {
                "id": cond_id,
                "passed": False,
                "error": str(e)
            }

    def _compare(
        self,
        left: Any,
        right: Any,
        operator: str
    ) -> bool:
        """执行比较操作"""
        if left is None or right is None:
            return False

        try:
            if operator == ">":
                return float(left) > float(right)
            elif operator == "<":
                return float(left) < float(right)
            elif operator == ">=":
                return float(left) >= float(right)
            elif operator == "<=":
                return float(left) <= float(right)
            elif operator == "==":
                return abs(float(left) - float(right)) < 0.0001
            elif operator == "!=":
                return abs(float(left) - float(right)) >= 0.0001
            elif operator == "cross_up":
                # 穿越需要历史数据，这里简化处理
                return False
            elif operator == "cross_down":
                return False
            else:
                return False
        except (TypeError, ValueError):
            return False

    def _combine_results(
        self,
        condition_results: List[Dict[str, Any]],
        logic: str
    ) -> bool:
        """根据逻辑组合条件结果"""
        if not condition_results:
            return False

        passed_list = [r.get("passed", False) for r in condition_results]

        if logic.upper() == "AND":
            return all(passed_list)
        elif logic.upper() == "OR":
            return any(passed_list)
        else:
            return False

    def _calculate_threshold(
        self,
        condition: Dict[str, Any],
        quote: Dict[str, Any]
    ) -> Any:
        """计算阈值类指标"""
        threshold_type = condition.get("threshold_type")

        if threshold_type == "change_percent":
            # 涨跌幅阈值
            start_price = condition.get("start_price")
            if start_price:
                current_price = quote.get("lastPrice", 0)
                return (current_price - start_price) / start_price * 100
            return quote.get("changePercent", 0)
        elif threshold_type == "turnover":
            # 换手率阈值
            return quote.get("turnoverRate", 0)
        elif threshold_type == "volume_ratio":
            # 量比阈值
            return quote.get("volumeRatio", 0)
        elif threshold_type == "amount":
            # 成交额阈值
            return quote.get("amount", 0)
        elif threshold_type == "market_value":
            # 市值阈值
            return quote.get("marketValue", 0)
        else:
            return None

    async def _get_klines(
        self,
        stock_code: str,
        days: int = 120
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            # 使用kline_service获取K线
            klines_data = await self.kline_service.get_klines(
                stock_code=stock_code,
                period="daily",
                limit=days
            )

            # 转换为指标计算器需要的格式
            klines = []
            for i in range(len(klines_data.get("dates", []))):
                klines.append({
                    "open": klines_data["open"][i],
                    "close": klines_data["close"][i],
                    "high": klines_data["high"][i],
                    "low": klines_data["low"][i],
                    "volume": klines_data["volume"][i],
                })

            return klines
        except Exception as e:
            logger.error(f"获取K线数据失败 {stock_code}: {e}")
            return []

    async def _get_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取实时行情"""
        try:
            # 格式化股票代码
            code = stock_code
            if '.' not in code:
                if code.startswith('6'):
                    code = f"{code}.SH"
                else:
                    code = f"{code}.SZ"

            quote = await qmt_client.get_stock_quote(code)
            if quote:
                quote["stock_name"] = quote.get("name", "")
            return quote or {}
        except Exception as e:
            logger.error(f"获取行情失败 {stock_code}: {e}")
            return {}

    async def execute_strategy(
        self,
        strategy: StockPickStrategy,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        执行选股策略

        Args:
            strategy: 策略对象
            save_results: 是否保存结果到追踪池

        Returns:
            执行结果
        """
        logger.info(f"执行选股策略: {strategy.strategy_name}")
        logger.info(f"策略配置: {strategy.strategy_config}")

        # 筛选股票
        results = await self.screen_stocks(strategy.strategy_config)
        logger.info(f"筛选结果: 找到 {len(results)} 只股票")

        # 保存结果
        if save_results and results:
            target_date = date.today()
            pool_type = "today"

            for result in results:
                try:
                    await StrategyTrackPool.create_track_record(
                        strategy=strategy,
                        stock_code=result["stock_code"],
                        stock_name=result.get("stock_name", ""),
                        target_date=target_date,
                        pool_type=pool_type,
                        anomaly_type="signal_buy",
                        confidence=result.get("confidence", 50),
                        anomaly_data={
                            "indicator_values": result.get("indicator_values"),
                            "matched_conditions": result.get("matched_conditions"),
                            "current_price": result.get("current_price"),
                            "change_percent": result.get("change_percent"),
                        },
                        confidence_reason=f"匹配 {len(result.get('matched_conditions', []))} 个条件"
                    )
                except Exception as e:
                    logger.error(f"保存筛选结果失败: {e}")

        return {
            "strategy_id": strategy.id,
            "strategy_name": strategy.strategy_name,
            "stocks_found": len(results),
            "stocks": results[:50],  # 只返回前50条
        }


# 单例
stock_screening_service = StockScreeningService()