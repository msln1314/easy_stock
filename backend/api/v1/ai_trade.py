"""
AI交易聊天API接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.response import success_response
from core.auth import get_current_user
from services.ai_trade import ai_trade_service
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

    # 调用AI服务
    result = await ai_trade_service.chat(request.message, context)

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