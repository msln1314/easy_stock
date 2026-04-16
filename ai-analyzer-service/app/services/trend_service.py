"""
趋势分析服务
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.core.logging import get_logger
from app.core.ai_provider import ai_provider_manager
from app.core.mcp_client import mcp_client
from app.models.trend_models import (
    TrendAnalysisResult,
    BatchTrendResponse,
    KeyIndicator,
    ScoreSummary
)

logger = get_logger(__name__)


TREND_PROMPT_TEMPLATE = """
你是一位专业的股票分析师。请根据以下数据分析股票趋势：

股票代码：{stock_code}
分析日期：{analysis_date}

关键指标数据：
{indicators_data}

评分数据：
{score_data}

请提供：
1. 趋势方向判断（上升/下降/横盘）
2. 趋势强度评估（0-1之间的数值）
3. 分析置信度（0-1之间的数值）
4. 关键支撑/压力位分析
5. 技术形态解读
6. 短中长期展望
7. 风险提示

请以JSON格式返回结果。
"""


class TrendService:
    """趋势分析服务"""

    def __init__(self):
        self.default_indicators = ["MA5", "MA10", "MA20", "RSI14", "MACD_DIF", "MACD_DEA"]

    async def analyze_trend(
        self,
        stock_code: str,
        analysis_type: str = "comprehensive",
        include_indicators: Optional[List[str]] = None,
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> TrendAnalysisResult:
        """
        分析单只股票趋势

        Args:
            stock_code: 股票代码
            analysis_type: 分析类型
            include_indicators: 包含的指标
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据

        Returns:
            趋势分析结果
        """
        logger.info(f"分析趋势: {stock_code}, type={analysis_type}")

        analysis_date = datetime.now().strftime("%Y%m%d")
        indicators = include_indicators or self.default_indicators

        # 获取指标数据
        indicator_data = {}
        if kline_data:
            # 如果提供了K线数据，使用内置计算
            indicator_data = self._calculate_basic_indicators(kline_data)
        else:
            # 尝试从 factor-service 获取
            try:
                result = await mcp_client.get_indicator_data(stock_code, indicators, analysis_date)
                indicator_data = result.get("indicators", {})
            except Exception as e:
                logger.warning(f"获取指标数据失败: {e}")

        # 获取评分数据（可选）
        score_data = {}
        try:
            score_result = await mcp_client.get_score_data([stock_code], [], analysis_date)
            score_data = score_result.get("stocks", [])
        except Exception as e:
            logger.warning(f"获取评分数据失败: {e}")

        # 构建分析上下文
        context = {
            "stock_code": stock_code,
            "stock_name": stock_name or stock_code,
            "analysis_date": analysis_date,
            "indicators_data": indicator_data,
            "score_data": score_data
        }

        # 使用 AI 分析
        provider = ai_provider_manager.get_provider()
        prompt = TREND_PROMPT_TEMPLATE.format(
            stock_code=stock_code,
            analysis_date=analysis_date,
            indicators_data=str(indicator_data),
            score_data=str(score_data)
        )

        analysis_text = await provider.analyze(prompt, context, model)

        # 解析结果
        result = self._parse_analysis_result(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=analysis_date,
            analysis_text=analysis_text,
            indicator_data=indicator_data,
            score_data=score_data
        )

        return result

    async def batch_analyze_trends(
        self,
        stock_codes: List[str],
        analysis_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> BatchTrendResponse:
        """
        批量趋势分析

        Args:
            stock_codes: 股票代码列表
            analysis_type: 分析类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            批量趋势分析响应
        """
        logger.info(f"批量趋势分析: {len(stock_codes)}只股票")

        analysis_date = datetime.now().strftime("%Y%m%d")
        results = []

        for stock_code in stock_codes:
            kline_data = stock_data_map.get(stock_code) if stock_data_map else None
            result = await self.analyze_trend(
                stock_code=stock_code,
                analysis_type=analysis_type,
                model=model,
                kline_data=kline_data
            )
            results.append(result)

        return BatchTrendResponse(
            analysis_date=analysis_date,
            results=results,
            count=len(results)
        )

    def _calculate_basic_indicators(self, kline_data: List[Dict]) -> Dict:
        """计算基础指标"""
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(kline_data)
        closes = df["close"].values

        indicators = {}

        # MA5, MA10, MA20
        if len(closes) >= 5:
            indicators["MA5"] = float(np.mean(closes[-5:]))
        if len(closes) >= 10:
            indicators["MA10"] = float(np.mean(closes[-10:]))
        if len(closes) >= 20:
            indicators["MA20"] = float(np.mean(closes[-20:]))

        # RSI14
        if len(closes) >= 15:
            deltas = np.diff(closes[-15:])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            indicators["RSI14"] = float(rsi)

        return indicators

    def _parse_analysis_result(
        self,
        stock_code: str,
        stock_name: Optional[str],
        analysis_date: str,
        analysis_text: str,
        indicator_data: Dict,
        score_data: Dict
    ) -> TrendAnalysisResult:
        """解析分析结果"""
        import json
        import re

        # 尝试从文本中提取 JSON
        try:
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                trend_direction = parsed.get("trend_direction", "sideways")
                trend_strength = float(parsed.get("trend_strength", 0.5))
                confidence = float(parsed.get("confidence", 0.5))
                key_points = parsed.get("key_points", [])
                warnings = parsed.get("warnings", [])
            else:
                trend_direction = "sideways"
                trend_strength = 0.5
                confidence = 0.5
                key_points = []
                warnings = []
        except Exception:
            trend_direction = "sideways"
            trend_strength = 0.5
            confidence = 0.5
            key_points = []
            warnings = []

        # 构建关键指标
        key_indicators = {}
        for ind_name, value in indicator_data.items():
            signal = self._get_indicator_signal(ind_name, value)
            key_indicators[ind_name] = KeyIndicator(value=float(value), signal=signal)

        # 构建评分摘要
        score_summary = None
        if score_data:
            first_stock = score_data[0] if isinstance(score_data, list) and score_data else {}
            score_summary = ScoreSummary(
                composite_score=float(first_stock.get("score", 0)),
                rank=first_stock.get("rank")
            )

        return TrendAnalysisResult(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=analysis_date,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence=confidence,
            key_indicators=key_indicators,
            score_summary=score_summary,
            analysis_text=analysis_text,
            key_points=key_points,
            warnings=warnings
        )

    def _get_indicator_signal(self, indicator_name: str, value: float) -> str:
        """获取指标信号"""
        if indicator_name.startswith("RSI"):
            if value > 80:
                return "超买"
            elif value < 20:
                return "超卖"
            return "中性"
        elif indicator_name.startswith("MACD"):
            if value > 0:
                return "金叉"
            elif value < 0:
                return "死叉"
            return "中性"
        return "中性"


# 单例
trend_service = TrendService()