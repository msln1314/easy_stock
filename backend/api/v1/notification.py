"""
通知配置API接口
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.response import success_response, error_response
from models.notification import NotificationChannel, NotificationLog, NotificationChannelType, NotificationTemplate, NotificationRecipient, NotificationRecipientGroup
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


# ==================== 通知模板接口 ====================

class NotificationTemplateCreate(BaseModel):
    """创建通知模板"""
    template_key: str
    template_name: str
    template_type: str = "warning"
    title_template: str
    content_template: str
    warning_levels: Optional[List[str]] = None
    is_enabled: bool = True
    is_default: bool = False
    remark: Optional[str] = None


class NotificationTemplateUpdate(BaseModel):
    """更新通知模板"""
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    title_template: Optional[str] = None
    content_template: Optional[str] = None
    warning_levels: Optional[List[str]] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    remark: Optional[str] = None


@router.get("/templates")
async def get_notification_templates(
    template_type: Optional[str] = Query(None, description="模板类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用")
):
    """获取通知模板列表"""
    query = NotificationTemplate.all()

    if template_type:
        query = query.filter(template_type=template_type)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)

    templates = await query.order_by("-is_default", "-created_at")

    return success_response([{
        "id": t.id,
        "template_key": t.template_key,
        "template_name": t.template_name,
        "template_type": t.template_type,
        "title_template": t.title_template,
        "content_template": t.content_template,
        "warning_levels": t.warning_levels,
        "is_enabled": t.is_enabled,
        "is_default": t.is_default,
        "remark": t.remark,
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in templates])


@router.get("/templates/types")
async def get_template_types():
    """获取模板类型列表"""
    types = [
        {"value": "warning", "label": "预警通知"},
        {"value": "trade", "label": "交易通知"},
        {"value": "system", "label": "系统通知"},
    ]
    return success_response(types)


@router.get("/templates/variables")
async def get_template_variables():
    """获取模板可用变量列表"""
    variables = [
        {"name": "stock_code", "description": "股票代码"},
        {"name": "stock_name", "description": "股票名称"},
        {"name": "warning_level", "description": "预警级别"},
        {"name": "condition_name", "description": "预警条件名称"},
        {"name": "price", "description": "当前价格"},
        {"name": "change_percent", "description": "涨跌幅(%)"},
        {"name": "trigger_time", "description": "触发时间"},
        {"name": "trigger_value", "description": "触发指标值"},
        {"name": "monitor_type", "description": "监控类型"},
    ]
    return success_response(variables)


@router.post("/templates")
async def create_notification_template(data: NotificationTemplateCreate):
    """创建通知模板"""
    # 检查key是否重复
    existing = await NotificationTemplate.get_or_none(template_key=data.template_key)
    if existing:
        raise HTTPException(status_code=400, detail="模板标识已存在")

    # 如果设为默认，取消其他同类型模板的默认状态
    if data.is_default:
        await NotificationTemplate.filter(
            template_type=data.template_type,
            is_default=True
        ).update(is_default=False)

    template = await NotificationTemplate.create(
        template_key=data.template_key,
        template_name=data.template_name,
        template_type=data.template_type,
        title_template=data.title_template,
        content_template=data.content_template,
        warning_levels=data.warning_levels,
        is_enabled=data.is_enabled,
        is_default=data.is_default,
        remark=data.remark
    )

    return success_response({"id": template.id}, message="创建成功")


@router.put("/templates/{template_id}")
async def update_notification_template(template_id: int, data: NotificationTemplateUpdate):
    """更新通知模板"""
    template = await NotificationTemplate.get_or_none(id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    if data.is_default is not None and data.is_default:
        # 取消其他同类型模板的默认状态
        template_type = data.template_type or template.template_type
        await NotificationTemplate.filter(
            template_type=template_type,
            is_default=True
        ).exclude(id=template_id).update(is_default=False)

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    await template.save()
    return success_response(message="更新成功")


@router.delete("/templates/{template_id}")
async def delete_notification_template(template_id: int):
    """删除通知模板"""
    template = await NotificationTemplate.get_or_none(id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    await template.delete()
    return success_response(message="删除成功")


@router.post("/templates/{template_id}/set-default")
async def set_default_template(template_id: int):
    """设置默认模板"""
    template = await NotificationTemplate.get_or_none(id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 取消同类型其他模板的默认状态
    await NotificationTemplate.filter(
        template_type=template.template_type,
        is_default=True
    ).update(is_default=False)

    template.is_default = True
    await template.save()

    return success_response(message="已设为默认模板")


# ==================== 通知对象接口 ====================

class NotificationRecipientCreate(BaseModel):
    """创建通知对象"""
    name: str
    contact_type: str
    contact_value: str
    extra_config: Optional[dict] = None
    is_enabled: bool = True
    remark: Optional[str] = None


class NotificationRecipientUpdate(BaseModel):
    """更新通知对象"""
    name: Optional[str] = None
    contact_type: Optional[str] = None
    contact_value: Optional[str] = None
    extra_config: Optional[dict] = None
    is_enabled: Optional[bool] = None
    remark: Optional[str] = None


@router.get("/recipients")
async def get_notification_recipients(
    contact_type: Optional[str] = Query(None, description="联系方式类型筛选"),
    is_enabled: Optional[bool] = Query(None, description="是否启用"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """获取通知对象列表"""
    query = NotificationRecipient.all()

    if contact_type:
        query = query.filter(contact_type=contact_type)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)
    if keyword:
        query = query.filter(name__icontains=keyword)

    recipients = await query.order_by("-created_at")

    return success_response([{
        "id": r.id,
        "name": r.name,
        "contact_type": r.contact_type,
        "contact_value": r.contact_value,
        "extra_config": r.extra_config,
        "is_enabled": r.is_enabled,
        "remark": r.remark,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in recipients])


@router.get("/recipients/contact-types")
async def get_contact_types():
    """获取联系方式类型列表"""
    types = [
        {"value": "email", "label": "邮箱"},
        {"value": "phone", "label": "手机号"},
        {"value": "telegram", "label": "Telegram"},
        {"value": "wechat", "label": "微信"},
        {"value": "dingtalk", "label": "钉钉"},
    ]
    return success_response(types)


@router.post("/recipients")
async def create_notification_recipient(data: NotificationRecipientCreate):
    """创建通知对象"""
    recipient = await NotificationRecipient.create(
        name=data.name,
        contact_type=data.contact_type,
        contact_value=data.contact_value,
        extra_config=data.extra_config,
        is_enabled=data.is_enabled,
        remark=data.remark
    )
    return success_response({"id": recipient.id}, message="创建成功")


@router.put("/recipients/{recipient_id}")
async def update_notification_recipient(recipient_id: int, data: NotificationRecipientUpdate):
    """更新通知对象"""
    recipient = await NotificationRecipient.get_or_none(id=recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="通知对象不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recipient, key, value)

    await recipient.save()
    return success_response(message="更新成功")


@router.delete("/recipients/{recipient_id}")
async def delete_notification_recipient(recipient_id: int):
    """删除通知对象"""
    recipient = await NotificationRecipient.get_or_none(id=recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="通知对象不存在")

    await recipient.delete()
    return success_response(message="删除成功")


# ==================== 通知对象组接口 ====================

class NotificationRecipientGroupCreate(BaseModel):
    """创建通知对象组"""
    group_name: str
    group_code: str
    recipient_ids: List[int] = []
    channel_ids: List[int] = []
    default_template_id: Optional[int] = None
    is_enabled: bool = True
    remark: Optional[str] = None


class NotificationRecipientGroupUpdate(BaseModel):
    """更新通知对象组"""
    group_name: Optional[str] = None
    recipient_ids: Optional[List[int]] = None
    channel_ids: Optional[List[int]] = None
    default_template_id: Optional[int] = None
    is_enabled: Optional[bool] = None
    remark: Optional[str] = None


@router.get("/recipient-groups")
async def get_notification_recipient_groups(
    is_enabled: Optional[bool] = Query(None, description="是否启用")
):
    """获取通知对象组列表"""
    query = NotificationRecipientGroup.all()

    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)

    groups = await query.order_by("-created_at")

    # 获取关联的详细信息
    result = []
    for g in groups:
        # 获取通知对象详情
        recipients = []
        if g.recipient_ids:
            recipient_list = await NotificationRecipient.filter(id__in=g.recipient_ids).all()
            recipients = [{"id": r.id, "name": r.name, "contact_type": r.contact_type} for r in recipient_list]

        # 获取渠道详情
        channels = []
        if g.channel_ids:
            channel_list = await NotificationChannel.filter(id__in=g.channel_ids).all()
            channels = [{"id": c.id, "channel_name": c.channel_name, "channel_type": c.channel_type} for c in channel_list]

        result.append({
            "id": g.id,
            "group_name": g.group_name,
            "group_code": g.group_code,
            "recipient_ids": g.recipient_ids,
            "channel_ids": g.channel_ids,
            "recipients": recipients,
            "channels": channels,
            "default_template_id": g.default_template_id,
            "is_enabled": g.is_enabled,
            "remark": g.remark,
            "created_at": g.created_at.isoformat() if g.created_at else None
        })

    return success_response(result)


@router.get("/recipient-groups/{group_id}")
async def get_notification_recipient_group_detail(group_id: int):
    """获取通知对象组详情"""
    group = await NotificationRecipientGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="通知对象组不存在")

    # 获取关联的详细信息
    recipients = []
    if group.recipient_ids:
        recipient_list = await NotificationRecipient.filter(id__in=group.recipient_ids).all()
        recipients = [{
            "id": r.id,
            "name": r.name,
            "contact_type": r.contact_type,
            "contact_value": r.contact_value
        } for r in recipient_list]

    channels = []
    if group.channel_ids:
        channel_list = await NotificationChannel.filter(id__in=group.channel_ids).all()
        channels = [{
            "id": c.id,
            "channel_name": c.channel_name,
            "channel_type": c.channel_type,
            "is_enabled": c.is_enabled
        } for c in channel_list]

    template = None
    if group.default_template_id:
        t = await NotificationTemplate.get_or_none(id=group.default_template_id)
        if t:
            template = {
                "id": t.id,
                "template_name": t.template_name,
                "template_key": t.template_key
            }

    return success_response({
        "id": group.id,
        "group_name": group.group_name,
        "group_code": group.group_code,
        "recipient_ids": group.recipient_ids,
        "channel_ids": group.channel_ids,
        "recipients": recipients,
        "channels": channels,
        "default_template": template,
        "is_enabled": group.is_enabled,
        "remark": group.remark,
        "created_at": group.created_at.isoformat() if group.created_at else None
    })


@router.post("/recipient-groups")
async def create_notification_recipient_group(data: NotificationRecipientGroupCreate):
    """创建通知对象组"""
    # 检查编码是否重复
    existing = await NotificationRecipientGroup.get_or_none(group_code=data.group_code)
    if existing:
        raise HTTPException(status_code=400, detail="组编码已存在")

    group = await NotificationRecipientGroup.create(
        group_name=data.group_name,
        group_code=data.group_code,
        recipient_ids=data.recipient_ids,
        channel_ids=data.channel_ids,
        default_template_id=data.default_template_id,
        is_enabled=data.is_enabled,
        remark=data.remark
    )
    return success_response({"id": group.id}, message="创建成功")


@router.put("/recipient-groups/{group_id}")
async def update_notification_recipient_group(group_id: int, data: NotificationRecipientGroupUpdate):
    """更新通知对象组"""
    group = await NotificationRecipientGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="通知对象组不存在")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(group, key, value)

    await group.save()
    return success_response(message="更新成功")


@router.delete("/recipient-groups/{group_id}")
async def delete_notification_recipient_group(group_id: int):
    """删除通知对象组"""
    group = await NotificationRecipientGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="通知对象组不存在")

    await group.delete()
    return success_response(message="删除成功")


@router.post("/recipient-groups/{group_id}/send")
async def send_notification_to_group(
    group_id: int,
    title: str = Query(..., description="通知标题"),
    content: str = Query(..., description="通知内容")
):
    """向通知组发送消息"""
    group = await NotificationRecipientGroup.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="通知对象组不存在")

    if not group.channel_ids:
        raise HTTPException(status_code=400, detail="通知组未配置发送渠道")

    results = []

    # 遍历渠道发送
    for channel_id in group.channel_ids:
        channel = await NotificationChannel.get_or_none(id=channel_id)
        if not channel or not channel.is_enabled:
            continue

        result = await notification_service.send_test_notification(channel_id)
        results.append({
            "channel": channel.channel_name,
            "success": result.get("success", False),
            "error": result.get("error")
        })

    # 记录发送日志
    sent_count = len([r for r in results if r["success"]])
    return success_response({
        "total_channels": len(group.channel_ids),
        "sent_count": sent_count,
        "results": results
    }, message=f"已发送到 {sent_count} 个渠道")