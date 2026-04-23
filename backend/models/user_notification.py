"""
用户通知模型

用于记录用户的通知信息，支持多种类型：系统、交易、市场、策略
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class UserNotificationType(str, Enum):
    """用户通知类型"""
    SYSTEM = "system"       # 系统通知
    TRADE = "trade"         # 交易通知
    MARKET = "market"       # 市场通知
    STRATEGY = "strategy"   # 策略通知


class UserNotification(Model):
    """用户通知表"""
    id = fields.IntField(pk=True)
    user_id = fields.IntField(description="用户ID")

    # 通知类型
    type = fields.CharEnumField(UserNotificationType, description="通知类型")

    # 通知内容
    title = fields.CharField(max_length=100, description="通知标题")
    content = fields.TextField(description="通知内容")

    # 关联数据（可选）
    related_id = fields.IntField(null=True, description="关联数据ID（如交易ID、策略ID等）")
    related_type = fields.CharField(max_length=30, null=True, description="关联数据类型")

    # 已读状态
    is_read = fields.BooleanField(default=False, description="是否已读")
    read_at = fields.DatetimeField(null=True, description="阅读时间")

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user_notifications"
        indexes = [
            ("user_id",),
            ("type",),
            ("is_read",),
            ("created_at",),
        ]

    def __str__(self):
        return f"{self.type}: {self.title}"