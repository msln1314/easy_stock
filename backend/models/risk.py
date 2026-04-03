"""
止盈止损配置模型
"""
from tortoise import fields
from tortoise.models import Model
from models.strategy import Strategy


class StrategyRisk(Model):
    """止盈止损配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.Strategy",
        on_delete=fields.CASCADE,
        related_name="risk",
        description="策略ID"
    )
    stop_profit_type = fields.CharField(
        max_length=20,
        null=True,
        description="止盈类型: fixed_percent/dynamic/trailing"
    )
    stop_profit_value = fields.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        description="止盈值"
    )
    stop_loss_type = fields.CharField(
        max_length=20,
        null=True,
        description="止损类型: fixed_percent/dynamic"
    )
    stop_loss_value = fields.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        description="止损值"
    )
    max_position = fields.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        description="最大仓位比例"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_strategy_risk"
        table_description = "止盈止损配置表"

    def __str__(self):
        return f"Risk(strategy_id={self.strategy_id})"

    @property
    def stop_profit_type_display(self) -> str:
        """止盈类型显示文本"""
        type_map = {
            "fixed_percent": "固定百分比",
            "dynamic": "动态止盈",
            "trailing": "移动止盈"
        }
        return type_map.get(self.stop_profit_type, self.stop_profit_type or "")

    @property
    def stop_loss_type_display(self) -> str:
        """止损类型显示文本"""
        type_map = {
            "fixed_percent": "固定百分比",
            "dynamic": "动态止损"
        }
        return type_map.get(self.stop_loss_type, self.stop_loss_type or "")