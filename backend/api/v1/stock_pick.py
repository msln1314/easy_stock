"""
选股策略API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, date, timedelta

from core.response import success_response, error_response
from models.stock_pick import StockPickStrategy, StrategyTrackPool, StrategyExecutionLog
from models.indicator_library import IndicatorLibrary, IndicatorCategory
from services.stock_screening import stock_screening_service

router = APIRouter(prefix="/api/v1/stock-pick", tags=["选股策略管理"])


# ==================== 指标库接口 ====================

@router.get("/indicators")
async def get_indicators(
    category: Optional[str] = Query(None, description="指标分类筛选"),
    search: Optional[str] = Query(None, description="搜索关键字")
):
    """获取指标库列表"""
    query = IndicatorLibrary.filter(is_enabled=True)

    if category:
        try:
            cat_enum = IndicatorCategory(category)
            query = query.filter(category=cat_enum)
        except ValueError:
            pass

    if search:
        query = query.filter(
            indicator_key__icontains=search
        ) | query.filter(
            indicator_name__icontains=search
        )

    indicators = await query.order_by("sort_order", "id")

    return success_response([{
        "id": i.id,
        "indicator_key": i.indicator_key,
        "indicator_name": i.indicator_name,
        "category": i.category,
        "description": i.description,
        "params": i.params,
        "output_fields": i.output_fields,
        "default_output": i.default_output,
        "usage_guide": i.usage_guide,
        "signal_interpretation": i.signal_interpretation,
    } for i in indicators])


@router.get("/indicators/{indicator_key}")
async def get_indicator_detail(indicator_key: str):
    """获取指标详情"""
    indicator = await IndicatorLibrary.get_or_none(indicator_key=indicator_key)
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")

    return success_response({
        "id": indicator.id,
        "indicator_key": indicator.indicator_key,
        "indicator_name": indicator.indicator_name,
        "category": indicator.category,
        "description": indicator.description,
        "params": indicator.params,
        "output_fields": indicator.output_fields,
        "default_output": indicator.default_output,
        "usage_guide": indicator.usage_guide,
        "signal_interpretation": indicator.signal_interpretation,
    })


# ==================== Schemas ====================

class StrategyCreate(BaseModel):
    """创建选股策略"""
    strategy_key: str
    strategy_name: str
    strategy_type: str = "technical"
    description: Optional[str] = None
    strategy_config: dict
    duration_days: int = 3
    generate_time: str = "09:00"
    advance_days: int = 1
    auto_generate: bool = True


class StrategyUpdate(BaseModel):
    """更新选股策略"""
    strategy_name: Optional[str] = None
    description: Optional[str] = None
    strategy_config: Optional[dict] = None
    duration_days: Optional[int] = None
    generate_time: Optional[str] = None
    advance_days: Optional[int] = None
    is_active: Optional[bool] = None
    auto_generate: Optional[bool] = None


class TrackRecordCreate(BaseModel):
    """创建追踪记录"""
    strategy_id: int
    stock_code: str
    stock_name: Optional[str] = None
    target_date: date
    pool_type: str = "today"
    anomaly_type: str
    confidence: float = 50.0
    anomaly_data: Optional[dict] = None
    confidence_reason: Optional[str] = None


class TrackRecordUpdate(BaseModel):
    """更新追踪记录"""
    status: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    max_return: Optional[float] = None
    actual_return: Optional[float] = None
    verify_note: Optional[str] = None


class ScreeningRequest(BaseModel):
    """选股请求"""
    strategy_config: dict
    stock_pool: Optional[List[str]] = None


# ==================== 选股策略接口 ====================

@router.get("/strategies")
async def get_strategies(
    strategy_type: Optional[str] = Query(None, description="策略类型筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用")
):
    """获取选股策略列表"""
    query = StockPickStrategy.all()

    if strategy_type:
        query = query.filter(strategy_type=strategy_type)
    if is_active is not None:
        query = query.filter(is_active=is_active)

    strategies = await query.order_by("-created_at")

    return success_response([{
        "id": s.id,
        "strategy_key": s.strategy_key,
        "strategy_name": s.strategy_name,
        "strategy_type": s.strategy_type,
        "strategy_type_display": s.strategy_type_display,
        "description": s.description,
        "strategy_config": s.strategy_config,
        "duration_days": s.duration_days,
        "generate_time": s.generate_time,
        "advance_days": s.advance_days,
        "is_active": s.is_active,
        "auto_generate": s.auto_generate,
        "total_generated": s.total_generated,
        "success_rate": float(s.success_rate) if s.success_rate else None,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in strategies])


@router.post("/strategies")
async def create_strategy(data: StrategyCreate):
    """创建选股策略"""
    existing = await StockPickStrategy.get_or_none(strategy_key=data.strategy_key)
    if existing:
        raise HTTPException(status_code=400, detail="策略KEY已存在")

    strategy = await StockPickStrategy.create(**data.dict())
    return success_response({"id": strategy.id}, message="创建成功")


@router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: int, data: StrategyUpdate):
    """更新选股策略"""
    strategy = await StockPickStrategy.get_or_none(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(strategy, key, value)

    await strategy.save()
    return success_response(message="更新成功")


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int):
    """删除选股策略"""
    strategy = await StockPickStrategy.get_or_none(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    await strategy.delete()
    return success_response(message="删除成功")


@router.post("/strategies/{strategy_id}/execute")
async def execute_strategy(strategy_id: int, background_tasks: BackgroundTasks):
    """手动执行策略生成股票池"""
    strategy = await StockPickStrategy.get_or_none(id=strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    if not strategy.is_active:
        raise HTTPException(status_code=400, detail="策略未启用")

    # 执行选股
    result = await stock_screening_service.execute_strategy(strategy, save_results=True)

    return success_response({
        "strategy_id": strategy_id,
        "strategy_name": strategy.strategy_name,
        "stocks_found": result["stocks_found"],
        "stocks": result["stocks"],
        "message": f"筛选完成，找到 {result['stocks_found']} 只股票"
    })


@router.post("/screening")
async def quick_screening(data: ScreeningRequest):
    """
    快速选股接口

    用于测试策略配置，不保存结果
    """
    results = await stock_screening_service.screen_stocks(
        strategy_config=data.strategy_config,
        stock_pool=data.stock_pool
    )

    return success_response({
        "total": len(results),
        "stocks": results[:100],  # 只返回前100条
    })


# ==================== 追踪异动池接口 ====================

@router.get("/track-pool")
async def get_track_pool(
    strategy_id: Optional[int] = Query(None, description="策略ID筛选"),
    pool_type: Optional[str] = Query(None, description="股池类型: today/tomorrow"),
    status: Optional[str] = Query(None, description="状态筛选"),
    target_date: Optional[date] = Query(None, description="目标日期筛选"),
    limit: int = Query(100, description="返回数量")
):
    """获取策略追踪异动池"""
    query = StrategyTrackPool.all()

    if strategy_id:
        query = query.filter(strategy_id=strategy_id)
    if pool_type:
        query = query.filter(pool_type=pool_type)
    if status:
        query = query.filter(status=status)
    if target_date:
        query = query.filter(target_date=target_date)

    records = await query.order_by("-created_at").limit(limit)

    return success_response([{
        "id": r.id,
        "strategy_id": r.strategy_id,
        "strategy_key": r.strategy_key,
        "stock_code": r.stock_code,
        "stock_name": r.stock_name,
        "generate_date": r.generate_date.isoformat() if r.generate_date else None,
        "target_date": r.target_date.isoformat() if r.target_date else None,
        "pool_type": r.pool_type,
        "anomaly_type": r.anomaly_type,
        "anomaly_type_display": r.anomaly_type_display,
        "duration_days": r.duration_days,
        "effective_time": r.effective_time.isoformat() if r.effective_time else None,
        "expire_time": r.expire_time.isoformat() if r.expire_time else None,
        "confidence": float(r.confidence) if r.confidence else None,
        "confidence_reason": r.confidence_reason,
        "status": r.status,
        "status_display": r.status_display,
        "entry_price": float(r.entry_price) if r.entry_price else None,
        "exit_price": float(r.exit_price) if r.exit_price else None,
        "max_return": float(r.max_return) if r.max_return else None,
        "actual_return": float(r.actual_return) if r.actual_return else None,
        "is_active": r.is_active,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in records])


@router.get("/track-pool/today")
async def get_today_pool():
    """获取今日股池"""
    from core.qmt_client import qmt_client

    today = date.today()
    records = await StrategyTrackPool.filter(
        target_date=today,
        status__in=["pending", "verified"]
    ).order_by("-confidence")

    # 获取实时行情
    result = []
    for r in records:
        item = {
            "id": r.id,
            "strategy_key": r.strategy_key,
            "stock_code": r.stock_code,
            "stock_name": r.stock_name,
            "anomaly_type": r.anomaly_type,
            "anomaly_type_display": r.anomaly_type_display,
            "confidence": float(r.confidence) if r.confidence else None,
            "status": r.status,
            "status_display": r.status_display,
            "entry_price": float(r.entry_price) if r.entry_price else None,
            "pool_type": r.pool_type,
            # 新增行情字段
            "current_price": None,
            "change_percent": None,
            "turnover_rate": None,
            "volume_ratio": None,
        }

        # 获取实时行情
        try:
            stock_code = r.stock_code
            if '.' not in stock_code:
                if stock_code.startswith('6'):
                    stock_code = f"{stock_code}.SH"
                else:
                    stock_code = f"{stock_code}.SZ"

            quote = await qmt_client.get_stock_quote(stock_code)
            if quote:
                item["current_price"] = quote.get("lastPrice", 0)
                item["change_percent"] = quote.get("changePercent", 0)
                # 换手率和量比需要额外计算或从tick获取
                tick_data = quote
                if tick_data.get("volume") and tick_data.get("amount"):
                    # 量比简化计算
                    item["volume_ratio"] = tick_data.get("volume", 0) / max(tick_data.get("avgVolume", 1), 1)
        except Exception:
            pass

        result.append(item)

    return success_response(result)


@router.get("/track-pool/tomorrow")
async def get_tomorrow_pool():
    """获取明日股池"""
    tomorrow = date.today() + timedelta(days=1)
    records = await StrategyTrackPool.filter(
        target_date=tomorrow,
        status="pending"
    ).order_by("-confidence")

    return success_response([{
        "id": r.id,
        "strategy_key": r.strategy_key,
        "stock_code": r.stock_code,
        "stock_name": r.stock_name,
        "anomaly_type": r.anomaly_type,
        "anomaly_type_display": r.anomaly_type_display,
        "confidence": float(r.confidence) if r.confidence else None,
        "generate_date": r.generate_date.isoformat() if r.generate_date else None
    } for r in records])


@router.post("/track-pool")
async def create_track_record(data: TrackRecordCreate):
    """创建追踪记录"""
    strategy = await StockPickStrategy.get_or_none(id=data.strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    record = await StrategyTrackPool.create_track_record(
        strategy=strategy,
        stock_code=data.stock_code,
        stock_name=data.stock_name or "",
        target_date=data.target_date,
        pool_type=data.pool_type,
        anomaly_type=data.anomaly_type,
        confidence=data.confidence,
        anomaly_data=data.anomaly_data,
        confidence_reason=data.confidence_reason
    )

    # 更新策略统计
    strategy.total_generated += 1
    await strategy.save()

    return success_response({"id": record.id}, message="创建成功")


@router.post("/track-pool/batch")
async def batch_create_track_records(records: List[TrackRecordCreate]):
    """批量创建追踪记录"""
    created = 0
    for record_data in records:
        try:
            strategy = await StockPickStrategy.get_or_none(id=record_data.strategy_id)
            if not strategy:
                continue

            await StrategyTrackPool.create_track_record(
                strategy=strategy,
                stock_code=record_data.stock_code,
                stock_name=record_data.stock_name or "",
                target_date=record_data.target_date,
                pool_type=record_data.pool_type,
                anomaly_type=record_data.anomaly_type,
                confidence=record_data.confidence,
                anomaly_data=record_data.anomaly_data,
                confidence_reason=record_data.confidence_reason
            )

            strategy.total_generated += 1
            await strategy.save()
            created += 1
        except Exception:
            continue

    return success_response({"created": created}, message=f"成功创建 {created} 条记录")


@router.put("/track-pool/{record_id}")
async def update_track_record(record_id: int, data: TrackRecordUpdate):
    """更新追踪记录"""
    record = await StrategyTrackPool.get_or_none(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    if data.status == "verified" and not record.verified_at:
        record.verified_at = datetime.now()

    await record.save()
    return success_response(message="更新成功")


@router.delete("/track-pool/{record_id}")
async def delete_track_record(record_id: int):
    """删除追踪记录"""
    record = await StrategyTrackPool.get_or_none(id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await record.delete()
    return success_response(message="删除成功")


# ==================== 执行日志接口 ====================

@router.get("/execution-logs")
async def get_execution_logs(
    strategy_id: Optional[int] = Query(None, description="策略ID筛选"),
    limit: int = Query(50, description="返回数量")
):
    """获取策略执行日志"""
    query = StrategyExecutionLog.all()

    if strategy_id:
        query = query.filter(strategy_id=strategy_id)

    logs = await query.order_by("-created_at").limit(limit)

    return success_response([{
        "id": l.id,
        "strategy_id": l.strategy_id,
        "strategy_key": l.strategy_key,
        "execution_date": l.execution_date.isoformat() if l.execution_date else None,
        "pool_type": l.pool_type,
        "status": l.status,
        "stocks_found": l.stocks_found,
        "stocks_saved": l.stocks_saved,
        "error_message": l.error_message,
        "started_at": l.started_at.isoformat() if l.started_at else None,
        "finished_at": l.finished_at.isoformat() if l.finished_at else None,
        "created_at": l.created_at.isoformat() if l.created_at else None
    } for l in logs])