"""
系统配置模型
"""
from tortoise import fields
from tortoise.models import Model


class SysConfig(Model):
    """系统配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    key = fields.CharField(max_length=100, unique=True, description="配置键")
    value = fields.TextField(description="配置值")
    category = fields.CharField(max_length=20, default="basic", description="类别: basic/security/notification")
    data_type = fields.CharField(max_length=10, default="plain", description="数据类型: plain/encrypted")
    access_type = fields.CharField(max_length=10, default="public", description="访问类型: public/private")
    description = fields.CharField(max_length=500, null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_sys_config"
        table_description = "系统配置表"

    def __str__(self):
        return f"SysConfig({self.key}: {self.value})"

    @property
    def category_display(self) -> str:
        """类别显示文本"""
        category_map = {
            "basic": "基础配置",
            "security": "安全认证",
            "notification": "通知渠道"
        }
        return category_map.get(self.category, self.category)

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