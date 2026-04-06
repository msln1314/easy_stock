"""
用户角色关联模型
"""
from tortoise import fields
from tortoise.models import Model


class UserRole(Model):
    """用户角色关联表"""
    id = fields.IntField(pk=True, description="主键ID")
    user_id = fields.IntField(description="用户ID")
    role_id = fields.IntField(description="角色ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "t_user_role"
        table_description = "用户角色关联表"
        unique_together = (("user_id", "role_id"),)

    def __str__(self):
        return f"UserRole(user={self.user_id}, role={self.role_id})"