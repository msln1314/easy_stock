# -*- coding: utf-8 -*-
"""
APScheduler 调度器工具类 - 适配 Tortoise ORM

提供定时任务的统一管理功能，包括：
- 任务的添加、删除、暂停、恢复
- 任务执行日志记录
- 任务状态监控
"""

import json
import importlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Union, List, Any, Optional

from apscheduler.job import Job
from apscheduler.events import JobExecutionEvent, EVENT_ALL, JobEvent
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from tortoise import Tortoise

from app.settings.config import settings

logger = logging.getLogger(__name__)


def get_db_url() -> str:
    """获取数据库连接URL"""
    db_config = settings.TORTOISE_ORM["connections"]["default"]["credentials"]
    return f"mysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"


# 配置任务存储
job_stores = {
    "default": MemoryJobStore(),
}

# 配置执行器
executors = {"default": AsyncIOExecutor(), "processpool": ProcessPoolExecutor(max_workers=1)}

# 配置默认参数
job_defaults = {
    "coalesce": False,
    "max_instances": 1,
}

# 配置调度器
scheduler = AsyncIOScheduler()
scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone="Asia/Shanghai")


class SchedulerUtil:
    """
    定时任务相关方法
    """

    @classmethod
    def scheduler_event_listener(cls, event: JobEvent | JobExecutionEvent) -> None:
        """
        监听任务执行事件。

        参数:
        - event (JobEvent | JobExecutionEvent): 任务事件对象。

        返回:
        - None
        """
        event_type = event.__class__.__name__
        status = True
        exception_info = ""

        if isinstance(event, JobExecutionEvent) and event.exception:
            exception_info = str(event.exception)
            status = False

        if hasattr(event, "job_id"):
            job_id = event.job_id
            query_job = cls.get_job(job_id=job_id)
            if query_job:
                query_job_info = query_job.__getstate__()
                job_name = query_job_info.get("name")
                job_group = query_job._jobstore_alias
                job_executor = query_job_info.get("executor")
                invoke_target = query_job_info.get("func")
                job_args = ",".join(map(str, query_job_info.get("args", [])))
                job_kwargs = json.dumps(query_job_info.get("kwargs"))
                job_trigger = str(query_job_info.get("trigger"))

                job_message = (
                    f"事件类型: {event_type}, 任务ID: {job_id}, 任务名称: {job_name}, "
                    f"状态: {status}, 任务组: {job_group}, 错误详情: {exception_info}, "
                    f"执行于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                logger.info(job_message)

                # 异步保存日志
                asyncio.create_task(
                    cls._save_job_log(
                        job_id=job_id,
                        job_name=job_name,
                        job_group=job_group,
                        job_executor=job_executor,
                        invoke_target=invoke_target,
                        job_args=job_args,
                        job_kwargs=job_kwargs,
                        job_trigger=job_trigger,
                        job_message=job_message,
                        status=status,
                        exception_info=exception_info,
                    )
                )

    @classmethod
    async def _save_job_log(
        cls,
        job_id: str,
        job_name: str,
        job_group: str,
        job_executor: str,
        invoke_target: str,
        job_args: str,
        job_kwargs: str,
        job_trigger: str,
        job_message: str,
        status: bool,
        exception_info: str,
    ) -> None:
        """
        异步保存任务日志

        参数:
        - 各任务日志字段

        返回:
        - None
        """
        try:
            # 使用 Tortoise ORM 保存日志
            # 如果有 TaskLog 模型，可以使用它保存日志
            # 这里暂时只记录到日志文件
            log_data = {
                "job_id": job_id,
                "job_name": job_name,
                "job_group": job_group,
                "job_executor": job_executor,
                "invoke_target": invoke_target,
                "job_args": job_args,
                "job_kwargs": job_kwargs,
                "job_trigger": job_trigger,
                "job_message": job_message,
                "status": status,
                "exception_info": exception_info,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logger.info(f"TaskLog: {json.dumps(log_data, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"保存任务日志失败: {str(e)}")

    @classmethod
    async def init_system_scheduler(cls) -> None:
        """
        应用启动时初始化定时任务。

        返回:
        - None
        """
        logger.info("🔎 开始启动定时任务...")
        scheduler.start()
        scheduler.add_listener(cls.scheduler_event_listener, EVENT_ALL)
        logger.info("✅️ 系统定时任务加载成功")

    @classmethod
    async def close_system_scheduler(cls) -> None:
        """
        关闭系统定时任务。

        返回:
        - None
        """
        try:
            scheduler.remove_all_jobs()
            scheduler.shutdown(wait=True)
            logger.info("✅️ 关闭定时任务成功")
        except Exception as e:
            logger.error(f"关闭定时任务失败: {str(e)}")

    @classmethod
    def get_job(cls, job_id: Union[str, int]) -> Optional[Job]:
        """
        根据任务ID获取任务对象。

        参数:
        - job_id (str | int): 任务ID。

        返回:
        - Optional[Job]: 任务对象，未找到则为 None。
        """
        return scheduler.get_job(job_id=str(job_id))

    @classmethod
    def get_all_jobs(cls) -> List[Job]:
        """
        获取全部调度任务列表。

        返回:
        - List[Job]: 任务列表。
        """
        return scheduler.get_jobs()

    @classmethod
    def add_job(
        cls,
        job_id: str,
        job_func: callable,
        trigger: str = "cron",
        trigger_args: str = None,
        job_name: str = None,
        job_args: list = None,
        job_kwargs: dict = None,
        start_date: datetime = None,
        end_date: datetime = None,
        coalesce: bool = False,
        max_instances: int = 1,
        jobstore: str = "default",
        executor: str = "default",
    ) -> Job:
        """
        添加调度任务。

        参数:
        - job_id: 任务ID
        - job_func: 任务函数
        - trigger: 触发器类型 (cron/interval/date)
        - trigger_args: 触发器参数
        - job_name: 任务名称
        - job_args: 位置参数
        - job_kwargs: 关键字参数
        - start_date: 开始日期
        - end_date: 结束日期
        - coalesce: 是否合并执行
        - max_instances: 最大实例数
        - jobstore: 任务存储
        - executor: 执行器

        返回:
        - Job: 新增的任务对象。
        """
        # 构建触发器
        if trigger == "date":
            trigger_obj = DateTrigger(run_date=trigger_args or datetime.now())
        elif trigger == "interval":
            if trigger_args is None:
                raise ValueError("interval 触发器缺少参数")
            fields = trigger_args.strip().split()
            if len(fields) != 5:
                raise ValueError("无效的 interval 表达式")
            second, minute, hour, day, week = tuple([int(field) if field != "*" else 0 for field in fields])
            trigger_obj = IntervalTrigger(
                weeks=week,
                days=day,
                hours=hour,
                minutes=minute,
                seconds=second,
                start_date=start_date,
                end_date=end_date,
                timezone="Asia/Shanghai",
            )
        elif trigger == "cron":
            if trigger_args is None:
                raise ValueError("cron 触发器缺少参数")
            fields = trigger_args.strip().split()
            if len(fields) not in (5, 6, 7):
                raise ValueError("无效的 Cron 表达式")

            # 支持 5/6/7 字段的 cron 表达式
            parsed_fields = [None if field in ("*", "?") else field for field in fields]

            # 5字段: 分 时 日 月 周
            # 6字段: 秒 分 时 日 月 周
            # 7字段: 秒 分 时 日 月 周 年
            if len(fields) == 5:
                minute, hour, day, month, day_of_week = parsed_fields
                second, year = None, None
            elif len(fields) == 6:
                second, minute, hour, day, month, day_of_week = parsed_fields
                year = None
            else:
                second, minute, hour, day, month, day_of_week, year = parsed_fields

            trigger_obj = CronTrigger(
                second=second,
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                year=year,
                start_date=start_date,
                end_date=end_date,
                timezone="Asia/Shanghai",
            )
        else:
            raise ValueError(f"无效的 trigger 触发器: {trigger}")

        # 添加任务
        job = scheduler.add_job(
            func=job_func,
            trigger=trigger_obj,
            args=job_args,
            kwargs=job_kwargs,
            id=str(job_id),
            name=job_name or str(job_id),
            coalesce=coalesce,
            max_instances=max_instances,
            jobstore=jobstore,
            executor=executor,
            replace_existing=True,
        )

        logger.info(f"添加任务成功: {job_id}, 触发器: {trigger}, 参数: {trigger_args}")
        return job

    @classmethod
    def add_job_by_path(
        cls,
        job_id: str,
        job_class: str,
        trigger: str = "cron",
        trigger_args: str = None,
        job_name: str = None,
        job_args: str = None,
        job_kwargs: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        coalesce: bool = False,
        max_instances: int = 1,
        jobstore: str = "default",
        executor: str = "default",
    ) -> Job:
        """
        通过函数路径添加调度任务。

        参数:
        - job_id: 任务ID
        - job_class: 函数路径 (如: app.scheduler.jobs.daily_report)
        - trigger: 触发器类型
        - trigger_args: 触发器参数
        - 其他参数同 add_job

        返回:
        - Job: 新增的任务对象。
        """
        try:
            module_path, func_name = job_class.rsplit(".", 1)
            module = importlib.import_module(module_path)
            job_func = getattr(module, func_name)
        except ModuleNotFoundError:
            raise ValueError(f"未找到该模块：{module_path}")
        except AttributeError:
            raise ValueError(f"未找到该模块下的方法：{func_name}")

        # 解析参数
        args_list = job_args.split(",") if job_args else None
        kwargs_dict = json.loads(job_kwargs) if job_kwargs else None

        return cls.add_job(
            job_id=job_id,
            job_func=job_func,
            trigger=trigger,
            trigger_args=trigger_args,
            job_name=job_name,
            job_args=args_list,
            job_kwargs=kwargs_dict,
            start_date=start_date,
            end_date=end_date,
            coalesce=coalesce,
            max_instances=max_instances,
            jobstore=jobstore,
            executor=executor,
        )

    @classmethod
    def run_job_now(cls, job_id: str, job_func: callable = None) -> None:
        """
        立即执行指定的任务（创建临时一次性任务）。

        参数:
        - job_id: 任务ID
        - job_func: 任务函数（可选，如果不提供则从现有任务获取）

        返回:
        - None
        """
        if job_func is None:
            existing_job = cls.get_job(job_id)
            if not existing_job:
                raise ValueError(f"未找到任务: {job_id}")
            job_func = existing_job.func
            job_args = existing_job.args
            job_kwargs = existing_job.kwargs
        else:
            job_args = None
            job_kwargs = None

        # 创建一次性任务
        scheduler.add_job(
            func=job_func,
            trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=1)),
            args=job_args,
            kwargs=job_kwargs,
            id=f"{job_id}_run_once_{datetime.now().timestamp()}",
            name=f"{job_id}_run_once",
        )

        logger.info(f"任务已创建一次性执行: {job_id}")

    @classmethod
    def remove_job(cls, job_id: Union[str, int]) -> bool:
        """
        根据任务ID删除调度任务。

        参数:
        - job_id (str | int): 任务ID。

        返回:
        - bool: 是否删除成功
        """
        query_job = cls.get_job(job_id=str(job_id))
        if query_job:
            scheduler.remove_job(job_id=str(job_id))
            logger.info(f"删除任务成功: {job_id}")
            return True
        return False

    @classmethod
    def clear_jobs(cls) -> None:
        """
        删除所有调度任务。

        返回:
        - None
        """
        scheduler.remove_all_jobs()
        logger.info("已清除所有任务")

    @classmethod
    def pause_job(cls, job_id: Union[str, int]) -> None:
        """
        暂停指定任务。

        参数:
        - job_id (str | int): 任务ID。

        返回:
        - None

        异常:
        - ValueError: 当任务不存在时抛出。
        """
        query_job = cls.get_job(job_id=str(job_id))
        if not query_job:
            raise ValueError(f"未找到该任务：{job_id}")
        scheduler.pause_job(job_id=str(job_id))
        logger.info(f"暂停任务成功: {job_id}")

    @classmethod
    def resume_job(cls, job_id: Union[str, int]) -> None:
        """
        恢复指定任务。

        参数:
        - job_id (str | int): 任务ID。

        返回:
        - None

        异常:
        - ValueError: 当任务不存在时抛出。
        """
        query_job = cls.get_job(job_id=str(job_id))
        if not query_job:
            raise ValueError(f"未找到该任务：{job_id}")
        scheduler.resume_job(job_id=str(job_id))
        logger.info(f"恢复任务成功: {job_id}")

    @classmethod
    def reschedule_job(
        cls,
        job_id: Union[str, int],
        trigger: str = None,
        trigger_args: str = None,
    ) -> Job:
        """
        重新调度指定任务。

        参数:
        - job_id: 任务ID
        - trigger: 新的触发器类型
        - trigger_args: 新的触发器参数

        返回:
        - Job: 更新后的任务对象。
        """
        query_job = cls.get_job(job_id=str(job_id))
        if not query_job:
            raise ValueError(f"未找到该任务：{job_id}")

        if trigger and trigger_args:
            # 构建新触发器
            if trigger == "cron":
                fields = trigger_args.strip().split()
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
                new_trigger = CronTrigger(
                    second=second,
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                    year=year,
                    timezone="Asia/Shanghai",
                )
            else:
                raise ValueError(f"暂不支持的触发器类型: {trigger}")

            return scheduler.reschedule_job(job_id=str(job_id), trigger=new_trigger)

        return scheduler.reschedule_job(job_id=str(job_id))

    @classmethod
    def get_job_status(cls) -> str:
        """
        获取调度器当前状态。

        返回:
        - str: 状态字符串（'stopped' | 'running' | 'paused' | 'unknown'）。
        """
        STATE_STOPPED = 0
        STATE_RUNNING = 1
        STATE_PAUSED = 2

        if scheduler.state == STATE_STOPPED:
            return "stopped"
        elif scheduler.state == STATE_RUNNING:
            return "running"
        elif scheduler.state == STATE_PAUSED:
            return "paused"
        else:
            return "unknown"

    @classmethod
    def print_jobs(cls, jobstore: Any | None = None, out: Any | None = None) -> None:
        """
        打印调度任务列表。

        参数:
        - jobstore: 任务存储别名。
        - out: 输出目标。

        返回:
        - None
        """
        scheduler.print_jobs(jobstore=jobstore, out=out)

    @classmethod
    def get_jobs_info(cls) -> List[dict]:
        """
        获取所有任务的信息列表。

        返回:
        - List[dict]: 任务信息列表
        """
        jobs = cls.get_all_jobs()
        result = []
        for job in jobs:
            job_info = job.__getstate__()
            result.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "func": str(job_info.get("func")),
                    "trigger": str(job_info.get("trigger")),
                    "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None,
                    "executor": job_info.get("executor"),
                    "jobstore": job._jobstore_alias,
                }
            )
        return result
