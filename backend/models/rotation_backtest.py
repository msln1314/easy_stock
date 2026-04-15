"""
回测记录模型
"""
from tortoise import fields
from tortoise.models import Model
from models.rotation_strategy import RotationStrategy


class RotationBacktest(Model):
    """回测记录表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.RotationStrategy",
        on_delete=fields.CASCADE,
        related_name="backtests",
        description="策略ID"
    )
    start_date = fields.DateField(description="回测开始日期")
    end_date = fields.DateField(description="回测结束日期")
    initial_capital = fields.DecimalField(max_digits=12, decimal_places=2, null=True, description="初始资金")
    final_capital = fields.DecimalField(max_digits=12, decimal_places=2, null=True, description="最终资金")
    total_return = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="总收益率")
    annual_return = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="年化收益率")
    max_drawdown = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="最大回撤")
    win_rate = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="胜率")
    trade_count = fields.IntField(null=True, description="交易次数")
    sharpe_ratio = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="夏普比率")
    calmar_ratio = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="卡尔马比率")
    benchmark_return = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="基准收益率")
    excess_return = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="超额收益")
    backtest_details = fields.JSONField(null=True, description="回测详细数据")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_rotation_backtest"
        table_description = "回测记录表"

    def __str__(self):
        return f"RotationBacktest({self.start_date} - {self.end_date})"