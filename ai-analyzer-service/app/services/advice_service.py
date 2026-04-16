"""
投资建议服务
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.core.logging import get_logger
from app.core.ai_provider import ai_provider_manager
from app.services.trend_service import trend_service
from app.services.risk_service import risk_service
from app.models.advice_models import (
    AdviceResult,
    BatchAdviceResponse,
    ReportResult,
    ActionSuggestion,
    Reasoning,
    TimeHorizon
)

logger = get_logger(__name__)


ADVICE_PROMPT_TEMPLATE = """
你是一位专业的投资顾问。请根据以下数据给出投资建议：

股票代码：{stock_code}
建议日期：{advice_date}

趋势分析：
{trend_analysis}

风险评估：
{risk_assessment}

评分排名：
{score_data}

请提供：
1. 投资建议（买入/卖出/持有/观望）
2. 建议置信度（0-1之间的数值）
3. 仓位建议
4. 入场/出场策略
5. 目标价位和止损位
6. 投资理由和风险提示

请以JSON格式返回结果。
"""


class AdviceService:
    """投资建议服务"""

    def __init__(self):
        pass

    async def generate_advice(
        self,
        stock_code: str,
        advice_type: str = "comprehensive",
        include_backtest: bool = True,
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None
    ) -> AdviceResult:
        """
        生成投资建议

        Args:
            stock_code: 股票代码
            advice_type: 建议类型
            include_backtest: 包含回测
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据

        Returns:
            投资建议结果
        """
        logger.info(f"生成投资建议: {stock_code}, type={advice_type}")

        advice_date = datetime.now().strftime("%Y%m%d")

        # 获取趋势分析
        trend_result = await trend_service.analyze_trend(
            stock_code=stock_code,
            model=model,
            stock_name=stock_name,
            kline_data=kline_data
        )

        # 获取风险评估
        risk_result = await risk_service.assess_risk(
            stock_code=stock_code,
            model=model,
            stock_name=stock_name,
            kline_data=kline_data
        )

        # 构建分析上下文
        context = {
            "stock_code": stock_code,
            "stock_name": stock_name or stock_code,
            "advice_date": advice_date,
            "trend_analysis": {
                "direction": trend_result.trend_direction,
                "strength": trend_result.trend_strength,
                "confidence": trend_result.confidence
            },
            "risk_assessment": {
                "level": risk_result.risk_level,
                "score": risk_result.risk_score
            },
            "score_data": {}
        }

        # 使用 AI 分析
        provider = ai_provider_manager.get_provider()
        prompt = ADVICE_PROMPT_TEMPLATE.format(
            stock_code=stock_code,
            advice_date=advice_date,
            trend_analysis=str(context["trend_analysis"]),
            risk_assessment=str(context["risk_assessment"]),
            score_data=str(context["score_data"])
        )

        analysis_text = await provider.analyze(prompt, context, model)

        # 解析结果
        result = self._parse_advice_result(
            stock_code=stock_code,
            stock_name=stock_name,
            advice_date=advice_date,
            analysis_text=analysis_text,
            trend_result=trend_result,
            risk_result=risk_result
        )

        return result

    async def batch_generate_advice(
        self,
        stock_codes: List[str],
        advice_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> BatchAdviceResponse:
        """
        批量投资建议

        Args:
            stock_codes: 股票代码列表
            advice_type: 建议类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            批量投资建议响应
        """
        logger.info(f"批量投资建议: {len(stock_codes)}只股票")

        advice_date = datetime.now().strftime("%Y%m%d")
        results = []

        for stock_code in stock_codes:
            kline_data = stock_data_map.get(stock_code) if stock_data_map else None
            advice = await self.generate_advice(
                stock_code=stock_code,
                advice_type=advice_type,
                model=model,
                kline_data=kline_data
            )
            results.append(advice)

        return BatchAdviceResponse(
            advice_date=advice_date,
            results=results,
            count=len(results)
        )

    async def generate_report(
        self,
        stock_codes: List[str],
        report_type: str = "portfolio",
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> ReportResult:
        """
        生成分析报告

        Args:
            stock_codes: 股票代码列表
            report_type: 报告类型
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            报告结果
        """
        logger.info(f"生成报告: {len(stock_codes)}只股票, type={report_type}")

        report_date = datetime.now().strftime("%Y%m%d")

        # 批量生成建议
        batch_result = await self.batch_generate_advice(
            stock_codes=stock_codes,
            model=model,
            stock_data_map=stock_data_map
        )

        # 统计建议分布
        buy_count = sum(1 for r in batch_result.results if r.recommendation == "buy")
        sell_count = sum(1 for r in batch_result.results if r.recommendation == "sell")
        hold_count = sum(1 for r in batch_result.results if r.recommendation == "hold")

        # 构建报告
        title = f"投资组合分析报告 ({report_date})"
        summary = f"共分析{len(stock_codes)}只股票：建议买入{buy_count}只，持有{hold_count}只，卖出{sell_count}只"

        return ReportResult(
            report_date=report_date,
            report_type=report_type,
            title=title,
            summary=summary,
            sections=["趋势分析", "风险评估", "投资建议"],
            recommendations=[r.recommendation for r in batch_result.results[:5]],
            risk_summary="组合风险中等",
            opportunities=["关注低估值标的", "关注成长性标的"]
        )

    def _parse_advice_result(
        self,
        stock_code: str,
        stock_name: Optional[str],
        advice_date: str,
        analysis_text: str,
        trend_result: Dict,
        risk_result: Dict
    ) -> AdviceResult:
        """解析建议结果"""
        import json
        import re

        try:
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                recommendation = parsed.get("recommendation", "hold")
                confidence = float(parsed.get("confidence", 0.5))
            else:
                recommendation = "hold"
                confidence = 0.5
        except Exception:
            recommendation = "hold"
            confidence = 0.5

        # 构建建议
        action_suggestion = ActionSuggestion(
            action=self._get_action_text(recommendation),
            position_size="中等仓位",
            entry_strategy="分批建仓",
            target_price=None,
            stop_loss=None
        )

        reasoning = Reasoning(
            trend_reason=f"趋势方向: {trend_result.trend_direction}",
            score_reason="评分数据待补充",
            risk_reason=f"风险等级: {risk_result.risk_level}"
        )

        time_horizon = TimeHorizon(
            short_term="中性",
            mid_term="中性",
            long_term="中性"
        )

        return AdviceResult(
            stock_code=stock_code,
            stock_name=stock_name,
            advice_date=advice_date,
            recommendation=recommendation,
            confidence=confidence,
            action_suggestion=action_suggestion,
            reasoning=reasoning,
            time_horizon=time_horizon,
            analysis_summary=analysis_text[:500] if len(analysis_text) > 500 else analysis_text,
            key_catalysts=[],
            risk_warnings=[],
            related_stocks=[]
        )

    def _get_action_text(self, recommendation: str) -> str:
        """获取行动文本"""
        mapping = {
            "buy": "建议买入",
            "sell": "建议卖出",
            "hold": "建议持有",
            "watch": "建议观望"
        }
        return mapping.get(recommendation, "建议观望")


# 单例
advice_service = AdviceService()