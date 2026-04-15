"""
ETF池管理API路由
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from core.response import success_response, error_response
from schemas.etf_pool import EtfPoolCreate, EtfPoolUpdate, EtfPoolResponse
from models.etf_pool import EtfPool

router = APIRouter(prefix="/api/v1/etf-pool", tags=["ETF池管理"])


@router.get("", response_model=None)
async def get_etf_pool_list(
    sector: Optional[str] = Query(None, description="行业板块筛选"),
    is_active: Optional[bool] = Query(None, description="启用状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """获取ETF池列表"""
    query = EtfPool.all()

    if sector:
        query = query.filter(sector=sector)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    if keyword:
        query = query.filter(name__icontains=keyword)

    etfs = await query.order_by("code").all()

    result = [
        {
            "id": etf.id,
            "name": etf.name,
            "code": etf.code,
            "sector": etf.sector,
            "is_active": etf.is_active,
            "created_at": etf.created_at.isoformat(),
            "updated_at": etf.updated_at.isoformat()
        }
        for etf in etfs
    ]

    return success_response(result)


@router.get("/{id}", response_model=None)
async def get_etf_detail(id: int):
    """获取ETF详情"""
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)

    return success_response({
        "id": etf.id,
        "name": etf.name,
        "code": etf.code,
        "sector": etf.sector,
        "is_active": etf.is_active,
        "created_at": etf.created_at.isoformat(),
        "updated_at": etf.updated_at.isoformat()
    })


@router.post("", response_model=None)
async def add_etf(data: EtfPoolCreate):
    """添加ETF到池中"""
    # 检查代码是否已存在
    existing = await EtfPool.filter(code=data.code).first()
    if existing:
        return error_response(f"ETF代码 {data.code} 已存在")

    etf = await EtfPool.create(**data.model_dump())

    return success_response({
        "id": etf.id,
        "name": etf.name,
        "code": etf.code,
        "sector": etf.sector,
        "is_active": etf.is_active,
        "created_at": etf.created_at.isoformat()
    })


@router.put("/{id}", response_model=None)
async def update_etf(id: int, data: EtfPoolUpdate):
    """更新ETF配置"""
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(etf, key, value)
        await etf.save()

    return success_response({
        "id": etf.id,
        "name": etf.name,
        "code": etf.code,
        "sector": etf.sector,
        "is_active": etf.is_active,
        "updated_at": etf.updated_at.isoformat()
    })


@router.delete("/{id}", response_model=None)
async def delete_etf(id: int):
    """从池中移除ETF"""
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)

    await etf.delete()
    return success_response(message="ETF已删除")


@router.put("/{id}/toggle", response_model=None)
async def toggle_etf_status(id: int):
    """切换ETF启用状态"""
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)

    etf.is_active = not etf.is_active
    await etf.save()

    return success_response({
        "id": etf.id,
        "is_active": etf.is_active,
        "updated_at": etf.updated_at.isoformat()
    })