"""
角色模型
"""
from tortoise import fields
from tortoise.models import Model


class Role(Model):
    """角色表"""
    id = fields.IntField(pk=True, description="主键ID")
    name = fields.CharField(max_length=50, unique=True, description="角色名称")
    code = fields.CharField(max_length=50, unique=True, description="角色编码")
    description = fields.CharField(max_length=200, null=True, description="描述")
    status = fields.CharField(max_length=10, default="active", description="状态: active/disabled")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_role"
        table_description = "角色表"

    def __str__(self):
        return f"Role({self.code}: {self.name})"

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "active": "正常",
            "disabled": "禁用"
        }
        return status_map.get(self.status, self.status)