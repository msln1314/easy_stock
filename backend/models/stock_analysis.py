"""
AI股票分析报告模型

存储AI生成的股票分析报告及其历史记录
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class AnalysisType(str, Enum):
    """分析类型"""
    FUNDAMENTAL = "fundamental"      # 基本面分析
    TECHNICAL = "technical"          # 技术面分析
    COMPREHENSIVE = "comprehensive"  # 综合分析
    INDUSTRY = "industry"            # 行业分析
    SENTIMENT = "sentiment"          # 情绪分析
    RISK = "risk"                    # 风险分析


class AnalysisStatus(str, Enum):
    """分析状态"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class StockAnalysisReport(Model):
    """
    AI股票分析报告表

    存储AI生成的股票分析报告
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 基本信息
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, description="股票名称")
    analysis_type = fields.CharField(
        max_length=20,
        default=AnalysisType.COMPREHENSIVE,
        description="分析类型: fundamental/technical/comprehensive/industry/sentiment/risk"
    )

    # 分析请求
    request_prompt = fields.TextField(description="用户的分析请求/问题")

    # 分析结果
    status = fields.CharField(
        max_length=20,
        default=AnalysisStatus.PENDING,
        description="状态: pending/processing/completed/failed"
    )

    # 报告内容 - 分段存储便于前端渲染
    summary = fields.TextField(null=True, description="摘要/结论")
    fundamental_analysis = fields.TextField(null=True, description="基本面分析")
    technical_analysis = fields.TextField(null=True, description="技术面分析")
    industry_analysis = fields.TextField(null=True, description="行业分析")
    risk_analysis = fields.TextField(null=True, description="风险分析")
    recommendation = fields.TextField(null=True, description="投资建议")

    # 结构化数据
    key_indicators = fields.JSONField(null=True, description="关键指标数据")
    # 示例: {"pe_ratio": 15.2, "pb_ratio": 1.5, "roe": 12.5, " revenue_growth": 8.3}

    financial_data = fields.JSONField(null=True, description="财务数据摘要")
    # 示例: {"revenue": [100, 120, 150], "net_income": [10, 15, 20], "years": ["2022", "2023", "2024"]}

    price_data = fields.JSONField(null=True, description="价格相关数据")
    # 示例: {"current_price": 25.5, "target_price": 30, "support": 23, "resistance": 28}

    # 完整报告（Markdown格式）
    full_report = fields.TextField(null=True, description="完整分析报告(Markdown)")

    # AI模型信息
    model_name = fields.CharField(max_length=50, null=True, description="使用的AI模型")
    tokens_used = fields.IntField(null=True, description="消耗的tokens数")

    # 时间信息
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    duration_ms = fields.IntField(null=True, description="生成耗时(毫秒)")

    # 用户信息
    user_id = fields.IntField(null=True, description="请求用户ID")

    # 错误信息
    error_message = fields.TextField(null=True, description="错误信息")

    # 标签和评分
    tags = fields.JSONField(null=True, description="分析标签列表")
    # 示例: ["白马股", "低估值", "高成长"]

    rating = fields.IntField(null=True, description="综合评分(1-10)")

    # 来源引用
    sources = fields.JSONField(null=True, description="数据来源引用")
    # 示例: [{"type": "sec_filing", "name": "10-K 2024", "url": "..."}]

    class Meta:
        table = "stock_analysis_reports"
        indexes = [
            ("stock_code",),
            ("analysis_type",),
            ("status",),
            ("created_at",),
            ("user_id",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.analysis_type} - {self.status}"

    @property
    def analysis_type_display(self) -> str:
        """分析类型显示文本"""
        type_map = {
            "fundamental": "基本面分析",
            "technical": "技术面分析",
            "comprehensive": "综合分析",
            "industry": "行业分析",
            "sentiment": "情绪分析",
            "risk": "风险分析",
        }
        return type_map.get(self.analysis_type, self.analysis_type)

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "pending": "待处理",
            "processing": "处理中",
            "completed": "已完成",
            "failed": "失败",
        }
        return status_map.get(self.status, self.status)


class AnalysisConversation(Model):
    """
    分析对话记录表

    存储用户与AI的分析对话历史
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 关联报告
    report_id = fields.IntField(null=True, description="关联分析报告ID")

    # 对话内容
    role = fields.CharField(max_length=20, description="角色: user/assistant")
    content = fields.TextField(description="消息内容")

    # 时间信息
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    # 元数据
    tokens_used = fields.IntField(null=True, description="消耗tokens")
    tool_calls = fields.JSONField(null=True, description="工具调用记录")

    class Meta:
        table = "analysis_conversations"
        indexes = [
            ("report_id",),
            ("created_at",),
        ]

    def __str__(self):
        return f"{self.role} - {self.created_at}"