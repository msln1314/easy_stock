"""
策略管理API路由
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from core.response import success_response, error_response
from schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyStatusUpdate,
    StrategyResponse, PaginatedResponse, StrategyStatsResponse
)
from services.strategy import StrategyService

router = APIRouter(prefix="/api/v1/strategies", tags=["策略管理"])
service = StrategyService()


@router.get("", response_model=None)
async def get_strategies(
    execute_mode: Optional[str] = Query(None, description="执行模式筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数")
):
    """获取策略列表"""
    result = await service.get_strategies(
        execute_mode=execute_mode,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return success_response(result.dict())


@router.get("/stats", response_model=None)
async def get_stats():
    """获取策略统计信息"""
    result = await service.get_stats()
    return success_response(result.dict())


@router.get("/{strategy_id}", response_model=None)
async def get_strategy_detail(strategy_id: int):
    """获取策略详情"""
    result = await service.get_strategy_detail(strategy_id)
    if not result:
        return error_response("策略不存在", 404)
    return success_response(result.dict())


@router.post("", response_model=None)
async def create_strategy(data: StrategyCreate):
    """创建策略"""
    # 验证执行模式和状态
    valid_modes = ["auto", "alert", "simulate"]
    valid_statuses = ["running", "paused", "stopped"]

    if data.execute_mode not in valid_modes:
        return error_response(f"无效的执行模式: {data.execute_mode}")
    if data.status not in valid_statuses:
        return error_response(f"无效的状态: {data.status}")

    strategy = await service.create_strategy(data)
    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "status": strategy.status,
        "created_at": strategy.created_at.isoformat()
    })


@router.put("/{strategy_id}", response_model=None)
async def update_strategy(strategy_id: int, data: StrategyUpdate):
    """更新策略"""
    strategy = await service.update_strategy(strategy_id, data)
    if not strategy:
        return error_response("策略不存在", 404)
    return success_response({
        "id": strategy.id,
        "name": strategy.name,
        "status": strategy.status,
        "updated_at": strategy.updated_at.isoformat()
    })


@router.delete("/{strategy_id}", response_model=None)
async def delete_strategy(strategy_id: int):
    """删除策略"""
    success = await service.delete_strategy(strategy_id)
    if not success:
        return error_response("策略不存在", 404)
    return success_response(message="删除成功")


@router.put("/{strategy_id}/status", response_model=None)
async def update_strategy_status(strategy_id: int, data: StrategyStatusUpdate):
    """更新策略状态"""
    valid_statuses = ["running", "paused", "stopped"]
    if data.status not in valid_statuses:
        return error_response(f"无效的状态: {data.status}")

    strategy = await service.update_status(strategy_id, data.status)
    if not strategy:
        return error_response("策略不存在", 404)
    return success_response({
        "id": strategy.id,
        "status": strategy.status,
        "updated_at": strategy.updated_at.isoformat()
    })