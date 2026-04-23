"""
交易日志API

提供日志查询和统计接口
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from core.response import success_response
from core.auth import get_current_user
from services.trade_log import trade_log_service
from models.trade_log import TradeLog, TradeLogSummary, TradeActionType

router = APIRouter(prefix="/api/v1/trade-log", tags=["交易日志"])


# ==================== Schemas ====================

class LogQueryRequest(BaseModel):
    """日志查询请求"""
    action_type: Optional[str] = None
    stock_code: Optional[str] = None
    strategy_key: Optional[str] = None
    result: Optional[str] = None
    order_id: Optional[str] = None
    start_time: Optional[str] = None  # YYYY-MM-DD HH:mm:ss
    end_time: Optional[str] = None    # YYYY-MM-DD HH:mm:ss
    limit: int = 100
    offset: int = 0


# ==================== 日志查询接口 ====================

@router.get("/list", summary="获取交易日志列表")
async def get_logs(
    action_type: Optional[str] = None,
    stock_code: Optional[str] = None,
    strategy_key: Optional[str] = None,
    result: Optional[str] = None,
    order_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user=Depends(get_current_user)
):
    """
    获取交易日志列表

    支持按行为类型、股票代码、策略、结果等筛选
    """
    start_time = None
    end_time = None

    if start_date:
        start_time = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_time = datetime.strptime(end_date, "%Y-%m-%d")
        end_time = end_time.replace(hour=23, minute=59, second=59)

    logs = await trade_log_service.get_logs(
        action_type=action_type,
        stock_code=stock_code,
        strategy_key=strategy_key,
        result=result,
        order_id=order_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )

    total = await trade_log_service.count_logs(
        action_type=action_type,
        result=result,
        start_time=start_time,
        end_time=end_time
    )

    return success_response({
        "logs": [
            {
                "id": log.id,
                "action_type": log.action_type,
                "action_type_display": log.action_type_display,
                "action_name": log.action_name,
                "action_source": log.action_source,
                "action_source_display": log.action_source_display,
                "strategy_key": log.strategy_key,
                "stock_code": log.stock_code,
                "stock_name": log.stock_name,
                "order_id": log.order_id,
                "action_data": log.action_data,
                "result": log.result,
                "result_display": log.result_display,
                "result_message": log.result_message,
                "error_message": log.error_message,
                "user_name": log.user_name,
                "action_time": log.action_time.isoformat(),
                "duration_ms": log.duration_ms,
                "tags": log.tags,
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    })


@router.get("/detail/{log_id}", summary="获取日志详情")
async def get_log_detail(log_id: int, user=Depends(get_current_user)):
    """获取单条日志详情"""
    log = await trade_log_service.get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    return success_response({
        "id": log.id,
        "action_type": log.action_type,
        "action_type_display": log.action_type_display,
        "action_name": log.action_name,
        "action_source": log.action_source,
        "action_source_display": log.action_source_display,
        "strategy_key": log.strategy_key,
        "stock_code": log.stock_code,
        "stock_name": log.stock_name,
        "order_id": log.order_id,
        "related_id": log.related_id,
        "action_data": log.action_data,
        "result": log.result,
        "result_display": log.result_display,
        "result_message": log.result_message,
        "error_message": log.error_message,
        "user_id": log.user_id,
        "user_name": log.user_name,
        "action_time": log.action_time.isoformat(),
        "duration_ms": log.duration_ms,
        "ip_address": log.ip_address,
        "device_info": log.device_info,
        "tags": log.tags,
        "remark": log.remark,
    })


@router.get("/order/{order_id}", summary="获取订单相关日志")
async def get_order_logs(order_id: str, user=Depends(get_current_user)):
    """
    获取某个订单的所有相关日志

    包括请求、审核、执行、成功/失败等完整链路
    """
    logs = await trade_log_service.get_order_logs(order_id)

    return success_response({
        "order_id": order_id,
        "logs": [
            {
                "id": log.id,
                "action_type": log.action_type,
                "action_type_display": log.action_type_display,
                "action_name": log.action_name,
                "stock_code": log.stock_code,
                "stock_name": log.stock_name,
                "action_data": log.action_data,
                "result": log.result,
                "result_message": log.result_message,
                "action_time": log.action_time.isoformat(),
            }
            for log in logs
        ],
        "total": len(logs)
    })


@router.get("/stock/{stock_code}", summary="获取股票相关日志")
async def get_stock_logs(
    stock_code: str,
    days: int = 7,
    limit: int = 50,
    user=Depends(get_current_user)
):
    """获取某股票的交易日志"""
    logs = await trade_log_service.get_stock_logs(
        stock_code=stock_code,
        days=days,
        limit=limit
    )

    return success_response({
        "stock_code": stock_code,
        "days": days,
        "logs": [
            {
                "id": log.id,
                "action_type": log.action_type,
                "action_type_display": log.action_type_display,
                "action_name": log.action_name,
                "result": log.result,
                "result_message": log.result_message,
                "action_time": log.action_time.isoformat(),
                "user_name": log.user_name,
            }
            for log in logs
        ],
        "total": len(logs)
    })


# ==================== 行为类型接口 ====================

@router.get("/action-types", summary="获取所有行为类型")
async def get_action_types(user=Depends(get_current_user)):
    """获取所有交易行为类型列表"""
    types = []
    for action in TradeActionType:
        types.append({
            "key": action.value,
            "name": action.name,
            "display": {
                "stock_pick": "选股执行",
                "stock_pick_result": "选股结果",
                "buy_request": "买入请求",
                "buy_audit": "买入审核",
                "buy_executed": "买入执行",
                "buy_success": "买入成功",
                "buy_failed": "买入失败",
                "sell_request": "卖出请求",
                "sell_executed": "卖出执行",
                "sell_success": "卖出成功",
                "sell_failed": "卖出失败",
                "audit_pass": "审核通过",
                "audit_reject": "审核拒绝",
                "audit_warning": "审核警告",
                "cancel_request": "撤单请求",
                "cancel_success": "撤单成功",
                "cancel_failed": "撤单失败",
                "warning_trigger": "预警触发",
                "warning_handle": "预警处理",
                "system_start": "系统启动",
                "system_stop": "系统停止",
                "config_change": "配置变更",
                "rule_change": "规则变更",
                "ai_chat": "AI对话",
                "manual_operation": "手动操作",
            }.get(action.value, action.value)
        })

    return success_response({"types": types})


# ==================== 统计接口 ====================

@router.get("/summary/{summary_date}", summary="获取每日汇总")
async def get_daily_summary(
    summary_date: str,  # YYYY-MM-DD
    user=Depends(get_current_user)
):
    """获取某日的交易统计汇总"""
    date_obj = date.fromisoformat(summary_date)
    summary = await trade_log_service.get_summary(date_obj)

    if not summary:
        # 生成汇总
        summary = await trade_log_service.generate_daily_summary(date_obj)

    return success_response({
        "summary_date": str(summary.summary_date),
        "stock_pick_count": summary.stock_pick_count,
        "buy_request_count": summary.buy_request_count,
        "buy_success_count": summary.buy_success_count,
        "buy_failed_count": summary.buy_failed_count,
        "buy_rejected_count": summary.buy_rejected_count,
        "buy_total_amount": float(summary.buy_total_amount),
        "buy_total_quantity": summary.buy_total_quantity,
        "sell_request_count": summary.sell_request_count,
        "sell_success_count": summary.sell_success_count,
        "sell_failed_count": summary.sell_failed_count,
        "sell_total_amount": float(summary.sell_total_amount),
        "sell_total_quantity": summary.sell_total_quantity,
        "audit_pass_count": summary.audit_pass_count,
        "audit_reject_count": summary.audit_reject_count,
        "audit_warning_count": summary.audit_warning_count,
        "warning_trigger_count": summary.warning_trigger_count,
        "warning_handle_count": summary.warning_handle_count,
        "cancel_count": summary.cancel_count,
        "ai_chat_count": summary.ai_chat_count,
    })


@router.get("/summary/range", summary="获取时间段汇总")
async def get_range_summary(
    start_date: str,  # YYYY-MM-DD
    end_date: str,    # YYYY-MM-DD
    user=Depends(get_current_user)
):
    """获取时间段内的统计汇总"""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    summaries = []
    current = start
    while current <= end:
        summary = await trade_log_service.get_summary(current)
        if not summary:
            summary = await trade_log_service.generate_daily_summary(current)

        summaries.append({
            "summary_date": str(summary.summary_date),
            "buy_success_count": summary.buy_success_count,
            "buy_total_amount": float(summary.buy_total_amount),
            "sell_success_count": summary.sell_success_count,
            "sell_total_amount": float(summary.sell_total_amount),
            "audit_reject_count": summary.audit_reject_count,
        })

        current += timedelta(days=1)

    return success_response({
        "start_date": start_date,
        "end_date": end_date,
        "summaries": summaries,
        "total_days": len(summaries)
    })


@router.get("/statistics", summary="获取统计数据")
@router.get("/stats", summary="获取统计数据（别名）")
async def get_statistics(
    days: int = 7,
    user=Depends(get_current_user)
):
    """
    获取交易统计数据

    包括各类行为的发生次数、成功率、拒绝率等
    """
    start_time = datetime.now() - timedelta(days=days)
    end_time = datetime.now()

    # 各行为类型统计
    action_stats = await trade_log_service.get_action_type_stats(
        start_time=start_time,
        end_time=end_time
    )

    # 买入成功率
    buy_total = action_stats.get("buy_request", 0)
    buy_success = action_stats.get("buy_success", 0)
    buy_failed = action_stats.get("buy_failed", 0)
    buy_rejected = action_stats.get("audit_reject", 0)
    buy_success_rate = (buy_success / buy_total * 100) if buy_total > 0 else 0
    buy_reject_rate = (buy_rejected / buy_total * 100) if buy_total > 0 else 0

    # 卖出成功率
    sell_total = action_stats.get("sell_request", 0)
    sell_success = action_stats.get("sell_success", 0)
    sell_success_rate = (sell_success / sell_total * 100) if sell_total > 0 else 0

    # 审核统计
    audit_pass = action_stats.get("audit_pass", 0)
    audit_reject = action_stats.get("audit_reject", 0)
    audit_warning = action_stats.get("audit_warning", 0)
    audit_total = audit_pass + audit_reject + audit_warning
    audit_pass_rate = (audit_pass / audit_total * 100) if audit_total > 0 else 0

    # 计算today_trades - 今日的交易日志数量
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = await trade_log_service.count_logs(start_time=today_start)

    # 总交易数 (买入+卖出相关)
    total_trades = buy_success + buy_failed + sell_success

    # 成功率 (基于买入和卖出成功数)
    success_rate = ((buy_success + sell_success) / total_trades * 100) if total_trades > 0 else 0

    return success_response({
        "total_trades": total_trades,
        "today_trades": today_logs,
        "success_rate": round(success_rate, 2),
        "buy_count": buy_success,
        "sell_count": sell_success,
        "cancel_count": action_stats.get("cancel_success", 0),
        # 保留详细统计供高级使用
        "action_statistics": action_stats,
        "buy_statistics": {
            "total_requests": buy_total,
            "success": buy_success,
            "failed": buy_failed,
            "rejected": buy_rejected,
            "success_rate": round(buy_success_rate, 2),
            "reject_rate": round(buy_reject_rate, 2),
        },
        "sell_statistics": {
            "total_requests": sell_total,
            "success": sell_success,
            "success_rate": round(sell_success_rate, 2),
        },
        "audit_statistics": {
            "pass": audit_pass,
            "reject": audit_reject,
            "warning": audit_warning,
            "pass_rate": round(audit_pass_rate, 2),
        },
        "warning_statistics": {
            "trigger": action_stats.get("warning_trigger", 0),
            "handle": action_stats.get("warning_handle", 0),
        }
    })


@router.post("/summary/generate", summary="生成每日汇总")
async def generate_summary(
    summary_date: str,  # YYYY-MM-DD
    user=Depends(get_current_user)
):
    """手动生成某日的统计汇总"""
    date_obj = date.fromisoformat(summary_date)
    summary = await trade_log_service.generate_daily_summary(date_obj)

    return success_response({
        "message": f"已生成 {summary_date} 的统计汇总",
        "summary_date": str(summary.summary_date)
    })


# ==================== 按类型统计 ====================

@router.get("/by-type", summary="按行为类型统计")
async def get_logs_by_type(
    days: int = 7,
    user=Depends(get_current_user)
):
    """按行为类型统计日志数量"""
    start_time = datetime.now() - timedelta(days=days)

    stats = await trade_log_service.get_action_type_stats(
        start_time=start_time
    )

    return success_response({
        "period_days": days,
        "statistics": stats
    })