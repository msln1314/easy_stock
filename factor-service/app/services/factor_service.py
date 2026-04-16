"""
因子选股与评分计算服务

提供因子筛选、评分计算等功能
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.logging import get_logger
from app.models.factor_models import (
    FactorCondition,
    ScoreWeight,
    FactorScreenRequest,
    FactorScreenResponse,
    ScoreCalculateRequest,
    ScoreCalculateResponse,
    StockScoreResult,
    FactorValueRequest,
    FactorValueResponse,
    FactorDefinition,
    FactorListResponse,
)
from app.services.indicator_service import IndicatorService

logger = get_logger(__name__)


class FactorService:
    """
    因子选股服务

    提供因子筛选和评分计算功能
    """

    # 预定义因子列表
    PRESET_FACTORS = [
        FactorDefinition(factor_id="RSI14", factor_name="14日RSI", category="momentum", description="相对强弱指标"),
        FactorDefinition(factor_id="RSI6", factor_name="6日RSI", category="momentum", description="相对强弱指标"),
        FactorDefinition(factor_id="MA5", factor_name="5日均线", category="trend", description="移动平均线"),
        FactorDefinition(factor_id="MA10", factor_name="10日均线", category="trend", description="移动平均线"),
        FactorDefinition(factor_id="MA20", factor_name="20日均线", category="trend", description="移动平均线"),
        FactorDefinition(factor_id="MACD_HIST", factor_name="MACD柱", category="momentum", description="MACD柱状图"),
        FactorDefinition(factor_id="KDJ_K", factor_name="KDJ-K值", category="momentum", description="KDJ的K值"),
        FactorDefinition(factor_id="BOLL_UP", factor_name="布林上轨", category="volatility", description="布林带上轨"),
        FactorDefinition(factor_id="AMP", factor_name="振幅", category="volatility", description="当日振幅"),
        FactorDefinition(factor_id="VOL_RATIO", factor_name="量比", category="volume", description="成交量比率"),
        FactorDefinition(factor_id="ATR14", factor_name="14日ATR", category="volatility", description="平均真实波幅"),
        # 组合因子
        FactorDefinition(factor_id="MA5_MA10", factor_name="MA5-MA10差值", category="custom", description="MA5与MA10的差值", is_custom=True),
        FactorDefinition(factor_id="MA5_MA20", factor_name="MA5-MA20差值", category="custom", description="MA5与MA20的差值", is_custom=True),
        FactorDefinition(factor_id="PRICE_BOLL", factor_name="价格位置", category="custom", description="价格在布林带中的位置", is_custom=True),
    ]

    def __init__(self):
        """初始化因子服务"""
        self.indicator_service = IndicatorService()
        self._factor_map = {f.factor_id: f for f in self.PRESET_FACTORS}

    async def screen_stocks(
        self,
        conditions: List[FactorCondition],
        stock_pool: Optional[List[str]] = None,
        date: Optional[str] = None,
        limit: int = 50,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> FactorScreenResponse:
        """
        因子选股

        Args:
            conditions: 筛选条件列表
            stock_pool: 股票池，默认全A股（需外部提供）
            date: 日期
            limit: 返回数量限制
            stock_data_map: 各股票K线数据映射

        Returns:
            FactorScreenResponse: 选股结果
        """
        logger.info(f"因子选股: conditions={len(conditions)}, stock_pool={len(stock_pool) if stock_pool else 'unknown'}")

        date_str = date or datetime.now().strftime("%Y%m%d")

        # 如果没有提供股票池或数据，返回空结果
        if stock_pool is None or stock_data_map is None:
            logger.warning("未提供股票池或K线数据，无法执行选股")
            return FactorScreenResponse(
                date=date_str,
                stocks=[],
                count=0
            )

        results = []
        for stock_code in stock_pool:
            kline_data = stock_data_map.get(stock_code)
            if not kline_data:
                continue

            # 计算所需因子值
            factor_values = {}
            match = True

            for condition in conditions:
                factor_id = condition.factor_id
                try:
                    value = await self._get_factor_value_internal(stock_code, factor_id, kline_data)
                    if value is None:
                        match = False
                        break
                    factor_values[factor_id] = value

                    # 判断条件
                    if not self._check_condition(value, condition):
                        match = False
                        break
                except Exception as e:
                    logger.debug(f"计算因子 {factor_id} 失败: {e}")
                    match = False
                    break

            if match and factor_values:
                # 计算简单评分（满足条件的因子数量）
                score = len(factor_values) * 10  # 基础分
                results.append(StockScoreResult(
                    stock_code=stock_code,
                    stock_name="",  # 需外部获取
                    score=float(score),
                    factor_values=factor_values
                ))

        # 按评分排序并限制数量
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:limit]

        # 添加排名
        for i, r in enumerate(results):
            r.rank = i + 1

        return FactorScreenResponse(
            date=date_str,
            stocks=results,
            count=len(results)
        )

    async def calculate_score(
        self,
        stock_codes: List[str],
        weights: List[ScoreWeight],
        date: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> ScoreCalculateResponse:
        """
        计算综合评分

        Args:
            stock_codes: 股票代码列表
            weights: 评分权重配置
            date: 日期
            stock_data_map: 各股票K线数据映射

        Returns:
            ScoreCalculateResponse: 评分结果
        """
        logger.info(f"计算评分: stocks={len(stock_codes)}, weights={len(weights)}")

        date_str = date or datetime.now().strftime("%Y%m%d")

        if stock_data_map is None:
            logger.warning("未提供K线数据，无法计算评分")
            return ScoreCalculateResponse(
                date=date_str,
                stocks=[],
                weights_summary={}
            )

        # 计算所有股票的因子值
        all_factor_values = {}
        factor_ids = [w.factor_id for w in weights]

        for stock_code in stock_codes:
            kline_data = stock_data_map.get(stock_code)
            if not kline_data:
                continue

            values = {}
            for factor_id in factor_ids:
                try:
                    value = await self._get_factor_value_internal(stock_code, factor_id, kline_data)
                    if value is not None:
                        values[factor_id] = value
                except Exception:
                    pass

            if values:
                all_factor_values[stock_code] = values

        # 对每个因子进行百分位排名
        factor_percentiles = {}
        for factor_id in factor_ids:
            values = [all_factor_values.get(s, {}).get(factor_id) for s in stock_codes]
            valid_values = [(s, v) for s, v in zip(stock_codes, values) if v is not None]

            if valid_values:
                sorted_values = sorted(valid_values, key=lambda x: x[1])
                for i, (s, v) in enumerate(sorted_values):
                    percentile = (i + 1) / len(sorted_values) * 100
                    if s not in factor_percentiles:
                        factor_percentiles[s] = {}
                    factor_percentiles[s][factor_id] = percentile

        # 计算加权评分
        results = []
        weights_summary = {w.factor_id: w.weight for w in weights}

        for stock_code in stock_codes:
            if stock_code not in all_factor_values:
                continue

            total_score = 0.0
            factor_scores = {}

            for weight in weights:
                factor_id = weight.factor_id
                percentile = factor_percentiles.get(stock_code, {}).get(factor_id, 50)

                # 根据方向调整评分
                if weight.direction == "low":
                    adjusted_score = 100 - percentile  # 低值更好
                else:
                    adjusted_score = percentile  # 高值更好

                weighted_score = adjusted_score * weight.weight
                total_score += weighted_score
                factor_scores[factor_id] = adjusted_score

            results.append(StockScoreResult(
                stock_code=stock_code,
                stock_name="",
                score=total_score,
                factor_values=all_factor_values[stock_code],
                factor_scores=factor_scores
            ))

        # 排序并添加排名
        results.sort(key=lambda x: x.score, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1

        return ScoreCalculateResponse(
            date=date_str,
            stocks=results,
            weights_summary=weights_summary
        )

    async def get_factor_value(
        self,
        stock_code: str,
        factor_id: str,
        date: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> FactorValueResponse:
        """
        获取单只股票的因子值

        Args:
            stock_code: 股票代码
            factor_id: 因子ID
            date: 日期
            kline_data: K线数据

        Returns:
            FactorValueResponse: 因子值结果
        """
        date_str = date or datetime.now().strftime("%Y%m%d")

        if kline_data is None:
            logger.warning(f"未提供K线数据，无法获取 {stock_code} 的因子值")
            return FactorValueResponse(
                stock_code=stock_code,
                factor_id=factor_id,
                factor_name=self._factor_map.get(factor_id, FactorDefinition(factor_id=factor_id, factor_name=factor_id, category="custom")).factor_name,
                value=0.0,
                date=date_str
            )

        value = await self._get_factor_value_internal(stock_code, factor_id, kline_data)

        return FactorValueResponse(
            stock_code=stock_code,
            factor_id=factor_id,
            factor_name=self._factor_map.get(factor_id, FactorDefinition(factor_id=factor_id, factor_name=factor_id, category="custom")).factor_name,
            value=value or 0.0,
            date=date_str
        )

    async def _get_factor_value_internal(
        stock_code: str,
        factor_id: str,
        kline_data: List[Dict]
    ) -> Optional[float]:
        """
        内部方法：计算因子值

        Args:
            stock_code: 股票代码
            factor_id: 因子ID
            kline_data: K线数据

        Returns:
            因子值
        """
        # 组合因子处理
        if factor_id == "MA5_MA10":
            ma5 = await self._get_indicator_value(kline_data, "MA5")
            ma10 = await self._get_indicator_value(kline_data, "MA10")
            if ma5 is not None and ma10 is not None:
                return ma5 - ma10
            return None

        if factor_id == "MA5_MA20":
            ma5 = await self._get_indicator_value(kline_data, "MA5")
            ma20 = await self._get_indicator_value(kline_data, "MA20")
            if ma5 is not None and ma20 is not None:
                return ma5 - ma20
            return None

        if factor_id == "PRICE_BOLL":
            boll = self.indicator_service.calculate_boll(pd.DataFrame(kline_data))
            close = kline_data[-1].get("close") if kline_data else None
            if boll.get("upper") and boll.get("lower") and close:
                return (close - boll["lower"]) / (boll["upper"] - boll["lower"]) * 100
            return None

        # 单指标因子
        return await self._get_indicator_value(kline_data, factor_id)

    async def _get_indicator_value(self, kline_data: List[Dict], indicator_id: str) -> Optional[float]:
        """
        获取指标值

        Args:
            kline_data: K线数据
            indicator_id: 指标ID

        Returns:
            指标值
        """
        df = pd.DataFrame(kline_data)
        if df.empty:
            return None

        # 直接调用指标服务的方法
        return self.indicator_service._calculate_single_indicator(df, indicator_id)

    def _check_condition(self, value: float, condition: FactorCondition) -> bool:
        """
        检查因子条件

        Args:
            value: 因子值
            condition: 条件

        Returns:
            是否满足条件
        """
        op = condition.operator
        threshold = condition.value
        threshold2 = condition.value2

        if op == "gt":
            return value > threshold
        elif op == "lt":
            return value < threshold
        elif op == "ge":
            return value >= threshold
        elif op == "le":
            return value <= threshold
        elif op == "eq":
            return value == threshold
        elif op == "between":
            return threshold <= value <= threshold2

        logger.warning(f"未知的操作符: {op}")
        return False

    def get_available_factors(self) -> FactorListResponse:
        """
        获取支持的因子列表

        Returns:
            FactorListResponse: 因子列表
        """
        return FactorListResponse(
            factors=self.PRESET_FACTORS,
            count=len(self.PRESET_FACTORS)
        )


# 单例
factor_service = FactorService()