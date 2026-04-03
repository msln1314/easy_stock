"""
买卖信号规则模型
"""
from tortoise import fields
from tortoise.models import Model
from models.strategy import Strategy


class StrategySignal(Model):
    """买卖信号规则表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.Strategy",
        on_delete=fields.CASCADE,
        related_name="signals",
        description="策略ID"
    )
    signal_type = fields.CharField(
        max_length=20,
        description="信号类型: buy/sell"
    )
    condition_type = fields.CharField(
        max_length=50,
        description="条件类型: indicator_cross/threshold/custom"
    )
    condition_config = fields.JSONField(description="条件配置JSON")
    priority = fields.IntField(default=0, description="优先级")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_strategy_signal"
        table_description = "买卖信号规则表"

    def __str__(self):
        return f"Signal({self.signal_type}: {self.condition_type})"

    @property
    def signal_type_display(self) -> str:
        """信号类型显示文本"""
        type_map = {
            "buy": "买入",
            "sell": "卖出"
        }
        return type_map.get(self.signal_type, self.signal_type)

    @property
    def condition_type_display(self) -> str:
        """条件类型显示文本"""
        type_map = {
            "indicator_cross": "指标交叉",
            "threshold": "阈值触发",
            "custom": "自定义"
        }
        return type_map.get(self.condition_type, self.condition_type)