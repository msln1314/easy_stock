"""
资金流向API接口

提供主力资金流入、板块资金流向等统计
"""
from typing import Optional, List
from fastapi import APIRouter, Query
from datetime import datetime, date, timedelta
from decimal import Decimal

from core.response import success_response
from core.qmt_client import qmt_client

router = APIRouter(prefix="/api/v1/fund-flow", tags=["资金流向"])


@router.get("/overview")
async def get_fund_flow_overview():
    """获取资金流向概览"""
    today = date.today()

    # 模拟数据（实际需要从数据源获取）
    # 可以从QMT或其他数据接口获取资金流向数据

    result = {
        # 今日资金流向
        "today_flow": {
            "main_inflow": 12500,  # 主力流入（万元）
            "main_outflow": 8800,  # 主力流出（万元）
            "main_net": 3700,  # 主力净流入
            "retail_inflow": 5500,
            "retail_outflow": 7200,
            "retail_net": -1700,
        },

        # 板块资金流向
        "sector_flow": [
            {"sector": "科技", "net_flow": 2800, "rank": 1},
            {"sector": "医药", "net_flow": 1500, "rank": 2},
            {"sector": "消费", "net_flow": 1200, "rank": 3},
            {"sector": "金融", "net_flow": -800, "rank": -1},
            {"sector": "地产", "net_flow": -1500, "rank": -2},
        ],

        # 个股资金TOP5
        "stock_flow_top5": [
            {"stock_code": "000001", "stock_name": "平安银行", "net_flow": 850, "change_pct": 2.5},
            {"stock_code": "600036", "stock_name": "招商银行", "net_flow": 720, "change_pct": 1.8},
            {"stock_code": "000333", "stock_name": "美的集团", "net_flow": 560, "change_pct": 1.2},
            {"stock_code": "002475", "stock_name": "立讯精密", "net_flow": 480, "change_pct": 0.9},
            {"stock_code": "300750", "stock_name": "宁德时代", "net_flow": 350, "change_pct": 0.6},
        ],

        # 个股资金流出TOP5
        "stock_flow_bottom5": [
            {"stock_code": "600519", "stock_name": "贵州茅台", "net_flow": -420, "change_pct": -0.8},
            {"stock_code": "601318", "stock_name": "中国平安", "net_flow": -380, "change_pct": -0.6},
            {"stock_code": "000002", "stock_name": "万科A", "net_flow": -320, "change_pct": -1.2},
            {"stock_code": "600000", "stock_name": "浦发银行", "net_flow": -280, "change_pct": -0.4},
            {"stock_code": "601166", "stock_name": "兴业银行", "net_flow": -250, "change_pct": -0.3},
        ],

        # 大单统计
        "large_order": {
            "buy_count": 125,
            "sell_count": 88,
            "buy_amount": 8500,
            "sell_amount": 6200,
        },

        # 时间统计
        "today_date": today.isoformat(),
    }

    return success_response(result)


@router.get("/sector-flow")
async def get_sector_fund_flow(limit: int = Query(10, description="返回数量")):
    """获取板块资金流向"""
    # 模拟数据
    sectors = [
        {"sector": "科技", "sector_name": "科技板块", "net_flow": 2800, "inflow": 4500, "outflow": 1700, "change_pct": 1.5, "leading_stock": "立讯精密"},
        {"sector": "医药", "sector_name": "医药板块", "net_flow": 1500, "inflow": 3200, "outflow": 1700, "change_pct": 0.8, "leading_stock": "恒瑞医药"},
        {"sector": "消费", "sector_name": "消费板块", "net_flow": 1200, "inflow": 2800, "outflow": 1600, "change_pct": 0.6, "leading_stock": "美的集团"},
        {"sector": "新能源", "sector_name": "新能源板块", "net_flow": 950, "inflow": 2200, "outflow": 1250, "change_pct": 0.4, "leading_stock": "宁德时代"},
        {"sector": "半导体", "sector_name": "半导体板块", "net_flow": 800, "inflow": 1800, "outflow": 1000, "change_pct": 0.3, "leading_stock": "韦尔股份"},
        {"sector": "金融", "sector_name": "金融板块", "net_flow": -800, "inflow": 1200, "outflow": 2000, "change_pct": -0.5, "leading_stock": "招商银行"},
        {"sector": "地产", "sector_name": "地产板块", "net_flow": -1500, "inflow": 800, "outflow": 2300, "change_pct": -1.2, "leading_stock": "万科A"},
        {"sector": "钢铁", "sector_name": "钢铁板块", "net_flow": -600, "inflow": 500, "outflow": 1100, "change_pct": -0.3, "leading_stock": "宝钢股份"},
        {"sector": "煤炭", "sector_name": "煤炭板块", "net_flow": -400, "inflow": 400, "outflow": 800, "change_pct": -0.2, "leading_stock": "中国神华"},
        {"sector": "有色", "sector_name": "有色金属", "net_flow": -200, "inflow": 600, "outflow": 800, "change_pct": 0.1, "leading_stock": "江西铜业"},
    ]

    return success_response(sectors[:limit])


@router.get("/stock-flow")
async def get_stock_fund_flow(
    direction: str = Query("inflow", description="方向: inflow-流入, outflow-流出"),
    limit: int = Query(20, description="返回数量")
):
    """获取个股资金流向"""
    # 模拟数据
    if direction == "inflow":
        stocks = [
            {"stock_code": "000001", "stock_name": "平安银行", "net_flow": 850, "change_pct": 2.5, "main_ratio": 65},
            {"stock_code": "600036", "stock_name": "招商银行", "net_flow": 720, "change_pct": 1.8, "main_ratio": 58},
            {"stock_code": "000333", "stock_name": "美的集团", "net_flow": 560, "change_pct": 1.2, "main_ratio": 52},
            {"stock_code": "002475", "stock_name": "立讯精密", "net_flow": 480, "change_pct": 0.9, "main_ratio": 48},
            {"stock_code": "300750", "stock_name": "宁德时代", "net_flow": 350, "change_pct": 0.6, "main_ratio": 42},
        ]
    else:
        stocks = [
            {"stock_code": "600519", "stock_name": "贵州茅台", "net_flow": -420, "change_pct": -0.8, "main_ratio": 35},
            {"stock_code": "601318", "stock_name": "中国平安", "net_flow": -380, "change_pct": -0.6, "main_ratio": 32},
            {"stock_code": "000002", "stock_name": "万科A", "net_flow": -320, "change_pct": -1.2, "main_ratio": 28},
            {"stock_code": "600000", "stock_name": "浦发银行", "net_flow": -280, "change_pct": -0.4, "main_ratio": 25},
            {"stock_code": "601166", "stock_name": "兴业银行", "net_flow": -250, "change_pct": -0.3, "main_ratio": 22},
        ]

    return success_response(stocks[:limit])


@router.get("/large-order")
async def get_large_order_stats():
    """获取大单交易统计"""
    # 模拟数据
    result = {
        "today": {
            "super_buy": {"count": 12, "amount": 5500},  # 超大单买入
            "super_sell": {"count": 5, "amount": 2800},  # 超大单卖出
            "big_buy": {"count": 125, "amount": 8500},  # 大单买入
            "big_sell": {"count": 88, "amount": 6200},  # 大单卖出
            "medium_buy": {"count": 350, "amount": 4200},  # 中单买入
            "medium_sell": {"count": 280, "amount": 3800},  # 中单卖出
            "small_buy": {"count": 850, "amount": 2800},  # 小单买入
            "small_sell": {"count": 720, "amount": 3200},  # 小单卖出
        },
        "summary": {
            "main_net": 3700,  # 主力净流入 = 超大单 + 大单
            "retail_net": -1700,  # 散户净流入 = 中单 + 小单
        }
    }

    return success_response(result)