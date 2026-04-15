"""
轮动策略API路由
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import date, timedelta
from loguru import logger

from core.response import success_response, error_response
from schemas.rotation_strategy import (
    RotationStrategyCreate, RotationStrategyUpdate,
    RotationStrategyResponse, RotationStrategyStatusUpdate,
    EtfScoreResponse, RotationSignalResponse
)
from schemas.rotation_backtest import BacktestRequest, BacktestResponse
from models.rotation_strategy import RotationStrategy
from models.etf_pool import EtfPool
from models.rotation_signal import RotationSignal
from models.rotation_backtest import RotationBacktest
from models.etf_score import EtfScore
from services.etf_rotation import EtfRotationService
from services.kline_service import kline_service

router = APIRouter(prefix="/api/v1/rotation-strategies", tags=["轮动策略"])
service = EtfRotationService()


@router.get("", response_model=None)
async def get_strategies(
    status: Optional[str] = Query(None, description="状态筛选"),
    execute_mode: Optional[str] = Query(None, description="执行模式筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """获取轮动策略列表"""
    query = RotationStrategy.all()

    if status:
        query = query.filter(status=status)
    if execute_mode:
        query = query.filter(execute_mode=execute_mode)
    if keyword:
        query = query.filter(name__icontains=keyword)

    strategies = await query.order_by("-created_at").all()

    result = [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "slope_period": s.slope_period,
            "rsrs_period": s.rsrs_period,
            "hold_count": s.hold_count,
            "rebalance_freq": s.rebalance_freq,
            "execute_mode": s.execute_mode,
            "execute_mode_display": s.execute_mode_display,
            "status": s.status,
            "status_display": s.status_display,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        for s in strategies
    ]

    return success_response(result)


@router.get("/stats", response_model=None)
async def get_stats():
    """获取轮动策略统计"""
    total = await RotationStrategy.all().count()
    running = await RotationStrategy.filter(status="running").count()
    paused = await RotationStrategy.filter(status="paused").count()
    stopped = await RotationStrategy.filter(status="stopped").count()

    simulate = await RotationStrategy.filter(execute_mode="simulate").count()
    alert = await RotationStrategy.filter(execute_mode="alert").count()

    return success_response({
        "total": total,
        "by_status": {
            "running": running,
            "paused": paused,
            "stopped": stopped
        },
        "by_execute_mode": {
            "simulate": simulate,
            "alert": alert
        }
    })


@router.post("", response_model=None)
async def create_strategy(data: RotationStrategyCreate):
    """创建轮动策略"""
    # 验证参数
    valid_freqs = ["daily", "weekly", "monthly"]
    if data.rebalance_freq not in valid_freqs:
        return error_response(f"无效的调仓频率: {data.rebalance_freq}")

    valid_modes = ["simulate", "alert"]
    if data.execute_mode not in valid_modes:
        return error_response(f"无效的执行模式: {data.execute_mode}")

    strategy = await RotationStrategy.create(**data.model_dump())

    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "status": strategy.status,
        "created_at": strategy.created_at.isoformat()
    })


@router.get("/{id}", response_model=None)
async def get_strategy_detail(id: int):
    """获取策略详情"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "slope_period": strategy.slope_period,
        "rsrs_period": strategy.rsrs_period,
        "rsrs_z_window": strategy.rsrs_z_window,
        "rsrs_buy_threshold": float(strategy.rsrs_buy_threshold),
        "rsrs_sell_threshold": float(strategy.rsrs_sell_threshold),
        "ma_period": strategy.ma_period,
        "hold_count": strategy.hold_count,
        "rebalance_freq": strategy.rebalance_freq,
        "rebalance_freq_display": strategy.rebalance_freq_display,
        "execute_mode": strategy.execute_mode,
        "execute_mode_display": strategy.execute_mode_display,
        "status": strategy.status,
        "status_display": strategy.status_display,
        "created_at": strategy.created_at.isoformat(),
        "updated_at": strategy.updated_at.isoformat()
    })


@router.put("/{id}", response_model=None)
async def update_strategy(id: int, data: RotationStrategyUpdate):
    """更新策略参数"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(strategy, key, value)
        await strategy.save()

    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "status": strategy.status,
        "updated_at": strategy.updated_at.isoformat()
    })


@router.put("/{id}/status", response_model=None)
async def update_strategy_status(id: int, data: RotationStrategyStatusUpdate):
    """更新策略状态（启动/暂停）"""
    valid_statuses = ["running", "paused", "stopped"]
    if data.status not in valid_statuses:
        return error_response(f"无效的状态: {data.status}")

    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    strategy.status = data.status
    await strategy.save()

    logger.info(f"策略 {strategy.name} 状态更新为 {strategy.status_display}")

    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "status": strategy.status,
        "status_display": strategy.status_display,
        "updated_at": strategy.updated_at.isoformat()
    })


@router.get("/{id}/scores/latest", response_model=None)
async def get_latest_scores(id: int):
    """获取最新ETF评分排名"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    try:
        scores = await service.calculate_scores(strategy, date.today())

        # 获取ETF名称
        result = []
        for score in scores:
            etf = await EtfPool.filter(code=score.etf_code).first()
            result.append({
                "etf_code": score.etf_code,
                "etf_name": etf.name if etf else "",
                "sector": etf.sector if etf else "",
                "momentum_score": float(score.momentum_score) if score.momentum_score else None,
                "slope_value": float(score.slope_value) if score.slope_value else None,
                "r_squared": float(score.r_squared) if score.r_squared else None,
                "rsrs_z_score": float(score.rsrs_z_score) if score.rsrs_z_score else None,
                "close_price": float(score.close_price) if score.close_price else None,
                "ma_value": float(score.ma_value) if score.ma_value else None,
                "rank": score.rank_position
            })

        return success_response({
            "trade_date": date.today().isoformat(),
            "strategy_name": strategy.name,
            "scores": result
        })

    except Exception as e:
        logger.error(f"计算评分失败: {e}")
        return error_response(f"计算评分失败: {str(e)}")


@router.get("/{id}/signals", response_model=None)
async def get_signals(
    id: int,
    signal_type: Optional[str] = Query(None, description="信号类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """获取信号记录"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    query = RotationSignal.filter(strategy_id=id).order_by("-signal_date")

    if signal_type:
        query = query.filter(signal_type=signal_type)

    signals = await query.limit(limit).all()

    result = [
        {
            "id": s.id,
            "signal_date": s.signal_date.isoformat(),
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
            "created_at": s.created_at.isoformat()
        }
        for s in signals
    ]

    return success_response(result)


@router.post("/{id}/signals/generate", response_model=None)
async def generate_signals(id: int):
    """手动触发信号生成"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    try:
        # 计算评分
        scores = await service.calculate_scores(strategy, date.today())

        # 生成信号
        signals = await service.generate_signals(strategy, scores)

        # 保存信号
        await service.save_signals(signals)

        result = [
            {
                "signal_date": s.signal_date.isoformat(),
                "signal_type": s.signal_type,
                "signal_type_display": s.signal_type_display,
                "etf_code": s.etf_code,
                "etf_name": s.etf_name,
                "action": s.action,
                "action_display": s.action_display,
                "score": float(s.score) if s.score else None,
                "rsrs_z": float(s.rsrs_z) if s.rsrs_z else None,
                "price": float(s.price) if s.price else None,
                "reason": s.reason
            }
            for s in signals
        ]

        return success_response({
            "generated_count": len(signals),
            "signals": result
        })

    except Exception as e:
        logger.error(f"生成信号失败: {e}")
        return error_response(f"生成信号失败: {str(e)}")


@router.post("/{id}/backtest", response_model=None)
async def run_backtest(id: int, data: BacktestRequest):
    """运行回测"""
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)

    try:
        from utils.backtest_engine import BacktestEngine
        from datetime import datetime

        logger.info(f"策略 {strategy.name} 回测请求: {data.start_date} - {data.end_date}")

        # 创建回测引擎
        engine = BacktestEngine(initial_capital=data.initial_capital)

        # 获取ETF池
        etf_pool = await EtfPool.filter(is_active=True).all()
        if not etf_pool:
            return error_response("ETF池为空，无法回测")

        # 获取K线数据（使用模拟数据）
        klines = {}
        for etf in etf_pool:
            klines_data = await kline_service.get_klines(etf.code, limit=200)
            klines[etf.code] = klines_data

        # 生成模拟信号（简化版，实际应根据策略参数计算）
        signals = []
        current_date = data.start_date
        end_date_obj = data.end_date

        # 每5天生成一个信号作为示例
        while current_date <= end_date_obj:
            for etf in etf_pool[:strategy.hold_count]:
                if etf.code in klines and klines[etf.code]['close']:
                    signals.append({
                        'date': current_date,
                        'action': 'buy',
                        'etf_code': etf.code,
                        'etf_name': etf.name,
                        'price': klines[etf.code]['close'][-1]
                    })
            current_date = current_date + timedelta(days=5)

        # 运行回测
        result = engine.run(klines, signals)

        # 保存回测结果
        backtest_record = await RotationBacktest.create(
            strategy_id=id,
            start_date=data.start_date,
            end_date=data.end_date,
            initial_capital=data.initial_capital,
            final_capital=result.final_capital,
            total_return=result.total_return,
            annual_return=result.annual_return,
            max_drawdown=result.max_drawdown,
            win_rate=result.win_rate,
            trade_count=result.trade_count,
            sharpe_ratio=result.sharpe_ratio,
            calmar_ratio=result.calmar_ratio
        )

        return success_response({
            "backtest_id": backtest_record.id,
            "status": "completed",
            "result": {
                "initial_capital": data.initial_capital,
                "final_capital": result.final_capital,
                "total_return": result.total_return,
                "annual_return": result.annual_return,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "trade_count": result.trade_count,
                "sharpe_ratio": result.sharpe_ratio,
                "calmar_ratio": result.calmar_ratio
            },
            "equity_curve": engine.get_equity_curve_data(),
            "trades": engine.get_trade_records()
        })

    except Exception as e:
        logger.error(f"回测失败: {e}")
        return error_response(f"回测失败: {str(e)}")