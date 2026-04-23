"""
仪表盘布局模型

存储用户的仪表盘布局配置
"""
from tortoise import fields
from tortoise.models import Model


class DashboardLayout(Model):
    """
    仪表盘布局表

    存储用户的自定义仪表盘布局配置
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 布局基本信息
    name = fields.CharField(max_length=50, description="布局名称")
    user_id = fields.IntField(description="用户ID")

    # 布局数据 (vue-grid-layout格式)
    # 示例: [{"i": "market-overview", "x": 0, "y": 0, "w": 12, "h": 2}, ...]
    layout_json = fields.JSONField(description="布局数据JSON")

    # 是否为默认布局
    is_default = fields.BooleanField(default=False, description="是否为默认布局")

    # 时间信息
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "dashboard_layouts"
        indexes = [
            ("user_id",),
            ("is_default",),
        ]
        unique_together = ("user_id", "name")

    def __str__(self):
        return f"布局[{self.name}] - 用户{self.user_id}"