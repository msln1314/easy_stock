"""
计划任务相关数据模型
"""
from tortoise import fields
from tortoise.models import Model


class SchedulerTask(Model):
    """计划任务表"""
    id = fields.IntField(pk=True)
    task_key = fields.CharField(max_length=50, unique=True, description="任务KEY")
    task_name = fields.CharField(max_length=100, description="任务名称")
    task_type = fields.CharField(max_length=50, default="monitor", description="任务类型")
    trigger_type = fields.CharField(max_length=20, default="cron", description="触发器类型: cron/interval/date")
    trigger_config = fields.CharField(max_length=200, description="触发器配置(cron表达式等)")
    job_path = fields.CharField(max_length=200, description="任务执行路径(模块.函数)")
    job_args = fields.TextField(null=True, description="任务参数JSON")
    job_kwargs = fields.TextField(null=True, description="任务关键字参数JSON")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    is_running = fields.BooleanField(default=False, description="是否正在运行")
    description = fields.TextField(null=True, description="任务描述")
    last_run_time = fields.DatetimeField(null=True, description="上次执行时间")
    next_run_time = fields.DatetimeField(null=True, description="下次执行时间")
    last_run_status = fields.CharField(max_length=20, null=True, description="上次执行状态")
    last_run_message = fields.TextField(null=True, description="上次执行消息")
    run_count = fields.IntField(default=0, description="执行次数")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "scheduler_tasks"
        indexes = [
            ("task_key",),
            ("is_enabled",),
            ("task_type",),
        ]

    def __str__(self):
        return f"{self.task_key} - {self.task_name}"


class TaskLog(Model):
    """任务执行日志表"""
    id = fields.IntField(pk=True)
    task_id = fields.IntField(description="任务ID")
    task_key = fields.CharField(max_length=50, description="任务KEY")
    task_name = fields.CharField(max_length=100, description="任务名称")
    job_group = fields.CharField(max_length=50, null=True, description="任务组")
    job_executor = fields.CharField(max_length=50, null=True, description="执行器")
    invoke_target = fields.CharField(max_length=200, description="执行目标")
    job_args = fields.TextField(null=True, description="位置参数")
    job_kwargs = fields.TextField(null=True, description="关键字参数")
    job_trigger = fields.CharField(max_length=100, null=True, description="触发器")
    job_message = fields.TextField(null=True, description="执行消息")
    status = fields.BooleanField(description="执行状态")
    exception_info = fields.TextField(null=True, description="异常信息")
    start_time = fields.DatetimeField(description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")
    duration = fields.IntField(null=True, description="执行耗时(毫秒)")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "task_logs"
        indexes = [
            ("task_id",),
            ("task_key",),
            ("status",),
            ("created_at",),
        ]

    def __str__(self):
        return f"{self.task_key} - {self.status}"