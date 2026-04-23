"""
AI交易聊天API接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.response import success_response
from core.auth import get_current_user
from services.ai_trade import ai_trade_service
from services.config import SysConfigService
from core.qmt_client import qmt_client

router = APIRouter(prefix="/api/v1/ai", tags=["AI交易助手"])


# ==================== Schemas ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user / assistant
    content: str


# ==================== API接口 ====================

@router.post("/chat", summary="AI聊天")
async def ai_chat(request: ChatRequest, user=Depends(get_current_user)):
    """
    与AI交易助手聊天

    支持的指令：
    - 查询行情：平安银行现在多少钱
    - 查看持仓：我的持仓
    - 查看资金：账户余额
    - 买入：买入平安银行100股
    - 卖出：卖出000001的100股
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    # 获取用户上下文信息
    context = {}
    try:
        # 获取持仓和资金信息作为上下文
        positions = await qmt_client.get_positions()
        balance = await qmt_client.get_balance()

        # 简化持仓信息
        if positions.get("positions"):
            context["positions"] = [
                {
                    "code": p.get("stock_code"),
                    "name": p.get("stock_name"),
                    "quantity": p.get("quantity"),
                    "available": p.get("available"),
                    "cost": p.get("cost_price"),
                    "current": p.get("current_price"),
                    "profit": p.get("profit")
                }
                for p in positions["positions"][:10]  # 只取前10条
            ]

        if balance:
            context["balance"] = {
                "total_asset": balance.get("total_asset"),
                "available_cash": balance.get("available_cash"),
                "market_value": balance.get("market_value")
            }
    except Exception as e:
        # 上下文获取失败不影响聊天
        pass

    # 调用AI服务（传入用户用于权限校验）
    result = await ai_trade_service.chat(request.message, context, user)

    return success_response(result)


@router.get("/history", summary="获取聊天历史")
async def get_chat_history(
    limit: int = 50,
    user=Depends(get_current_user)
):
    """
    获取聊天历史记录

    暂时返回空列表，后续可以实现持久化存储
    """
    return success_response({
        "messages": [],
        "total": 0
    })


@router.get("/qmt-status", summary="获取AI交易状态")
async def get_qmt_status(user=Depends(get_current_user)):
    """
    获取AI交易开关状态和QMT连接状态
    """
    service = SysConfigService()
    qmt_enabled = await service.get_config_value("ai.qmt_enabled") or "false"

    # 检查QMT连接状态
    qmt_connected = False
    try:
        trade_status = await qmt_client.get_trade_status()
        qmt_connected = True
    except:
        pass

    return success_response({
        "qmt_enabled": qmt_enabled.lower() == "true",
        "qmt_connected": qmt_connected
    })


@router.post("/toggle-qmt", summary="切换AI交易状态")
async def toggle_qmt_status(user=Depends(get_current_user)):
    """
    切换AI交易开关状态
    """
    service = SysConfigService()
    current_value = await service.get_config_value("ai.qmt_enabled") or "false"

    new_value = "true" if current_value.lower() != "true" else "false"

    # 更新配置
    config = await service.get_config_by_key("ai.qmt_enabled")
    if config:
        from schemas.config import SysConfigUpdate
        await service.update_config("ai.qmt_enabled", SysConfigUpdate(value=new_value))
    else:
        # 如果不存在，创建配置
        from schemas.config import SysConfigCreate
        await service.create_config(SysConfigCreate(
            key="ai.qmt_enabled",
            value=new_value,
            category="ai",
            data_type="plain",
            access_type="public",
            description="AI交易功能开关"
        ))

    return success_response({
        "qmt_enabled": new_value == "true",
        "message": f"AI交易已{'开启' if new_value == 'true' else '关闭'}"
    })