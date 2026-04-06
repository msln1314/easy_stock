"""
交易红线模型

用于定义交易安全审计规则，确保交易符合风控要求
"""
from tortoise import fields
from tortoise.models import Model
from datetime import datetime


class TradeRedLine(Model):
    """
    交易红线规则表

    定义交易安全审计规则，不符合规则的交易将被拒绝
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 规则基本信息
    rule_key = fields.CharField(max_length=50, unique=True, description="规则KEY")
    rule_name = fields.CharField(max_length=100, description="规则名称")
    rule_type = fields.CharField(
        max_length=30,
        description="规则类型: position_limit-仓位限制, stock_blacklist-股票黑名单, "
                    "amount_limit-金额限制, price_limit-价格限制, time_limit-时间限制, "
                    "frequency_limit-频率限制, risk_control-风控指标"
    )
    description = fields.TextField(null=True, description="规则描述")

    # 规则配置
    rule_config = fields.JSONField(description="规则配置JSON")
    # 配置示例:
    # position_limit: {"max_single_position_pct": 20, "max_total_position_pct": 80}
    # stock_blacklist: {"blacklist": ["ST*", "退市*", "新股*"], "reasons": {...}}
    # amount_limit: {"max_single_amount": 50000, "max_daily_amount": 200000}
    # price_limit: {"min_price": 2.0, "max_price": 500.0, "avoid_limit_up": true}
    # time_limit: {"allowed_sessions": ["morning", "afternoon"], "avoid_first_minutes": 5}
    # frequency_limit: {"max_trades_per_day": 10, "max_trades_per_hour": 3}
    # risk_control: {"require_profit_signal": true, "avoid_loss_stock": true}

    # 规则状态
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    severity = fields.CharField(
        max_length=20,
        default="critical",
        description="严重级别: critical-必须通过, warning-警告但允许, info-提示"
    )

    # 生效时间
    effective_from = fields.DateField(null=True, description="生效开始日期")
    effective_to = fields.DateField(null=True, description="生效结束日期")

    # 统计信息
    total_checked = fields.IntField(default=0, description="累计检查次数")
    total_rejected = fields.IntField(default=0, description="累计拒绝次数")

    created_by = fields.CharField(max_length=50, null=True, description="创建人")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "trade_red_lines"
        indexes = [
            ("rule_key",),
            ("is_enabled",),
            ("rule_type",),
        ]

    def __str__(self):
        return f"{self.rule_key} - {self.rule_name}"

    @property
    def severity_display(self) -> str:
        """严重级别显示文本"""
        severity_map = {
            "critical": "必须通过",
            "warning": "警告",
            "info": "提示"
        }
        return severity_map.get(self.severity, self.severity)

    @property
    def rule_type_display(self) -> str:
        """规则类型显示文本"""
        type_map = {
            "position_limit": "仓位限制",
            "stock_blacklist": "股票黑名单",
            "amount_limit": "金额限制",
            "price_limit": "价格限制",
            "time_limit": "时间限制",
            "frequency_limit": "频率限制",
            "risk_control": "风控指标"
        }
        return type_map.get(self.rule_type, self.rule_type)

    @property
    def is_effective(self) -> bool:
        """检查规则是否在生效期内"""
        if not self.is_enabled:
            return False
        today = datetime.now().date()
        if self.effective_from and today < self.effective_from:
            return False
        if self.effective_to and today > self.effective_to:
            return False
        return True


class TradeAuditLog(Model):
    """
    交易审计日志表

    记录每次交易的审核过程和结果
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 交易信息
    trade_type = fields.CharField(max_length=10, description="交易类型: buy-买入, sell-卖出")
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")
    price = fields.DecimalField(max_digits=10, decimal_places=3, description="委托价格")
    quantity = fields.IntField(description="委托数量")
    amount = fields.DecimalField(max_digits=12, decimal_places=2, description="委托金额")

    # 审核结果
    audit_result = fields.CharField(
        max_length=20,
        description="审核结果: passed-通过, rejected-拒绝, warning-警告通过"
    )
    failed_rules = fields.JSONField(null=True, description="未通过的规则列表")
    warning_rules = fields.JSONField(null=True, description="警告的规则列表")
    reject_reason = fields.TextField(null=True, description="拒绝原因")

    # 审核详情
    audit_details = fields.JSONField(null=True, description="审核详情JSON")
    # 包含每条规则的检查结果: {"rule_key": {"passed": true/false, "value": ..., "limit": ...}}

    # 用户信息
    user_id = fields.IntField(null=True, description="操作用户ID")
    user_name = fields.CharField(max_length=50, null=True, description="操作用户名")

    # 时间信息
    audit_time = fields.DatetimeField(auto_now_add=True, description="审核时间")

    # 后续处理
    is_executed = fields.BooleanField(default=False, description="是否已执行交易")
    order_id = fields.CharField(max_length=50, null=True, description="委托单号")
    execute_time = fields.DatetimeField(null=True, description="执行时间")

    class Meta:
        table = "trade_audit_logs"
        indexes = [
            ("stock_code",),
            ("audit_time",),
            ("audit_result",),
            ("user_id",),
        ]

    def __str__(self):
        return f"{self.trade_type} {self.stock_code} - {self.audit_result}"

    @property
    def audit_result_display(self) -> str:
        """审核结果显示文本"""
        result_map = {
            "passed": "通过",
            "rejected": "拒绝",
            "warning": "警告通过"
        }
        return result_map.get(self.audit_result, self.audit_result)


# 预置红线规则
PRESET_RED_LINES = [
    {
        "rule_key": "SINGLE_POSITION_LIMIT",
        "rule_name": "单只股票仓位限制",
        "rule_type": "position_limit",
        "description": "单只股票持仓不超过总资产的指定比例，防止过度集中",
        "rule_config": {
            "max_single_position_pct": 20,  # 单只股票最大仓位比例(%)
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "TOTAL_POSITION_LIMIT",
        "rule_name": "总仓位限制",
        "rule_type": "position_limit",
        "description": "总持仓不超过总资产的指定比例，保留现金应对风险",
        "rule_config": {
            "max_total_position_pct": 80,  # 总仓位最大比例(%)
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "STOCK_BLACKLIST",
        "rule_name": "股票黑名单",
        "rule_type": "stock_blacklist",
        "description": "禁止买入特定类型的股票（ST股、退市股、新股等）",
        "rule_config": {
            "blacklist_patterns": [
                {"pattern": "ST*", "reason": "ST股票风险高"},
                {"pattern": "*ST", "reason": "退市风险股票"},
                {"pattern": "退市*", "reason": "已退市股票"},
            ],
            "ipo_days": 30,  # 新股上市后30天内禁止买入
            "new_stock_reason": "新股波动大，需要观察期"
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "SINGLE_AMOUNT_LIMIT",
        "rule_name": "单笔金额限制",
        "rule_type": "amount_limit",
        "description": "单笔交易金额不超过指定限额，控制单次风险敞口",
        "rule_config": {
            "max_single_amount": 50000,  # 单笔最大金额(元)
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "DAILY_AMOUNT_LIMIT",
        "rule_name": "日累计金额限制",
        "rule_type": "amount_limit",
        "description": "每日累计买入金额不超过指定限额，控制日内风险",
        "rule_config": {
            "max_daily_buy_amount": 200000,  # 日最大买入金额(元)
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "PRICE_RANGE_LIMIT",
        "rule_name": "价格区间限制",
        "rule_type": "price_limit",
        "description": "限制买入股票的价格范围，避免买入高价股或低价股",
        "rule_config": {
            "min_price": 2.0,  # 最低价格(元)，低于此价格的股票不买
            "max_price": 500.0,  # 最高价格(元)
            "min_price_reason": "低价股风险高",
            "max_price_reason": "高价股波动大"
        },
        "severity": "warning",
        "is_enabled": True
    },
    {
        "rule_key": "AVOID_LIMIT_UP",
        "rule_name": "涨停板限制",
        "rule_type": "price_limit",
        "description": "禁止买入已经涨停的股票，防止追高被套",
        "rule_config": {
            "avoid_limit_up": True,
            "limit_up_threshold_pct": 9.5,  # 接近涨停的阈值(%)
        },
        "severity": "critical",
        "is_enabled": True
    },
    {
        "rule_key": "TRADE_TIME_LIMIT",
        "rule_name": "交易时段限制",
        "rule_type": "time_limit",
        "description": "限制交易时段，避免开盘前和收盘前的高波动时段",
        "rule_config": {
            "avoid_first_minutes": 5,  # 开盘前5分钟不交易
            "avoid_last_minutes": 5,  # 收盘前5分钟不交易
            "allowed_sessions": ["morning", "afternoon"]
        },
        "severity": "warning",
        "is_enabled": True
    },
    {
        "rule_key": "DAILY_TRADE_FREQUENCY",
        "rule_name": "日内交易频率限制",
        "rule_type": "frequency_limit",
        "description": "限制日内买入次数，避免过度交易",
        "rule_config": {
            "max_buy_per_day": 10,  # 每日最大买入次数
        },
        "severity": "warning",
        "is_enabled": True
    },
    {
        "rule_key": "LOSS_STOCK_BAN",
        "rule_name": "亏损股票限制",
        "rule_type": "risk_control",
        "description": "禁止加仓已经亏损超过阈值的股票，防止亏损扩大",
        "rule_config": {
            "max_loss_pct_before_add": -10,  # 持仓亏损超过此比例禁止加仓(%)
        },
        "severity": "critical",
        "is_enabled": True
    },
]