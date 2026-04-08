"""
交易审计服务

对交易请求进行安全审核，确保符合红线规则
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger
from tortoise.expressions import Q

from models.trade_red_line import TradeRedLine, TradeAuditLog, PRESET_RED_LINES
from models.sys_config import SysConfig
from core.qmt_client import qmt_client


# 红线开关配置KEY
RED_LINE_SWITCH_KEY = "trade_red_line_enabled"


class TradeAuditService:
    """交易审计服务"""

    def __init__(self):
        self._rules_cache: Optional[List[TradeRedLine]] = None
        self._cache_time: Optional[datetime] = None
        self._switch_cache: Optional[bool] = None
        self._switch_cache_time: Optional[datetime] = None

    async def is_red_line_enabled(self) -> bool:
        """
        检查红线是否启用

        Returns:
            bool: True-启用红线审核，False-禁用红线审核
        """
        # 使用缓存，每30秒刷新一次
        if self._switch_cache is not None and self._switch_cache_time:
            if datetime.now() - self._switch_cache_time < timedelta(seconds=30):
                return self._switch_cache

        # 从数据库读取配置
        config = await SysConfig.filter(key=RED_LINE_SWITCH_KEY).first()

        if config:
            # 配置值: "true"/"false" 或 "1"/"0"
            value = config.value.lower()
            self._switch_cache = value in ("true", "1", "yes", "on")
        else:
            # 默认启用红线
            self._switch_cache = True

        self._switch_cache_time = datetime.now()
        return self._switch_cache

    async def set_red_line_enabled(self, enabled: bool, user_name: str = "system") -> bool:
        """
        设置红线开关状态

        Args:
            enabled: True-启用，False-禁用
            user_name: 操作用户名

        Returns:
            bool: 是否设置成功
        """
        config = await SysConfig.filter(key=RED_LINE_SWITCH_KEY).first()

        if config:
            await SysConfig.filter(key=RED_LINE_SWITCH_KEY).update(
                value="true" if enabled else "false"
            )
        else:
            await SysConfig.create(
                key=RED_LINE_SWITCH_KEY,
                value="true" if enabled else "false",
                category="security",
                data_type="plain",
                access_type="public",
                description="交易红线开关: true-启用审核, false-禁用审核"
            )

        # 清除缓存
        self._switch_cache = enabled
        self._switch_cache_time = datetime.now()

        logger.info(f"交易红线开关已{'启用' if enabled else '禁用'} by {user_name}")
        return True

    async def get_active_rules(self) -> List[TradeRedLine]:
        """获取所有生效的红线规则"""
        # 使用缓存，每分钟刷新一次
        if self._rules_cache and self._cache_time:
            if datetime.now() - self._cache_time < timedelta(minutes=1):
                return self._rules_cache

        rules = await TradeRedLine.filter(
            is_enabled=True
        ).order_by("severity", "rule_type")

        # 过滤生效期
        today = datetime.now().date()
        effective_rules = []
        for rule in rules:
            if rule.effective_from and today < rule.effective_from:
                continue
            if rule.effective_to and today > rule.effective_to:
                continue
            effective_rules.append(rule)

        self._rules_cache = effective_rules
        self._cache_time = datetime.now()
        return effective_rules

    async def audit_buy_request(
        self,
        stock_code: str,
        price: float,
        quantity: int,
        user_id: int = None,
        user_name: str = None
    ) -> Tuple[bool, Dict]:
        """
        审核买入请求

        Args:
            stock_code: 股票代码
            price: 委托价格
            quantity: 委托数量
            user_id: 用户ID
            user_name: 用户名

        Returns:
            (是否通过, 审核详情)
        """
        # 计算委托金额
        amount = price * quantity

        # 获取股票行情信息
        quote = await qmt_client.get_stock_quote(stock_code)
        stock_name = quote.get("stock_name", "")
        current_price = quote.get("current_price", price)
        change_percent = quote.get("change_percent", 0)
        limit_up = quote.get("limit_up", 0)
        limit_down = quote.get("limit_down", 0)

        # 获取账户信息
        balance = await qmt_client.get_balance()
        positions = await qmt_client.get_positions()

        total_asset = balance.get("total_asset", 0)
        available_cash = balance.get("available_cash", 0)
        market_value = balance.get("market_value", 0)

        # 获取今日已买入金额
        today_trades = await qmt_client.get_today_trades()
        today_buy_amount = sum(
            t.get("amount", 0) for t in today_trades.get("trades", [])
            if t.get("trade_type") == "buy"
        )
        today_buy_count = sum(
            1 for t in today_trades.get("trades", [])
            if t.get("trade_type") == "buy"
        )

        # 检查该股票当前持仓
        current_position = None
        current_position_value = 0
        for pos in positions.get("positions", []):
            if pos.get("stock_code") == stock_code:
                current_position = pos
                current_position_value = pos.get("market_value", 0)
                break

        # 审核上下文
        context = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "price": price,
            "quantity": quantity,
            "amount": amount,
            "current_price": current_price,
            "change_percent": change_percent,
            "limit_up": limit_up,
            "limit_down": limit_down,
            "total_asset": total_asset,
            "available_cash": available_cash,
            "market_value": market_value,
            "current_position": current_position,
            "current_position_value": current_position_value,
            "today_buy_amount": today_buy_amount,
            "today_buy_count": today_buy_count,
            "trade_time": datetime.now(),
        }

        # 执行规则检查
        rules = await self.get_active_rules()
        failed_rules = []
        warning_rules = []
        audit_details = {}

        for rule in rules:
            passed, detail = await self._check_rule(rule, context)
            audit_details[rule.rule_key] = {
                "passed": passed,
                "rule_name": rule.rule_name,
                "severity": rule.severity,
                "detail": detail
            }

            if not passed:
                if rule.severity == "critical":
                    failed_rules.append({
                        "rule_key": rule.rule_key,
                        "rule_name": rule.rule_name,
                        "reason": detail.get("reason", ""),
                        "value": detail.get("value"),
                        "limit": detail.get("limit")
                    })
                elif rule.severity == "warning":
                    warning_rules.append({
                        "rule_key": rule.rule_key,
                        "rule_name": rule.rule_name,
                        "reason": detail.get("reason", ""),
                        "value": detail.get("value"),
                        "limit": detail.get("limit")
                    })

            # 更新规则统计
            await TradeRedLine.filter(id=rule.id).update(
                total_checked=rule.total_checked + 1
            )
            if not passed and rule.severity == "critical":
                await TradeRedLine.filter(id=rule.id).update(
                    total_rejected=rule.total_rejected + 1
                )

        # 确定审核结果
        if failed_rules:
            audit_result = "rejected"
            reject_reason = failed_rules[0].get("reason", "不符合交易红线规则")
        elif warning_rules:
            audit_result = "warning"
            reject_reason = None
        else:
            audit_result = "passed"
            reject_reason = None

        # 记录审计日志
        await TradeAuditLog.create(
            trade_type="buy",
            stock_code=stock_code,
            stock_name=stock_name,
            price=price,
            quantity=quantity,
            amount=amount,
            audit_result=audit_result,
            failed_rules=failed_rules,
            warning_rules=warning_rules,
            reject_reason=reject_reason,
            audit_details=audit_details,
            user_id=user_id,
            user_name=user_name,
        )

        result = {
            "audit_result": audit_result,
            "passed": audit_result != "rejected",
            "failed_rules": failed_rules,
            "warning_rules": warning_rules,
            "reject_reason": reject_reason,
            "audit_details": audit_details,
            "stock_code": stock_code,
            "stock_name": stock_name,
            "price": price,
            "quantity": quantity,
            "amount": amount,
        }

        if failed_rules:
            logger.warning(f"买入请求被拒绝: {stock_code} {quantity}股 @ {price}, 原因: {reject_reason}")

        return audit_result != "rejected", result

    async def _check_rule(self, rule: TradeRedLine, context: Dict) -> Tuple[bool, Dict]:
        """
        检查单条规则

        Args:
            rule: 红线规则
            context: 审核上下文

        Returns:
            (是否通过, 检查详情)
        """
        config = rule.rule_config
        rule_type = rule.rule_type

        try:
            if rule_type == "position_limit":
                return self._check_position_limit(config, context)
            elif rule_type == "stock_blacklist":
                return self._check_stock_blacklist(config, context)
            elif rule_type == "amount_limit":
                return self._check_amount_limit(config, context)
            elif rule_type == "price_limit":
                return self._check_price_limit(config, context)
            elif rule_type == "time_limit":
                return self._check_time_limit(config, context)
            elif rule_type == "frequency_limit":
                return self._check_frequency_limit(config, context)
            elif rule_type == "risk_control":
                return self._check_risk_control(config, context)
            else:
                return True, {"reason": "未知的规则类型"}
        except Exception as e:
            logger.error(f"检查规则 {rule.rule_key} 失败: {e}")
            return True, {"reason": f"规则检查异常: {str(e)}"}

    def _check_position_limit(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查仓位限制"""
        # 单只股票仓位限制
        if "max_single_position_pct" in config:
            max_pct = config["max_single_position_pct"]
            total_asset = context.get("total_asset", 0)
            amount = context.get("amount", 0)
            current_position_value = context.get("current_position_value", 0)

            # 计算买入后的仓位
            new_position_value = current_position_value + amount
            position_pct = (new_position_value / total_asset * 100) if total_asset > 0 else 0

            if position_pct > max_pct:
                return False, {
                    "reason": f"单只股票仓位将达到 {position_pct:.1f}%，超过限制 {max_pct}%",
                    "value": round(position_pct, 2),
                    "limit": max_pct,
                    "current_position_pct": round(current_position_value / total_asset * 100, 2) if total_asset > 0 else 0
                }

        # 总仓位限制
        if "max_total_position_pct" in config:
            max_pct = config["max_total_position_pct"]
            total_asset = context.get("total_asset", 0)
            market_value = context.get("market_value", 0)
            amount = context.get("amount", 0)

            # 计算买入后的总仓位
            new_market_value = market_value + amount
            total_position_pct = (new_market_value / total_asset * 100) if total_asset > 0 else 0

            if total_position_pct > max_pct:
                return False, {
                    "reason": f"总仓位将达到 {total_position_pct:.1f}%，超过限制 {max_pct}%",
                    "value": round(total_position_pct, 2),
                    "limit": max_pct,
                    "current_total_pct": round(market_value / total_asset * 100, 2) if total_asset > 0 else 0
                }

        return True, {"reason": "仓位检查通过"}

    def _check_stock_blacklist(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查股票黑名单"""
        stock_code = context.get("stock_code", "")
        stock_name = context.get("stock_name", "")
        patterns = config.get("blacklist_patterns", [])

        # 检查股票名称/代码是否匹配黑名单模式
        for pattern in patterns:
            p = pattern.get("pattern", "")
            reason = pattern.get("reason", "")

            # 匹配ST股票
            if p.startswith("ST") or p.startswith("*ST"):
                if stock_name and ("ST" in stock_name or "*ST" in stock_name):
                    return False, {
                        "reason": f"股票 {stock_name} 是ST股票: {reason}",
                        "value": stock_name,
                        "limit": p
                    }

            # 匹配退市股票
            if p.startswith("退市"):
                if stock_name and "退市" in stock_name:
                    return False, {
                        "reason": f"股票 {stock_name} 是退市股票: {reason}",
                        "value": stock_name,
                        "limit": p
                    }

        # 检查新股限制
        if "ipo_days" in config:
            # 这里需要从行情数据判断是否是新股
            # 简化处理：如果股票名称包含"N"开头，视为新股
            if stock_name and stock_name.startswith("N"):
                ipo_days = config.get("ipo_days", 30)
                return False, {
                    "reason": f"新股 {stock_name} 上市未满 {ipo_days} 天",
                    "value": stock_name,
                    "limit": f"新股需满{ipo_days}天",
                    "note": config.get("new_stock_reason", "")
                }

        return True, {"reason": "黑名单检查通过"}

    def _check_amount_limit(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查金额限制"""
        amount = context.get("amount", 0)

        # 单笔金额限制
        if "max_single_amount" in config:
            max_amount = config["max_single_amount"]
            if amount > max_amount:
                return False, {
                    "reason": f"单笔金额 {amount:.2f}元 超过限制 {max_amount}元",
                    "value": round(amount, 2),
                    "limit": max_amount
                }

        # 日累计金额限制
        if "max_daily_buy_amount" in config:
            max_amount = config["max_daily_buy_amount"]
            today_buy_amount = context.get("today_buy_amount", 0)
            new_total = today_buy_amount + amount

            if new_total > max_amount:
                return False, {
                    "reason": f"今日累计买入将达到 {new_total:.2f}元，超过限制 {max_amount}元",
                    "value": round(new_total, 2),
                    "limit": max_amount,
                    "already_bought": round(today_buy_amount, 2)
                }

        return True, {"reason": "金额检查通过"}

    def _check_price_limit(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查价格限制"""
        price = context.get("price", 0)
        current_price = context.get("current_price", price)
        change_percent = context.get("change_percent", 0)
        limit_up = context.get("limit_up", 0)
        stock_code = context.get("stock_code", "")

        # 价格区间限制
        if "min_price" in config:
            min_price = config["min_price"]
            if current_price < min_price:
                return False, {
                    "reason": f"股票价格 {current_price:.2f}元 低于最低限制 {min_price}元: {config.get('min_price_reason', '')}",
                    "value": round(current_price, 2),
                    "limit": min_price
                }

        if "max_price" in config:
            max_price = config["max_price"]
            if current_price > max_price:
                return False, {
                    "reason": f"股票价格 {current_price:.2f}元 超过最高限制 {max_price}元: {config.get('max_price_reason', '')}",
                    "value": round(current_price, 2),
                    "limit": max_price
                }

        # 涨停板限制
        if config.get("avoid_limit_up"):
            threshold_pct = config.get("limit_up_threshold_pct", 9.5)
            if change_percent >= threshold_pct:
                return False, {
                    "reason": f"股票涨幅已达 {change_percent:.2f}%，接近涨停，禁止买入",
                    "value": round(change_percent, 2),
                    "limit": threshold_pct,
                    "limit_up_price": round(limit_up, 2) if limit_up else None
                }

        return True, {"reason": "价格检查通过"}

    def _check_time_limit(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查时间限制"""
        trade_time = context.get("trade_time", datetime.now())
        hour = trade_time.hour
        minute = trade_time.minute

        # 开盘前几分钟限制
        if "avoid_first_minutes" in config:
            avoid_minutes = config["avoid_first_minutes"]
            # 早盘9:30开盘
            if hour == 9 and minute >= 30 and minute < 30 + avoid_minutes:
                return False, {
                    "reason": f"开盘后 {avoid_minutes} 分钟内禁止交易，当前时间 {hour}:{minute}",
                    "value": f"{hour}:{minute}",
                    "limit": f"9:30-{9}:{30+avoid_minutes}"
                }

        # 收盘前几分钟限制
        if "avoid_last_minutes" in config:
            avoid_minutes = config["avoid_last_minutes"]
            # 下午15:00收盘
            if hour == 14 and minute >= 60 - avoid_minutes:
                return False, {
                    "reason": f"收盘前 {avoid_minutes} 分钟内禁止交易，当前时间 {hour}:{minute}",
                    "value": f"{hour}:{minute}",
                    "limit": f"14:{60-avoid_minutes}-15:00"
                }

        # 允许的交易时段
        allowed_sessions = config.get("allowed_sessions", ["morning", "afternoon"])
        current_session = None
        if (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute < 30):
            current_session = "morning"
        elif hour == 13 or hour == 14:
            current_session = "afternoon"

        if current_session and current_session not in allowed_sessions:
            return False, {
                "reason": f"当前时段 {current_session} 不在允许的交易时段内",
                "value": current_session,
                "limit": allowed_sessions
            }

        return True, {"reason": "时间检查通过"}

    def _check_frequency_limit(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查频率限制"""
        today_buy_count = context.get("today_buy_count", 0)

        # 日内买入次数限制
        if "max_buy_per_day" in config:
            max_count = config["max_buy_per_day"]
            if today_buy_count >= max_count:
                return False, {
                    "reason": f"今日已买入 {today_buy_count} 次，达到限制 {max_count} 次",
                    "value": today_buy_count,
                    "limit": max_count
                }

        return True, {"reason": "频率检查通过"}

    def _check_risk_control(self, config: Dict, context: Dict) -> Tuple[bool, Dict]:
        """检查风控指标"""
        current_position = context.get("current_position")

        # 亏损股票禁止加仓
        if "max_loss_pct_before_add" in config and current_position:
            max_loss_pct = config["max_loss_pct_before_add"]
            profit_pct = current_position.get("profit_pct", 0)

            if profit_pct < max_loss_pct:
                return False, {
                    "reason": f"持仓已亏损 {abs(profit_pct):.2f}%，超过 {abs(max_loss_pct)}% 限制，禁止加仓",
                    "value": round(profit_pct, 2),
                    "limit": max_loss_pct,
                    "current_position": current_position
                }

        return True, {"reason": "风控检查通过"}

    async def init_preset_rules(self):
        """初始化预置红线规则和开关配置"""
        # 初始化红线开关配置
        switch_exists = await SysConfig.filter(key=RED_LINE_SWITCH_KEY).exists()
        if not switch_exists:
            await SysConfig.create(
                key=RED_LINE_SWITCH_KEY,
                value="true",  # 默认启用
                category="security",
                data_type="plain",
                access_type="public",
                description="交易红线开关: true-启用审核, false-禁用审核"
            )
            logger.info("初始化交易红线开关配置: 默认启用")

        # 初始化预置红线规则
        for preset in PRESET_RED_LINES:
            exists = await TradeRedLine.filter(rule_key=preset["rule_key"]).exists()
            if not exists:
                await TradeRedLine.create(**preset)
                logger.info(f"初始化红线规则: {preset['rule_key']}")

    async def get_audit_logs(
        self,
        stock_code: str = None,
        audit_result: str = None,
        user_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 50
    ) -> List[TradeAuditLog]:
        """查询审计日志"""
        query = TradeAuditLog.all()

        if stock_code:
            query = query.filter(stock_code=stock_code)
        if audit_result:
            query = query.filter(audit_result=audit_result)
        if user_id:
            query = query.filter(user_id=user_id)
        if start_date:
            query = query.filter(audit_time__gte=start_date)
        if end_date:
            query = query.filter(audit_time__lte=end_date)

        return await query.order_by("-audit_time").limit(limit)


# 单例
trade_audit_service = TradeAuditService()