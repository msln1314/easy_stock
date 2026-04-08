"""
通知渠道配置模型

支持多种通知渠道：邮件、钉钉、Telegram、企业微信等
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class NotificationChannelType(str, Enum):
    """通知渠道类型"""
    EMAIL = "email"           # 邮件
    DINGTALK = "dingtalk"     # 钉钉机器人
    TELEGRAM = "telegram"     # Telegram
    WECHAT_WORK = "wechat_work"  # 企业微信
    WEBHOOK = "webhook"       # 自定义Webhook
    SMS = "sms"               # 短信（预留）


class NotificationChannel(Model):
    """通知渠道配置表"""
    id = fields.IntField(pk=True)
    channel_type = fields.CharEnumField(NotificationChannelType, description="渠道类型")
    channel_name = fields.CharField(max_length=50, description="渠道名称")
    is_enabled = fields.BooleanField(default=True, description="是否启用")

    # 渠道配置（JSON格式，不同渠道有不同的配置字段）
    # email: {"smtp_server", "smtp_port", "username", "password", "from_addr", "to_list"}
    # dingtalk: {"webhook_url", "secret"}
    # telegram: {"bot_token", "chat_id"}
    # wechat_work: {"webhook_url"}
    # webhook: {"url", "method", "headers"}
    config = fields.JSONField(description="渠道配置")

    # 关联的预警级别（哪些级别的预警发送到此渠道）
    # ["critical", "warning", "info"]
    warning_levels = fields.JSONField(default=["critical", "warning"], description="预警级别过滤")

    # 关联的监控类型（哪些类型的监控发送到此渠道）
    # ["hold", "watch"]
    monitor_types = fields.JSONField(default=["hold"], description="监控类型过滤")

    # 发送频率限制
    rate_limit_minutes = fields.IntField(default=5, description="发送频率限制(分钟)")

    # 最后发送时间（用于频率限制）
    last_sent_at = fields.DatetimeField(null=True, description="最后发送时间")

    remark = fields.CharField(max_length=200, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_channels"
        indexes = [
            ("channel_type",),
            ("is_enabled",),
        ]

    def __str__(self):
        return f"{self.channel_name} ({self.channel_type})"


class NotificationTemplate(Model):
    """通知消息模板表"""
    id = fields.IntField(pk=True)
    template_key = fields.CharField(max_length=50, unique=True, description="模板标识")
    template_name = fields.CharField(max_length=100, description="模板名称")
    template_type = fields.CharField(max_length=20, default="warning", description="模板类型: warning/trade/system")

    # 标题模板，支持变量: {stock_code}, {stock_name}, {warning_level}, {condition_name}
    title_template = fields.CharField(max_length=200, description="标题模板")

    # 内容模板，支持变量: {stock_code}, {stock_name}, {warning_level}, {condition_name},
    # {price}, {change_percent}, {trigger_time}, {trigger_value}
    content_template = fields.TextField(description="内容模板")

    # 关联的预警级别（空表示全部）
    warning_levels = fields.JSONField(null=True, description="适用预警级别")

    is_enabled = fields.BooleanField(default=True, description="是否启用")
    is_default = fields.BooleanField(default=False, description="是否默认模板")

    remark = fields.CharField(max_length=200, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_templates"
        indexes = [
            ("template_key",),
            ("template_type",),
            ("is_enabled",),
        ]

    def __str__(self):
        return f"{self.template_name} ({self.template_key})"


class NotificationRecipient(Model):
    """通知对象表（收件人）"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, description="姓名")

    # 各种联系方式
    email = fields.CharField(max_length=100, null=True, description="邮箱")
    phone = fields.CharField(max_length=20, null=True, description="手机号")
    wechat = fields.CharField(max_length=50, null=True, description="微信号")
    dingtalk = fields.CharField(max_length=50, null=True, description="钉钉账号")
    telegram_chat_id = fields.CharField(max_length=50, null=True, description="Telegram Chat ID")

    # 额外配置（如钉钉手机号等）
    extra_config = fields.JSONField(null=True, description="额外配置")

    is_enabled = fields.BooleanField(default=True, description="是否启用")
    remark = fields.CharField(max_length=200, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_recipients"
        indexes = [
            ("is_enabled",),
        ]

    def __str__(self):
        contacts = []
        if self.email:
            contacts.append(f"邮箱:{self.email}")
        if self.phone:
            contacts.append(f"手机:{self.phone}")
        if self.wechat:
            contacts.append(f"微信:{self.wechat}")
        return f"{self.name} ({', '.join(contacts) if contacts else '无联系方式'})"


class NotificationRecipientGroup(Model):
    """通知对象组表（按渠道类型分组，关联发送渠道）"""
    id = fields.IntField(pk=True)
    group_name = fields.CharField(max_length=50, description="组名称")
    group_code = fields.CharField(max_length=30, unique=True, description="组编码")

    # 关联的发送渠道（必须有对应的渠道才能发送）
    channel_id = fields.IntField(null=True, description="关联通知渠道ID")

    # 该渠道类型的联系方式列表
    # email类型: ["user1@example.com", "user2@example.com"]
    # dingtalk类型: ["手机号1", "手机号2"]（群通知时webhook已在channel配置）
    # telegram类型: ["chat_id1", "chat_id2"]
    contact_list = fields.JSONField(default=list, description="联系方式列表")

    # 关联的通知对象ID（可选，从通知对象中提取对应联系方式）
    recipient_ids = fields.JSONField(default=list, description="关联通知对象ID")

    # 默认模板
    default_template_id = fields.IntField(null=True, description="默认模板ID")

    is_enabled = fields.BooleanField(default=True, description="是否启用")
    remark = fields.CharField(max_length=200, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_recipient_groups"
        indexes = [
            ("group_code",),
            ("channel_id",),
            ("is_enabled",),
        ]

    def __str__(self):
        return f"{self.group_name}"


class NotificationLog(Model):
    """通知发送记录表"""
    id = fields.IntField(pk=True)

    # 关联的预警记录
    warning_id = fields.IntField(null=True, description="关联预警ID")
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")

    # 通知内容
    title = fields.CharField(max_length=100, description="通知标题")
    content = fields.TextField(description="通知内容")
    warning_level = fields.CharField(max_length=20, description="预警级别")
    condition_name = fields.CharField(max_length=100, null=True, description="预警条件名称")

    # 发送渠道
    channel_id = fields.IntField(description="渠道ID")
    channel_type = fields.CharField(max_length=20, description="渠道类型")
    channel_name = fields.CharField(max_length=50, description="渠道名称")

    # 发送状态
    status = fields.CharField(max_length=20, default="pending", description="状态: pending/sent/failed")
    error_message = fields.TextField(null=True, description="错误信息")

    # 发送时间
    sent_at = fields.DatetimeField(null=True, description="发送时间")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notification_logs"
        indexes = [
            ("stock_code",),
            ("warning_level",),
            ("channel_id",),
            ("status",),
            ("created_at",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.title}"