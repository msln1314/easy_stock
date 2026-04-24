"""
资金概览API接口

提供资金统计：今日盈利、本月盈亏、总盈亏、日收益率、总收益率
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from models.trade_log import TradeLog, TradeLogSummary
from models.trade_red_line import TradeAuditLog

router = APIRouter(prefix="/api/v1/capital-overview", tags=["资金概览"])


@router.get("/stats")
async def get_capital_overview_stats():
    """获取资金概览统计数据"""
    today = date.today()
    month_start = date(today.year, today.month, 1)

    # 1. 今日盈亏统计
    today_buys = await TradeLog.filter(
        action_type__in=["buy_success", "buy_executed"],
        action_time__gte=datetime.combine(today, datetime.min.time()),
        result="success"
    ).all()

    today_sells = await TradeLog.filter(
        action_type__in=["sell_success", "sell_executed"],
        action_time__gte=datetime.combine(today, datetime.min.time()),
        result="success"
    ).all()

    # 计算今日买入金额
    today_buy_amount = Decimal("0")
    for log in today_buys:
        if log.action_data and log.action_data.get("amount"):
            today_buy_amount += Decimal(str(log.action_data.get("amount", 0)))

    # 计算今日卖出金额
    today_sell_amount = Decimal("0")
    today_profit = Decimal("0")
    for log in today_sells:
        if log.action_data:
            sell_amount = Decimal(str(log.action_data.get("amount", 0)))
            today_sell_amount += sell_amount
            # 卖出盈亏
            if log.action_data.get("profit"):
                today_profit += Decimal(str(log.action_data.get("profit", 0)))

    # 今日盈亏 = 卖出金额 - 买入金额（简化计算，实际需要考虑持仓成本）
    today_profit_loss = today_profit

    # 2. 本月盈亏统计
    month_sells = await TradeLog.filter(
        action_type__in=["sell_success", "sell_executed"],
        action_time__gte=datetime.combine(month_start, datetime.min.time()),
        result="success"
    ).all()

    month_profit = Decimal("0")
    for log in month_sells:
        if log.action_data and log.action_data.get("profit"):
            month_profit += Decimal(str(log.action_data.get("profit", 0)))

    month_profit_loss = month_profit

    # 3. 总盈亏统计（从所有卖出记录）
    all_sells = await TradeLog.filter(
        action_type__in=["sell_success", "sell_executed"],
        result="success"
    ).all()

    total_profit = Decimal("0")
    for log in all_sells:
        if log.action_data and log.action_data.get("profit"):
            total_profit += Decimal(str(log.action_data.get("profit", 0)))

    total_profit_loss = total_profit

    # 4. 交易次数统计
    today_trade_count = len(today_buys) + len(today_sells)
    month_trade_count = await TradeLog.filter(
        action_type__in=["buy_success", "sell_success"],
        action_time__gte=datetime.combine(month_start, datetime.min.time()),
        result="success"
    ).count()
    total_trade_count = await TradeLog.filter(
        action_type__in=["buy_success", "sell_success"],
        result="success"
    ).count()

    # 5. 审核统计
    today_audit_passed = await TradeAuditLog.filter(
        audit_time__gte=datetime.combine(today, datetime.min.time()),
        audit_result__in=["passed", "warning"]
    ).count()
    today_audit_rejected = await TradeAuditLog.filter(
        audit_time__gte=datetime.combine(today, datetime.min.time()),
        audit_result="rejected"
    ).count()

    # 6. 计算收益率（需要总资产数据）
    # 假设总资产为100万（实际需要从账户获取）
    total_assets = Decimal("1000000")  # 默认值

    # 今日收益率
    today_return_rate = (today_profit_loss / total_assets * 100) if total_assets > 0 else 0

    # 总收益率
    total_return_rate = (total_profit_loss / total_assets * 100) if total_assets > 0 else 0

    # 7. 本月收益率
    month_return_rate = (month_profit_loss / total_assets * 100) if total_assets > 0 else 0

    # 8. 从TradeLogSummary获取汇总数据（如果有）
    today_summary = await TradeLogSummary.get_or_none(summary_date=today)

    return success_response({
        # 盈亏统计
        "today_profit_loss": float(today_profit_loss),
        "month_profit_loss": float(month_profit_loss),
        "total_profit_loss": float(total_profit_loss),

        # 收益率
        "today_return_rate": float(today_return_rate),
        "month_return_rate": float(month_return_rate),
        "total_return_rate": float(total_return_rate),

        # 交易统计
        "today_trade_count": today_trade_count,
        "today_buy_count": len(today_buys),
        "today_sell_count": len(today_sells),
        "today_buy_amount": float(today_buy_amount),
        "today_sell_amount": float(today_sell_amount),

        "month_trade_count": month_trade_count,
        "total_trade_count": total_trade_count,

        # 审核统计
        "today_audit_passed": today_audit_passed,
        "today_audit_rejected": today_audit_rejected,

        # 资产信息
        "total_assets": float(total_assets),

        # 概览摘要数据
        "summary": {
            "today_summary": {
                "buy_count": today_summary.buy_success_count if today_summary else len(today_buys),
                "sell_count": today_summary.sell_success_count if today_summary else len(today_sells),
                "buy_amount": float(today_summary.buy_total_amount) if today_summary else float(today_buy_amount),
                "sell_amount": float(today_summary.sell_total_amount) if today_summary else float(today_sell_amount),
            } if today_summary else None
        }
    })


@router.get("/history")
async def get_capital_history(
    days: int = Query(30, ge=1, le=90, description="查询天数")
):
    """获取资金历史统计"""
    start_date = date.today() - timedelta(days=days)

    summaries = await TradeLogSummary.filter(
        summary_date__gte=start_date
    ).order_by("summary_date").all()

    result = []
    for s in summaries:
        # 计算当日盈亏（卖出金额 - 买入金额，简化）
        daily_profit_loss = float(s.sell_total_amount) - float(s.buy_total_amount)

        result.append({
            "date": s.summary_date.isoformat(),
            "buy_count": s.buy_success_count,
            "sell_count": s.sell_success_count,
            "buy_amount": float(s.buy_total_amount),
            "sell_amount": float(s.sell_total_amount),
            "profit_loss": daily_profit_loss,
            "audit_pass": s.audit_pass_count,
            "audit_reject": s.audit_reject_count,
            "warning_count": s.warning_trigger_count
        })

    return success_response({
        "days": days,
        "history": result
    })


@router.get("/monthly")
async def get_monthly_stats(
    months: int = Query(12, ge=1, le=24, description="查询月数")
):
    """获取月度统计"""
    from collections import defaultdict

    today = date.today()
    start_date = date(today.year, today.month, 1) - timedelta(days=months * 31)

    logs = await TradeLog.filter(
        action_type__in=["buy_success", "sell_success"],
        action_time__gte=datetime.combine(start_date, datetime.min.time()),
        result="success"
    ).all()

    # 按月汇总
    monthly_stats = defaultdict(lambda: {
        "buy_count": 0,
        "sell_count": 0,
        "buy_amount": Decimal("0"),
        "sell_amount": Decimal("0"),
        "profit": Decimal("0")
    })

    for log in logs:
        month_key = log.action_time.strftime("%Y-%m")
        if log.action_type in ["buy_success"]:
            monthly_stats[month_key]["buy_count"] += 1
            if log.action_data and log.action_data.get("amount"):
                monthly_stats[month_key]["buy_amount"] += Decimal(str(log.action_data.get("amount", 0)))
        elif log.action_type in ["sell_success"]:
            monthly_stats[month_key]["sell_count"] += 1
            if log.action_data:
                monthly_stats[month_key]["sell_amount"] += Decimal(str(log.action_data.get("amount", 0)))
                if log.action_data.get("profit"):
                    monthly_stats[month_key]["profit"] += Decimal(str(log.action_data.get("profit", 0)))

    result = []
    for month_key in sorted(monthly_stats.keys()):
        stats = monthly_stats[month_key]
        result.append({
            "month": month_key,
            "buy_count": stats["buy_count"],
            "sell_count": stats["sell_count"],
            "buy_amount": float(stats["buy_amount"]),
            "sell_amount": float(stats["sell_amount"]),
            "profit_loss": float(stats["profit"]),
            "trade_count": stats["buy_count"] + stats["sell_count"]
        })

    return success_response({
        "months": months,
        "monthly_stats": result
    })