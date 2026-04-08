"""
交易红线管理API

提供红线的增删改查接口
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
from loguru import logger

from core.response import success_response
from core.auth import get_current_user
from models.trade_red_line import TradeRedLine, TradeAuditLog, PRESET_RED_LINES
from services.trade_audit import trade_audit_service

router = APIRouter(prefix="/api/v1/red-line", tags=["交易红线管理"])


# ==================== Schemas ====================

class RedLineCreate(BaseModel):
    """创建红线规则"""
    rule_key: str
    rule_name: str
    rule_type: str
    description: Optional[str] = None
    rule_config: dict
    severity: str = "critical"
    is_enabled: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class RedLineUpdate(BaseModel):
    """更新红线规则"""
    rule_name: Optional[str] = None
    description: Optional[str] = None
    rule_config: Optional[dict] = None
    severity: Optional[str] = None
    is_enabled: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class RedLineBatchUpdate(BaseModel):
    """批量更新红线状态"""
    rule_keys: List[str]
    is_enabled: bool


class AuditTestRequest(BaseModel):
    """测试审核请求"""
    stock_code: str
    price: float
    quantity: int


class RedLineSwitch(BaseModel):
    """红线开关"""
    enabled: bool


# ==================== 红线开关接口 ====================

@router.get("/switch", summary="获取红线开关状态")
async def get_red_line_switch(user=Depends(get_current_user)):
    """
    获取交易红线开关状态

    Returns:
        enabled: True-红线启用，False-红线禁用
    """
    enabled = await trade_audit_service.is_red_line_enabled()
    return success_response({
        "enabled": enabled,
        "message": "交易红线已启用" if enabled else "交易红线已禁用"
    })


@router.post("/switch", summary="设置红线开关状态")
async def set_red_line_switch(
    request: RedLineSwitch,
    user=Depends(get_current_user)
):
    """
    设置交易红线开关状态

    - enabled=True: 启用红线，买入时必须通过审核
    - enabled=False: 禁用红线，买入时直接交易

    需要管理员权限
    """
    # 检查管理员权限
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="只有管理员可以设置红线开关")

    success = await trade_audit_service.set_red_line_enabled(
        enabled=request.enabled,
        user_name=user.get("username", "unknown")
    )

    # 记录日志
    from services.trade_log import trade_log_service
    await trade_log_service.log_rule_change(
        rule_key="trade_red_line_switch",
        rule_name="交易红线开关",
        change_type="enable" if request.enabled else "disable",
        new_config={"enabled": request.enabled},
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    return success_response({
        "enabled": request.enabled,
        "message": f"交易红线已{'启用' if request.enabled else '禁用'}"
    })


# ==================== 红线规则接口 ====================

@router.get("/rules", summary="获取红线规则列表")
async def get_red_lines(
    rule_type: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    severity: Optional[str] = None,
    user=Depends(get_current_user)
):
    """
    获取红线规则列表

    可以按类型、状态、严重级别筛选
    """
    query = TradeRedLine.all()

    if rule_type:
        query = query.filter(rule_type=rule_type)
    if is_enabled is not None:
        query = query.filter(is_enabled=is_enabled)
    if severity:
        query = query.filter(severity=severity)

    rules = await query.order_by("severity", "-created_at")

    return success_response({
        "rules": [
            {
                "id": rule.id,
                "rule_key": rule.rule_key,
                "rule_name": rule.rule_name,
                "rule_type": rule.rule_type,
                "rule_type_display": rule.rule_type_display,
                "description": rule.description,
                "rule_config": rule.rule_config,
                "severity": rule.severity,
                "severity_display": rule.severity_display,
                "is_enabled": rule.is_enabled,
                "is_effective": rule.is_effective,
                "effective_from": str(rule.effective_from) if rule.effective_from else None,
                "effective_to": str(rule.effective_to) if rule.effective_to else None,
                "total_checked": rule.total_checked,
                "total_rejected": rule.total_rejected,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat(),
            }
            for rule in rules
        ],
        "total": len(rules)
    })


@router.get("/rules/{rule_key}", summary="获取单个红线规则")
async def get_red_line(rule_key: str, user=Depends(get_current_user)):
    """获取单个红线规则详情"""
    rule = await TradeRedLine.filter(rule_key=rule_key).first()
    if not rule:
        raise HTTPException(status_code=404, detail="红线规则不存在")

    return success_response({
        "id": rule.id,
        "rule_key": rule.rule_key,
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "rule_type_display": rule.rule_type_display,
        "description": rule.description,
        "rule_config": rule.rule_config,
        "severity": rule.severity,
        "severity_display": rule.severity_display,
        "is_enabled": rule.is_enabled,
        "is_effective": rule.is_effective,
        "effective_from": str(rule.effective_from) if rule.effective_from else None,
        "effective_to": str(rule.effective_to) if rule.effective_to else None,
        "total_checked": rule.total_checked,
        "total_rejected": rule.total_rejected,
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat(),
    })


@router.post("/rules", summary="创建红线规则")
async def create_red_line(request: RedLineCreate, user=Depends(get_current_user)):
    """创建新的红线规则"""
    # 检查是否已存在
    exists = await TradeRedLine.filter(rule_key=request.rule_key).exists()
    if exists:
        raise HTTPException(status_code=400, detail=f"规则KEY {request.rule_key} 已存在")

    rule = await TradeRedLine.create(
        rule_key=request.rule_key,
        rule_name=request.rule_name,
        rule_type=request.rule_type,
        description=request.description,
        rule_config=request.rule_config,
        severity=request.severity,
        is_enabled=request.is_enabled,
        effective_from=request.effective_from,
        effective_to=request.effective_to,
        created_by=user.get("username", "system")
    )

    logger.info(f"创建红线规则: {request.rule_key} by {user.get('username')}")

    return success_response({
        "id": rule.id,
        "rule_key": rule.rule_key,
        "rule_name": rule.rule_name,
        "message": "红线规则创建成功"
    })


@router.put("/rules/{rule_key}", summary="更新红线规则")
async def update_red_line(
    rule_key: str,
    request: RedLineUpdate,
    user=Depends(get_current_user)
):
    """更新红线规则"""
    rule = await TradeRedLine.filter(rule_key=rule_key).first()
    if not rule:
        raise HTTPException(status_code=404, detail="红线规则不存在")

    # 更新字段
    update_data = {}
    if request.rule_name is not None:
        update_data["rule_name"] = request.rule_name
    if request.description is not None:
        update_data["description"] = request.description
    if request.rule_config is not None:
        update_data["rule_config"] = request.rule_config
    if request.severity is not None:
        update_data["severity"] = request.severity
    if request.is_enabled is not None:
        update_data["is_enabled"] = request.is_enabled
    if request.effective_from is not None:
        update_data["effective_from"] = request.effective_from
    if request.effective_to is not None:
        update_data["effective_to"] = request.effective_to

    if update_data:
        await TradeRedLine.filter(id=rule.id).update(**update_data)
        logger.info(f"更新红线规则: {rule_key} by {user.get('username')}, 更新字段: {update_data.keys()}")

    return success_response({"message": "红线规则更新成功"})


@router.delete("/rules/{rule_key}", summary="删除红线规则")
async def delete_red_line(rule_key: str, user=Depends(get_current_user)):
    """删除红线规则"""
    rule = await TradeRedLine.filter(rule_key=rule_key).first()
    if not rule:
        raise HTTPException(status_code=404, detail="红线规则不存在")

    await TradeRedLine.filter(id=rule.id).delete()
    logger.info(f"删除红线规则: {rule_key} by {user.get('username')}")

    return success_response({"message": "红线规则删除成功"})


@router.post("/rules/batch-status", summary="批量更新红线状态")
async def batch_update_status(
    request: RedLineBatchUpdate,
    user=Depends(get_current_user)
):
    """批量启用或禁用红线规则"""
    updated = await TradeRedLine.filter(
        rule_key__in=request.rule_keys
    ).update(is_enabled=request.is_enabled)

    logger.info(
        f"批量更新红线状态: {request.rule_keys} -> {request.is_enabled} "
        f"by {user.get('username')}, 更新 {updated} 条"
    )

    return success_response({
        "message": f"已更新 {updated} 条红线规则",
        "updated_count": updated
    })


@router.post("/rules/init", summary="初始化预置红线规则")
async def init_preset_rules(user=Depends(get_current_user)):
    """
    初始化预置的红线规则

    将预置规则写入数据库，已存在的规则不会重复创建
    """
    await trade_audit_service.init_preset_rules()
    return success_response({"message": "预置红线规则初始化完成"})


@router.get("/rule-types", summary="获取红线类型列表")
async def get_rule_types(user=Depends(get_current_user)):
    """获取所有红线规则类型"""
    return success_response({
        "types": [
            {"key": "position_limit", "name": "仓位限制", "description": "控制持仓比例"},
            {"key": "stock_blacklist", "name": "股票黑名单", "description": "禁止买入特定股票"},
            {"key": "amount_limit", "name": "金额限制", "description": "限制交易金额"},
            {"key": "price_limit", "name": "价格限制", "description": "限制交易价格范围"},
            {"key": "time_limit", "name": "时间限制", "description": "限制交易时段"},
            {"key": "frequency_limit", "name": "频率限制", "description": "限制交易频率"},
            {"key": "risk_control", "name": "风控指标", "description": "风控指标检查"},
        ]
    })


@router.get("/severities", summary="获取严重级别列表")
async def get_severities(user=Depends(get_current_user)):
    """获取所有严重级别"""
    return success_response({
        "severities": [
            {"key": "critical", "name": "必须通过", "description": "不通过则拒绝交易"},
            {"key": "warning", "name": "警告", "description": "警告但允许交易"},
            {"key": "info", "name": "提示", "description": "仅提示信息"},
        ]
    })


# ==================== 测试接口 ====================

@router.post("/audit/test", summary="测试红线校验")
async def test_audit(request: AuditTestRequest, user=Depends(get_current_user)):
    """
    测试红线校验

    模拟买入请求进行红线校验，不实际执行交易
    用于验证红线规则配置是否正确
    """
    passed, result = await trade_audit_service.audit_buy_request(
        stock_code=request.stock_code,
        price=request.price,
        quantity=request.quantity,
        user_id=user.get("id") if user else None,
        user_name=user.get("username") if user else "test"
    )

    return success_response(result)


# ==================== 审计统计接口 ====================

@router.get("/statistics", summary="获取红线审计统计")
async def get_audit_statistics(
    days: int = 7,
    user=Depends(get_current_user)
):
    """
    获取红线审核统计数据

    包括拒绝率、各规则触发次数等
    """
    start_date = datetime.now() - timedelta(days=days)

    # 统计审核结果
    total_logs = await TradeAuditLog.filter(audit_time__gte=start_date).count()
    rejected_logs = await TradeAuditLog.filter(
        audit_time__gte=start_date,
        audit_result="rejected"
    ).count()
    warning_logs = await TradeAuditLog.filter(
        audit_time__gte=start_date,
        audit_result="warning"
    ).count()
    passed_logs = await TradeAuditLog.filter(
        audit_time__gte=start_date,
        audit_result="passed"
    ).count()

    # 计算拒绝率
    reject_rate = (rejected_logs / total_logs * 100) if total_logs > 0 else 0

    # 获取各规则的触发统计
    rules = await TradeRedLine.all()
    rule_stats = []
    for rule in rules:
        rule_stats.append({
            "rule_key": rule.rule_key,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "total_checked": rule.total_checked,
            "total_rejected": rule.total_rejected,
            "reject_rate": (rule.total_rejected / rule.total_checked * 100) if rule.total_checked > 0 else 0
        })

    return success_response({
        "period_days": days,
        "total_audits": total_logs,
        "rejected": rejected_logs,
        "warnings": warning_logs,
        "passed": passed_logs,
        "reject_rate": round(reject_rate, 2),
        "rule_statistics": rule_stats
    })


