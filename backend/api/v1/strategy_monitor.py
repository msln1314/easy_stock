"""
策略监控API接口

提供策略统计数据：总策略数、运行中、异常、收益率等
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from models.stock_pick import StockPickStrategy, StrategyTrackPool, StrategyExecutionLog
from models.rotation_strategy import RotationStrategy
from tortoise.functions import Count, Sum

router = APIRouter(prefix="/api/v1/strategy-monitor", tags=["策略监控"])


@router.get("/stats")
async def get_strategy_monitor_stats():
    """获取策略监控统计数据"""
    today = date.today()

    # 1. 选股策略统计
    total_pick_strategies = await StockPickStrategy.all().count()
    active_pick_strategies = await StockPickStrategy.filter(is_active=True).count()

    # 今日执行情况
    today_executions = await StrategyExecutionLog.filter(execution_date=today).all()
    running_count = sum(1 for e in today_executions if e.status == "running")
    failed_count = sum(1 for e in today_executions if e.status == "failed")
    success_count = sum(1 for e in today_executions if e.status == "success")

    # 2. 轮动策略统计
    total_rotation_strategies = await RotationStrategy.all().count()
    running_rotation = await RotationStrategy.filter(status="running").count()
    paused_rotation = await RotationStrategy.filter(status="paused").count()

    # 3. 今日股池统计
    today_pool = await StrategyTrackPool.filter(target_date=today).all()
    today_pool_count = len(today_pool)

    # 4. 计算收益率（从已验证的追踪记录计算）
    verified_records = await StrategyTrackPool.filter(
        status="verified",
        actual_return__isnull=False
    ).all()

    # 总收益率（累计）
    total_return = Decimal("0")
    for r in verified_records:
        if r.actual_return:
            total_return += r.actual_return

    # 今日收益（今日验证的记录）
    today_verified = await StrategyTrackPool.filter(
        status="verified",
        verified_at__gte=datetime.combine(today, datetime.min.time())
    ).all()

    today_return = Decimal("0")
    today_profit_loss = Decimal("0")
    for r in today_verified:
        if r.actual_return:
            today_return += r.actual_return
            # 计算盈亏金额（假设平均入场金额10000元）
            if r.entry_price and r.exit_price:
                # 简化计算：盈亏 = (出场价 - 入场价) * 假设1000股
                profit = (r.exit_price - r.entry_price) * 1000
                today_profit_loss += profit

    # 5. 异常策略（执行失败的）
    failed_strategies = await StrategyExecutionLog.filter(
        execution_date__gte=today - timedelta(days=7),
        status="failed"
    ).count()

    # 6. 策略成功率
    all_verified = await StrategyTrackPool.filter(status__in=["verified", "failed"]).all()
    success_verified = sum(1 for r in all_verified if r.status == "verified")
    strategy_success_rate = (success_verified / len(all_verified) * 100) if all_verified else 0

    return success_response({
        # 策略数量统计
        "total_strategies": total_pick_strategies + total_rotation_strategies,
        "pick_strategies": total_pick_strategies,
        "rotation_strategies": total_rotation_strategies,
        "running": active_pick_strategies + running_rotation,
        "paused": paused_rotation,
        "abnormal": failed_strategies,

        # 今日执行情况
        "today_running": running_count,
        "today_failed": failed_count,
        "today_success": success_count,

        # 收益统计
        "total_return": float(total_return),
        "today_return": float(today_return),
        "today_profit_loss": float(today_profit_loss),

        # 股池统计
        "today_pool_count": today_pool_count,
        "strategy_success_rate": round(strategy_success_rate, 2),

        # 详细数据
        "pick_strategy_stats": {
            "total": total_pick_strategies,
            "active": active_pick_strategies,
            "inactive": total_pick_strategies - active_pick_strategies
        },
        "rotation_strategy_stats": {
            "total": total_rotation_strategies,
            "running": running_rotation,
            "paused": paused_rotation,
            "stopped": total_rotation_strategies - running_rotation - paused_rotation
        }
    })


@router.get("/running-list")
async def get_running_strategies(limit: int = Query(10, description="返回数量")):
    """获取运行中的策略列表"""
    # 选股策略
    pick_strategies = await StockPickStrategy.filter(is_active=True).order_by("-updated_at").limit(limit)

    # 轮动策略
    rotation_strategies = await RotationStrategy.filter(status="running").order_by("-updated_at").limit(limit)

    result = []

    for s in pick_strategies:
        result.append({
            "id": s.id,
            "type": "pick",
            "key": s.strategy_key,
            "name": s.strategy_name,
            "status": "running",
            "success_rate": float(s.success_rate) if s.success_rate else None,
            "total_generated": s.total_generated,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        })

    for s in rotation_strategies:
        result.append({
            "id": s.id,
            "type": "rotation",
            "key": f"rotation_{s.id}",
            "name": s.name,
            "status": s.status,
            "execute_mode": s.execute_mode,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        })

    return success_response(result)


@router.get("/abnormal-list")
async def get_abnormal_strategies(
    days: int = Query(7, description="查询天数"),
    limit: int = Query(20, description="返回数量")
):
    """获取异常策略列表"""
    start_date = date.today() - timedelta(days=days)

    # 执行失败的日志
    failed_logs = await StrategyExecutionLog.filter(
        execution_date__gte=start_date,
        status="failed"
    ).order_by("-created_at").limit(limit)

    result = []
    for log in failed_logs:
        strategy = await StockPickStrategy.get_or_none(id=log.strategy_id)
        result.append({
            "id": log.id,
            "strategy_id": log.strategy_id,
            "strategy_key": log.strategy_key,
            "strategy_name": strategy.strategy_name if strategy else log.strategy_key,
            "execution_date": log.execution_date.isoformat(),
            "error_message": log.error_message,
            "pool_type": log.pool_type,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })

    return success_response(result)


@router.get("/return-stats")
async def get_strategy_return_stats(days: int = Query(30, description="统计天数")):
    """获取策略收益统计（按策略分组）"""
    start_date = date.today() - timedelta(days=days)

    # 获取验证记录
    verified_records = await StrategyTrackPool.filter(
        status="verified",
        verified_at__gte=datetime.combine(start_date, datetime.min.time())
    ).all()

    # 按策略分组统计
    strategy_stats = {}
    for r in verified_records:
        key = r.strategy_key
        if key not in strategy_stats:
            strategy_stats[key] = {
                "strategy_key": key,
                "count": 0,
                "total_return": Decimal("0"),
                "success_count": 0,
                "failed_count": 0
            }

        strategy_stats[key]["count"] += 1
        if r.actual_return:
            strategy_stats[key]["total_return"] += r.actual_return

        if r.status == "verified":
            strategy_stats[key]["success_count"] += 1
        elif r.status == "failed":
            strategy_stats[key]["failed_count"] += 1

    # 计算成功率
    result = []
    for key, stats in strategy_stats.items():
        stats["success_rate"] = (
            stats["success_count"] / stats["count"] * 100
        ) if stats["count"] > 0 else 0
        stats["total_return"] = float(stats["total_return"])
        result.append(stats)

    # 按收益率排序
    result.sort(key=lambda x: x["total_return"], reverse=True)

    return success_response({
        "days": days,
        "strategies": result[:20]  # 返回前20个
    })