"""
ETF轮动信号API接口

提供轮动信号、ETF评分排行、持仓列表等
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from models.rotation_signal import RotationSignal
from models.rotation_position import RotationPosition
from models.etf_score import EtfScore
from models.rotation_strategy import RotationStrategy

router = APIRouter(prefix="/api/v1/etf-rotation-signal", tags=["ETF轮动信号"])


@router.get("/current")
async def get_current_rotation_signal():
    """获取当前轮动信号"""
    today = date.today()

    # 获取运行中的策略
    running_strategies = await RotationStrategy.filter(status="running").all()

    # 获取今日信号
    today_signals = await RotationSignal.filter(signal_date=today).order_by("-created_at").all()

    # 获取最新评分排行
    latest_scores = await EtfScore.filter(trade_date=today).order_by("-momentum_score").limit(10).all()

    # 如果今日没有数据，获取最近一天的数据
    if not latest_scores:
        latest_date = await EtfScore.all().order_by("-trade_date").first()
        if latest_date:
            latest_scores = await EtfScore.filter(trade_date=latest_date.trade_date).order_by("-momentum_score").limit(10).all()

    # 获取当前持仓
    current_positions = await RotationPosition.filter(status="holding").all()

    # 构建返回数据
    result = {
        "strategy_status": {
            "total": len(running_strategies),
            "running": sum(1 for s in running_strategies if s.status == "running"),
            "paused": sum(1 for s in running_strategies if s.status == "paused"),
        },
        "today_signals": [{
            "id": s.id,
            "signal_type": s.signal_type,
            "signal_type_display": s.signal_type_display,
            "etf_code": s.etf_code,
            "etf_name": s.etf_name,
            "action": s.action,
            "action_display": s.action_display,
            "score": float(s.score) if s.score else None,
            "rsrs_z": float(s.rsrs_z) if s.rsrs_z else None,
            "price": float(s.price) if s.price else None,
            "reason": s.reason,
            "is_executed": s.is_executed,
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in today_signals],
        "etf_ranking": [{
            "id": s.id,
            "etf_code": s.etf_code,
            "trade_date": s.trade_date.isoformat(),
            "momentum_score": float(s.momentum_score) if s.momentum_score else None,
            "rsrs_z_score": float(s.rsrs_z_score) if s.rsrs_z_score else None,
            "slope_value": float(s.slope_value) if s.slope_value else None,
            "r_squared": float(s.r_squared) if s.r_squared else None,
            "close_price": float(s.close_price) if s.close_price else None,
            "rank_position": s.rank_position
        } for s in latest_scores],
        "current_positions": [{
            "id": p.id,
            "etf_code": p.etf_code,
            "etf_name": p.etf_name,
            "buy_date": p.buy_date.isoformat(),
            "buy_price": float(p.buy_price) if p.buy_price else None,
            "buy_score": float(p.buy_score) if p.buy_score else None,
            "quantity": p.quantity,
            "current_price": float(p.current_price) if p.current_price else None,
            "profit_pct": float(p.profit_pct) if p.profit_pct else None,
            "hold_days": p.hold_days,
            "status": p.status
        } for p in current_positions],
        "signal_count": len(today_signals),
        "pending_count": sum(1 for s in today_signals if not s.is_executed)
    }

    return success_response(result)


@router.get("/ranking")
async def get_etf_ranking(limit: int = Query(10, description="返回数量")):
    """获取ETF评分排行"""
    today = date.today()

    # 获取今日评分
    scores = await EtfScore.filter(trade_date=today).order_by("-momentum_score").limit(limit).all()

    # 如果今日没有，获取最近数据
    if not scores:
        latest = await EtfScore.all().order_by("-trade_date").first()
        if latest:
            scores = await EtfScore.filter(trade_date=latest.trade_date).order_by("-momentum_score").limit(limit).all()

    return success_response([{
        "etf_code": s.etf_code,
        "trade_date": s.trade_date.isoformat(),
        "momentum_score": float(s.momentum_score) if s.momentum_score else None,
        "rsrs_z_score": float(s.rsrs_z_score) if s.rsrs_z_score else None,
        "slope_value": float(s.slope_value) if s.slope_value else None,
        "r_squared": float(s.r_squared) if s.r_squared else None,
        "close_price": float(s.close_price) if s.close_price else None,
        "rank_position": s.rank_position,
        # 信号建议
        "signal_suggestion": "buy" if float(s.momentum_score or 0) > 0.7 else "hold" if float(s.momentum_score or 0) > 0 else "sell"
    } for s in scores])


@router.get("/positions")
async def get_rotation_positions(status: Optional[str] = Query(None, description="状态筛选")):
    """获取轮动持仓"""
    query = RotationPosition.all()

    if status:
        query = query.filter(status=status)
    else:
        query = query.filter(status="holding")

    positions = await query.order_by("-buy_date").all()

    return success_response([{
        "id": p.id,
        "etf_code": p.etf_code,
        "etf_name": p.etf_name,
        "buy_date": p.buy_date.isoformat(),
        "buy_price": float(p.buy_price) if p.buy_price else None,
        "buy_score": float(p.buy_score) if p.buy_score else None,
        "quantity": p.quantity,
        "cost_amount": float(p.cost_amount) if p.cost_amount else None,
        "current_price": float(p.current_price) if p.current_price else None,
        "current_value": float(p.current_value) if p.current_value else None,
        "profit_pct": float(p.profit_pct) if p.profit_pct else None,
        "hold_days": p.hold_days,
        "status": p.status,
        "status_display": p.status_display
    } for p in positions])


@router.get("/signal-history")
async def get_signal_history(days: int = Query(30, description="查询天数")):
    """获取历史信号"""
    start_date = date.today() - timedelta(days=days)

    signals = await RotationSignal.filter(signal_date__gte=start_date).order_by("-signal_date").all()

    return success_response([{
        "id": s.id,
        "signal_date": s.signal_date.isoformat(),
        "signal_type": s.signal_type,
        "etf_code": s.etf_code,
        "etf_name": s.etf_name,
        "action": s.action,
        "score": float(s.score) if s.score else None,
        "rsrs_z": float(s.rsrs_z) if s.rsrs_z else None,
        "price": float(s.price) if s.price else None,
        "reason": s.reason,
        "is_executed": s.is_executed,
        "executed_at": s.executed_at.isoformat() if s.executed_at else None
    } for s in signals])