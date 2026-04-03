"""
技术指标配置模型
"""
from tortoise import fields
from tortoise.models import Model
from models.strategy import Strategy


class StrategyIndicator(Model):
    """技术指标配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    strategy = fields.ForeignKeyField(
        "models.Strategy",
        on_delete=fields.CASCADE,
        related_name="indicators",
        description="策略ID"
    )
    indicator_type = fields.CharField(
        max_length=50,
        description="指标类型: MA/MACD/RSI/KDJ/BOLL等"
    )
    parameters = fields.JSONField(description="指标参数JSON")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_strategy_indicator"
        table_description = "技术指标配置表"

    def __str__(self):
        return f"Indicator({self.indicator_type})"

    @property
    def indicator_type_display(self) -> str:
        """指标类型显示文本"""
        type_map = {
            "MA": "均线",
            "MACD": "MACD指标",
            "RSI": "相对强弱指数",
            "KDJ": "KDJ指标",
            "BOLL": "布林带"
        }
        return type_map.get(self.indicator_type, self.indicator_type)