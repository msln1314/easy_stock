"""
交易日志服务

提供统一的日志记录接口，支持各类交易行为的记录和查询
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta, date
from loguru import logger
from tortoise.expressions import Q

from models.trade_log import TradeLog, TradeLogSummary, TradeActionType


class TradeLogService:
    """交易日志服务"""

    async def log_action(
        self,
        action_type: str,
        action_name: str,
        action_source: str = "system",
        strategy_key: str = None,
        stock_code: str = None,
        stock_name: str = None,
        order_id: str = None,
        related_id: int = None,
        action_data: dict = None,
        result: str = None,
        result_message: str = None,
        error_message: str = None,
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None,
        ip_address: str = None,
        device_info: str = None,
        tags: list = None,
        remark: str = None
    ) -> TradeLog:
        """
        记录交易行为日志

        Args:
            action_type: 行为类型
            action_name: 行为名称
            action_source: 行为来源 system/user/ai/strategy
            strategy_key: 关联策略KEY
            stock_code: 股票代码
            stock_name: 股票名称
            order_id: 委托单号
            related_id: 关联记录ID
            action_data: 行为数据
            result: 结果 success/failed/pending/rejected
            result_message: 结果消息
            error_message: 错误信息
            user_id: 用户ID
            user_name: 用户名
            duration_ms: 执行耗时
            ip_address: IP地址
            device_info: 设备信息
            tags: 标签列表
            remark: 备注

        Returns:
            TradeLog: 创建的日志记录
        """
        try:
            log = await TradeLog.create(
                action_type=action_type,
                action_name=action_name,
                action_source=action_source,
                strategy_key=strategy_key,
                stock_code=stock_code,
                stock_name=stock_name,
                order_id=order_id,
                related_id=related_id,
                action_data=action_data,
                result=result,
                result_message=result_message,
                error_message=error_message,
                user_id=user_id,
                user_name=user_name,
                duration_ms=duration_ms,
                ip_address=ip_address,
                device_info=device_info,
                tags=tags,
                remark=remark
            )

            logger.debug(
                f"记录交易日志: {action_type} | {stock_code or 'N/A'} | "
                f"{result or 'pending'} | {result_message or ''}"
            )

            return log

        except Exception as e:
            logger.error(f"记录交易日志失败: {e}")
            return None

    # ==================== 快捷记录方法 ====================

    async def log_stock_pick(
        self,
        strategy_key: str,
        stocks_found: int,
        stocks_saved: int,
        stocks: list = None,
        action_source: str = "strategy",
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None
    ) -> TradeLog:
        """记录选股行为"""
        return await self.log_action(
            action_type=TradeActionType.STOCK_PICK.value,
            action_name=f"策略 {strategy_key} 执行选股",
            action_source=action_source,
            strategy_key=strategy_key,
            action_data={
                "stocks_found": stocks_found,
                "stocks_saved": stocks_saved,
                "stocks": stocks or [],
            },
            result="success" if stocks_saved > 0 else "failed",
            result_message=f"发现 {stocks_found} 只股票，保存 {stocks_saved} 只",
            user_id=user_id,
            user_name=user_name,
            duration_ms=duration_ms,
            tags=["选股", strategy_key]
        )

    async def log_stock_pick_result(
        self,
        strategy_key: str,
        stock_code: str,
        stock_name: str,
        anomaly_type: str,
        confidence: float,
        anomaly_data: dict = None,
        action_source: str = "strategy"
    ) -> TradeLog:
        """记录选股结果"""
        return await self.log_action(
            action_type=TradeActionType.STOCK_PICK_RESULT.value,
            action_name=f"选股结果: {stock_name}",
            action_source=action_source,
            strategy_key=strategy_key,
            stock_code=stock_code,
            stock_name=stock_name,
            action_data={
                "anomaly_type": anomaly_type,
                "confidence": confidence,
                "anomaly_data": anomaly_data,
            },
            result="success",
            tags=["选股结果", strategy_key, anomaly_type]
        )

    async def log_buy_request(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        amount: float,
        order_type: str = "limit",
        user_id: int = None,
        user_name: str = None,
        ip_address: str = None
    ) -> TradeLog:
        """记录买入请求"""
        return await self.log_action(
            action_type=TradeActionType.BUY_REQUEST.value,
            action_name=f"买入请求: {stock_name}",
            action_source="user",
            stock_code=stock_code,
            stock_name=stock_name,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": amount,
                "order_type": order_type,
            },
            result="pending",
            result_message=f"请求买入 {stock_code} {quantity}股 @ {price}",
            user_id=user_id,
            user_name=user_name,
            ip_address=ip_address,
            tags=["买入", "请求"]
        )

    async def log_buy_audit(
        self,
        stock_code: str,
        stock_name: str,
        passed: bool,
        failed_rules: list,
        warning_rules: list,
        audit_details: dict,
        related_id: int = None,
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None
    ) -> TradeLog:
        """记录买入审核"""
        if passed:
            if warning_rules:
                action_type = TradeActionType.AUDIT_WARNING.value
                result = "success"
                message = "审核通过（有警告）"
            else:
                action_type = TradeActionType.AUDIT_PASS.value
                result = "success"
                message = "审核通过"
        else:
            action_type = TradeActionType.AUDIT_REJECT.value
            result = "rejected"
            message = failed_rules[0].get("reason", "审核拒绝") if failed_rules else "审核拒绝"

        return await self.log_action(
            action_type=action_type.value,
            action_name=f"买入审核: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            related_id=related_id,
            action_data={
                "passed": passed,
                "failed_rules": failed_rules,
                "warning_rules": warning_rules,
                "audit_details": audit_details,
            },
            result=result,
            result_message=message,
            user_id=user_id,
            user_name=user_name,
            duration_ms=duration_ms,
            tags=["审核", "买入"]
        )

    async def log_buy_executed(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        order_id: str,
        order_type: str = "limit",
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None
    ) -> TradeLog:
        """记录买入执行"""
        return await self.log_action(
            action_type=TradeActionType.BUY_EXECUTED.value,
            action_name=f"买入执行: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": price * quantity,
                "order_type": order_type,
            },
            result="pending",
            result_message=f"买入委托已提交，订单号: {order_id}",
            user_id=user_id,
            user_name=user_name,
            duration_ms=duration_ms,
            tags=["买入", "执行"]
        )

    async def log_buy_success(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        order_id: str,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录买入成功"""
        return await self.log_action(
            action_type=TradeActionType.BUY_SUCCESS.value,
            action_name=f"买入成功: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": price * quantity,
            },
            result="success",
            result_message=f"买入成功 {stock_code} {quantity}股 @ {price}",
            user_id=user_id,
            user_name=user_name,
            tags=["买入", "成功"]
        )

    async def log_buy_failed(
        self,
        stock_code: str,
        stock_name: str,
        order_id: str = None,
        error_message: str = None,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录买入失败"""
        return await self.log_action(
            action_type=TradeActionType.BUY_FAILED.value,
            action_name=f"买入失败: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            result="failed",
            error_message=error_message,
            user_id=user_id,
            user_name=user_name,
            tags=["买入", "失败"]
        )

    async def log_sell_request(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        order_type: str = "limit",
        user_id: int = None,
        user_name: str = None,
        ip_address: str = None
    ) -> TradeLog:
        """记录卖出请求"""
        return await self.log_action(
            action_type=TradeActionType.SELL_REQUEST.value,
            action_name=f"卖出请求: {stock_name}",
            action_source="user",
            stock_code=stock_code,
            stock_name=stock_name,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": price * quantity,
                "order_type": order_type,
            },
            result="pending",
            result_message=f"请求卖出 {stock_code} {quantity}股 @ {price}",
            user_id=user_id,
            user_name=user_name,
            ip_address=ip_address,
            tags=["卖出", "请求"]
        )

    async def log_sell_executed(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        order_id: str,
        order_type: str = "limit",
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None
    ) -> TradeLog:
        """记录卖出执行"""
        return await self.log_action(
            action_type=TradeActionType.SELL_EXECUTED.value,
            action_name=f"卖出执行: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": price * quantity,
                "order_type": order_type,
            },
            result="pending",
            result_message=f"卖出委托已提交，订单号: {order_id}",
            user_id=user_id,
            user_name=user_name,
            duration_ms=duration_ms,
            tags=["卖出", "执行"]
        )

    async def log_sell_success(
        self,
        stock_code: str,
        stock_name: str,
        price: float,
        quantity: int,
        order_id: str,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录卖出成功"""
        return await self.log_action(
            action_type=TradeActionType.SELL_SUCCESS.value,
            action_name=f"卖出成功: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            action_data={
                "price": price,
                "quantity": quantity,
                "amount": price * quantity,
            },
            result="success",
            result_message=f"卖出成功 {stock_code} {quantity}股 @ {price}",
            user_id=user_id,
            user_name=user_name,
            tags=["卖出", "成功"]
        )

    async def log_sell_failed(
        self,
        stock_code: str,
        stock_name: str,
        order_id: str = None,
        error_message: str = None,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录卖出失败"""
        return await self.log_action(
            action_type=TradeActionType.SELL_FAILED.value,
            action_name=f"卖出失败: {stock_name}",
            action_source="system",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            result="failed",
            error_message=error_message,
            user_id=user_id,
            user_name=user_name,
            tags=["卖出", "失败"]
        )

    async def log_cancel(
        self,
        order_id: str,
        success: bool,
        stock_code: str = None,
        stock_name: str = None,
        error_message: str = None,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录撤单"""
        action_type = TradeActionType.CANCEL_SUCCESS.value if success else TradeActionType.CANCEL_FAILED.value
        return await self.log_action(
            action_type=action_type.value,
            action_name=f"撤单: {order_id}",
            action_source="user",
            stock_code=stock_code,
            stock_name=stock_name,
            order_id=order_id,
            result="success" if success else "failed",
            result_message=f"撤单成功: {order_id}" if success else None,
            error_message=error_message,
            user_id=user_id,
            user_name=user_name,
            tags=["撤单"]
        )

    async def log_warning_trigger(
        self,
        stock_code: str,
        stock_name: str,
        condition_key: str,
        condition_name: str,
        warning_level: str,
        trigger_value: dict,
        strategy_key: str = None
    ) -> TradeLog:
        """记录预警触发"""
        return await self.log_action(
            action_type=TradeActionType.WARNING_TRIGGER.value,
            action_name=f"预警触发: {stock_name}",
            action_source="system",
            strategy_key=strategy_key,
            stock_code=stock_code,
            stock_name=stock_name,
            action_data={
                "condition_key": condition_key,
                "condition_name": condition_name,
                "warning_level": warning_level,
                "trigger_value": trigger_value,
            },
            result="success",
            result_message=f"预警 {condition_name} 触发",
            tags=["预警", condition_key, warning_level]
        )

    async def log_warning_handle(
        self,
        stock_code: str,
        stock_name: str,
        condition_key: str,
        handle_action: str,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录预警处理"""
        return await self.log_action(
            action_type=TradeActionType.WARNING_HANDLE.value,
            action_name=f"预警处理: {stock_name}",
            action_source="user",
            stock_code=stock_code,
            stock_name=stock_name,
            action_data={
                "condition_key": condition_key,
                "handle_action": handle_action,
            },
            result="success",
            result_message=f"预警处理: {handle_action}",
            user_id=user_id,
            user_name=user_name,
            tags=["预警处理", handle_action]
        )

    async def log_ai_chat(
        self,
        message: str,
        response: str,
        intent: str = None,
        user_id: int = None,
        user_name: str = None,
        duration_ms: int = None
    ) -> TradeLog:
        """记录AI对话"""
        return await self.log_action(
            action_type=TradeActionType.AI_CHAT.value,
            action_name="AI对话",
            action_source="ai",
            action_data={
                "message": message,
                "response": response,
                "intent": intent,
            },
            result="success",
            user_id=user_id,
            user_name=user_name,
            duration_ms=duration_ms,
            tags=["AI对话"]
        )

    async def log_config_change(
        self,
        config_type: str,
        config_key: str,
        old_value: str,
        new_value: str,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录配置变更"""
        return await self.log_action(
            action_type=TradeActionType.CONFIG_CHANGE.value,
            action_name=f"配置变更: {config_key}",
            action_source="user",
            action_data={
                "config_type": config_type,
                "config_key": config_key,
                "old_value": old_value,
                "new_value": new_value,
            },
            result="success",
            result_message=f"配置 {config_key} 已变更",
            user_id=user_id,
            user_name=user_name,
            tags=["配置变更", config_type]
        )

    async def log_rule_change(
        self,
        rule_key: str,
        rule_name: str,
        change_type: str,  # create/update/delete/enable/disable
        old_config: dict = None,
        new_config: dict = None,
        user_id: int = None,
        user_name: str = None
    ) -> TradeLog:
        """记录规则变更"""
        return await self.log_action(
            action_type=TradeActionType.RULE_CHANGE.value,
            action_name=f"规则变更: {rule_name}",
            action_source="user",
            action_data={
                "rule_key": rule_key,
                "change_type": change_type,
                "old_config": old_config,
                "new_config": new_config,
            },
            result="success",
            result_message=f"规则 {rule_key} {change_type}",
            user_id=user_id,
            user_name=user_name,
            tags=["规则变更", rule_key, change_type]
        )

    # ==================== 查询方法 ====================

    async def get_logs(
        self,
        action_type: str = None,
        stock_code: str = None,
        strategy_key: str = None,
        result: str = None,
        user_id: int = None,
        start_time: datetime = None,
        end_time: datetime = None,
        order_id: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TradeLog]:
        """查询交易日志"""
        query = TradeLog.all()

        if action_type:
            query = query.filter(action_type=action_type)
        if stock_code:
            query = query.filter(stock_code=stock_code)
        if strategy_key:
            query = query.filter(strategy_key=strategy_key)
        if result:
            query = query.filter(result=result)
        if user_id:
            query = query.filter(user_id=user_id)
        if start_time:
            query = query.filter(action_time__gte=start_time)
        if end_time:
            query = query.filter(action_time__lte=end_time)
        if order_id:
            query = query.filter(order_id=order_id)

        return await query.order_by("-action_time").offset(offset).limit(limit)

    async def get_log_by_id(self, log_id: int) -> Optional[TradeLog]:
        """根据ID获取日志"""
        return await TradeLog.filter(id=log_id).first()

    async def get_order_logs(self, order_id: str) -> List[TradeLog]:
        """获取某个订单的所有日志"""
        return await TradeLog.filter(order_id=order_id).order_by("action_time")

    async def get_stock_logs(
        self,
        stock_code: str,
        days: int = 7,
        limit: int = 50
    ) -> List[TradeLog]:
        """获取某股票的日志"""
        start_time = datetime.now() - timedelta(days=days)
        return await TradeLog.filter(
            stock_code=stock_code,
            action_time__gte=start_time
        ).order_by("-action_time").limit(limit)

    async def count_logs(
        self,
        action_type: str = None,
        result: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> int:
        """统计日志数量"""
        query = TradeLog.all()

        if action_type:
            query = query.filter(action_type=action_type)
        if result:
            query = query.filter(result=result)
        if start_time:
            query = query.filter(action_time__gte=start_time)
        if end_time:
            query = query.filter(action_time__lte=end_time)

        return await query.count()

    # ==================== 统计方法 ====================

    async def get_summary(self, summary_date: date) -> Optional[TradeLogSummary]:
        """获取某日的统计汇总"""
        return await TradeLogSummary.filter(summary_date=summary_date).first()

    async def generate_daily_summary(self, summary_date: date) -> TradeLogSummary:
        """生成每日统计汇总"""
        start_time = datetime.combine(summary_date, datetime.min.time())
        end_time = datetime.combine(summary_date, datetime.max.time())

        # 统计各项数据
        stock_pick_count = await self.count_logs(
            action_type=TradeActionType.STOCK_PICK.value,
            start_time=start_time, end_time=end_time
        )

        buy_request_count = await self.count_logs(
            action_type=TradeActionType.BUY_REQUEST.value,
            start_time=start_time, end_time=end_time
        )
        buy_success_count = await self.count_logs(
            action_type=TradeActionType.BUY_SUCCESS.value,
            result="success",
            start_time=start_time, end_time=end_time
        )
        buy_failed_count = await self.count_logs(
            action_type=TradeActionType.BUY_FAILED.value,
            start_time=start_time, end_time=end_time
        )
        buy_rejected_count = await self.count_logs(
            action_type=TradeActionType.AUDIT_REJECT.value,
            start_time=start_time, end_time=end_time
        )

        sell_request_count = await self.count_logs(
            action_type=TradeActionType.SELL_REQUEST.value,
            start_time=start_time, end_time=end_time
        )
        sell_success_count = await self.count_logs(
            action_type=TradeActionType.SELL_SUCCESS.value,
            start_time=start_time, end_time=end_time
        )
        sell_failed_count = await self.count_logs(
            action_type=TradeActionType.SELL_FAILED.value,
            start_time=start_time, end_time=end_time
        )

        audit_pass_count = await self.count_logs(
            action_type=TradeActionType.AUDIT_PASS.value,
            start_time=start_time, end_time=end_time
        )
        audit_reject_count = await self.count_logs(
            action_type=TradeActionType.AUDIT_REJECT.value,
            start_time=start_time, end_time=end_time
        )
        audit_warning_count = await self.count_logs(
            action_type=TradeActionType.AUDIT_WARNING.value,
            start_time=start_time, end_time=end_time
        )

        warning_trigger_count = await self.count_logs(
            action_type=TradeActionType.WARNING_TRIGGER.value,
            start_time=start_time, end_time=end_time
        )
        warning_handle_count = await self.count_logs(
            action_type=TradeActionType.WARNING_HANDLE.value,
            start_time=start_time, end_time=end_time
        )

        cancel_count = await self.count_logs(
            action_type=TradeActionType.CANCEL_SUCCESS.value,
            start_time=start_time, end_time=end_time
        ) + await self.count_logs(
            action_type=TradeActionType.CANCEL_FAILED.value,
            start_time=start_time, end_time=end_time
        )

        ai_chat_count = await self.count_logs(
            action_type=TradeActionType.AI_CHAT.value,
            start_time=start_time, end_time=end_time
        )

        # 计算买入卖出金额
        buy_logs = await TradeLog.filter(
            action_type=TradeActionType.BUY_SUCCESS.value,
            action_time__gte=start_time,
            action_time__lte=end_time
        ).all()
        buy_total_amount = sum(
            log.action_data.get("amount", 0) for log in buy_logs
            if log.action_data
        )
        buy_total_quantity = sum(
            log.action_data.get("quantity", 0) for log in buy_logs
            if log.action_data
        )

        sell_logs = await TradeLog.filter(
            action_type=TradeActionType.SELL_SUCCESS.value,
            action_time__gte=start_time,
            action_time__lte=end_time
        ).all()
        sell_total_amount = sum(
            log.action_data.get("amount", 0) for log in sell_logs
            if log.action_data
        )
        sell_total_quantity = sum(
            log.action_data.get("quantity", 0) for log in sell_logs
            if log.action_data
        )

        # 创建或更新汇总
        summary = await TradeLogSummary.filter(summary_date=summary_date).first()
        if summary:
            await TradeLogSummary.filter(id=summary.id).update(
                stock_pick_count=stock_pick_count,
                buy_request_count=buy_request_count,
                buy_success_count=buy_success_count,
                buy_failed_count=buy_failed_count,
                buy_rejected_count=buy_rejected_count,
                buy_total_amount=buy_total_amount,
                buy_total_quantity=buy_total_quantity,
                sell_request_count=sell_request_count,
                sell_success_count=sell_success_count,
                sell_failed_count=sell_failed_count,
                sell_total_amount=sell_total_amount,
                sell_total_quantity=sell_total_quantity,
                audit_pass_count=audit_pass_count,
                audit_reject_count=audit_reject_count,
                audit_warning_count=audit_warning_count,
                warning_trigger_count=warning_trigger_count,
                warning_handle_count=warning_handle_count,
                cancel_count=cancel_count,
                ai_chat_count=ai_chat_count,
            )
        else:
            summary = await TradeLogSummary.create(
                summary_date=summary_date,
                stock_pick_count=stock_pick_count,
                buy_request_count=buy_request_count,
                buy_success_count=buy_success_count,
                buy_failed_count=buy_failed_count,
                buy_rejected_count=buy_rejected_count,
                buy_total_amount=buy_total_amount,
                buy_total_quantity=buy_total_quantity,
                sell_request_count=sell_request_count,
                sell_success_count=sell_success_count,
                sell_failed_count=sell_failed_count,
                sell_total_amount=sell_total_amount,
                sell_total_quantity=sell_total_quantity,
                audit_pass_count=audit_pass_count,
                audit_reject_count=audit_reject_count,
                audit_warning_count=audit_warning_count,
                warning_trigger_count=warning_trigger_count,
                warning_handle_count=warning_handle_count,
                cancel_count=cancel_count,
                ai_chat_count=ai_chat_count,
            )

        logger.info(f"生成日志汇总: {summary_date}")
        return summary

    async def get_action_type_stats(
        self,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict:
        """获取各类行为的统计"""
        result = {}

        for action_type in TradeActionType:
            count = await self.count_logs(
                action_type=action_type.value,
                start_time=start_time,
                end_time=end_time
            )
            result[action_type.value] = count

        return result


# 单例
trade_log_service = TradeLogService()