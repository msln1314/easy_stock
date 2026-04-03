"""
用户模型
"""
from tortoise import fields
from tortoise.models import Model


class User(Model):
    """用户表"""
    id = fields.IntField(pk=True, description="主键ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=255, description="密码(bcrypt加密)")
    email = fields.CharField(max_length=100, null=True, unique=True, description="邮箱")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    role = fields.CharField(max_length=20, default="user", description="角色: admin/user")
    status = fields.CharField(max_length=20, default="active", description="状态: active/disabled")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_user"
        table_description = "用户表"

    def __str__(self):
        return f"User({self.id}: {self.username})"

    @property
    def role_display(self) -> str:
        """角色显示文本"""
        role_map = {
            "admin": "管理员",
            "user": "普通用户"
        }
        return role_map.get(self.role, self.role)

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "active": "正常",
            "disabled": "禁用"
        }
        return status_map.get(self.status, self.status)