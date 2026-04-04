"""
通知配置API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.response import success_response, error_response
from models.notification import NotificationChannel, NotificationLog, NotificationChannelType
from services.notification_service import notification_service

router = APIRouter(prefix="/api/notification", tags=["通知管理"])


# ==================== Schemas ====================

class ChannelConfig(BaseModel):
    """渠道配置基类"""
    pass


class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_server: str
    smtp_port: int = 465
    username: str
    password: str
    from_addr: str
    to_list: List[str]


class DingTalkConfig(BaseModel):
    """钉钉配置"""
    webhook_url: str
    secret: Optional[str] = None


class TelegramConfig(BaseModel):
    """Telegram配置"""
    bot_token: str
    chat_id: str


class WechatWorkConfig(BaseModel):
    """企业微信配置"""
    webhook_url: str


class WebhookConfig(BaseModel):
    """自定义Webhook配置"""
    url: str
    method: str = "POST"
    headers: Optional[dict] = None


class NotificationChannelCreate(BaseModel):
    """创建通知渠道"""
    channel_type: str
    channel_name: str
    config: dict
    warning_levels: Optional[List[str]] = ["critical", "warning"]
    monitor_types: Optional[List[str]] = ["hold"]
    rate_limit_minutes: Optional[int] = 5
    remark: Optional[str] = None


class NotificationChannelUpdate(BaseModel):
    """更新通知渠道"""
    channel_name: Optional[str] = None
    config: Optional[dict] = None
    is_enabled: Optional[bool] = None
    warning_levels: Optional[List[str]] = None
    monitor_types: Optional[List[str]] = None
    rate_limit_minutes: Optional[int] = None
    remark: Optional[str] = None


# ==================== 通知渠道接口 ====================

@router.get("/channels")
async def get_notification_channels(
    channel_type: Optional[str] = Query(None, description="渠道类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用")
):
    """获取通知渠道列表"""
    query = NotificationChannel.all()

    if channel_type:
        query = query.filter(channel_type=channel_type)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)

    channels = await query.order_by("-created_at")

    return success_response([{
        "id": c.id,
        "channel_type": c.channel_type,
        "channel_name": c.channel_name,
        "is_enabled": c.is_enabled,
        "config": c.config,
        "warning_levels": c.warning_levels,
        "monitor_types": c.monitor_types,
        "rate_limit_minutes": c.rate_limit_minutes,
        "last_sent_at": c.last_sent_at.isoformat() if c.last_sent_at else None,
        "remark": c.remark,
        "created_at": c.created_at.isoformat() if c.created_at else None
    } for c in channels])


@router.get("/channels/types")
async def get_channel_types():
    """获取可用的渠道类型列表"""
    types = [
        {"value": "dingtalk", "label": "钉钉机器人", "config_fields": ["webhook_url", "secret"]},
        {"value": "telegram", "label": "Telegram", "config_fields": ["bot_token", "chat_id"]},
        {"value": "wechat_work", "label": "企业微信", "config_fields": ["webhook_url"]},
        {"value": "webhook", "label": "自定义Webhook", "config_fields": ["url", "method", "headers"]},
        {"value": "email", "label": "邮件", "config_fields": ["smtp_server", "smtp_port", "username", "password", "from_addr", "to_list"]},
    ]
    return success_response(types)


@router.post("/channels")
async def create_notification_channel(data: NotificationChannelCreate):
    """创建通知渠道"""
    # 验证渠道类型
    valid_types = [t.value for t in NotificationChannelType]
    if data.channel_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"无效的渠道类型: {data.channel_type}")

    # 检查名称是否重复
    existing = await NotificationChannel.get_or_none(channel_name=data.channel_name)
    if existing:
        raise HTTPException(status_code=400, detail="渠道名称已存在")

    channel = await NotificationChannel.create(
        channel_type=data.channel_type,
        channel_name=data.channel_name,
        config=data.config,
        warning_levels=data.warning_levels,
        monitor_types=data.monitor_types,
        rate_limit_minutes=data.rate_limit_minutes,
        remark=data.remark
    )

    return success_response({"id": channel.id}, message="创建成功")


@router.put("/channels/{channel_id}")
async def update_notification_channel(channel_id: int, data: NotificationChannelUpdate):
    """更新通知渠道"""
    channel = await NotificationChannel.get_or_none(id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    if data.channel_name is not None:
        # 检查名称是否重复
        existing = await NotificationChannel.get_or_none(channel_name=data.channel_name)
        if existing and existing.id != channel_id:
            raise HTTPException(status_code=400, detail="渠道名称已存在")
        channel.channel_name = data.channel_name

    if data.config is not None:
        channel.config = data.config
    if data.is_enabled is not None:
        channel.is_enabled = data.is_enabled
    if data.warning_levels is not None:
        channel.warning_levels = data.warning_levels
    if data.monitor_types is not None:
        channel.monitor_types = data.monitor_types
    if data.rate_limit_minutes is not None:
        channel.rate_limit_minutes = data.rate_limit_minutes
    if data.remark is not None:
        channel.remark = data.remark

    await channel.save()
    return success_response(message="更新成功")


@router.delete("/channels/{channel_id}")
async def delete_notification_channel(channel_id: int):
    """删除通知渠道"""
    channel = await NotificationChannel.get_or_none(id=channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")

    await channel.delete()
    return success_response(message="删除成功")


@router.post("/channels/{channel_id}/test")
async def test_notification_channel(channel_id: int):
    """测试通知渠道"""
    result = await notification_service.send_test_notification(channel_id)

    if result["success"]:
        return success_response(message="测试通知发送成功")
    else:
        return error_response(message=f"测试通知发送失败: {result.get('error', '未知错误')}")


# ==================== 通知记录接口 ====================

@router.get("/logs")
async def get_notification_logs(
    stock_code: Optional[str] = Query(None, description="股票代码筛选"),
    warning_level: Optional[str] = Query(None, description="预警级别筛选"),
    channel_type: Optional[str] = Query(None, description="渠道类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    limit: int = Query(50, ge=1, le=200, description="返回数量限制")
):
    """获取通知记录列表"""
    query = NotificationLog.all()

    if stock_code:
        query = query.filter(stock_code=stock_code)
    if warning_level:
        query = query.filter(warning_level=warning_level)
    if channel_type:
        query = query.filter(channel_type=channel_type)
    if status:
        query = query.filter(status=status)

    logs = await query.order_by("-created_at").limit(limit)

    return success_response([{
        "id": log.id,
        "warning_id": log.warning_id,
        "stock_code": log.stock_code,
        "stock_name": log.stock_name,
        "title": log.title,
        "content": log.content,
        "warning_level": log.warning_level,
        "condition_name": log.condition_name,
        "channel_id": log.channel_id,
        "channel_type": log.channel_type,
        "channel_name": log.channel_name,
        "status": log.status,
        "error_message": log.error_message,
        "sent_at": log.sent_at.isoformat() if log.sent_at else None,
        "created_at": log.created_at.isoformat() if log.created_at else None
    } for log in logs])


@router.get("/logs/stats")
async def get_notification_stats(
    days: int = Query(7, ge=1, le=30, description="统计天数")
):
    """获取通知统计"""
    from datetime import timedelta
    from tortoise.functions import Count

    start_date = datetime.now() - timedelta(days=days)

    # 按渠道统计
    channel_stats = await NotificationLog.filter(
        created_at__gte=start_date
    ).group_by("channel_type").annotate(count=Count("id"))

    # 按状态统计
    status_stats = await NotificationLog.filter(
        created_at__gte=start_date
    ).group_by("status").annotate(count=Count("id"))

    # 按预警级别统计
    level_stats = await NotificationLog.filter(
        created_at__gte=start_date
    ).group_by("warning_level").annotate(count=Count("id"))

    return success_response({
        "channel_stats": [{"channel_type": s["channel_type"], "count": s["count"]} for s in channel_stats],
        "status_stats": [{"status": s["status"], "count": s["count"]} for s in status_stats],
        "level_stats": [{"warning_level": s["warning_level"], "count": s["count"]} for s in level_stats],
        "days": days
    })


@router.delete("/logs")
async def clear_notification_logs(
    days: int = Query(30, ge=7, le=90, description="清理超过N天的记录")
):
    """清理旧通知记录"""
    from datetime import timedelta

    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = await NotificationLog.filter(created_at__lt=cutoff_date).delete()

    return success_response({"deleted_count": deleted_count}, message=f"已清理 {deleted_count} 条记录")