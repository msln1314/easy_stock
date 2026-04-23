"""
仪表盘布局API

管理用户的仪表盘布局配置
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models.dashboard_layout import DashboardLayout
from models.user import User
from core.auth import get_current_user_required
from core.response import success_response

router = APIRouter(prefix="/api/v1/dashboard", tags=["仪表盘布局"])


# ==================== 类型定义 ====================

class GridLayoutItem(BaseModel):
    """Grid布局项"""
    i: str
    x: int
    y: int
    w: int
    h: int
    minW: Optional[int] = None
    minH: Optional[int] = None
    static: Optional[bool] = False


class LayoutCreate(BaseModel):
    """创建布局请求"""
    name: str
    layout: List[GridLayoutItem]
    is_default: bool = False


class LayoutUpdate(BaseModel):
    """更新布局请求"""
    name: Optional[str] = None
    layout: Optional[List[GridLayoutItem]] = None
    is_default: Optional[bool] = None


class LayoutResponse(BaseModel):
    """布局响应"""
    id: int
    name: str
    user_id: int
    layout: List[GridLayoutItem]
    is_default: bool
    created_at: datetime
    updated_at: datetime


# ==================== 默认布局 ====================

DEFAULT_LAYOUT = [
    {"i": "market-overview", "x": 0, "y": 0, "w": 12, "h": 2, "minW": 8, "minH": 2},
    {"i": "positions", "x": 0, "y": 2, "w": 4, "h": 4, "minW": 3, "minH": 3},
    {"i": "ai-assistant", "x": 4, "y": 2, "w": 4, "h": 4, "minW": 3, "minH": 4},
    {"i": "sell-warning", "x": 8, "y": 2, "w": 4, "h": 4, "minW": 3, "minH": 3},
    {"i": "trade-records", "x": 0, "y": 6, "w": 6, "h": 4, "minW": 3, "minH": 3},
    {"i": "selection-pool", "x": 6, "y": 6, "w": 6, "h": 4, "minW": 3, "minH": 3},
]


# ==================== API接口 ====================

@router.get("/layouts", summary="获取用户所有布局")
async def get_layouts(user: User = Depends(get_current_user_required)):
    """获取当前用户的所有仪表盘布局"""
    layouts = await DashboardLayout.filter(user_id=user.id).order_by("-is_default", "-updated_at")
    data = [
        {
            "id": l.id,
            "name": l.name,
            "user_id": l.user_id,
            "layout": l.layout_json,
            "is_default": l.is_default,
            "created_at": l.created_at.isoformat(),
            "updated_at": l.updated_at.isoformat()
        }
        for l in layouts
    ]
    return success_response(data)


@router.get("/layout/default", summary="获取默认布局")
async def get_default_layout(user: User = Depends(get_current_user_required)):
    """获取用户的默认布局，如果没有则返回系统默认布局"""
    layout = await DashboardLayout.get_or_none(user_id=user.id, is_default=True)

    if layout:
        data = {
            "id": layout.id,
            "name": layout.name,
            "user_id": layout.user_id,
            "layout": layout.layout_json,
            "is_default": layout.is_default,
            "created_at": layout.created_at.isoformat(),
            "updated_at": layout.updated_at.isoformat()
        }
        return success_response(data)

    # 返回系统默认布局
    data = {
        "id": 0,
        "name": "默认布局",
        "user_id": user.id,
        "layout": DEFAULT_LAYOUT,
        "is_default": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return success_response(data)


@router.get("/layout/{layout_id}", summary="获取指定布局")
async def get_layout(layout_id: int, user: User = Depends(get_current_user_required)):
    """获取指定的布局详情"""
    layout = await DashboardLayout.get_or_none(id=layout_id, user_id=user.id)

    if not layout:
        raise HTTPException(status_code=404, detail="布局不存在")

    data = {
        "id": layout.id,
        "name": layout.name,
        "user_id": layout.user_id,
        "layout": layout.layout_json,
        "is_default": layout.is_default,
        "created_at": layout.created_at.isoformat(),
        "updated_at": layout.updated_at.isoformat()
    }
    return success_response(data)


@router.post("/layout", summary="创建新布局")
async def create_layout(request: LayoutCreate, user: User = Depends(get_current_user_required)):
    """创建新的仪表盘布局"""
    # 检查名称是否重复
    existing = await DashboardLayout.get_or_none(user_id=user.id, name=request.name)
    if existing:
        raise HTTPException(status_code=400, detail="布局名称已存在")

    # 如果设置为默认，先取消其他默认布局
    if request.is_default:
        await DashboardLayout.filter(user_id=user.id, is_default=True).update(is_default=False)

    layout = await DashboardLayout.create(
        name=request.name,
        user_id=user.id,
        layout_json=[item.model_dump() for item in request.layout],
        is_default=request.is_default
    )

    data = {
        "id": layout.id,
        "name": layout.name,
        "user_id": layout.user_id,
        "layout": layout.layout_json,
        "is_default": layout.is_default,
        "created_at": layout.created_at.isoformat(),
        "updated_at": layout.updated_at.isoformat()
    }
    return success_response(data)


@router.put("/layout/{layout_id}", summary="更新布局")
async def update_layout(layout_id: int, request: LayoutUpdate, user: User = Depends(get_current_user_required)):
    """更新指定的布局"""
    layout = await DashboardLayout.get_or_none(id=layout_id, user_id=user.id)

    if not layout:
        raise HTTPException(status_code=404, detail="布局不存在")

    # 更新名称时检查重复
    if request.name and request.name != layout.name:
        existing = await DashboardLayout.get_or_none(user_id=user.id, name=request.name)
        if existing:
            raise HTTPException(status_code=400, detail="布局名称已存在")
        layout.name = request.name

    # 更新布局数据
    if request.layout:
        layout.layout_json = [item.model_dump() for item in request.layout]

    # 更新默认状态
    if request.is_default is not None:
        if request.is_default:
            await DashboardLayout.filter(user_id=user.id, is_default=True).update(is_default=False)
        layout.is_default = request.is_default

    await layout.save()

    data = {
        "id": layout.id,
        "name": layout.name,
        "user_id": layout.user_id,
        "layout": layout.layout_json,
        "is_default": layout.is_default,
        "created_at": layout.created_at.isoformat(),
        "updated_at": layout.updated_at.isoformat()
    }
    return success_response(data)


@router.delete("/layout/{layout_id}", summary="删除布局")
async def delete_layout(layout_id: int, user: User = Depends(get_current_user_required)):
    """删除指定的布局"""
    layout = await DashboardLayout.get_or_none(id=layout_id, user_id=user.id)

    if not layout:
        raise HTTPException(status_code=404, detail="布局不存在")

    await layout.delete()
    return success_response({"message": "布局已删除"})


@router.post("/layout/{layout_id}/set-default", summary="设为默认布局")
async def set_default_layout(layout_id: int, user: User = Depends(get_current_user_required)):
    """将指定布局设为默认"""
    layout = await DashboardLayout.get_or_none(id=layout_id, user_id=user.id)

    if not layout:
        raise HTTPException(status_code=404, detail="布局不存在")

    # 取消其他默认布局
    await DashboardLayout.filter(user_id=user.id, is_default=True).update(is_default=False)

    # 设置当前布局为默认
    layout.is_default = True
    await layout.save()

    data = {
        "id": layout.id,
        "name": layout.name,
        "user_id": layout.user_id,
        "layout": layout.layout_json,
        "is_default": layout.is_default,
        "created_at": layout.created_at.isoformat(),
        "updated_at": layout.updated_at.isoformat()
    }
    return success_response(data)