"""
委托状态API接口

提供今日委托、委托状态统计等数据
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from core.qmt_client import qmt_client

router = APIRouter(prefix="/api/v1/order-status", tags=["委托状态"])


@router.get("/overview")
async def get_order_status_overview():
    """获取委托状态概览"""
    today = date.today()

    try:
        # 从QMT获取委托数据
        orders = await qmt_client.get_orders()
    except Exception as e:
        print(f"获取QMT委托失败: {e}")
        orders = []

    # 如果没有实际数据，使用模拟数据
    if not orders:
        orders = [
            {"order_id": "ORD001", "stock_code": "000001", "stock_name": "平安银行", "direction": "buy", "price": 10.25, "quantity": 1000, "status": "filled", "order_time": "2026-04-23 10:15:00"},
            {"order_id": "ORD002", "stock_code": "600036", "stock_name": "招商银行", "direction": "buy", "price": 35.80, "quantity": 500, "status": "pending", "order_time": "2026-04-23 10:20:00"},
            {"order_id": "ORD003", "stock_code": "000333", "stock_name": "美的集团", "direction": "sell", "price": 58.60, "quantity": 200, "status": "partial", "order_time": "2026-04-23 11:05:00"},
            {"order_id": "ORD004", "stock_code": "002475", "stock_name": "立讯精密", "direction": "sell", "price": 28.50, "quantity": 300, "status": "cancelled", "order_time": "2026-04-23 13:30:00"},
            {"order_id": "ORD005", "stock_code": "300750", "stock_name": "宁德时代", "direction": "buy", "price": 185.20, "quantity": 100, "status": "rejected", "order_time": "2026-04-23 14:10:00"},
        ]

    # 统计各状态数量
    status_count = {
        "pending": 0,      # 待成交
        "partial": 0,      # 部分成交
        "filled": 0,       # 已成交
        "cancelled": 0,    # 已撤单
        "rejected": 0,     # 已拒绝
    }

    direction_count = {
        "buy": 0,
        "sell": 0
    }

    total_amount = Decimal("0")
    filled_amount = Decimal("0")

    for order in orders:
        status = order.get("status", "pending")
        direction = order.get("direction", "buy")

        if status in status_count:
            status_count[status] += 1

        if direction in direction_count:
            direction_count[direction] += 1

        # 计算金额
        price = Decimal(str(order.get("price", 0)))
        quantity = int(order.get("quantity", 0))
        amount = price * quantity

        total_amount += amount
        if status == "filled":
            filled_amount += amount

    # 委托成功率
    success_rate = (status_count["filled"] / len(orders) * 100) if orders else 0

    return success_response({
        # 委托统计
        "total_orders": len(orders),
        "status_count": status_count,
        "direction_count": direction_count,
        "success_rate": round(success_rate, 2),

        # 金额统计
        "total_amount": float(total_amount),
        "filled_amount": float(filled_amount),

        # 今日委托列表
        "orders": [{
            "order_id": o.get("order_id"),
            "stock_code": o.get("stock_code"),
            "stock_name": o.get("stock_name"),
            "direction": o.get("direction"),
            "direction_display": "买入" if o.get("direction") == "buy" else "卖出",
            "price": o.get("price"),
            "quantity": o.get("quantity"),
            "amount": float(Decimal(str(o.get("price", 0))) * int(o.get("quantity", 0))),
            "status": o.get("status"),
            "status_display": {
                "pending": "待成交",
                "partial": "部分成交",
                "filled": "已成交",
                "cancelled": "已撤单",
                "rejected": "已拒绝"
            }.get(o.get("status"), o.get("status")),
            "order_time": o.get("order_time"),
        } for o in orders],

        # 汇总信息
        "pending_amount": sum(float(Decimal(str(o.get("price", 0))) * int(o.get("quantity", 0))) for o in orders if o.get("status") == "pending"),
        "today_date": today.isoformat(),
    })


@router.get("/pending")
async def get_pending_orders(limit: int = Query(20, description="返回数量")):
    """获取待成交委托"""
    try:
        orders = await qmt_client.get_orders(status="pending")
    except Exception:
        orders = []

    if not orders:
        orders = [
            {"order_id": "ORD002", "stock_code": "600036", "stock_name": "招商银行", "direction": "buy", "price": 35.80, "quantity": 500, "status": "pending", "order_time": "2026-04-23 10:20:00"},
        ]

    return success_response([{
        "order_id": o.get("order_id"),
        "stock_code": o.get("stock_code"),
        "stock_name": o.get("stock_name"),
        "direction": o.get("direction"),
        "price": o.get("price"),
        "quantity": o.get("quantity"),
        "amount": float(Decimal(str(o.get("price", 0))) * int(o.get("quantity", 0))),
        "order_time": o.get("order_time"),
    } for o in orders[:limit]])


@router.get("/history")
async def get_order_history(days: int = Query(7, description="查询天数")):
    """获取历史委托"""
    start_date = date.today() - timedelta(days=days)

    # 模拟历史数据
    history_orders = [
        {"order_id": "ORD001", "stock_code": "000001", "stock_name": "平安银行", "direction": "buy", "price": 10.25, "quantity": 1000, "status": "filled", "order_time": "2026-04-23 10:15:00"},
        {"order_id": "ORD004", "stock_code": "002475", "stock_name": "立讯精密", "direction": "sell", "price": 28.50, "quantity": 300, "status": "cancelled", "order_time": "2026-04-23 13:30:00"},
        {"order_id": "ORD006", "stock_code": "000002", "stock_name": "万科A", "direction": "buy", "price": 8.50, "quantity": 2000, "status": "filled", "order_time": "2026-04-22 09:45:00"},
        {"order_id": "ORD007", "stock_code": "600000", "stock_name": "浦发银行", "direction": "sell", "price": 9.80, "quantity": 500, "status": "filled", "order_time": "2026-04-22 14:20:00"},
    ]

    # 统计
    total_count = len(history_orders)
    filled_count = sum(1 for o in history_orders if o.get("status") == "filled")
    cancelled_count = sum(1 for o in history_orders if o.get("status") == "cancelled")

    return success_response({
        "days": days,
        "total_count": total_count,
        "filled_count": filled_count,
        "cancelled_count": cancelled_count,
        "orders": [{
            "order_id": o.get("order_id"),
            "stock_code": o.get("stock_code"),
            "stock_name": o.get("stock_name"),
            "direction": o.get("direction"),
            "price": o.get("price"),
            "quantity": o.get("quantity"),
            "status": o.get("status"),
            "order_time": o.get("order_time"),
        } for o in history_orders]
    })


@router.get("/stats")
async def get_order_stats():
    """获取委托统计"""
    # 今日统计
    today_stats = {
        "buy_orders": 3,
        "sell_orders": 2,
        "filled": 1,
        "pending": 1,
        "partial": 1,
        "cancelled": 1,
        "rejected": 1,
        "buy_amount": 45000,
        "sell_amount": 23600,
        "avg_fill_time": 15,  # 平均成交时间（分钟）
    }

    # 成功率
    success_rate = (today_stats["filled"] / (today_stats["buy_orders"] + today_stats["sell_orders"]) * 100)

    return success_response({
        "today": today_stats,
        "success_rate": round(success_rate, 2),
        "cancel_rate": round(today_stats["cancelled"] / (today_stats["buy_orders"] + today_stats["sell_orders"]) * 100, 2),
    })