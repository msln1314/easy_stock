"""
用户通知服务

提供通知创建、批量创建等功能
"""
from datetime import datetime
from typing import Optional, List
from models.user_notification import UserNotification, UserNotificationType


class UserNotificationService:
    """用户通知服务"""

    async def create_notification(
        self,
        user_id: int,
        type: str,
        title: str,
        content: str,
        related_id: Optional[int] = None,
        related_type: Optional[str] = None
    ) -> UserNotification:
        """创建单条通知"""
        return await UserNotification.create(
            user_id=user_id,
            type=type,
            title=title,
            content=content,
            related_id=related_id,
            related_type=related_type
        )

    async def batch_create_notifications(
        self,
        user_id: int,
        notifications: List[dict]
    ) -> List[UserNotification]:
        """批量创建通知"""
        created = []
        for n in notifications:
            notification = await UserNotification.create(
                user_id=user_id,
                type=n.get("type", "system"),
                title=n.get("title", ""),
                content=n.get("content", ""),
                related_id=n.get("related_id"),
                related_type=n.get("related_type")
            )
            created.append(notification)
        return created

    async def create_trade_notification(
        self,
        user_id: int,
        stock_code: str,
        stock_name: str,
        direction: str,
        price: float,
        quantity: int,
        trade_id: Optional[int] = None
    ) -> UserNotification:
        """创建交易通知"""
        direction_text = "买入" if direction == "buy" else "卖出"
        title = f"{stock_name}{direction_text}成交"
        content = f"以{price:.2f}元{direction_text}{quantity}股{stock_code}"

        return await self.create_notification(
            user_id=user_id,
            type="trade",
            title=title,
            content=content,
            related_id=trade_id,
            related_type="trade_log"
        )

    async def create_strategy_notification(
        self,
        user_id: int,
        strategy_name: str,
        stock_code: str,
        stock_name: str,
        signal_type: str,
        strategy_id: Optional[int] = None
    ) -> UserNotification:
        """创建策略通知"""
        title = f"{strategy_name}策略触发"
        content = f"{stock_name}({stock_code})触发{signal_type}信号"

        return await self.create_notification(
            user_id=user_id,
            type="strategy",
            title=title,
            content=content,
            related_id=strategy_id,
            related_type="strategy"
        )

    async def create_system_notification(
        self,
        user_id: int,
        title: str,
        content: str
    ) -> UserNotification:
        """创建系统通知"""
        return await self.create_notification(
            user_id=user_id,
            type="system",
            title=title,
            content=content
        )

    async def create_market_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        related_id: Optional[int] = None
    ) -> UserNotification:
        """创建市场通知"""
        return await self.create_notification(
            user_id=user_id,
            type="market",
            title=title,
            content=content,
            related_id=related_id,
            related_type="market_data"
        )


# 全局实例
user_notification_service = UserNotificationService()