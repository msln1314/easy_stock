"""
字典项模型
"""
from tortoise import fields
from tortoise.models import Model


class DictItem(Model):
    """字典项表"""
    id = fields.IntField(pk=True, description="主键ID")
    type_id = fields.IntField(description="字典类型ID")
    code = fields.CharField(max_length=50, description="项编码")
    name = fields.CharField(max_length=100, description="项名称")
    value = fields.TextField(null=True, description="项值")
    data_type = fields.CharField(max_length=10, default="plain", description="数据类型: plain/encrypted")
    access_type = fields.CharField(max_length=10, default="public", description="访问类型: public/private")
    parent_id = fields.IntField(null=True, description="父级ID(支持树形)")
    sort = fields.IntField(default=0, description="排序")
    status = fields.CharField(max_length=10, default="active", description="状态: active/disabled")
    remark = fields.CharField(max_length=500, null=True, description="备注")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_dict_item"
        table_description = "字典项表"
        # 联合唯一约束：同一类型下编码唯一
        unique_together = (("type_id", "code"),)

    def __str__(self):
        return f"DictItem({self.type_id}:{self.code}: {self.name})"

    @property
    def data_type_display(self) -> str:
        """数据类型显示文本"""
        data_type_map = {
            "plain": "明文",
            "encrypted": "加密"
        }
        return data_type_map.get(self.data_type, self.data_type)

    @property
    def access_type_display(self) -> str:
        """访问类型显示文本"""
        access_map = {
            "public": "公开",
            "private": "私有"
        }
        return access_map.get(self.access_type, self.access_type)