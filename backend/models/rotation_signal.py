"""
轮动信号记录模型
"""
from tortoise import fields
from tortoise.models import Model
from models.rotation_strategy import RotationStrategy


class RotationSignal(Model):
    """轮动信号记录表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.RotationStrategy",
        on_delete=fields.CASCADE,
        related_name="signals",
        description="策略ID"
    )
    signal_date = fields.DateField(description="信号日期")
    signal_type = fields.CharField(max_length=20, description="信号类型: buy/sell/rebalance")
    etf_code = fields.CharField(max_length=20, description="ETF代码")
    etf_name = fields.CharField(max_length=100, null=True, description="ETF名称")
    action = fields.CharField(max_length=20, description="操作动作: buy/sell/hold")
    score = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="动量评分")
    rsrs_z = fields.DecimalField(max_digits=10, decimal_places=6, null=True, description="RSRS Z-score")
    price = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="参考价格")
    reason = fields.CharField(max_length=500, null=True, description="信号原因")
    is_executed = fields.BooleanField(default=False, description="是否已执行")
    executed_at = fields.DatetimeField(null=True, description="执行时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_rotation_signal"
        table_description = "轮动信号记录表"

    def __str__(self):
        return f"RotationSignal({self.signal_date}: {self.action} {self.etf_code})"

    @property
    def signal_type_display(self) -> str:
        """信号类型显示文本"""
        type_map = {
            "buy": "买入",
            "sell": "卖出",
            "rebalance": "调仓"
        }
        return type_map.get(self.signal_type, self.signal_type)

    @property
    def action_display(self) -> str:
        """操作动作显示文本"""
        action_map = {
            "buy": "买入",
            "sell": "卖出",
            "hold": "持有"
        }
        return action_map.get(self.action, self.action)