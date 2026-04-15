"""
轮动持仓记录模型
"""
from tortoise import fields
from tortoise.models import Model
from models.rotation_strategy import RotationStrategy


class RotationPosition(Model):
    """轮动持仓记录表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.RotationStrategy",
        on_delete=fields.CASCADE,
        related_name="positions",
        description="策略ID"
    )
    etf_code = fields.CharField(max_length=20, description="ETF代码")
    etf_name = fields.CharField(max_length=100, null=True, description="ETF名称")
    buy_date = fields.DateField(description="买入日期")
    buy_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="买入价格")
    buy_score = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="买入时评分")
    quantity = fields.IntField(null=True, description="持仓数量（股）")
    cost_amount = fields.DecimalField(max_digits=12, decimal_places=2, null=True, description="成本金额")
    current_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="当前价格")
    current_value = fields.DecimalField(max_digits=12, decimal_places=2, null=True, description="当前市值")
    profit_pct = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="盈亏百分比")
    hold_days = fields.IntField(null=True, description="持有天数")
    status = fields.CharField(max_length=20, default="holding", description="状态: holding/sold")
    sell_date = fields.DateField(null=True, description="卖出日期")
    sell_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="卖出价格")
    sell_reason = fields.CharField(max_length=200, null=True, description="卖出原因")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_rotation_position"
        table_description = "轮动持仓记录表"

    def __str__(self):
        return f"RotationPosition({self.etf_code}: {self.status})"

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "holding": "持有中",
            "sold": "已卖出"
        }
        return status_map.get(self.status, self.status)