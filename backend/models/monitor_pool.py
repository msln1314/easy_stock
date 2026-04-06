"""
监控股票池模型

用于存储需要监控预警的股票列表
"""
from tortoise import fields
from tortoise.models import Model


class MonitorStock(Model):
    """监控股票池表"""
    id = fields.IntField(pk=True)
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")
    monitor_type = fields.CharField(max_length=20, default="hold", description="监控类型: hold-持仓监控, watch-关注监控")
    conditions = fields.JSONField(null=True, description="关联的预警条件KEY列表")
    is_active = fields.BooleanField(default=True, description="是否启用监控")
    entry_price = fields.DecimalField(max_digits=10, decimal_places=3, null=True, description="加入时价格")
    last_check_time = fields.DatetimeField(null=True, description="上次检查时间")
    last_price = fields.DecimalField(max_digits=10, decimal_places=3, null=True, description="最新价格")
    change_percent = fields.DecimalField(max_digits=6, decimal_places=4, null=True, description="最新涨跌幅")
    remark = fields.CharField(max_length=200, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "monitor_stocks"
        indexes = [
            ("stock_code",),
            ("is_active",),
            ("monitor_type",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.stock_name}"

    @property
    def condition_list(self) -> list:
        """获取条件列表"""
        return self.conditions or []