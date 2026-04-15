"""
ETF池配置模型
"""
from tortoise import fields
from tortoise.models import Model


class EtfPool(Model):
    """ETF池配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    name = fields.CharField(max_length=100, description="ETF名称")
    code = fields.CharField(max_length=20, description="ETF代码")
    sector = fields.CharField(max_length=50, description="所属行业板块")
    is_active = fields.BooleanField(default=True, description="是否启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_etf_pool"
        table_description = "ETF池配置表"

    def __str__(self):
        return f"EtfPool({self.code}: {self.name})"

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        return "启用" if self.is_active else "禁用"