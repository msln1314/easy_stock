"""
市场情绪API接口

提供涨跌统计、涨停跌停、北向资金、板块热度等
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from core.qmt_client import qmt_client

router = APIRouter(prefix="/api/v1/market-sentiment", tags=["市场情绪"])


@router.get("/overview")
async def get_market_sentiment_overview():
    """获取市场情绪概览"""
    today = date.today()

    try:
        # 从QMT获取市场数据
        quotes = await qmt_client.get_market_quotes()
    except Exception as e:
        print(f"获取市场数据失败: {e}")
        quotes = None

    # 模拟数据（当QMT未返回数据时）
    result = {
        # 涨跌统计
        "rise_fall": {
            "rise_count": 1856,       # 上涨家数
            "fall_count": 2342,       # 下跌家数
            "flat_count": 156,        # 平盘家数
            "rise_ratio": 44.2,       # 上涨比例(%)
        },

        # 涨停跌停
        "limit_stats": {
            "limit_up_count": 25,     # 涨停数
            "limit_down_count": 8,    # 跌停数
            "near_limit_up": 45,      # 接近涨停(>9%)
            "near_limit_down": 12,    # 接近跌停(<-9%)
        },

        # 强弱指数
        "strength_index": {
            "value": 62.5,            # 市场强弱指数 (0-100)
            "level": "中性偏强",       # 情绪等级
            "trend": "上升",          # 趋势方向
        },

        # 北向资金
        "north_flow": {
            "today_flow": 28.5,       # 今日流入(亿元)
            "month_flow": 156.8,      # 本月流入(亿元)
            "year_flow": 892.5,       # 今年流入(亿元)
            "status": "流入",          # 状态
        },

        # 板块热度排行
        "hot_sectors": [
            {"sector": "人工智能", "heat": 95, "change_avg": 3.5, "leading_stock": "科大讯飞"},
            {"sector": "机器人", "heat": 88, "change_avg": 2.8, "leading_stock": "埃斯顿"},
            {"sector": "算力", "heat": 82, "change_avg": 2.2, "leading_stock": "寒武纪"},
            {"sector": "新能源", "heat": 75, "change_avg": 1.5, "leading_stock": "宁德时代"},
            {"sector": "半导体", "heat": 68, "change_avg": 1.2, "leading_stock": "韦尔股份"},
        ],

        # 冷门板块
        "cold_sectors": [
            {"sector": "地产", "heat": 25, "change_avg": -1.5, "leading_stock": "万科A"},
            {"sector": "煤炭", "heat": 32, "change_avg": -0.8, "leading_stock": "中国神华"},
            {"sector": "钢铁", "heat": 38, "change_avg": -0.5, "leading_stock": "宝钢股份"},
        ],

        # 市场成交量
        "volume_stats": {
            "today_volume": 12500,    # 今日成交额(亿)
            "yesterday_volume": 10800,
            "volume_change": 15.7,    # 成交量变化(%)
        },

        # 指数涨跌
        "index_change": [
            {"index": "上证指数", "code": "000001.SH", "price": 3089.34, "change": 0.56},
            {"index": "深证成指", "code": "399001.SZ", "price": 10234.56, "change": 1.23},
            {"index": "创业板指", "code": "399006.SZ", "price": 2156.78, "change": -0.45},
            {"index": "沪深300", "code": "000300.SH", "price": 3567.89, "change": 0.32},
        ],

        "today_date": today.isoformat(),
    }

    # 如果有QMT数据，替换部分值
    if quotes:
        # 更新指数数据
        for i, idx in enumerate(result["index_change"]):
            if idx["code"] in quotes:
                q = quotes[idx["code"]]
                result["index_change"][i]["price"] = q.get("lastPrice", idx["price"])
                result["index_change"][i]["change"] = q.get("changePercent", idx["change"])

    return success_response(result)


@router.get("/rise-fall")
async def get_rise_fall_stats():
    """获取涨跌统计"""
    # 模拟数据
    result = {
        "rise_count": 1856,
        "fall_count": 2342,
        "flat_count": 156,
        "rise_ratio": 44.2,
        "limit_up": 25,
        "limit_down": 8,
        "big_rise": 156,  # 大涨(>5%)
        "big_fall": 82,   # 大跌(<-5%)
        "distribution": [
            {"range": ">9%", "count": 25, "type": "涨停"},
            {"range": "5-9%", "count": 131, "type": "大涨"},
            {"range": "2-5%", "count": 450, "type": "中涨"},
            {"range": "0-2%", "count": 1250, "type": "小涨"},
            {"range": "-2-0%", "count": 156, "type": "平盘"},
            {"range": "-5--2%", "count": 1520, "type": "小跌"},
            {"range": "-9--5%", "count": 810, "type": "中跌"},
            {"range": "<-9%", "count": 8, "type": "跌停"},
        ]
    }

    return success_response(result)


@router.get("/north-flow")
async def get_north_flow_stats(days: int = Query(30, description="查询天数")):
    """获取北向资金统计"""
    start_date = date.today() - timedelta(days=days)

    # 模拟历史数据
    history = []
    base_flow = 25.5
    for i in range(days):
        d = start_date + timedelta(days=i)
        # 模拟波动
        flow = base_flow + (i % 7 - 3) * 8 + (i % 3) * 2
        history.append({
            "date": d.isoformat(),
            "flow": round(flow, 2),
            "status": "流入" if flow > 0 else "流出"
        })

    # 统计汇总
    total_inflow = sum(h["flow"] for h in history if h["flow"] > 0)
    total_outflow = sum(abs(h["flow"]) for h in history if h["flow"] < 0)
    net_flow = total_inflow - total_outflow

    return success_response({
        "days": days,
        "history": history[-10:],  # 返回最近10天
        "summary": {
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "net_flow": round(net_flow, 2),
            "avg_daily_flow": round(net_flow / days, 2),
        }
    })


@router.get("/sector-heat")
async def get_sector_heat(limit: int = Query(10, description="返回数量")):
    """获取板块热度排行"""
    sectors = [
        {"sector": "人工智能", "heat": 95, "change_avg": 3.5, "volume_ratio": 2.5, "leading_stock": "科大讯飞", "stocks_count": 45},
        {"sector": "机器人", "heat": 88, "change_avg": 2.8, "volume_ratio": 2.2, "leading_stock": "埃斯顿", "stocks_count": 32},
        {"sector": "算力", "heat": 82, "change_avg": 2.2, "volume_ratio": 1.8, "leading_stock": "寒武纪", "stocks_count": 28},
        {"sector": "新能源", "heat": 75, "change_avg": 1.5, "volume_ratio": 1.5, "leading_stock": "宁德时代", "stocks_count": 85},
        {"sector": "半导体", "heat": 68, "change_avg": 1.2, "volume_ratio": 1.3, "leading_stock": "韦尔股份", "stocks_count": 56},
        {"sector": "医药", "heat": 55, "change_avg": 0.8, "volume_ratio": 1.1, "leading_stock": "恒瑞医药", "stocks_count": 120},
        {"sector": "消费", "heat": 48, "change_avg": 0.5, "volume_ratio": 0.9, "leading_stock": "美的集团", "stocks_count": 78},
        {"sector": "金融", "heat": 35, "change_avg": -0.5, "volume_ratio": 0.7, "leading_stock": "招商银行", "stocks_count": 45},
        {"sector": "地产", "heat": 25, "change_avg": -1.5, "volume_ratio": 0.5, "leading_stock": "万科A", "stocks_count": 38},
        {"sector": "煤炭", "heat": 32, "change_avg": -0.8, "volume_ratio": 0.6, "leading_stock": "中国神华", "stocks_count": 22},
    ]

    return success_response(sectors[:limit])


@router.get("/strength")
async def get_market_strength():
    """获取市场强弱指数"""
    # 市场强弱指数计算（综合涨跌比例、成交量变化、北向资金等）
    rise_ratio = 44.2
    volume_change = 15.7
    north_flow_status = 1  # 流入为1，流出为-1

    # 计算强弱指数 (0-100)
    strength = (rise_ratio * 0.4 + (50 + volume_change) * 0.3 + (50 + north_flow_status * 25) * 0.3)

    # 确定等级
    if strength >= 70:
        level = "强势"
    elif strength >= 55:
        level = "中性偏强"
    elif strength >= 45:
        level = "中性"
    elif strength >= 30:
        level = "中性偏弱"
    else:
        level = "弱势"

    return success_response({
        "value": round(strength, 2),
        "level": level,
        "components": {
            "rise_fall_score": rise_ratio,
            "volume_score": 50 + volume_change,
            "flow_score": 50 + north_flow_status * 25,
        },
        "trend": "上升" if strength > 50 else "下降",
        "suggestion": "适合积极操作" if strength >= 55 else "谨慎操作" if strength >= 45 else "观望为主"
    })