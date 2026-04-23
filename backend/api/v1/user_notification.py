"""
用户通知API接口

提供用户通知的统计、最近通知等接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta

from core.response import success_response, error_response
from models.user_notification import UserNotification, UserNotificationType
from services.user_notification_service import user_notification_service

router = APIRouter(prefix="/api/v1/user-notification", tags=["用户通知"])


# ==================== Schemas ====================

class UserNotificationCreate(BaseModel):
    """创建用户通知"""
    type: str
    title: str
    content: str
    related_id: Optional[int] = None
    related_type: Optional[str] = None


class UserNotificationUpdate(BaseModel):
    """更新用户通知"""
    is_read: Optional[bool] = None


# ==================== 统计接口 ====================

@router.get("/stats")
async def get_user_notification_stats(
    days: int = Query(3, ge=1, le=30, description="统计天数"),
    user_id: int = Query(1, description="用户ID")
):
    """获取用户通知统计"""
    start_date = datetime.now() - timedelta(days=days)

    # 按类型统计总数
    from tortoise.functions import Count

    type_stats = await UserNotification.filter(
        user_id=user_id,
        created_at__gte=start_date
    ).group_by("type").annotate(count=Count("id"))

    # 按类型统计未读数
    unread_stats = await UserNotification.filter(
        user_id=user_id,
        is_read=False
    ).group_by("type").annotate(count=Count("id"))

    # 构建返回数据
    stats = {"system": 0, "trade": 0, "market": 0, "strategy": 0}
    unread = {"system": 0, "trade": 0, "market": 0, "strategy": 0}

    for s in type_stats:
        stats[s["type"]] = s["count"]

    for s in unread_stats:
        unread[s["type"]] = s["count"]

    return success_response({
        "stats": stats,
        "unread": unread,
        "total": sum(stats.values()),
        "unread_total": sum(unread.values()),
        "days": days
    })


@router.get("/unread-count")
async def get_user_unread_count(
    user_id: int = Query(1, description="用户ID")
):
    """获取用户未读通知数量"""
    from tortoise.functions import Count

    total_unread = await UserNotification.filter(
        user_id=user_id,
        is_read=False
    ).count()

    unread_by_type = await UserNotification.filter(
        user_id=user_id,
        is_read=False
    ).group_by("type").annotate(count=Count("id"))

    unread = {"system": 0, "trade": 0, "market": 0, "strategy": 0}
    for s in unread_by_type:
        unread[s["type"]] = s["count"]

    return success_response({
        "total": total_unread,
        "unread": unread
    })


# ==================== 最近通知接口 ====================

@router.get("/recent")
async def get_recent_notifications(
    limit: int = Query(3, ge=1, le=20, description="返回数量限制"),
    user_id: int = Query(1, description="用户ID")
):
    """获取最近通知"""
    notifications = await UserNotification.filter(
        user_id=user_id
    ).order_by("-created_at").limit(limit)

    return success_response([{
        "id": n.id,
        "type": n.type,
        "title": n.title,
        "content": n.content,
        "is_read": n.is_read,
        "related_id": n.related_id,
        "related_type": n.related_type,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "read_at": n.read_at.isoformat() if n.read_at else None
    } for n in notifications])


# ==================== 通知列表接口 ====================

@router.get("/list")
async def get_user_notifications(
    type: Optional[str] = Query(None, description="通知类型筛选"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    user_id: int = Query(1, description="用户ID")
):
    """获取用户通知列表"""
    query = UserNotification.filter(user_id=user_id)

    if type:
        query = query.filter(type=type)
    if is_read is not None:
        query = query.filter(is_read=is_read)

    notifications = await query.order_by("-created_at").offset(offset).limit(limit)

    # 获取总数
    total_query = UserNotification.filter(user_id=user_id)
    if type:
        total_query = total_query.filter(type=type)
    if is_read is not None:
        total_query = total_query.filter(is_read=is_read)
    total = await total_query.count()

    return success_response({
        "items": [{
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "is_read": n.is_read,
            "related_id": n.related_id,
            "related_type": n.related_type,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "read_at": n.read_at.isoformat() if n.read_at else None
        } for n in notifications],
        "total": total,
        "offset": offset,
        "limit": limit
    })


# ==================== 通知详情接口 ====================

@router.get("/{notification_id}")
async def get_notification_detail(notification_id: int, user_id: int = Query(1, description="用户ID")):
    """获取通知详情"""
    notification = await UserNotification.get_or_none(id=notification_id, user_id=user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    return success_response({
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "content": notification.content,
        "is_read": notification.is_read,
        "related_id": notification.related_id,
        "related_type": notification.related_type,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "read_at": notification.read_at.isoformat() if notification.read_at else None
    })


# ==================== 操作接口 ====================

@router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: int, user_id: int = Query(1, description="用户ID")):
    """标记通知为已读"""
    notification = await UserNotification.get_or_none(id=notification_id, user_id=user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    notification.is_read = True
    notification.read_at = datetime.now()
    await notification.save()

    return success_response(message="已标记为已读")


@router.put("/read-all")
async def mark_all_notifications_read(
    type: Optional[str] = Query(None, description="通知类型（可选，不传则标记全部）"),
    user_id: int = Query(1, description="用户ID")
):
    """批量标记通知为已读"""
    query = UserNotification.filter(user_id=user_id, is_read=False)
    if type:
        query = query.filter(type=type)

    updated_count = await query.update(is_read=True, read_at=datetime.now())

    return success_response({"updated_count": updated_count}, message=f"已标记 {updated_count} 条通知为已读")


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, user_id: int = Query(1, description="用户ID")):
    """删除通知"""
    notification = await UserNotification.get_or_none(id=notification_id, user_id=user_id)
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    await notification.delete()
    return success_response(message="删除成功")


# ==================== 创建通知接口（内部使用） ====================

@router.post("/")
async def create_user_notification(data: UserNotificationCreate, user_id: int = Query(1, description="用户ID")):
    """创建用户通知（供系统内部调用）"""
    # 验证类型
    valid_types = [t.value for t in UserNotificationType]
    if data.type not in valid_types:
        raise HTTPException(status_code=400, detail=f"无效的通知类型: {data.type}")

    notification = await UserNotification.create(
        user_id=user_id,
        type=data.type,
        title=data.title,
        content=data.content,
        related_id=data.related_id,
        related_type=data.related_type
    )

    return success_response({"id": notification.id}, message="创建成功")