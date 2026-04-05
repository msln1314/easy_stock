"""
组合条件数据模型
"""
from tortoise import fields
from tortoise.models import Model


class WarningConditionGroup(Model):
    """组合条件组表"""
    id = fields.IntField(pk=True)
    group_key = fields.CharField(max_length=50, unique=True, description="组合唯一标识")
    group_name = fields.CharField(max_length=100, description="组合名称")
    logic_type = fields.CharField(max_length=10, default="AND", description="逻辑类型: AND/OR")
    parent_id = fields.IntField(null=True, description="父分组ID，支持嵌套")
    priority = fields.CharField(max_length=20, default="warning", description="优先级")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    description = fields.TextField(null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_condition_groups"
        indexes = [("parent_id",), ("group_key",)]

    def __str__(self):
        return f"{self.group_key} - {self.group_name}"


class GroupConditionItem(Model):
    """组合条件项表 - 关联具体预警条件到分组"""
    id = fields.IntField(pk=True)
    group_id = fields.IntField(description="所属分组ID")
    condition_id = fields.IntField(description="关联的预警条件ID")
    sort_order = fields.IntField(default=0, description="排序")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "group_condition_items"
        indexes = [("group_id",), ("condition_id",)]

    def __str__(self):
        return f"Group {self.group_id} - Condition {self.condition_id}"