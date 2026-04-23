"""
Industry Mapper - 行业分类映射工具

根据股票代码查询行业分类，支持申万行业分类标准。
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class IndustryMapper:
    """行业分类映射器"""

    # 申万一级行业代码映射
    SW_INDUSTRIES = {
        "01": "农林牧渔",
        "02": "采掘",
        "03": "化工",
        "04": "钢铁",
        "05": "有色金属",
        "06": "电子",
        "07": "家用电器",
        "08": "食品饮料",
        "09": "纺织服装",
        "10": "轻工制造",
        "11": "医药生物",
        "12": "公用事业",
        "13": "交通运输",
        "14": "房地产",
        "15": "商贸零售",
        "16": "休闲服务",
        "17": "银行",
        "18": "非银金融",
        "19": "综合",
        "20": "建筑材料",
        "21": "建筑装饰",
        "22": "电气设备",
        "23": "机械设备",
        "24": "国防军工",
        "25": "计算机",
        "26": "传媒",
        "27": "通信",
        "28": "汽车",
    }

    # 股票代码到行业的手动映射（常用股票）
    STOCK_INDUSTRY_MAP = {
        # 银行
        "600000.SH": "银行",
        "600016.SH": "银行",
        "600036.SH": "银行",
        "601398.SH": "银行",
        "601939.SH": "银行",
        "601288.SH": "银行",
        "601328.SH": "银行",
        "601988.SH": "银行",
        "601818.SH": "银行",
        "000001.SZ": "银行",
        # 证券
        "600030.SH": "证券",
        "601211.SH": "证券",
        "601688.SH": "证券",
        "600837.SH": "证券",
        "000776.SZ": "证券",
        # 保险
        "601318.SH": "保险",
        "601601.SH": "保险",
        # 酒类
        "600519.SH": "食品饮料",
        "000858.SZ": "食品饮料",
        "000568.SZ": "食品饮料",
        # 医药
        "600276.SH": "医药生物",
        "000661.SZ": "医药生物",
        "300760.SZ": "医药生物",
        # 科技
        "000063.SZ": "通信",
        "002415.SZ": "电子",
        "300059.SZ": "计算机",
        "600584.SH": "电子",
        # 汽车
        "000625.SZ": "汽车",
        "600104.SH": "汽车",
        # 地产
        "000002.SZ": "房地产",
        "600048.SH": "房地产",
        # 能源
        "601857.SH": "石油石化",
        "600028.SH": "石油石化",
    }

    def __init__(self, cache_file: Optional[Path] = None):
        """
        初始化行业映射器。

        Args:
            cache_file: 行业数据缓存文件路径（可选）
        """
        self._cache: Dict[str, str] = {}
        self._cache_file = cache_file

        # 加载手动映射作为初始缓存
        self._cache.update(self.STOCK_INDUSTRY_MAP)

        # 尝试从缓存文件加载
        if cache_file and cache_file.exists():
            self._load_cache(cache_file)

    def _load_cache(self, cache_file: Path) -> None:
        """从缓存文件加载行业数据"""
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._cache.update(data)
                    logger.info(f"Loaded {len(data)} industry mappings from cache")
        except Exception as e:
            logger.warning(f"Failed to load industry cache: {e}")

    def _save_cache(self) -> None:
        """保存缓存到文件"""
        if self._cache_file:
            try:
                with open(self._cache_file, "w", encoding="utf-8") as f:
                    json.dump(self._cache, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Failed to save industry cache: {e}")

    def get_industry(self, symbol: str) -> str:
        """
        获取股票的行业分类。

        Args:
            symbol: 股票代码（如 600036.SH 或 SH600036）

        Returns:
            行业名称，未找到时返回 "其他"
        """
        # 标准化符号格式
        normalized = self._normalize_symbol(symbol)

        # 从缓存查找
        if normalized in self._cache:
            return self._cache[normalized]

        # 从原始符号查找
        if symbol in self._cache:
            return self._cache[symbol]

        # 尝试从代码推断
        inferred = self._infer_industry(symbol)
        if inferred != "其他":
            # 缓存推断结果
            self._cache[normalized] = inferred
            logger.debug(f"Inferred industry for {symbol}: {inferred}")

        return inferred

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码格式"""
        symbol = symbol.strip().upper()

        # 处理 SH600036 -> 600036.SH
        if symbol.startswith("SH") and len(symbol) == 8:
            return f"{symbol[2:]}.SH"
        if symbol.startswith("SZ") and len(symbol) == 8:
            return f"{symbol[2:]}.SZ"
        if symbol.startswith("BJ") and len(symbol) == 8:
            return f"{symbol[2:]}.BJ"

        return symbol

    def _infer_industry(self, symbol: str) -> str:
        """
        根据股票代码特征推断行业。

        Args:
            symbol: 股票代码

        Returns:
            推断的行业名称
        """
        code = symbol.split(".")[0] if "." in symbol else symbol
        exchange = symbol.split(".")[1] if "." in symbol else ""

        # 科创板（688开头）多为科技类
        if code.startswith("688"):
            return "电子"

        # 创业板（30开头）
        if code.startswith("30"):
            # 创业板多为新兴产业，需要更细的判断
            return "计算机"

        # 北交所（8开头）
        if exchange == "BJ" or code.startswith("8"):
            return "其他"

        return "其他"

    def update_industry(self, symbol: str, industry: str) -> None:
        """
        更新股票的行业分类。

        Args:
            symbol: 股票代码
            industry: 行业名称
        """
        normalized = self._normalize_symbol(symbol)
        self._cache[normalized] = industry
        self._save_cache()

    def batch_update(self, mapping: Dict[str, str]) -> None:
        """
        批量更新行业分类。

        Args:
            mapping: 股票代码 -> 行业名称的映射字典
        """
        for symbol, industry in mapping.items():
            normalized = self._normalize_symbol(symbol)
            self._cache[normalized] = industry
        self._save_cache()
        logger.info(f"Batch updated {len(mapping)} industry mappings")


# 全局单例（可在启动时配置缓存文件路径）
_industry_mapper_instance: Optional[IndustryMapper] = None


def get_industry_mapper(cache_file: Optional[Path] = None) -> IndustryMapper:
    """
    获取行业映射器单例。

    Args:
        cache_file: 缓存文件路径（可选）

    Returns:
        IndustryMapper 实例
    """
    global _industry_mapper_instance
    if _industry_mapper_instance is None:
        _industry_mapper_instance = IndustryMapper(cache_file)
    return _industry_mapper_instance


def get_industry(symbol: str) -> str:
    """
    快捷方法：获取股票行业。

    Args:
        symbol: 股票代码

    Returns:
        行业名称
    """
    return get_industry_mapper().get_industry(symbol)