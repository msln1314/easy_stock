"""
角色菜单关联模型
"""
from tortoise import fields
from tortoise.models import Model


class RoleMenu(Model):
    """角色菜单关联表"""
    id = fields.IntField(pk=True, description="主键ID")
    role_id = fields.IntField(description="角色ID")
    menu_id = fields.IntField(description="菜单ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_role_menu"
        table_description = "角色菜单关联表"
        unique_together = (("role_id", "menu_id"),)

    def __str__(self):
        return f"RoleMenu(role={self.role_id}, menu={self.menu_id})"