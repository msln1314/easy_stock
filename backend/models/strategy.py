"""
策略主表模型
"""
from tortoise import fields
from tortoise.models import Model


class Strategy(Model):
    """策略主表"""
    id = fields.IntField(pk=True, description="主键ID")
    name = fields.CharField(max_length=100, description="策略名称")
    description = fields.CharField(max_length=500, null=True, description="策略描述")
    execute_mode = fields.CharField(
        max_length=20,
        default="simulate",
        description="执行模式: auto/alert/simulate"
    )
    status = fields.CharField(
        max_length=20,
        default="paused",
        description="状态: running/paused/stopped"
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_strategy"
        table_description = "策略主表"

    def __str__(self):
        return f"Strategy({self.id}: {self.name})"

    @property
    def execute_mode_display(self) -> str:
        """执行模式显示文本"""
        mode_map = {
            "auto": "自动交易",
            "alert": "信号提醒",
            "simulate": "模拟运行"
        }
        return mode_map.get(self.execute_mode, self.execute_mode)

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "running": "运行中",
            "paused": "已暂停",
            "stopped": "已停止"
        }
        return status_map.get(self.status, self.status)