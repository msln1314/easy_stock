"""
交易管理API路由
代理调用qmt-service获取持仓和资金信息，执行交易

增加交易红线审核，不符合安全审计的交易不允许开仓
增加交易日志记录，记录所有交易行为
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from loguru import logger

from core.qmt_client import qmt_client
from core.auth import get_current_user
from core.response import success_response, error_response
from services.trade_audit import trade_audit_service
from services.trade_log import trade_log_service

router = APIRouter(prefix="/api/v1/position", tags=["交易管理"])


# ==================== Schemas ====================

class TradeRequest(BaseModel):
    """交易请求"""
    stock_code: str
    price: float
    quantity: int
    order_type: str = "limit"  # limit-限价 market-市价
    skip_audit: bool = False  # 是否跳过审核（仅管理员可用）


class CancelRequest(BaseModel):
    """撤单请求"""
    order_id: str


class AuditResult(BaseModel):
    """审核结果"""
    passed: bool
    audit_result: str
    failed_rules: List[dict] = []
    warning_rules: List[dict] = []
    reject_reason: Optional[str] = None


# ==================== 行情接口 ====================

@router.get("/quote/{stock_code}", summary="获取股票行情")
async def get_stock_quote(stock_code: str, user=Depends(get_current_user)):
    """获取单只股票实时行情"""
    data = await qmt_client.get_stock_quote(stock_code)
    return success_response(data)


@router.post("/quote/batch", summary="批量获取行情")
async def get_stock_quotes(stock_codes: list, user=Depends(get_current_user)):
    """批量获取股票行情"""
    data = await qmt_client.get_stock_quotes(stock_codes)
    return success_response(data)


@router.get("/indexes", summary="获取主要指数行情")
async def get_index_quotes(user=Depends(get_current_user)):
    """获取主要指数行情（上证、深证、创业板、沪深300等）"""
    data = await qmt_client.get_index_quotes()
    return success_response(data)


# ==================== 持仓和资金接口 ====================

@router.get("/list", summary="获取持仓列表")
async def get_positions(user=Depends(get_current_user)):
    """获取持仓列表"""
    data = await qmt_client.get_positions()
    return success_response(data)


@router.get("/balance", summary="获取资金余额")
async def get_balance(user=Depends(get_current_user)):
    """获取资金余额"""
    data = await qmt_client.get_balance()
    return success_response(data)


@router.get("/trades/today", summary="获取今日成交")
async def get_today_trades(user=Depends(get_current_user)):
    """获取今日成交记录"""
    data = await qmt_client.get_today_trades()
    return success_response(data)


@router.get("/entrusts/today", summary="获取今日委托")
async def get_today_entrusts(user=Depends(get_current_user)):
    """获取今日委托记录"""
    data = await qmt_client.get_today_entrusts()
    return success_response(data)


# ==================== 交易审核接口 ====================

@router.post("/audit", summary="预审核交易请求")
async def pre_audit_trade(request: TradeRequest, user=Depends(get_current_user)):
    """
    预审核交易请求

    在实际下单前，可以先调用此接口检查交易是否符合红线规则，
    返回审核结果但不执行交易
    """
    passed, result = await trade_audit_service.audit_buy_request(
        stock_code=request.stock_code,
        price=request.price,
        quantity=request.quantity,
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    return success_response(result)


# ==================== 交易接口 ====================

@router.post("/buy", summary="买入股票")
async def buy_stock(request: TradeRequest, user=Depends(get_current_user)):
    """
    买入股票

    会先进行交易红线审核，审核通过后才执行买入
    """
    start_time = datetime.now()
    stock_name = ""

    # 获取股票名称
    try:
        quote = await qmt_client.get_stock_quote(request.stock_code)
        stock_name = quote.get("stock_name", "")
    except:
        pass

    # 检查交易时间
    trade_status = await qmt_client.get_trade_status()
    if not trade_status.get("is_trade_time"):
        raise HTTPException(status_code=400, detail="当前非交易时间")

    # 检查数量是否为100的整数倍
    if request.quantity % 100 != 0:
        raise HTTPException(status_code=400, detail="买入数量必须是100的整数倍")

    # 记录买入请求日志
    await trade_log_service.log_buy_request(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=request.price,
        quantity=request.quantity,
        amount=request.price * request.quantity,
        order_type=request.order_type,
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    # 检查红线开关是否启用
    red_line_enabled = await trade_audit_service.is_red_line_enabled()

    # 进行交易红线审核（红线启用时）
    if red_line_enabled and not request.skip_audit:
        audit_start = datetime.now()
        passed, audit_result = await trade_audit_service.audit_buy_request(
            stock_code=request.stock_code,
            price=request.price,
            quantity=request.quantity,
            user_id=user.get("id"),
            user_name=user.get("username")
        )
        audit_duration = (datetime.now() - audit_start).total_seconds() * 1000

        # 记录审核日志
        await trade_log_service.log_buy_audit(
            stock_code=request.stock_code,
            stock_name=stock_name,
            passed=passed,
            failed_rules=audit_result.get("failed_rules", []),
            warning_rules=audit_result.get("warning_rules", []),
            audit_details=audit_result.get("audit_details", {}),
            user_id=user.get("id"),
            user_name=user.get("username"),
            duration_ms=int(audit_duration)
        )

        if not passed:
            # 审核失败，返回拒绝原因
            logger.warning(
                f"买入请求被红线拦截: {request.stock_code} "
                f"{request.quantity}股 @ {request.price}, "
                f"原因: {audit_result.get('reject_reason')}"
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "message": audit_result.get("reject_reason", "不符合交易红线规则"),
                    "audit_result": audit_result.get("audit_result"),
                    "failed_rules": audit_result.get("failed_rules", []),
                    "warning_rules": audit_result.get("warning_rules", [])
                }
            )

        # 有警告但允许通过，记录日志
        if audit_result.get("warning_rules"):
            logger.info(
                f"买入请求有警告: {request.stock_code}, "
                f"警告规则: {audit_result.get('warning_rules')}"
            )
    elif not red_line_enabled:
        # 红线已禁用，记录日志
        logger.info(f"交易红线已禁用，跳过审核: {request.stock_code}")
    elif request.skip_audit:
        # 跳过审核，需要管理员权限
        if not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="只有管理员可以跳过审核")
        logger.info(f"管理员跳过红线审核: {request.stock_code} by {user.get('username')}")

    # 执行买入
    result = await qmt_client.buy_stock(
        stock_code=request.stock_code,
        price=request.price,
        quantity=request.quantity,
        order_type=request.order_type
    )

    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    order_id = result.get("order_id", "")

    # 记录买入执行日志
    await trade_log_service.log_buy_executed(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=request.price,
        quantity=request.quantity,
        order_id=order_id,
        order_type=request.order_type,
        user_id=user.get("id"),
        user_name=user.get("username"),
        duration_ms=int(duration_ms)
    )

    return success_response(result, message="买入委托成功")


@router.post("/sell", summary="卖出股票")
async def sell_stock(request: TradeRequest, user=Depends(get_current_user)):
    """卖出股票"""
    start_time = datetime.now()
    stock_name = ""

    # 获取股票名称
    try:
        quote = await qmt_client.get_stock_quote(request.stock_code)
        stock_name = quote.get("stock_name", "")
    except:
        pass

    # 检查交易时间
    trade_status = await qmt_client.get_trade_status()
    if not trade_status.get("is_trade_time"):
        raise HTTPException(status_code=400, detail="当前非交易时间")

    # 检查数量是否为100的整数倍
    if request.quantity % 100 != 0:
        raise HTTPException(status_code=400, detail="卖出数量必须是100的整数倍")

    # 记录卖出请求日志
    await trade_log_service.log_sell_request(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=request.price,
        quantity=request.quantity,
        order_type=request.order_type,
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    result = await qmt_client.sell_stock(
        stock_code=request.stock_code,
        price=request.price,
        quantity=request.quantity,
        order_type=request.order_type
    )

    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    order_id = result.get("order_id", "")

    # 记录卖出执行日志
    await trade_log_service.log_sell_executed(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=request.price,
        quantity=request.quantity,
        order_id=order_id,
        order_type=request.order_type,
        user_id=user.get("id"),
        user_name=user.get("username"),
        duration_ms=int(duration_ms)
    )

    return success_response(result, message="卖出委托成功")


@router.post("/cancel", summary="撤单")
async def cancel_order(request: CancelRequest, user=Depends(get_current_user)):
    """撤销委托订单"""
    result = await qmt_client.cancel_order(request.order_id)

    # 记录撤单日志
    success = result.get("success", False)
    await trade_log_service.log_cancel(
        order_id=request.order_id,
        success=success,
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    return success_response(result, message="撤单成功")


@router.get("/trade-status", summary="获取交易状态")
async def get_trade_status(user=Depends(get_current_user)):
    """获取当前交易状态和时间"""
    data = await qmt_client.get_trade_status()
    return success_response(data)


# ==================== 快捷交易 ====================

@router.post("/quick-buy", summary="快捷买入")
async def quick_buy(request: TradeRequest, user=Depends(get_current_user)):
    """
    快捷买入（市价单）
    自动以涨停价委托，确保快速成交

    注意：也会进行红线审核
    """
    start_time = datetime.now()

    # 获取当前行情
    quote = await qmt_client.get_stock_quote(request.stock_code)
    if not quote:
        raise HTTPException(status_code=404, detail="无法获取股票行情")

    stock_name = quote.get("stock_name", "")

    # 使用涨停价委托
    limit_up = quote.get("limit_up", request.price)
    if limit_up <= 0:
        limit_up = request.price

    # 检查交易时间
    trade_status = await qmt_client.get_trade_status()
    if not trade_status.get("is_trade_time"):
        raise HTTPException(status_code=400, detail="当前非交易时间")

    # 检查数量是否为100的整数倍
    if request.quantity % 100 != 0:
        raise HTTPException(status_code=400, detail="买入数量必须是100的整数倍")

    # 记录买入请求日志
    await trade_log_service.log_buy_request(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=limit_up,
        quantity=request.quantity,
        amount=limit_up * request.quantity,
        order_type="quick_buy",
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    # 检查红线开关
    red_line_enabled = await trade_audit_service.is_red_line_enabled()

    # 进行红线审核（红线启用时）
    if red_line_enabled:
        passed, audit_result = await trade_audit_service.audit_buy_request(
            stock_code=request.stock_code,
            price=limit_up,
            quantity=request.quantity,
            user_id=user.get("id"),
            user_name=user.get("username")
        )

        if not passed:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": audit_result.get("reject_reason", "不符合交易红线规则"),
                    "audit_result": audit_result.get("audit_result"),
                    "failed_rules": audit_result.get("failed_rules", [])
                }
            )
    else:
        logger.info(f"红线已禁用，快捷买入跳过审核: {request.stock_code}")

    result = await qmt_client.buy_stock(
        stock_code=request.stock_code,
        price=limit_up,
        quantity=request.quantity,
        order_type="limit"
    )

    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    order_id = result.get("order_id", "")

    # 记录买入执行日志
    await trade_log_service.log_buy_executed(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=limit_up,
        quantity=request.quantity,
        order_id=order_id,
        order_type="quick_buy",
        user_id=user.get("id"),
        user_name=user.get("username"),
        duration_ms=int(duration_ms)
    )

    return success_response({
        **result,
        "limit_up_price": limit_up,
        "message": f"以涨停价 {limit_up:.2f} 委托买入"
    })


@router.post("/quick-sell", summary="快捷卖出")
async def quick_sell(request: TradeRequest, user=Depends(get_current_user)):
    """
    快捷卖出（市价单）
    自动以跌停价委托，确保快速成交
    """
    start_time = datetime.now()

    # 获取当前行情
    quote = await qmt_client.get_stock_quote(request.stock_code)
    if not quote:
        raise HTTPException(status_code=404, detail="无法获取股票行情")

    stock_name = quote.get("stock_name", "")

    # 使用跌停价委托
    limit_down = quote.get("limit_down", request.price)
    if limit_down <= 0:
        limit_down = request.price

    # 记录卖出请求日志
    await trade_log_service.log_sell_request(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=limit_down,
        quantity=request.quantity,
        order_type="quick_sell",
        user_id=user.get("id"),
        user_name=user.get("username")
    )

    result = await qmt_client.sell_stock(
        stock_code=request.stock_code,
        price=limit_down,
        quantity=request.quantity,
        order_type="limit"
    )

    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    order_id = result.get("order_id", "")

    # 记录卖出执行日志
    await trade_log_service.log_sell_executed(
        stock_code=request.stock_code,
        stock_name=stock_name,
        price=limit_down,
        quantity=request.quantity,
        order_id=order_id,
        order_type="quick_sell",
        user_id=user.get("id"),
        user_name=user.get("username"),
        duration_ms=int(duration_ms)
    )

    return success_response({
        **result,
        "limit_down_price": limit_down,
        "message": f"以跌停价 {limit_down:.2f} 委托卖出"
    })


# ==================== 市场统计接口 ====================

@router.get("/market-stats", summary="获取市场统计数据")
async def get_market_stats(user=Depends(get_current_user)):
    """
    获取市场统计数据

    包括涨跌停数量、板块资金流向等
    """
    try:
        data = await qmt_client.get_market_stats()
        return success_response(data)
    except Exception as e:
        logger.error(f"获取市场统计数据失败: {e}")
        return success_response({
            "limit_up_count": 0,
            "limit_down_count": 0,
            "top_sectors": [],
            "error": str(e)
        })


# ==================== 审计日志接口 ====================

@router.get("/audit-logs", summary="获取交易审计日志")
async def get_audit_logs(
    stock_code: Optional[str] = None,
    audit_result: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    user=Depends(get_current_user)
):
    """
    获取交易审计日志

    可以按股票代码、审核结果、时间范围筛选
    """
    start_dt = None
    end_dt = None

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # 包含结束日期的全天
        end_dt = end_dt.replace(hour=23, minute=59, second=59)

    logs = await trade_audit_service.get_audit_logs(
        stock_code=stock_code,
        audit_result=audit_result,
        user_id=user.get("id"),
        start_date=start_dt,
        end_date=end_dt,
        limit=limit
    )

    return success_response({
        "logs": [
            {
                "id": log.id,
                "trade_type": log.trade_type,
                "stock_code": log.stock_code,
                "stock_name": log.stock_name,
                "price": float(log.price),
                "quantity": log.quantity,
                "amount": float(log.amount),
                "audit_result": log.audit_result,
                "failed_rules": log.failed_rules,
                "warning_rules": log.warning_rules,
                "reject_reason": log.reject_reason,
                "audit_time": log.audit_time.isoformat(),
                "is_executed": log.is_executed,
                "order_id": log.order_id,
            }
            for log in logs
        ],
        "total": len(logs)
    })