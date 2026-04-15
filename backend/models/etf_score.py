"""
ETF评分记录模型
"""
from tortoise import fields
from tortoise.models import Model
from models.rotation_strategy import RotationStrategy


class EtfScore(Model):
    """ETF评分记录表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.RotationStrategy",
        on_delete=fields.CASCADE,
        related_name="scores",
        description="策略ID"
    )
    etf_code = fields.CharField(max_length=20, description="ETF代码")
    trade_date = fields.DateField(description="交易日期")
    slope_value = fields.DecimalField(max_digits=10, decimal_places=6, null=True, description="斜率值")
    r_squared = fields.DecimalField(max_digits=10, decimal_places=6, null=True, description="R²值")
    momentum_score = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="动量评分")
    rsrs_beta = fields.DecimalField(max_digits=10, decimal_places=6, null=True, description="RSRS斜率β")
    rsrs_z_score = fields.DecimalField(max_digits=10, decimal_places=6, null=True, description="RSRS Z-score")
    ma_value = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="MA值")
    close_price = fields.DecimalField(max_digits=10, decimal_places=4, null=True, description="收盘价")
    rank_position = fields.IntField(null=True, description="排名位置")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_etf_score"
        table_description = "ETF评分记录表"
        unique_together = ("strategy", "trade_date", "etf_code")

    def __str__(self):
        return f"EtfScore({self.etf_code}: {self.trade_date}, rank={self.rank_position})"