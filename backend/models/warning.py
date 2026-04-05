"""
预警相关数据模型
"""
from tortoise import fields
from tortoise.models import Model


class IndicatorLibrary(Model):
    """指标库表"""
    id = fields.IntField(pk=True)
    indicator_key = fields.CharField(max_length=50, unique=True, description="指标KEY")
    indicator_name = fields.CharField(max_length=100, description="指标名称")
    category = fields.CharField(max_length=50, null=True, description="分类")
    description = fields.TextField(null=True, description="指标说明")
    parameters = fields.JSONField(null=True, description="参数定义")
    output_fields = fields.JSONField(null=True, description="输出字段")
    is_builtin = fields.BooleanField(default=True, description="是否内置指标")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "indicator_library"

    def __str__(self):
        return f"{self.indicator_key} - {self.indicator_name}"


class WarningCondition(Model):
    """预警条件表"""
    id = fields.IntField(pk=True)
    condition_key = fields.CharField(max_length=50, unique=True, description="条件KEY")
    condition_name = fields.CharField(max_length=100, description="条件名称")
    indicator_key = fields.CharField(max_length=50, description="主指标KEY")
    indicator_key2 = fields.CharField(max_length=50, null=True, description="副指标KEY")
    period = fields.CharField(max_length=20, description="周期")
    condition_rule = fields.TextField(description="条件规则JSON")
    priority = fields.CharField(max_length=20, default="warning", description="优先级")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    description = fields.TextField(null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_conditions"

    def __str__(self):
        return f"{self.condition_key} - {self.condition_name}"


class WarningStockPool(Model):
    """预警股票池表"""
    id = fields.IntField(pk=True)
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")
    price = fields.DecimalField(max_digits=10, decimal_places=3, null=True, description="当前价格")
    change_percent = fields.DecimalField(max_digits=6, decimal_places=4, null=True, description="涨跌幅")
    condition_key = fields.CharField(max_length=50, description="预警条件KEY")
    condition_name = fields.CharField(max_length=100, description="预警条件名称")
    warning_level = fields.CharField(max_length=20, description="预警级别")
    trigger_time = fields.DatetimeField(description="触发时间")
    trigger_value = fields.JSONField(null=True, description="触发时的指标值")
    is_handled = fields.BooleanField(default=False, description="是否已处理")
    handle_action = fields.CharField(max_length=50, null=True, description="处理动作")
    handled_at = fields.DatetimeField(null=True, description="处理时间")
    # 组合条件相关字段
    group_key = fields.CharField(max_length=50, null=True, description="触发组合KEY")
    is_group = fields.BooleanField(default=False, description="是否组合预警")
    triggered_conditions = fields.JSONField(null=True, description="满足的条件列表")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "warning_stock_pool"
        indexes = [
            ("stock_code",),
            ("condition_key",),
            ("trigger_time",),
            ("is_handled",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.condition_name}"