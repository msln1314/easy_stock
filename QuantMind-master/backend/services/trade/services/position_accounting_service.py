"""
Position Accounting Service - 持仓核算服务

提供实时盈亏核算和持仓结构分析功能。
"""

import logging
from collections import defaultdict
from decimal import Decimal
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PositionAccountingService:
    """持仓核算服务"""

    # 行业板块映射（申万一级 -> 大板块）
    SECTOR_MAPPING = {
        # 金融板块
        "银行": "金融",
        "证券": "金融",
        "保险": "金融",
        "多元金融": "金融",
        # 科技板块
        "计算机": "科技",
        "电子": "科技",
        "通信": "科技",
        "传媒": "科技",
        # 消费板块
        "食品饮料": "消费",
        "家用电器": "消费",
        "纺织服装": "消费",
        "商贸零售": "消费",
        "医药生物": "消费",
        # 制造板块
        "机械设备": "制造",
        "电气设备": "制造",
        "汽车": "制造",
        "化工": "制造",
        # 基建板块
        "建筑装饰": "基建",
        "建筑材料": "基建",
        "房地产": "基建",
        "公用事业": "基建",
        "交通运输": "基建",
        # 能源板块
        "采掘": "能源",
        "石油石化": "能源",
        "煤炭": "能源",
        "电力": "能源",
        # 其他
        "钢铁": "制造",
        "有色金属": "制造",
        "农林牧渔": "消费",
        "国防军工": "制造",
        "综合": "其他",
    }

    def __init__(self):
        self._industry_cache: Dict[str, str] = {}

    def calculate_realtime_pnl(
        self,
        positions: List[Dict[str, Any]],
        total_asset: float,
        today_pnl_raw: float = 0.0,
        total_pnl_raw: float = 0.0,
        initial_equity: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        计算实时盈亏核算指标。

        Args:
            positions: 持仓列表，每个包含 symbol, volume, cost_price, last_price, market_value, floating_pnl 等
            total_asset: 总资产
            today_pnl_raw: 券商上报的今日盈亏原始值
            total_pnl_raw: 券商上报的累计盈亏原始值
            initial_equity: 初始资金（用于计算收益率）

        Returns:
            盈亏核算指标字典
        """
        # 计算浮动盈亏汇总
        total_floating_pnl = 0.0
        profitable_count = 0
        losing_count = 0
        total_cost = 0.0

        for pos in positions:
            floating_pnl = float(pos.get("floating_pnl") or pos.get("profit") or 0)
            cost_price = float(pos.get("cost_price") or pos.get("avg_cost") or 0)
            volume = float(pos.get("volume") or pos.get("quantity") or pos.get("shares") or 0)

            total_floating_pnl += floating_pnl
            total_cost += cost_price * volume

            if floating_pnl > 0:
                profitable_count += 1
            elif floating_pnl < 0:
                losing_count += 1

        # 计算盈亏比例
        floating_pnl_pct = total_floating_pnl / total_cost if total_cost > 0 else 0

        # 今日盈亏
        today_pnl = today_pnl_raw
        today_pnl_pct = today_pnl / total_asset if total_asset > 0 else 0

        # 累计盈亏（优先使用券商上报值，否则使用浮动盈亏累计）
        total_pnl = total_pnl_raw if total_pnl_raw != 0 else total_floating_pnl
        total_pnl_pct = total_pnl / initial_equity if initial_equity and initial_equity > 0 else 0

        # 胜率计算
        total_position_count = profitable_count + losing_count
        win_rate = profitable_count / total_position_count if total_position_count > 0 else 0

        return {
            "floating_pnl": round(total_floating_pnl, 2),
            "floating_pnl_pct": round(floating_pnl_pct, 4),
            "today_pnl": round(today_pnl, 2),
            "today_pnl_pct": round(today_pnl_pct, 4),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 4),
            "win_rate": round(win_rate, 4),
            "profitable_count": profitable_count,
            "losing_count": losing_count,
            "total_position_count": total_position_count,
        }

    def analyze_position_structure(
        self,
        positions: List[Dict[str, Any]],
        total_asset: float,
    ) -> Dict[str, Any]:
        """
        分析持仓结构。

        Args:
            positions: 持仓列表
            total_asset: 总资产

        Returns:
            持仓结构分析结果
        """
        if not positions:
            return {
                "industry_distribution": [],
                "sector_concentration": {},
                "risk_exposure": {},
                "position_count": 0,
                "top_holdings": [],
            }

        # 按行业聚合
        industry_values: Dict[str, float] = defaultdict(float)
        industry_positions: Dict[str, List[Dict]] = defaultdict(list)

        # 按板块聚合
        sector_values: Dict[str, float] = defaultdict(float)

        # 多空统计
        long_value = 0.0
        short_value = 0.0

        # 按市值排序用于 top_holdings
        sorted_positions = sorted(
            positions,
            key=lambda x: float(x.get("market_value") or x.get("value") or 0),
            reverse=True
        )

        for pos in positions:
            market_value = float(pos.get("market_value") or pos.get("value") or 0)
            symbol = str(pos.get("symbol") or pos.get("code") or "")
            name = str(pos.get("name") or pos.get("symbol_name") or symbol)

            # 获取行业（优先使用上报值，其次使用映射）
            industry = str(pos.get("industry") or "").strip()
            if not industry:
                industry = self._get_industry_from_symbol(symbol)

            # 获取板块
            sector = self._get_sector(industry)

            # 行业聚合
            industry_values[industry] += market_value
            industry_positions[industry].append(pos)

            # 板块聚合
            sector_values[sector] += market_value

            # 多空统计
            side = str(pos.get("side") or "").lower()
            if side == "short":
                short_value += market_value
            else:
                long_value += market_value

        # 计算行业分布权重
        total_market_value = sum(industry_values.values())
        industry_distribution = []
        for industry, value in sorted(industry_values.items(), key=lambda x: x[1], reverse=True):
            weight = value / total_market_value if total_market_value > 0 else 0
            industry_distribution.append({
                "industry": industry,
                "weight": round(weight, 4),
                "value": round(value, 2),
                "position_count": len(industry_positions[industry]),
            })

        # 计算板块集中度
        sector_concentration = {}
        for sector, value in sorted(sector_values.items(), key=lambda x: x[1], reverse=True):
            weight = value / total_asset if total_asset > 0 else 0
            sector_concentration[f"{sector}_sector_weight"] = round(weight, 4)

        # 计算风险敞口
        total_exposure = long_value + short_value
        long_exposure = long_value / total_asset if total_asset > 0 else 0
        short_exposure = short_value / total_asset if total_asset > 0 else 0
        net_exposure = (long_value - short_value) / total_asset if total_asset > 0 else 0

        risk_exposure = {
            "long_exposure": round(long_exposure, 4),
            "short_exposure": round(short_exposure, 4),
            "net_exposure": round(net_exposure, 4),
            "long_value": round(long_value, 2),
            "short_value": round(short_value, 2),
        }

        # Top 持仓（前5名）
        top_holdings = []
        for pos in sorted_positions[:5]:
            market_value = float(pos.get("market_value") or pos.get("value") or 0)
            weight = market_value / total_asset if total_asset > 0 else 0
            top_holdings.append({
                "symbol": str(pos.get("symbol") or pos.get("code") or ""),
                "name": str(pos.get("name") or pos.get("symbol_name") or ""),
                "weight": round(weight, 4),
                "market_value": round(market_value, 2),
            })

        return {
            "industry_distribution": industry_distribution,
            "sector_concentration": sector_concentration,
            "risk_exposure": risk_exposure,
            "position_count": len(positions),
            "top_holdings": top_holdings,
        }

    def _get_industry_from_symbol(self, symbol: str) -> str:
        """
        根据股票代码推断行业（简化版本）。

        Args:
            symbol: 股票代码（如 600036.SH）

        Returns:
            行业名称
        """
        # 简化映射：根据代码前缀推断
        code = symbol.split(".")[0] if "." in symbol else symbol

        # 银行股
        if code.startswith("600") and len(code) == 6:
            # 简化判断
            if code in ("600000", "600036", "600016", "600015", "601398", "601939"):
                return "银行"

        return "其他"

    def _get_sector(self, industry: str) -> str:
        """
        根据行业获取所属板块。

        Args:
            industry: 行业名称

        Returns:
            板块名称
        """
        return self.SECTOR_MAPPING.get(industry, "其他")


# 全局单例
position_accounting_service = PositionAccountingService()