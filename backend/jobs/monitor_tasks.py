"""
计划任务执行模块 - 监控告警卖出信息
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from tortoise import Tortoise
from models.warning import WarningStockPool, WarningCondition
from models.scheduler import SchedulerTask, TaskLog

logger = logging.getLogger(__name__)


async def check_sell_warnings():
    """
    定时检查预警股票池，生成卖出信号

    执行逻辑:
    1. 获取未处理的预警股票
    2. 根据预警级别判断是否需要卖出
    3. 更新预警状态
    """
    logger.info(f"[{datetime.now()}] 开始检查卖出预警...")

    try:
        # 获取未处理的关键预警
        critical_warnings = await WarningStockPool.filter(
            is_handled=False,
            warning_level="critical"
        ).order_by("-trigger_time").limit(50)

        warning_count = 0
        for warning in critical_warnings:
            # 判断是否需要生成卖出信号
            if should_generate_sell_signal(warning):
                warning.is_handled = True
                warning.handle_action = "SELL"
                warning.handled_at = datetime.now()
                await warning.save()
                warning_count += 1

                logger.info(
                    f"生成卖出信号: {warning.stock_code} {warning.stock_name} "
                    f"触发条件: {warning.condition_name} "
                    f"触发时间: {warning.trigger_time}"
                )

        # 获取普通预警（供观察）
        normal_warnings = await WarningStockPool.filter(
            is_handled=False,
            warning_level="warning"
        ).order_by("-trigger_time").limit(20)

        logger.info(
            f"预警检查完成: 生成卖出信号 {warning_count} 个, "
            f"待观察预警 {len(normal_warnings)} 个"
        )

        return {
            "success": True,
            "sell_count": warning_count,
            "watch_count": len(normal_warnings),
            "message": f"检查完成，生成 {warning_count} 个卖出信号"
        }

    except Exception as e:
        logger.error(f"检查卖出预警失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"检查失败: {str(e)}"
        }


def should_generate_sell_signal(warning: WarningStockPool) -> bool:
    """
    判断是否应该生成卖出信号

    规则:
    1. 关键级别预警直接卖出
    2. 根据涨跌幅判断（跌幅超过阈值）
    3. 根据触发条件类型判断
    """
    # 关键级别直接卖出
    if warning.warning_level == "critical":
        return True

    # 涨跌幅判断
    if warning.change_percent:
        # 跌幅超过5%
        if float(warning.change_percent) < -5:
            return True

    return False


async def generate_daily_report():
    """
    生成每日策略运行报告

    统计:
    1. 当日预警数量
    2. 当日卖出信号数量
    3. 预警处理率
    """
    logger.info(f"[{datetime.now()}] 开始生成每日报告...")

    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 统计当日预警
        total_warnings = await WarningStockPool.filter(
            trigger_time__gte=today_start,
            trigger_time__lte=today_end
        ).count()

        # 统计当日卖出信号
        sell_signals = await WarningStockPool.filter(
            trigger_time__gte=today_start,
            trigger_time__lte=today_end,
            handle_action="SELL"
        ).count()

        # 统计已处理预警
        handled_warnings = await WarningStockPool.filter(
            trigger_time__gte=today_start,
            trigger_time__lte=today_end,
            is_handled=True
        ).count()

        # 处理率
        handle_rate = 0
        if total_warnings > 0:
            handle_rate = (handled_warnings / total_warnings) * 100

        report_data = {
            "date": today.isoformat(),
            "total_warnings": total_warnings,
            "sell_signals": sell_signals,
            "handled_warnings": handled_warnings,
            "handle_rate": round(handle_rate, 2),
            "pending_warnings": total_warnings - handled_warnings
        }

        logger.info(f"每日报告生成完成: {report_data}")

        return {
            "success": True,
            "data": report_data,
            "message": "报告生成成功"
        }

    except Exception as e:
        logger.error(f"生成每日报告失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"生成失败: {str(e)}"
        }


async def cleanup_old_logs():
    """
    清理过期的任务日志（保留最近30天）
    """
    logger.info(f"[{datetime.now()}] 开始清理过期日志...")

    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=30)

        deleted = await TaskLog.filter(
            created_at__lt=cutoff_date
        ).delete()

        logger.info(f"清理完成: 删除 {deleted} 条过期日志")

        return {
            "success": True,
            "deleted_count": deleted,
            "message": f"清理了 {deleted} 条过期日志"
        }

    except Exception as e:
        logger.error(f"清理日志失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"清理失败: {str(e)}"
        }