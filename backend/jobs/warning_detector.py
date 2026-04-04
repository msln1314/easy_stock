"""
预警检测任务模块（集成通知功能）

定期检查监控股票池中的股票，根据预警条件生成预警通知，并发送多渠道通知
"""
import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional

from models.monitor_pool import MonitorStock
from models.warning import WarningCondition, WarningStockPool
from models.notification import NotificationChannel
from utils.warning_evaluator import warning_evaluator
from services.notification_service import notification_service
from config.settings import QMT_SERVICE_URL

logger = logging.getLogger(__name__)


async def get_kline_from_stock_service(
    stock_code: str,
    period: str = "d",
    days: int = 100
) -> List[Dict]:
    """
    从 qmt-service 获取K线数据

    Args:
        stock_code: 股票代码，如 '000001'
        period: 周期 d-日线, w-周线, m-月线
        days: 获取最近N天数据

    Returns:
        K线数据列表
    """
    try:
        # 转换股票代码格式 (000001 -> 000001.SZ)
        if '.' not in stock_code:
            if stock_code.startswith('6'):
                stock_code = f"{stock_code}.SH"
            else:
                stock_code = f"{stock_code}.SZ"

        async with httpx.AsyncClient(timeout=30) as client:
            # 调用 qmt-service 的K线接口
            url = f"{QMT_SERVICE_URL}/api/v1/quote/kline/{stock_code}"
            params = {
                "period": "1d",  # 日线
                "count": days
            }
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()

            # 转换为指标计算需要的格式
            klines = []
            for item in result.get("klines", []):
                klines.append({
                    "date": item.get("date", ""),
                    "open": float(item.get("open", 0)),
                    "high": float(item.get("high", 0)),
                    "low": float(item.get("low", 0)),
                    "close": float(item.get("close", 0)),
                    "volume": float(item.get("volume", 0)),
                })

            return klines

    except httpx.HTTPError as e:
        logger.error(f"获取K线数据失败: {stock_code}, 错误: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"获取K线数据异常: {stock_code}, 错误: {str(e)}")
        return []


async def get_realtime_quote(stock_code: str) -> Optional[Dict]:
    """
    获取实时行情 (从qmt-service)

    Args:
        stock_code: 股票代码

    Returns:
        实时行情数据
    """
    try:
        # 转换股票代码格式
        if '.' not in stock_code:
            if stock_code.startswith('6'):
                stock_code = f"{stock_code}.SH"
            else:
                stock_code = f"{stock_code}.SZ"

        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{QMT_SERVICE_URL}/api/v1/quote/l2/{stock_code}"
            response = await client.get(url)
            response.raise_for_status()
            quote = response.json()

            if quote:
                pre_close = quote.get("pre_close", 0)
                last_price = quote.get("price", 0)
                change_percent = 0
                if pre_close > 0:
                    change_percent = (last_price - pre_close) / pre_close * 100

                return {
                    "price": last_price,
                    "change_percent": change_percent,
                    "open": quote.get("open", 0),
                    "high": quote.get("high", 0),
                    "low": quote.get("low", 0),
                    "volume": quote.get("volume", 0),
                }
            return None
    except Exception as e:
        logger.error(f"获取实时行情失败: {stock_code}, 错误: {str(e)}")
        return None


async def detect_warnings():
    """
    预警检测主任务（集成通知发送）

    执行逻辑:
    1. 获取所有启用的监控股票
    2. 获取启用的预警条件
    3. 对每只股票检查每个预警条件
    4. 触发预警时写入预警股票池
    5. 发送多渠道通知
    """
    logger.info(f"[{datetime.now()}] 开始预警检测...")

    # 先检查是否有启用的通知渠道
    enabled_channels = await NotificationChannel.filter(is_enabled=True).count()
    if enabled_channels > 0:
        logger.info(f"已启用 {enabled_channels} 个通知渠道")

    try:
        # 1. 获取启用的监控股票
        monitor_stocks = await MonitorStock.filter(is_active=True).all()

        if not monitor_stocks:
            logger.info("没有启用的监控股票")
            return {"success": True, "checked": 0, "triggered": 0, "notified": 0}

        # 2. 获取启用的预警条件
        conditions = await WarningCondition.filter(is_enabled=True).all()

        if not conditions:
            logger.info("没有启用的预警条件")
            return {"success": True, "checked": 0, "triggered": 0, "notified": 0}

        checked_count = 0
        triggered_count = 0
        notified_count = 0
        notification_results = []

        # 3. 遍历监控股票
        for stock in monitor_stocks:
            # 获取股票关联的条件，如果没有指定则使用全部启用条件
            stock_conditions = []
            if stock.conditions:
                condition_keys = stock.conditions if isinstance(stock.conditions, list) else []
                stock_conditions = [c for c in conditions if c.condition_key in condition_keys]
            if not stock_conditions:
                stock_conditions = conditions

            if not stock_conditions:
                continue

            # 获取K线数据
            klines = await get_kline_from_stock_service(stock.stock_code, period="d", days=100)

            if not klines or len(klines) < 30:
                logger.warning(f"股票 {stock.stock_code} K线数据不足，跳过检测")
                continue

            checked_count += 1

            # 获取实时行情更新价格
            quote = await get_realtime_quote(stock.stock_code)
            if quote:
                stock.last_price = quote.get("price")
                stock.change_percent = quote.get("change_percent")
                stock.last_check_time = datetime.now()
                await stock.save()

            # 检查每个预警条件
            for condition in stock_conditions:
                try:
                    # 构建条件字典
                    condition_dict = {
                        "indicator_key": condition.indicator_key,
                        "indicator_key2": condition.indicator_key2,
                        "condition_rule": condition.condition_rule,
                    }

                    # 评估预警条件
                    triggered, trigger_value = warning_evaluator.evaluate(klines, condition_dict)

                    if triggered:
                        # 检查是否已存在相同预警（当天内）
                        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        existing = await WarningStockPool.filter(
                            stock_code=stock.stock_code,
                            condition_key=condition.condition_key,
                            trigger_time__gte=today_start
                        ).first()

                        if existing:
                            logger.debug(f"股票 {stock.stock_code} 已存在相同预警: {condition.condition_name}")
                            continue

                        # 写入预警股票池
                        warning = await WarningStockPool.create(
                            stock_code=stock.stock_code,
                            stock_name=stock.stock_name,
                            price=stock.last_price,
                            change_percent=stock.change_percent,
                            condition_key=condition.condition_key,
                            condition_name=condition.condition_name,
                            warning_level=condition.priority,
                            trigger_time=datetime.now(),
                            trigger_value=trigger_value,
                            is_handled=False
                        )

                        triggered_count += 1
                        logger.info(
                            f"触发预警: {stock.stock_code} {stock.stock_name} - "
                            f"{condition.condition_name}, 触发值: {trigger_value}"
                        )

                        # 发送通知
                        stock_info = {
                            "monitor_type": stock.monitor_type,
                            "entry_price": float(stock.entry_price) if stock.entry_price else None
                        }

                        notification_result = await notification_service.send_notification(
                            warning,
                            stock_info=stock_info
                        )

                        if notification_result:
                            notified_count += len([r for r in notification_result if r["success"]])
                            notification_results.append({
                                "stock_code": stock.stock_code,
                                "results": notification_result
                            })

                except Exception as e:
                    logger.error(f"评估预警条件失败: {condition.condition_key}, 错误: {str(e)}")

        logger.info(f"预警检测完成: 检查 {checked_count} 只股票, 触发 {triggered_count} 条预警, 发送 {notified_count} 条通知")

        return {
            "success": True,
            "checked": checked_count,
            "triggered": triggered_count,
            "notified": notified_count,
            "notifications": notification_results,
            "message": f"检测完成: 检查 {checked_count} 只股票, 触发 {triggered_count} 条预警, 发送 {notified_count} 条通知"
        }

    except Exception as e:
        logger.error(f"预警检测失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"预警检测失败: {str(e)}"
        }


async def detect_single_stock(stock_code: str) -> Dict[str, Any]:
    """
    检测单只股票的预警

    Args:
        stock_code: 股票代码

    Returns:
        检测结果
    """
    stock = await MonitorStock.filter(stock_code=stock_code, is_active=True).first()
    if not stock:
        return {"success": False, "message": "股票不在监控池中"}

    conditions = await WarningCondition.filter(is_enabled=True).all()
    if not conditions:
        return {"success": False, "message": "没有启用的预警条件"}

    klines = await get_kline_from_stock_service(stock_code, period="d", days=100)
    if not klines:
        return {"success": False, "message": "获取K线数据失败"}

    triggered_list = []

    for condition in conditions:
        condition_dict = {
            "indicator_key": condition.indicator_key,
            "indicator_key2": condition.indicator_key2,
            "condition_rule": condition.condition_rule,
        }

        triggered, trigger_value = warning_evaluator.evaluate(klines, condition_dict)

        if triggered:
            triggered_list.append({
                "condition_key": condition.condition_key,
                "condition_name": condition.condition_name,
                "warning_level": condition.priority,
                "trigger_value": trigger_value
            })

    return {
        "success": True,
        "stock_code": stock_code,
        "stock_name": stock.stock_name,
        "triggered_count": len(triggered_list),
        "warnings": triggered_list
    }