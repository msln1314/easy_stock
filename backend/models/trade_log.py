"""
交易日志模型

记录所有交易相关行为：选股、买入、审核、卖出、预警等
"""
from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from enum import Enum


class TradeActionType(str, Enum):
    """交易行为类型"""
    # 选股相关
    STOCK_PICK = "stock_pick"              # 选股策略执行
    STOCK_PICK_RESULT = "stock_pick_result"  # 选股结果生成

    # 交易相关
    BUY_REQUEST = "buy_request"            # 买入请求
    BUY_AUDIT = "buy_audit"                # 买入审核
    BUY_EXECUTED = "buy_executed"          # 买入执行
    BUY_SUCCESS = "buy_success"            # 买入成功
    BUY_FAILED = "buy_failed"              # 买入失败

    SELL_REQUEST = "sell_request"          # 卖出请求
    SELL_EXECUTED = "sell_executed"        # 卖出执行
    SELL_SUCCESS = "sell_success"          # 卖出成功
    SELL_FAILED = "sell_failed"            # 卖出失败

    # 审核相关
    AUDIT_PASS = "audit_pass"              # 审核通过
    AUDIT_REJECT = "audit_reject"          # 审核拒绝
    AUDIT_WARNING = "audit_warning"        # 审核警告

    # 撤单相关
    CANCEL_REQUEST = "cancel_request"      # 撤单请求
    CANCEL_SUCCESS = "cancel_success"      # 撤单成功
    CANCEL_FAILED = "cancel_failed"        # 撤单失败

    # 预警相关
    WARNING_TRIGGER = "warning_trigger"    # 预警触发
    WARNING_HANDLE = "warning_handle"      # 预警处理

    # 系统相关
    SYSTEM_START = "system_start"          # 系统启动
    SYSTEM_STOP = "system_stop"            # 系统停止
    CONFIG_CHANGE = "config_change"        # 配置变更
    RULE_CHANGE = "rule_change"            # 规则变更

    # 其他
    AI_CHAT = "ai_chat"                    # AI对话
    MANUAL_OPERATION = "manual_operation"  # 手动操作


class TradeLog(Model):
    """
    交易日志表

    记录所有交易相关行为的完整日志
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 行为基本信息
    action_type = fields.CharField(
        max_length=30,
        description="行为类型: stock_pick/buy_request/buy_audit/sell_request等"
    )
    action_name = fields.CharField(max_length=100, description="行为名称")
    action_source = fields.CharField(
        max_length=20,
        default="system",
        description="行为来源: system-系统自动, user-用户操作, ai-AI决策, strategy-策略触发"
    )

    # 关联信息
    strategy_key = fields.CharField(max_length=50, null=True, description="关联策略KEY")
    stock_code = fields.CharField(max_length=20, null=True, description="关联股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")
    order_id = fields.CharField(max_length=50, null=True, description="委托单号")
    related_id = fields.IntField(null=True, description="关联记录ID（如审核日志ID）")

    # 行为详情
    action_data = fields.JSONField(null=True, description="行为数据JSON")
    # 示例:
    # buy_request: {"price": 10.5, "quantity": 1000, "amount": 10500, "order_type": "limit"}
    # audit: {"passed": true, "failed_rules": [], "warning_rules": [...]}
    # stock_pick: {"strategy_key": "xxx", "stocks_found": 5, "stocks_saved": 3}

    # 结果信息
    result = fields.CharField(
        max_length=20,
        null=True,
        description="结果: success-成功, failed-失败, pending-进行中, rejected-拒绝"
    )
    result_message = fields.TextField(null=True, description="结果消息")
    error_message = fields.TextField(null=True, description="错误信息")

    # 用户信息
    user_id = fields.IntField(null=True, description="操作用户ID")
    user_name = fields.CharField(max_length=50, null=True, description="操作用户名")

    # 时间信息
    action_time = fields.DatetimeField(auto_now_add=True, description="行为时间")
    duration_ms = fields.IntField(null=True, description="执行耗时(毫秒)")

    # 附加信息
    ip_address = fields.CharField(max_length=50, null=True, description="IP地址")
    device_info = fields.CharField(max_length=100, null=True, description="设备信息")
    tags = fields.JSONField(null=True, description="标签列表")
    remark = fields.TextField(null=True, description="备注")

    class Meta:
        table = "trade_logs"
        indexes = [
            ("action_type",),
            ("stock_code",),
            ("strategy_key",),
            ("action_time",),
            ("result",),
            ("user_id",),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.stock_code or 'N/A'} - {self.result or 'pending'}"

    @property
    def action_type_display(self) -> str:
        """行为类型显示文本"""
        type_map = {
            "stock_pick": "选股执行",
            "stock_pick_result": "选股结果",
            "buy_request": "买入请求",
            "buy_audit": "买入审核",
            "buy_executed": "买入执行",
            "buy_success": "买入成功",
            "buy_failed": "买入失败",
            "sell_request": "卖出请求",
            "sell_executed": "卖出执行",
            "sell_success": "卖出成功",
            "sell_failed": "卖出失败",
            "audit_pass": "审核通过",
            "audit_reject": "审核拒绝",
            "audit_warning": "审核警告",
            "cancel_request": "撤单请求",
            "cancel_success": "撤单成功",
            "cancel_failed": "撤单失败",
            "warning_trigger": "预警触发",
            "warning_handle": "预警处理",
            "system_start": "系统启动",
            "system_stop": "系统停止",
            "config_change": "配置变更",
            "rule_change": "规则变更",
            "ai_chat": "AI对话",
            "manual_operation": "手动操作",
        }
        return type_map.get(self.action_type, self.action_type)

    @property
    def action_source_display(self) -> str:
        """行为来源显示文本"""
        source_map = {
            "system": "系统自动",
            "user": "用户操作",
            "ai": "AI决策",
            "strategy": "策略触发",
        }
        return source_map.get(self.action_source, self.action_source)

    @property
    def result_display(self) -> str:
        """结果显示文本"""
        result_map = {
            "success": "成功",
            "failed": "失败",
            "pending": "进行中",
            "rejected": "拒绝",
        }
        return result_map.get(self.result, self.result or "未知")


class TradeLogSummary(Model):
    """
    交易日志统计汇总表

    按日期汇总交易行为统计
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 统计日期
    summary_date = fields.DateField(description="统计日期")

    # 选股统计
    stock_pick_count = fields.IntField(default=0, description="选股执行次数")
    stock_pick_stocks_found = fields.IntField(default=0, description="选股发现股票数")

    # 买入统计
    buy_request_count = fields.IntField(default=0, description="买入请求次数")
    buy_success_count = fields.IntField(default=0, description="买入成功次数")
    buy_failed_count = fields.IntField(default=0, description="买入失败次数")
    buy_rejected_count = fields.IntField(default=0, description="买入拒绝次数")
    buy_total_amount = fields.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        description="买入总金额"
    )
    buy_total_quantity = fields.IntField(default=0, description="买入总数量")

    # 卖出统计
    sell_request_count = fields.IntField(default=0, description="卖出请求次数")
    sell_success_count = fields.IntField(default=0, description="卖出成功次数")
    sell_failed_count = fields.IntField(default=0, description="卖出失败次数")
    sell_total_amount = fields.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        description="卖出总金额"
    )
    sell_total_quantity = fields.IntField(default=0, description="卖出总数量")

    # 审核统计
    audit_pass_count = fields.IntField(default=0, description="审核通过次数")
    audit_reject_count = fields.IntField(default=0, description="审核拒绝次数")
    audit_warning_count = fields.IntField(default=0, description="审核警告次数")

    # 预警统计
    warning_trigger_count = fields.IntField(default=0, description="预警触发次数")
    warning_handle_count = fields.IntField(default=0, description="预警处理次数")

    # 其他统计
    cancel_count = fields.IntField(default=0, description="撤单次数")
    ai_chat_count = fields.IntField(default=0, description="AI对话次数")

    # 时间信息
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "trade_log_summary"
        indexes = [
            ("summary_date",),
        ]
        unique_together = ("summary_date",)

    def __str__(self):
        return f"日志汇总 - {self.summary_date}"