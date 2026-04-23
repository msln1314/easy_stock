"""
用户模型
"""
from tortoise import fields
from tortoise.models import Model
import secrets
import hashlib


class User(Model):
    """用户表"""
    id = fields.IntField(pk=True, description="主键ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=255, description="密码(bcrypt加密)")
    email = fields.CharField(max_length=100, null=True, unique=True, description="邮箱")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    role = fields.CharField(max_length=20, default="user", description="角色: admin/user/trader")
    status = fields.CharField(max_length=20, default="active", description="状态: active/disabled")
    # API Key（用于调用系统API）
    api_key = fields.CharField(max_length=64, null=True, unique=True, description="API Key(用于接口认证)")
    # QMT账户绑定字段
    qmt_account_id = fields.CharField(max_length=50, null=True, description="QMT账户ID/账号")
    qmt_account_name = fields.CharField(max_length=100, null=True, description="QMT账户名称")
    qmt_client_path = fields.CharField(max_length=200, null=True, description="QMT客户端路径")
    qmt_session_id = fields.IntField(default=123456, description="QMT会话ID")
    qmt_api_key = fields.CharField(max_length=100, null=True, description="QMT API Key(加密存储)")
    qmt_enabled = fields.BooleanField(default=False, description="是否启用QMT交易")
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
            "user": "普通用户",
            "trader": "交易员"
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

    @staticmethod
    def generate_api_key() -> str:
        """生成 API Key (16位)"""
        return secrets.token_hex(8)  # 8字节 = 16字符