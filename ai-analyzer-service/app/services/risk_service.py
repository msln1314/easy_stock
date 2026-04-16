"""
风险评估服务
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.core.logging import get_logger
from app.core.ai_provider import ai_provider_manager
from app.core.mcp_client import mcp_client
from app.models.risk_models import (
    RiskAssessmentResult,
    PortfolioRiskResult,
    CompareRiskResult,
    VolatilityMetrics,
    DrawdownMetrics,
    TailRisk,
    BacktestRisk,
    RiskFactor
)

logger = get_logger(__name__)


RISK_PROMPT_TEMPLATE = """
你是一位专业的风险管理专家。请根据以下数据评估股票风险：

股票代码：{stock_code}
评估日期：{assessment_date}

波动率数据：
{volatility_data}

回撤数据：
{drawdown_data}

回测数据：
{backtest_data}

请提供：
1. 风险等级判断（低/中/高/极高）
2. 风险评分（0-100的数值）
3. 主要风险因素识别
4. 极端情况分析
5. 风险控制建议

请以JSON格式返回结果。
"""


class RiskService:
    """风险评估服务"""

    def __init__(self):
        pass

    async def assess_risk(
        self,
        stock_code: str,
        assessment_type: str = "comprehensive",
        model: Optional[str] = None,
        stock_name: Optional[str] = None,
        kline_data: Optional[List[Dict]] = None,
        backtest_data: Optional[Dict] = None
    ) -> RiskAssessmentResult:
        """
        单只股票风险评估

        Args:
            stock_code: 股票代码
            assessment_type: 评估类型
            model: AI模型
            stock_name: 股票名称
            kline_data: K线数据
            backtest_data: 回测数据

        Returns:
            风险评估结果
        """
        logger.info(f"风险评估: {stock_code}, type={assessment_type}")

        assessment_date = datetime.now().strftime("%Y%m%d")

        # 计算波动率和回撤指标
        volatility_data = {}
        drawdown_data = {}
        backtest_risk_data = {}

        if kline_data:
            volatility_data, drawdown_data = self._calculate_risk_metrics(kline_data)

        if backtest_data:
            backtest_risk_data = self._parse_backtest_risk(backtest_data)

        # 构建分析上下文
        context = {
            "stock_code": stock_code,
            "stock_name": stock_name or stock_code,
            "assessment_date": assessment_date,
            "volatility_data": volatility_data,
            "drawdown_data": drawdown_data,
            "backtest_data": backtest_risk_data
        }

        # 使用 AI 分析
        provider = ai_provider_manager.get_provider()
        prompt = RISK_PROMPT_TEMPLATE.format(
            stock_code=stock_code,
            assessment_date=assessment_date,
            volatility_data=str(volatility_data),
            drawdown_data=str(drawdown_data),
            backtest_data=str(backtest_risk_data)
        )

        analysis_text = await provider.analyze(prompt, context, model)

        # 解析结果
        result = self._parse_assessment_result(
            stock_code=stock_code,
            stock_name=stock_name,
            assessment_date=assessment_date,
            analysis_text=analysis_text,
            volatility_data=volatility_data,
            drawdown_data=drawdown_data,
            backtest_data=backtest_risk_data
        )

        return result

    async def portfolio_risk(
        self,
        stock_codes: List[str],
        weights: Optional[List[float]] = None,
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> PortfolioRiskResult:
        """
        组合风险评估

        Args:
            stock_codes: 股票代码列表
            weights: 权重列表
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            组合风险评估结果
        """
        logger.info(f"组合风险评估: {len(stock_codes)}只股票")

        assessment_date = datetime.now().strftime("%Y%m%d")
        individual_risks = []

        for stock_code in stock_codes:
            kline_data = stock_data_map.get(stock_code) if stock_data_map else None
            risk = await self.assess_risk(
                stock_code=stock_code,
                model=model,
                kline_data=kline_data
            )
            individual_risks.append(risk)

        # 计算组合风险评分
        risk_scores = [r.risk_score for r in individual_risks]
        avg_score = sum(risk_scores) / len(risk_scores) if risk_scores else 50

        if weights:
            weighted_score = sum(s * w for s, w in zip(risk_scores, weights))
        else:
            weighted_score = avg_score

        risk_level = self._get_risk_level(weighted_score)

        return PortfolioRiskResult(
            assessment_date=assessment_date,
            portfolio_risk_level=risk_level,
            portfolio_risk_score=int(weighted_score),
            individual_risks=individual_risks,
            diversification_score=0.7,
            correlation_matrix={},
            analysis_text=f"组合包含{len(stock_codes)}只股票，平均风险评分{avg_score:.1f}"
        )

    async def compare_risk(
        self,
        stock_codes: List[str],
        model: Optional[str] = None,
        stock_data_map: Optional[Dict[str, List[Dict]]] = None
    ) -> CompareRiskResult:
        """
        多股风险对比

        Args:
            stock_codes: 股票代码列表
            model: AI模型
            stock_data_map: 股票数据映射

        Returns:
            风险对比结果
        """
        logger.info(f"风险对比: {len(stock_codes)}只股票")

        assessment_date = datetime.now().strftime("%Y%m%d")
        comparisons = []

        for stock_code in stock_codes:
            kline_data = stock_data_map.get(stock_code) if stock_data_map else None
            risk = await self.assess_risk(
                stock_code=stock_code,
                model=model,
                kline_data=kline_data
            )
            comparisons.append(risk)

        # 按风险评分排序
        sorted_risks = sorted(comparisons, key=lambda x: x.risk_score)
        ranking = [r.stock_code for r in sorted_risks]

        return CompareRiskResult(
            assessment_date=assessment_date,
            comparisons=comparisons,
            ranking=ranking,
            summary=f"风险最低: {ranking[0]}, 风险最高: {ranking[-1]}"
        )

    def _calculate_risk_metrics(self, kline_data: List[Dict]) -> tuple:
        """计算风险指标"""
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(kline_data)
        closes = df["close"].values

        volatility_data = {}
        drawdown_data = {}

        # 日波动率
        returns = np.diff(closes) / closes[:-1]
        daily_vol = np.std(returns) * 100 if len(returns) > 0 else 0
        volatility_data["daily_volatility"] = float(daily_vol)
        volatility_data["annual_volatility"] = float(daily_vol * np.sqrt(250))

        # 最大回撤
        peak = closes[0]
        max_dd = 0
        for price in closes:
            if price > peak:
                peak = price
            dd = (peak - price) / peak * 100
            if dd > max_dd:
                max_dd = dd

        drawdown_data["max_drawdown"] = float(-max_dd)
        drawdown_data["avg_drawdown"] = float(-max_dd / 2)

        return volatility_data, drawdown_data

    def _parse_backtest_risk(self, backtest_data: Dict) -> Dict:
        """解析回测风险数据"""
        return {
            "win_rate": backtest_data.get("win_rate", 0),
            "max_drawdown": backtest_data.get("max_drawdown", 0),
            "sharpe_ratio": backtest_data.get("sharpe_ratio", 0)
        }

    def _parse_assessment_result(
        self,
        stock_code: str,
        stock_name: Optional[str],
        assessment_date: str,
        analysis_text: str,
        volatility_data: Dict,
        drawdown_data: Dict,
        backtest_data: Dict
    ) -> RiskAssessmentResult:
        """解析评估结果"""
        import json
        import re

        try:
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                risk_level = parsed.get("risk_level", "medium")
                risk_score = int(parsed.get("risk_score", 50))
            else:
                risk_level = "medium"
                risk_score = 50
        except Exception:
            risk_level = "medium"
            risk_score = 50

        # 构建指标
        volatility_metrics = VolatilityMetrics(
            daily_volatility=volatility_data.get("daily_volatility", 0),
            annual_volatility=volatility_data.get("annual_volatility", 0),
            atr_ratio=0
        )

        drawdown_metrics = DrawdownMetrics(
            max_drawdown=drawdown_data.get("max_drawdown", 0),
            avg_drawdown=drawdown_data.get("avg_drawdown", 0),
            drawdown_duration=0
        )

        tail_risk = TailRisk()

        backtest_risk = BacktestRisk(
            win_rate=backtest_data.get("win_rate", 0),
            loss_streak_max=0,
            avg_loss=0
        )

        return RiskAssessmentResult(
            stock_code=stock_code,
            stock_name=stock_name,
            assessment_date=assessment_date,
            risk_level=risk_level,
            risk_score=risk_score,
            volatility_metrics=volatility_metrics,
            drawdown_metrics=drawdown_metrics,
            tail_risk=tail_risk,
            backtest_risk=backtest_risk,
            risk_factors=[],
            analysis_text=analysis_text,
            risk_mitigation=[]
        )

    def _get_risk_level(self, score: float) -> str:
        """根据评分获取风险等级"""
        if score < 30:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 70:
            return "high"
        else:
            return "extreme"


# 单例
risk_service = RiskService()