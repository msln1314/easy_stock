"""
MCP服务配置模型
"""
from tortoise import fields
from tortoise.models import Model


class McpConfig(Model):
    """MCP服务配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    service_name = fields.CharField(max_length=50, unique=True, description="服务名称")
    service_url = fields.CharField(max_length=200, description="服务地址")
    api_key = fields.CharField(max_length=100, null=True, description="API Key(加密存储)")
    enabled = fields.BooleanField(default=True, description="是否启用")
    description = fields.CharField(max_length=500, null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_mcp_config"
        table_description = "MCP服务配置表"

    def __str__(self):
        return f"McpConfig({self.service_name}: {self.service_url})"