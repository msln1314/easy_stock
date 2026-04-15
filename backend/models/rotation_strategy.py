"""
轮动策略配置模型
"""
from tortoise import fields
from tortoise.models import Model


class RotationStrategy(Model):
    """轮动策略配置表"""
    id = fields.IntField(pk=True, description="主键ID")
    name = fields.CharField(max_length=100, description="策略名称")
    description = fields.CharField(max_length=500, null=True, description="策略描述")
    slope_period = fields.IntField(default=20, description="斜率计算周期")
    rsrs_period = fields.IntField(default=18, description="RSRS窗口周期")
    rsrs_z_window = fields.IntField(default=100, description="Z-score标准化窗口")
    rsrs_buy_threshold = fields.DecimalField(max_digits=10, decimal_places=4, default=0.7, description="RSRS买入阈值")
    rsrs_sell_threshold = fields.DecimalField(max_digits=10, decimal_places=4, default=-0.7, description="RSRS卖出阈值")
    ma_period = fields.IntField(default=20, description="MA过滤周期")
    hold_count = fields.IntField(default=2, description="持仓数量")
    rebalance_freq = fields.CharField(max_length=20, default="weekly", description="调仓频率: daily/weekly/monthly")
    execute_mode = fields.CharField(max_length=20, default="simulate", description="执行模式: simulate/alert")
    status = fields.CharField(max_length=20, default="paused", description="状态: running/paused/stopped")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "t_rotation_strategy"
        table_description = "轮动策略配置表"

    def __str__(self):
        return f"RotationStrategy({self.id}: {self.name})"

    @property
    def execute_mode_display(self) -> str:
        """执行模式显示文本"""
        mode_map = {
            "simulate": "模拟运行",
            "alert": "信号提醒",
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

    @property
    def rebalance_freq_display(self) -> str:
        """调仓频率显示文本"""
        freq_map = {
            "daily": "每日",
            "weekly": "每周",
            "monthly": "每月"
        }
        return freq_map.get(self.rebalance_freq, self.rebalance_freq)