"""
风控指标API接口

提供仓位占比、红线规则触发、日内交易统计等风控数据
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from models.trade_red_line import TradeRedLine, TradeAuditLog
from models.trade_log import TradeLog
from tortoise.functions import Count, Sum

router = APIRouter(prefix="/api/v1/risk-control", tags=["风控指标"])


@router.get("/overview")
async def get_risk_control_overview():
    """获取风控概览"""
    today = date.today()

    # 1. 红线规则统计
    total_rules = await TradeRedLine.all().count()
    enabled_rules = await TradeRedLine.filter(is_enabled=True).count()
    critical_rules = await TradeRedLine.filter(is_enabled=True, severity="critical").count()
    warning_rules = await TradeRedLine.filter(is_enabled=True, severity="warning").count()

    # 2. 今日审核统计
    today_audits = await TradeAuditLog.filter(
        audit_time__gte=datetime.combine(today, datetime.min.time())
    ).all()

    passed_count = sum(1 for a in today_audits if a.audit_result in ["passed", "warning"])
    rejected_count = sum(1 for a in today_audits if a.audit_result == "rejected")
    warning_count = sum(1 for a in today_audits if a.audit_result == "warning")

    # 3. 今日交易统计
    today_buy_logs = await TradeLog.filter(
        action_type__in=["buy_request", "buy_success"],
        action_time__gte=datetime.combine(today, datetime.min.time())
    ).all()

    today_buy_count = len(today_buy_logs)
    today_buy_amount = sum(
        Decimal(str(log.action_data.get("amount", 0))) if log.action_data else Decimal("0")
        for log in today_buy_logs if log.action_type == "buy_success"
    )

    # 4. 红线触发统计（今日）
    today_rejected_detail = await TradeAuditLog.filter(
        audit_time__gte=datetime.combine(today, datetime.min.time()),
        audit_result="rejected"
    ).all()

    # 统计触发的规则
    rule_trigger_count = {}
    for audit in today_rejected_detail:
        if audit.failed_rules:
            for rule in audit.failed_rules:
                rule_key = rule.get("rule_key", "unknown")
                rule_trigger_count[rule_key] = rule_trigger_count.get(rule_key, 0) + 1

    # 5. 仓位估算（简化）
    # 假设总资产100万
    total_assets = Decimal("1000000")
    current_position_value = today_buy_amount  # 简化：今日买入金额作为持仓估算
    position_ratio = (current_position_value / total_assets * 100) if total_assets > 0 else 0

    # 6. 获取规则详情
    rules = await TradeRedLine.filter(is_enabled=True).order_by("severity").limit(10).all()

    return success_response({
        # 规则统计
        "total_rules": total_rules,
        "enabled_rules": enabled_rules,
        "critical_rules": critical_rules,
        "warning_rules": warning_rules,

        # 今日审核统计
        "today_audit_total": len(today_audits),
        "today_passed": passed_count,
        "today_rejected": rejected_count,
        "today_warning": warning_count,
        "audit_pass_rate": (passed_count / len(today_audits) * 100) if today_audits else 100,

        # 今日交易统计
        "today_buy_count": today_buy_count,
        "today_buy_amount": float(today_buy_amount),

        # 仓位统计
        "total_assets": float(total_assets),
        "position_value": float(current_position_value),
        "position_ratio": float(position_ratio),
        "available_cash": float(total_assets - current_position_value),

        # 红线触发统计
        "rule_trigger_count": rule_trigger_count,

        # 规则列表
        "rules": [{
            "id": r.id,
            "rule_key": r.rule_key,
            "rule_name": r.rule_name,
            "rule_type": r.rule_type,
            "rule_type_display": r.rule_type_display,
            "severity": r.severity,
            "severity_display": r.severity_display,
            "is_enabled": r.is_enabled,
            "total_checked": r.total_checked,
            "total_rejected": r.total_rejected,
            "reject_rate": (r.total_rejected / r.total_checked * 100) if r.total_checked > 0 else 0
        } for r in rules]
    })


@router.get("/rule-triggers")
async def get_rule_triggers(days: int = Query(7, description="查询天数")):
    """获取红线规则触发统计"""
    start_date = date.today() - timedelta(days=days)

    audits = await TradeAuditLog.filter(
        audit_time__gte=datetime.combine(start_date, datetime.min.time()),
        audit_result="rejected"
    ).all()

    # 按规则统计
    rule_stats = {}
    for audit in audits:
        if audit.failed_rules:
            for rule in audit.failed_rules:
                rule_key = rule.get("rule_key", "unknown")
                rule_name = rule.get("rule_name", rule_key)
                if rule_key not in rule_stats:
                    rule_stats[rule_key] = {
                        "rule_key": rule_key,
                        "rule_name": rule_name,
                        "trigger_count": 0,
                        "stock_list": []
                    }
                rule_stats[rule_key]["trigger_count"] += 1
                if audit.stock_code and audit.stock_code not in rule_stats[rule_key]["stock_list"]:
                    rule_stats[rule_key]["stock_list"].append({
                        "stock_code": audit.stock_code,
                        "stock_name": audit.stock_name,
                        "audit_time": audit.audit_time.isoformat()
                    })

    return success_response({
        "days": days,
        "total_triggers": len(audits),
        "rules": list(rule_stats.values())
    })


@router.get("/position-check")
async def check_position_status():
    """检查仓位状态"""
    # 获取红线规则中的仓位限制
    position_rules = await TradeRedLine.filter(
        rule_type="position_limit",
        is_enabled=True
    ).all()

    # 获取今日买入金额
    today = date.today()
    today_buys = await TradeLog.filter(
        action_type="buy_success",
        action_time__gte=datetime.combine(today, datetime.min.time()),
        result="success"
    ).all()

    today_buy_amount = sum(
        Decimal(str(log.action_data.get("amount", 0))) if log.action_data else Decimal("0")
        for log in today_buys
    )

    # 检查仓位限制
    violations = []
    for rule in position_rules:
        config = rule.rule_config
        max_position_pct = config.get("max_single_position_pct", 20) if config else 20

        # 检查是否超限
        is_violated = False
        if rule.rule_key == "SINGLE_POSITION_LIMIT":
            # 单只股票仓位检查（简化）
            pass
        elif rule.rule_key == "TOTAL_POSITION_LIMIT":
            # 总仓位检查
            max_total = config.get("max_total_position_pct", 80) if config else 80
            total_assets = Decimal("1000000")
            current_ratio = (today_buy_amount / total_assets * 100) if total_assets > 0 else 0
            if current_ratio > max_total:
                is_violated = True
                violations.append({
                    "rule_key": rule.rule_key,
                    "rule_name": rule.rule_name,
                    "current_value": float(current_ratio),
                    "limit_value": max_total,
                    "message": f"总仓位{current_ratio:.2f}%超过限制{max_total}%"
                })

    return success_response({
        "today_buy_amount": float(today_buy_amount),
        "position_rules": [{
            "rule_key": r.rule_key,
            "rule_name": r.rule_name,
            "rule_config": r.rule_config,
            "severity": r.severity
        } for r in position_rules],
        "violations": violations,
        "is_safe": len(violations) == 0
    })


@router.get("/daily-trade-limit")
async def check_daily_trade_limit():
    """检查日内交易限制"""
    today = date.today()

    # 获取频率限制规则
    frequency_rules = await TradeRedLine.filter(
        rule_type="frequency_limit",
        is_enabled=True
    ).all()

    # 获取今日交易次数
    today_trades = await TradeLog.filter(
        action_type__in=["buy_request", "buy_success"],
        action_time__gte=datetime.combine(today, datetime.min.time())
    ).count()

    # 检查限制
    status_list = []
    for rule in frequency_rules:
        config = rule.rule_config
        max_buy = config.get("max_buy_per_day", 10) if config else 10

        is_exceeded = today_trades >= max_buy
        remaining = max_buy - today_trades if not is_exceeded else 0

        status_list.append({
            "rule_key": rule.rule_key,
            "rule_name": rule.rule_name,
            "limit_value": max_buy,
            "current_value": today_trades,
            "is_exceeded": is_exceeded,
            "remaining": remaining,
            "severity": rule.severity
        })

    return success_response({
        "today_trade_count": today_trades,
        "limits": status_list,
        "can_trade": all(s["remaining"] > 0 for s in status_list)
    })