"""
AI股票分析服务模块
使用AI生成股票分析报告
"""
import json
import time
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from loguru import logger

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from services.config import SysConfigService
from models.stock_analysis import (
    StockAnalysisReport, AnalysisConversation,
    AnalysisType, AnalysisStatus
)


async def get_ai_config(key: str, default: str = "") -> str:
    """从数据库获取AI配置"""
    service = SysConfigService()
    value = await service.get_config_value(key)
    return value if value else default


class StockAnalysisService:
    """AI股票分析服务"""

    def __init__(self):
        self.client = None
        self.model = None

    async def _init_client(self):
        """初始化OpenAI客户端"""
        api_key = await get_ai_config("ai.openai_api_key", OPENAI_API_KEY)
        base_url = await get_ai_config("ai.openai_base_url", OPENAI_BASE_URL)
        model = await get_ai_config("ai.openai_model", OPENAI_MODEL)

        if not api_key:
            raise ValueError("未配置OpenAI API Key")

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _get_system_prompt(self, analysis_type: AnalysisType) -> str:
        """根据分析类型获取系统提示词"""
        base_prompt = """你是一位专业的股票分析师，拥有丰富的投资分析经验。
请基于用户提供的股票信息，生成一份专业、客观的分析报告。

报告需要包含以下部分（使用Markdown格式）：

## 摘要
简要概括分析结论和核心观点

## 基本面分析
- 财务状况分析（营收、利润、ROE等）
- 行业地位和竞争优势
- 管理层和公司治理

## 技术面分析
- 价格走势和关键技术指标
- 支撑位和阻力位分析
- 量价关系

## 风险分析
- 主要风险因素
- 市场风险、经营风险、财务风险

## 投资建议
- 综合评估和投资评级
- 目标价位区间
- 操作建议

注意事项：
- 分析要客观、理性，避免主观臆断
- 数据引用要有依据，注明数据来源
- 风险提示要充分、明确
- 投资建议要审慎，不做过于绝对的判断
"""

        type_prompts = {
            AnalysisType.FUNDAMENTAL: "\n请重点聚焦基本面分析，深入挖掘财务数据和经营状况。",
            AnalysisType.TECHNICAL: "\n请重点聚焦技术面分析，详细分析价格走势和技术指标。",
            AnalysisType.COMPREHENSIVE: "\n请进行全面分析，涵盖基本面、技术面、风险等多个维度。",
            AnalysisType.INDUSTRY: "\n请重点分析行业背景、竞争格局、发展趋势。",
            AnalysisType.SENTIMENT: "\n请重点分析市场情绪、舆情动态、投资者预期。",
            AnalysisType.RISK: "\n请重点进行风险评估，识别潜在风险因素并提出应对建议。",
        }

        return base_prompt + type_prompts.get(analysis_type, "")

    async def create_analysis(
        self,
        stock_code: str,
        stock_name: str,
        request_prompt: str,
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        user_id: Optional[int] = None,
        stock_data: Optional[Dict[str, Any]] = None,
    ) -> StockAnalysisReport:
        """
        创建AI分析报告

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            request_prompt: 用户分析请求
            analysis_type: 分析类型
            user_id: 用户ID
            stock_data: 股票数据（行情、财务等）

        Returns:
            StockAnalysisReport: 分析报告对象
        """
        # 初始化客户端
        if not self.client:
            await self._init_client()

        # 创建报告记录
        report = await StockAnalysisReport.create(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_type=analysis_type.value if isinstance(analysis_type, AnalysisType) else analysis_type,
            request_prompt=request_prompt,
            status=AnalysisStatus.PROCESSING.value,
            user_id=user_id,
            model_name=self.model,
        )

        start_time = time.time()

        try:
            # 构建消息
            system_prompt = self._get_system_prompt(analysis_type)

            user_message = f"""请分析股票：{stock_name}（{stock_code}）

用户需求：{request_prompt}

股票数据：
{json.dumps(stock_data or {}, ensure_ascii=False, indent=2)}
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # 调用AI生成分析报告
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000,
            )

            assistant_message = response.choices[0].message
            full_report = assistant_message.content

            # 解析报告结构
            parsed = self._parse_report(full_report)

            # 记录对话
            await AnalysisConversation.create(
                report_id=report.id,
                role="user",
                content=user_message,
            )
            await AnalysisConversation.create(
                report_id=report.id,
                role="assistant",
                content=full_report,
                tokens_used=response.usage.total_tokens if response.usage else None,
            )

            # 更新报告
            duration_ms = int((time.time() - start_time) * 1000)

            report.status = AnalysisStatus.COMPLETED.value
            report.full_report = full_report
            report.summary = parsed.get("summary")
            report.fundamental_analysis = parsed.get("fundamental")
            report.technical_analysis = parsed.get("technical")
            report.risk_analysis = parsed.get("risk")
            report.recommendation = parsed.get("recommendation")
            report.duration_ms = duration_ms
            report.tokens_used = response.usage.total_tokens if response.usage else None
            await report.save()

            logger.info(f"AI分析报告生成成功: {stock_code}, 耗时{duration_ms}ms")
            return report

        except Exception as e:
            logger.error(f"AI分析报告生成失败: {stock_code}, {e}")

            report.status = AnalysisStatus.FAILED.value
            report.error_message = str(e)
            await report.save()

            return report

    def _parse_report(self, full_report: str) -> Dict[str, str]:
        """解析报告内容，提取各部分"""
        result = {}

        sections = {
            "summary": ["## 摘要", "##摘要", "# 摘要"],
            "fundamental": ["## 基本面分析", "##基本面分析", "# 基本面分析"],
            "technical": ["## 技术面分析", "##技术面分析", "# 技术面分析"],
            "risk": ["## 风险分析", "##风险分析", "# 风险分析"],
            "recommendation": ["## 投资建议", "##投资建议", "# 投资建议"],
        }

        lines = full_report.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # 检查是否是新section开始
            found_new_section = False
            for section_name, markers in sections.items():
                for marker in markers:
                    if line.strip().startswith(marker):
                        # 保存上一个section
                        if current_section and current_content:
                            result[current_section] = "\n".join(current_content).strip()
                        current_section = section_name
                        current_content = []
                        found_new_section = True
                        break
                if found_new_section:
                    break

            if not found_new_section and current_section:
                current_content.append(line)

        # 保存最后一个section
        if current_section and current_content:
            result[current_section] = "\n".join(current_content).strip()

        return result

    async def get_report(self, report_id: int) -> Optional[StockAnalysisReport]:
        """获取报告详情"""
        return await StockAnalysisReport.get_or_none(id=report_id)

    async def get_report_history(
        self,
        stock_code: Optional[str] = None,
        user_id: Optional[int] = None,
        status: Optional[AnalysisStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[StockAnalysisReport]:
        """获取报告历史列表"""
        query = StockAnalysisReport.all()

        if stock_code:
            query = query.filter(stock_code=stock_code)
        if user_id:
            query = query.filter(user_id=user_id)
        if status:
            query = query.filter(status=status)

        return await query.order_by("-created_at").limit(limit).offset(offset)

    async def get_conversations(self, report_id: int) -> List[AnalysisConversation]:
        """获取报告的对话历史"""
        return await AnalysisConversation.filter(report_id=report_id).order_by("created_at")

    async def delete_report(self, report_id: int, user_id: Optional[int] = None) -> bool:
        """删除报告"""
        report = await StockAnalysisReport.get_or_none(id=report_id)
        if not report:
            return False

        # 检查权限
        if user_id and report.user_id != user_id:
            return False

        # 删除对话记录
        await AnalysisConversation.filter(report_id=report_id).delete()

        # 删除报告
        await report.delete()
        return True

    async def get_statistics(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取分析报告统计"""
        query = StockAnalysisReport.filter(status=AnalysisStatus.COMPLETED)

        if user_id:
            query = query.filter(user_id=user_id)

        # 日期过滤需要特殊处理
        # 这里简化处理，实际需要根据数据库字段类型调整

        reports = await query.all()

        return {
            "total_count": len(reports),
            "avg_duration_ms": sum(r.duration_ms or 0 for r in reports) / len(reports) if reports else 0,
            "avg_tokens": sum(r.tokens_used or 0 for r in reports) / len(reports) if reports else 0,
            "analysis_types": {
                t: len([r for r in reports if r.analysis_type == t])
                for t in AnalysisType
            },
            "stocks_analyzed": len(set(r.stock_code for r in reports)),
        }


# 单例
stock_analysis_service = StockAnalysisService()