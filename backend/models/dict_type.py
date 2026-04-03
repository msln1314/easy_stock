"""
字典类型模型
"""
from tortoise import fields
from tortoise.models import Model


class DictType(Model):
    """字典类型表"""
    id = fields.IntField(pk=True, description="主键ID")
    code = fields.CharField(max_length=50, unique=True, description="类型编码")
    name = fields.CharField(max_length=100, description="类型名称")
    category = fields.CharField(max_length=20, default="system", description="类别: system/custom/config")
    access_type = fields.CharField(max_length=10, default="public", description="访问类型: public/private")
    description = fields.CharField(max_length=500, null=True, description="描述")
    sort = fields.IntField(default=0, description="排序")
    status = fields.CharField(max_length=10, default="active", description="状态: active/disabled")
    created_by = fields.IntField(null=True, description="创建用户ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_dict_type"
        table_description = "字典类型表"

    def __str__(self):
        return f"DictType({self.code}: {self.name})"

    @property
    def category_display(self) -> str:
        """类别显示文本"""
        category_map = {
            "system": "系统预置",
            "custom": "用户自定义",
            "config": "系统配置"
        }
        return category_map.get(self.category, self.category)

    @property
    def access_type_display(self) -> str:
        """访问类型显示文本"""
        access_map = {
            "public": "公开",
            "private": "私有"
        }
        return access_map.get(self.access_type, self.access_type)