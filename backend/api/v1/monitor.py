"""
监控股票池API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.response import success_response, error_response
from models.monitor_pool import MonitorStock
from jobs.warning_detector import detect_single_stock

router = APIRouter(prefix="/api/monitor", tags=["监控股票池管理"])


# ==================== Schemas ====================

class MonitorStockCreate(BaseModel):
    """添加监控股票"""
    stock_code: str
    stock_name: Optional[str] = None
    monitor_type: str = "hold"
    conditions: Optional[List[str]] = None
    entry_price: Optional[float] = None
    remark: Optional[str] = None


class MonitorStockUpdate(BaseModel):
    """更新监控股票"""
    stock_name: Optional[str] = None
    monitor_type: Optional[str] = None
    conditions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    entry_price: Optional[float] = None
    remark: Optional[str] = None


class BatchAddStocks(BaseModel):
    """批量添加监控股票"""
    stocks: List[MonitorStockCreate]


# ==================== 监控股票接口 ====================

@router.get("/stocks")
async def get_monitor_stocks(
    monitor_type: Optional[str] = Query(None, description="监控类型筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用")
):
    """获取监控股票列表"""
    query = MonitorStock.all()

    if monitor_type:
        query = query.filter(monitor_type=monitor_type)
    if is_active is not None:
        query = query.filter(is_active=is_active)

    stocks = await query.order_by("-created_at")

    return success_response([{
        "id": s.id,
        "stock_code": s.stock_code,
        "stock_name": s.stock_name,
        "monitor_type": s.monitor_type,
        "conditions": s.conditions or [],
        "is_active": s.is_active,
        "entry_price": float(s.entry_price) if s.entry_price else None,
        "last_check_time": s.last_check_time.isoformat() if s.last_check_time else None,
        "last_price": float(s.last_price) if s.last_price else None,
        "change_percent": float(s.change_percent) if s.change_percent else None,
        "remark": s.remark,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in stocks])


@router.post("/stocks")
async def add_monitor_stock(data: MonitorStockCreate):
    """添加监控股票"""
    # 检查是否已存在
    existing = await MonitorStock.get_or_none(stock_code=data.stock_code)
    if existing:
        raise HTTPException(status_code=400, detail="该股票已在监控池中")

    stock = await MonitorStock.create(
        stock_code=data.stock_code,
        stock_name=data.stock_name,
        monitor_type=data.monitor_type,
        conditions=data.conditions,
        entry_price=data.entry_price,
        remark=data.remark
    )

    return success_response({"id": stock.id}, message="添加成功")


@router.post("/stocks/batch")
async def batch_add_stocks(data: BatchAddStocks):
    """批量添加监控股票"""
    added = 0
    skipped = 0

    for stock_data in data.stocks:
        existing = await MonitorStock.get_or_none(stock_code=stock_data.stock_code)
        if existing:
            skipped += 1
            continue

        await MonitorStock.create(
            stock_code=stock_data.stock_code,
            stock_name=stock_data.stock_name,
            monitor_type=stock_data.monitor_type,
            conditions=stock_data.conditions,
            remark=stock_data.remark
        )
        added += 1

    return success_response({
        "added": added,
        "skipped": skipped
    }, message=f"成功添加 {added} 只股票，跳过 {skipped} 只已存在的股票")


@router.put("/stocks/{stock_id}")
async def update_monitor_stock(stock_id: int, data: MonitorStockUpdate):
    """更新监控股票"""
    stock = await MonitorStock.get_or_none(id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="监控股票不存在")

    if data.stock_name is not None:
        stock.stock_name = data.stock_name
    if data.monitor_type is not None:
        stock.monitor_type = data.monitor_type
    if data.conditions is not None:
        stock.conditions = data.conditions
    if data.is_active is not None:
        stock.is_active = data.is_active
    if data.entry_price is not None:
        stock.entry_price = data.entry_price
    if data.remark is not None:
        stock.remark = data.remark

    await stock.save()
    return success_response(message="更新成功")


@router.delete("/stocks/{stock_id}")
async def delete_monitor_stock(stock_id: int):
    """删除监控股票"""
    stock = await MonitorStock.get_or_none(id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="监控股票不存在")

    await stock.delete()
    return success_response(message="删除成功")


@router.post("/stocks/{stock_id}/check")
async def check_single_stock(stock_id: int):
    """手动检测单只股票"""
    stock = await MonitorStock.get_or_none(id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="监控股票不存在")

    result = await detect_single_stock(stock.stock_code)
    return success_response(result)


@router.post("/stocks/check-all")
async def check_all_stocks():
    """手动检测所有监控股票"""
    from jobs.warning_detector import detect_warnings
    result = await detect_warnings()
    return success_response(result)


@router.get("/conditions")
async def get_available_conditions():
    """获取可用的预警条件列表"""
    from models.warning import WarningCondition

    conditions = await WarningCondition.filter(is_enabled=True).all()
    return success_response([{
        "condition_key": c.condition_key,
        "condition_name": c.condition_name,
        "indicator_key": c.indicator_key,
        "period": c.period,
        "priority": c.priority,
        "description": c.description
    } for c in conditions])


@router.get("/stocks/search")
async def search_stocks(keyword: str = Query(..., min_length=1, description="搜索关键词")):
    """
    模糊搜索股票

    支持股票代码或名称模糊匹配
    """
    import json
    from pathlib import Path

    if not keyword or len(keyword.strip()) < 1:
        return success_response([])

    keyword = keyword.strip().upper()

    try:
        # 从本地文件读取股票列表
        stock_file = Path(__file__).parent.parent.parent / "data" / "stocks.json"
        if not stock_file.exists():
            return success_response([])

        with open(stock_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        stocks = data.get("stocks", [])
        results = []

        for stock in stocks:
            code = stock.get("code", "")
            name = stock.get("name", "")

            # 模糊匹配：代码或名称包含关键词
            if keyword in code.upper() or keyword in name.upper():
                results.append({
                    "stock_code": code,
                    "stock_name": name
                })

            if len(results) >= 20:  # 最多返回20条
                break

        return success_response(results)

    except Exception as e:
        # 搜索失败返回空列表
        return success_response([])