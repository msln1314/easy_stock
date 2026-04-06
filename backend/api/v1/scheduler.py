"""
计划任务管理API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
import json

from core.response import success_response, error_response
from models.scheduler import SchedulerTask, TaskLog
from core.ap_scheduler import SchedulerUtil

router = APIRouter(prefix="/api/scheduler", tags=["计划任务管理"])


# ==================== Schemas ====================

class TaskCreate(BaseModel):
    """创建计划任务"""
    task_key: str
    task_name: str
    task_type: str = "monitor"
    trigger_type: str = "cron"
    trigger_config: str
    job_path: str
    job_args: Optional[str] = None
    job_kwargs: Optional[str] = None
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """更新计划任务"""
    task_name: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[str] = None
    is_enabled: Optional[bool] = None
    description: Optional[str] = None


class CronPreview(BaseModel):
    """Cron表达式预览"""
    cron_expr: str


# ==================== 任务管理接口 ====================

@router.get("/tasks")
async def get_tasks(
    task_type: Optional[str] = Query(None, description="任务类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用")
):
    """获取计划任务列表"""
    query = SchedulerTask.all()

    if task_type:
        query = query.filter(task_type=task_type)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)

    tasks = await query.order_by("-created_at")

    return success_response([{
        "id": t.id,
        "task_key": t.task_key,
        "task_name": t.task_name,
        "task_type": t.task_type,
        "trigger_type": t.trigger_type,
        "trigger_config": t.trigger_config,
        "job_path": t.job_path,
        "is_enabled": t.is_enabled,
        "is_running": t.is_running,
        "description": t.description,
        "last_run_time": t.last_run_time.isoformat() if t.last_run_time else None,
        "next_run_time": t.next_run_time.isoformat() if t.next_run_time else None,
        "last_run_status": t.last_run_status,
        "run_count": t.run_count
    } for t in tasks])


@router.post("/tasks")
async def create_task(data: TaskCreate):
    """创建计划任务"""
    # 检查任务key是否已存在
    existing = await SchedulerTask.get_or_none(task_key=data.task_key)
    if existing:
        raise HTTPException(status_code=400, detail="任务KEY已存在")

    task = await SchedulerTask.create(
        task_key=data.task_key,
        task_name=data.task_name,
        task_type=data.task_type,
        trigger_type=data.trigger_type,
        trigger_config=data.trigger_config,
        job_path=data.job_path,
        job_args=data.job_args,
        job_kwargs=data.job_kwargs,
        description=data.description
    )

    # 如果启用，添加到调度器
    if task.is_enabled:
        try:
            SchedulerUtil.add_job_by_path(
                job_id=task.task_key,
                job_class=task.job_path,
                trigger=task.trigger_type,
                trigger_args=task.trigger_config,
                job_name=task.task_name,
                job_args=task.job_args,
                job_kwargs=task.job_kwargs,
            )
            # 更新下次执行时间
            job = SchedulerUtil.get_job(task.task_key)
            if job:
                task.next_run_time = job.next_run_time
                await task.save()
        except Exception as e:
            task.is_enabled = False
            task.last_run_status = "error"
            task.last_run_message = str(e)
            await task.save()

    return success_response({"id": task.id})


@router.put("/tasks/{task_id}")
async def update_task(task_id: int, data: TaskUpdate):
    """更新计划任务"""
    task = await SchedulerTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 更新字段
    if data.task_name:
        task.task_name = data.task_name
    if data.trigger_type:
        task.trigger_type = data.trigger_type
    if data.trigger_config:
        task.trigger_config = data.trigger_config
    if data.description:
        task.description = data.description
    if data.is_enabled is not None:
        task.is_enabled = data.is_enabled

    await task.save()

    # 更新调度器
    if task.is_enabled:
        # 先移除旧任务
        SchedulerUtil.remove_job(task.task_key)
        # 重新添加
        try:
            SchedulerUtil.add_job_by_path(
                job_id=task.task_key,
                job_class=task.job_path,
                trigger=task.trigger_type,
                trigger_args=task.trigger_config,
                job_name=task.task_name,
                job_args=task.job_args,
                job_kwargs=task.job_kwargs,
            )
            job = SchedulerUtil.get_job(task.task_key)
            if job:
                task.next_run_time = job.next_run_time
                await task.save()
        except Exception as e:
            task.last_run_status = "error"
            task.last_run_message = str(e)
            await task.save()
    else:
        # 禁用时移除任务
        SchedulerUtil.remove_job(task.task_key)
        task.next_run_time = None
        await task.save()

    return success_response(message="更新成功")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """删除计划任务"""
    task = await SchedulerTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 从调度器移除
    SchedulerUtil.remove_job(task.task_key)

    await task.delete()
    return success_response(message="删除成功")


# ==================== 任务控制接口 ====================

@router.post("/tasks/{task_id}/start")
async def start_task(task_id: int):
    """启动任务"""
    task = await SchedulerTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.is_enabled:
        return success_response(message="任务已处于启用状态")

    try:
        SchedulerUtil.add_job_by_path(
            job_id=task.task_key,
            job_class=task.job_path,
            trigger=task.trigger_type,
            trigger_args=task.trigger_config,
            job_name=task.task_name,
            job_args=task.job_args,
            job_kwargs=task.job_kwargs,
        )
        task.is_enabled = True
        job = SchedulerUtil.get_job(task.task_key)
        if job:
            task.next_run_time = job.next_run_time
        await task.save()
        return success_response(message="任务已启动")
    except Exception as e:
        task.last_run_status = "error"
        task.last_run_message = str(e)
        await task.save()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/stop")
async def stop_task(task_id: int):
    """停止任务"""
    task = await SchedulerTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    SchedulerUtil.remove_job(task.task_key)
    task.is_enabled = False
    task.is_running = False
    task.next_run_time = None
    await task.save()

    return success_response(message="任务已停止")


@router.post("/tasks/{task_id}/run")
async def run_task_now(task_id: int):
    """立即执行任务"""
    task = await SchedulerTask.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        # 导入任务函数
        module_path, func_name = task.job_path.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        job_func = getattr(module, func_name)

        SchedulerUtil.run_job_now(task.task_key, job_func)
        return success_response(message="任务已触发执行")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 任务日志接口 ====================

@router.get("/tasks/{task_id}/logs")
async def get_task_logs(
    task_id: int,
    limit: int = Query(50, description="返回数量")
):
    """获取任务执行日志"""
    logs = await TaskLog.filter(task_id=task_id).order_by("-created_at").limit(limit)

    return success_response([{
        "id": l.id,
        "task_key": l.task_key,
        "task_name": l.task_name,
        "status": l.status,
        "job_message": l.job_message,
        "exception_info": l.exception_info,
        "start_time": l.start_time.isoformat() if l.start_time else None,
        "end_time": l.end_time.isoformat() if l.end_time else None,
        "duration": l.duration,
        "created_at": l.created_at.isoformat() if l.created_at else None
    } for l in logs])


@router.get("/logs")
async def get_all_logs(
    task_key: Optional[str] = Query(None, description="任务KEY筛选"),
    status: Optional[bool] = Query(None, description="执行状态筛选"),
    limit: int = Query(100, description="返回数量")
):
    """获取所有任务日志"""
    query = TaskLog.all()

    if task_key:
        query = query.filter(task_key=task_key)
    if status is not None:
        query = query.filter(status=status)

    logs = await query.order_by("-created_at").limit(limit)

    return success_response([{
        "id": l.id,
        "task_key": l.task_key,
        "task_name": l.task_name,
        "status": l.status,
        "job_message": l.job_message,
        "exception_info": l.exception_info,
        "start_time": l.start_time.isoformat() if l.start_time else None,
        "end_time": l.end_time.isoformat() if l.end_time else None,
        "duration": l.duration
    } for l in logs])


# ==================== Cron表达式辅助接口 ====================

@router.post("/cron/preview")
async def preview_cron(data: CronPreview):
    """预览Cron表达式执行时间"""
    try:
        from apscheduler.triggers.cron import CronTrigger
        from datetime import timedelta

        fields = data.cron_expr.strip().split()
        if len(fields) not in (5, 6, 7):
            raise ValueError("无效的 Cron 表达式")

        parsed_fields = [None if field in ("*", "?") else field for field in fields]

        if len(fields) == 5:
            minute, hour, day, month, day_of_week = parsed_fields
            second, year = None, None
        elif len(fields) == 6:
            second, minute, hour, day, month, day_of_week = parsed_fields
            year = None
        else:
            second, minute, hour, day, month, day_of_week, year = parsed_fields

        trigger = CronTrigger(
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            year=year,
            timezone="Asia/Shanghai",
        )

        # 获取接下来5次执行时间
        now = datetime.now()
        next_runs = []
        for i in range(5):
            next_run = trigger.get_next_fire_time(trigger.get_next_fire_time(now, now + timedelta(days=365)), now)
            if next_run:
                next_runs.append(next_run.strftime("%Y-%m-%d %H:%M:%S"))

        return success_response({
            "cron_expr": data.cron_expr,
            "valid": True,
            "next_runs": next_runs[:5]
        })
    except Exception as e:
        return success_response({
            "cron_expr": data.cron_expr,
            "valid": False,
            "error": str(e)
        })


@router.get("/cron/examples")
async def get_cron_examples():
    """获取常用Cron表达式示例"""
    examples = [
        {"expr": "0 9 * * *", "desc": "每天早上9点执行"},
        {"expr": "0 9,15 * * *", "desc": "每天9点和15点执行"},
        {"expr": "0 9 * * 1-5", "desc": "周一到周五早上9点执行"},
        {"expr": "0 9 1 * *", "desc": "每月1号早上9点执行"},
        {"expr": "*/5 * * * *", "desc": "每5分钟执行一次"},
        {"expr": "0 */2 * * *", "desc": "每2小时执行一次"},
        {"expr": "0 9,12,15 * * *", "desc": "每天9点、12点、15点执行"},
        {"expr": "30 14 * * *", "desc": "每天下午2:30执行"},
        {"expr": "0 0 * * *", "desc": "每天凌晨0点执行"},
        {"expr": "0 0 * * 0", "desc": "每周日凌晨0点执行"},
    ]
    return success_response(examples)


# ==================== 调度器状态接口 ====================

@router.get("/status")
async def get_scheduler_status():
    """获取调度器状态"""
    status = SchedulerUtil.get_job_status()
    jobs_info = SchedulerUtil.get_jobs_info()

    return success_response({
        "status": status,
        "job_count": len(jobs_info),
        "jobs": jobs_info
    })


# ==================== 初始化预设任务 ====================

@router.post("/init")
async def init_default_tasks():
    """初始化预设任务"""
    default_tasks = [
        {
            "task_key": "detect_warning_signals",
            "task_name": "预警信号检测",
            "task_type": "monitor",
            "trigger_type": "cron",
            "trigger_config": "*/15 9-15 * * 1-5",  # 交易时间每15分钟
            "job_path": "jobs.warning_detector.detect_warnings",
            "description": "定期检查监控股票池，根据预警条件生成预警通知"
        },
        {
            "task_key": "monitor_sell_warning",
            "task_name": "监控卖出预警信息",
            "task_type": "monitor",
            "trigger_type": "cron",
            "trigger_config": "*/10 9-15 * * 1-5",  # 交易时间每10分钟
            "job_path": "jobs.monitor_tasks.check_sell_warnings",
            "description": "定时检查预警股票池，生成卖出信号"
        },
        {
            "task_key": "daily_report",
            "task_name": "每日策略报告",
            "task_type": "report",
            "trigger_type": "cron",
            "trigger_config": "0 16 * * 1-5",  # 每个交易日16点
            "job_path": "jobs.monitor_tasks.generate_daily_report",
            "description": "生成每日策略运行报告"
        },
    ]

    count = 0
    for task_data in default_tasks:
        existing = await SchedulerTask.get_or_none(task_key=task_data['task_key'])
        if not existing:
            await SchedulerTask.create(**task_data)
            count += 1

    return success_response(message=f"已初始化 {count} 个预设任务")