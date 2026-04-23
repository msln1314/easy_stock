"""
菜单模型
"""
from tortoise import fields
from tortoise.models import Model


class Menu(Model):
    """菜单表"""
    id = fields.IntField(pk=True, description="主键ID")
    parent_id = fields.IntField(null=True, description="父菜单ID")
    name = fields.CharField(max_length=50, description="菜单名称")
    path = fields.CharField(max_length=100, description="路由路径")
    component = fields.CharField(max_length=100, null=True, description="组件路径")
    icon = fields.CharField(max_length=50, null=True, description="图标")
    sort = fields.IntField(default=0, description="排序")
    visible = fields.BooleanField(default=True, description="是否显示")
    status = fields.CharField(max_length=10, default="active", description="状态: active/disabled")
    menu_type = fields.CharField(max_length=10, description="类型: directory/menu/button/link")
    permission = fields.CharField(max_length=100, null=True, description="权限标识")
    is_external = fields.BooleanField(default=False, description="是否外部链接")
    external_url = fields.CharField(max_length=500, null=True, description="外部链接URL")
    link_target = fields.CharField(max_length=20, default="_blank", description="打开方式: _blank/_self/_iframe")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_menu"
        table_description = "菜单表"

    def __str__(self):
        return f"Menu({self.id}: {self.name})"

    @property
    def menu_type_display(self) -> str:
        """菜单类型显示文本"""
        type_map = {
            "directory": "目录",
            "menu": "菜单",
            "button": "按钮"
        }
        return type_map.get(self.menu_type, self.menu_type)

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "active": "正常",
            "disabled": "禁用"
        }
        return status_map.get(self.status, self.status)