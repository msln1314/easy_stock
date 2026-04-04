"""
通知发送服务

支持多种通知渠道：邮件、钉钉、Telegram、企业微信、自定义Webhook
"""
import logging
import json
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

from models.notification import NotificationChannel, NotificationLog, NotificationChannelType
from models.warning import WarningStockPool

logger = logging.getLogger(__name__)


class NotificationSender(ABC):
    """通知发送器抽象基类"""

    @abstractmethod
    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        """
        发送通知

        Args:
            config: 渠道配置
            title: 通知标题
            content: 通知内容

        Returns:
            {"success": bool, "error": str}
        """
        pass


class EmailSender(NotificationSender):
    """邮件发送器"""

    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        # 预留邮件发送实现
        # 实际使用时需要配置SMTP服务器
        logger.info(f"[EMAIL] 发送邮件: {title}")
        logger.debug(f"配置: {config}")
        # TODO: 实现邮件发送逻辑
        return {"success": False, "error": "邮件发送功能尚未实现，请配置SMTP服务器"}


class DingTalkSender(NotificationSender):
    """钉钉机器人发送器"""

    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        webhook_url = config.get("webhook_url")
        secret = config.get("secret")

        if not webhook_url:
            return {"success": False, "error": "缺少webhook_url配置"}

        try:
            # 构建钉钉消息格式
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }

            # 如果有签名密钥，计算签名
            if secret:
                import time
                import hmac
                import hashlib
                import base64
                import urllib.parse

                timestamp = str(round(time.time() * 1000))
                string_to_sign = f"{timestamp}\n{secret}"
                hmac_code = hmac.new(
                    secret.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    digestmod=hashlib.sha256
                ).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook_url, json=message)
                result = response.json()

                if result.get("errcode") == 0:
                    logger.info(f"[DINGTALK] 发送成功: {title}")
                    return {"success": True}
                else:
                    error_msg = result.get("errmsg", "未知错误")
                    logger.error(f"[DINGTALK] 发送失败: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"[DINGTALK] 发送异常: {str(e)}")
            return {"success": False, "error": str(e)}


class TelegramSender(NotificationSender):
    """Telegram Bot发送器"""

    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        bot_token = config.get("bot_token")
        chat_id = config.get("chat_id")

        if not bot_token or not chat_id:
            return {"success": False, "error": "缺少bot_token或chat_id配置"}

        try:
            # Telegram API URL
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

            # 构建消息
            message = {
                "chat_id": chat_id,
                "text": f"**{title}**\n\n{content}",
                "parse_mode": "Markdown"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=message)
                result = response.json()

                if result.get("ok"):
                    logger.info(f"[TELEGRAM] 发送成功: {title}")
                    return {"success": True}
                else:
                    error_msg = result.get("description", "未知错误")
                    logger.error(f"[TELEGRAM] 发送失败: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"[TELEGRAM] 发送异常: {str(e)}")
            return {"success": False, "error": str(e)}


class WechatWorkSender(NotificationSender):
    """企业微信机器人发送器"""

    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        webhook_url = config.get("webhook_url")

        if not webhook_url:
            return {"success": False, "error": "缺少webhook_url配置"}

        try:
            # 企业微信消息格式
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"**{title}**\n\n{content}"
                }
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook_url, json=message)
                result = response.json()

                if result.get("errcode") == 0:
                    logger.info(f"[WECHAT_WORK] 发送成功: {title}")
                    return {"success": True}
                else:
                    error_msg = result.get("errmsg", "未知错误")
                    logger.error(f"[WECHAT_WORK] 发送失败: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"[WECHAT_WORK] 发送异常: {str(e)}")
            return {"success": False, "error": str(e)}


class WebhookSender(NotificationSender):
    """自定义Webhook发送器"""

    async def send(self, config: Dict, title: str, content: str, **kwargs) -> Dict:
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})

        if not url:
            return {"success": False, "error": "缺少url配置"}

        try:
            # 构建消息体
            body = {
                "title": title,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                **kwargs  # 附加信息
            }

            async with httpx.AsyncClient(timeout=10) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=body, headers=headers)
                else:
                    response = await client.get(url, params=body, headers=headers)

                if response.status_code == 200:
                    logger.info(f"[WEBHOOK] 发送成功: {title}")
                    return {"success": True}
                else:
                    error_msg = f"HTTP {response.status_code}"
                    logger.error(f"[WEBHOOK] 发送失败: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"[WEBHOOK] 发送异常: {str(e)}")
            return {"success": False, "error": str(e)}


# 渠道发送器映射
CHANNEL_SENDERS: Dict[NotificationChannelType, NotificationSender] = {
    NotificationChannelType.EMAIL: EmailSender(),
    NotificationChannelType.DINGTALK: DingTalkSender(),
    NotificationChannelType.TELEGRAM: TelegramSender(),
    NotificationChannelType.WECHAT_WORK: WechatWorkSender(),
    NotificationChannelType.WEBHOOK: WebhookSender(),
}


class NotificationService:
    """通知服务"""

    def __init__(self):
        self.senders = CHANNEL_SENDERS

    def _format_notification_content(
        self,
        warning: WarningStockPool,
        stock_info: Optional[Dict] = None
    ) -> tuple:
        """
        格式化通知内容

        Args:
            warning: 预警记录
            stock_info: 股票额外信息

        Returns:
            (标题, 内容)
        """
        title = f"【{warning.warning_level}】{warning.stock_name or warning.stock_code} 预警通知"

        # 构建Markdown内容
        lines = [
            f"### {warning.stock_name or warning.stock_code}",
            f"- **股票代码**: {warning.stock_code}",
            f"- **预警条件**: {warning.condition_name}",
            f"- **预警级别**: {warning.warning_level}",
            f"- **触发时间**: {warning.trigger_time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if warning.price:
            lines.append(f"- **当前价格**: ¥{float(warning.price):.2f}")
        if warning.change_percent:
            change = float(warning.change_percent)
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            lines.append(f"- **涨跌幅**: {change_str}")

        if warning.trigger_value:
            lines.append(f"- **触发指标值**: {json.dumps(warning.trigger_value, ensure_ascii=False)}")

        if stock_info:
            if stock_info.get("monitor_type"):
                lines.append(f"- **监控类型**: {stock_info['monitor_type']}")

        content = "\n".join(lines)
        return title, content

    async def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """
        检查发送频率限制

        Returns:
            True: 可以发送, False: 被限制
        """
        if not channel.last_sent_at:
            return True

        elapsed = datetime.now() - channel.last_sent_at
        if elapsed.total_seconds() < channel.rate_limit_minutes * 60:
            logger.debug(f"渠道 {channel.channel_name} 频率限制，需等待 {channel.rate_limit_minutes} 分钟")
            return False

        return True

    async def send_notification(
        self,
        warning: WarningStockPool,
        stock_info: Optional[Dict] = None,
        force: bool = False
    ) -> List[Dict]:
        """
        发送预警通知到所有匹配的渠道

        Args:
            warning: 预警记录
            stock_info: 股票额外信息（如monitor_type）
            force: 强制发送（忽略频率限制）

        Returns:
            发送结果列表
        """
        results = []

        # 获取所有启用的通知渠道
        channels = await NotificationChannel.filter(is_enabled=True).all()

        if not channels:
            logger.warning("没有启用的通知渠道")
            return results

        # 格式化通知内容
        title, content = self._format_notification_content(warning, stock_info)

        for channel in channels:
            # 检查预警级别过滤
            if warning.warning_level not in channel.warning_levels:
                logger.debug(f"渠道 {channel.channel_name} 不处理 {warning.warning_level} 级别")
                continue

            # 检查监控类型过滤
            monitor_type = stock_info.get("monitor_type") if stock_info else None
            if monitor_type and monitor_type not in channel.monitor_types:
                logger.debug(f"渠道 {channel.channel_name} 不处理 {monitor_type} 类型")
                continue

            # 检查频率限制
            if not force and not await self._check_rate_limit(channel):
                continue

            # 获取发送器
            sender = self.senders.get(channel.channel_type)
            if not sender:
                logger.error(f"未知的渠道类型: {channel.channel_type}")
                continue

            # 创建通知记录
            log = await NotificationLog.create(
                warning_id=warning.id,
                stock_code=warning.stock_code,
                stock_name=warning.stock_name,
                title=title,
                content=content,
                warning_level=warning.warning_level,
                condition_name=warning.condition_name,
                channel_id=channel.id,
                channel_type=channel.channel_type,
                channel_name=channel.channel_name,
                status="pending"
            )

            # 发送通知
            try:
                result = await sender.send(
                    channel.config,
                    title,
                    content,
                    stock_code=warning.stock_code,
                    warning_level=warning.warning_level
                )

                if result["success"]:
                    log.status = "sent"
                    log.sent_at = datetime.now()
                    channel.last_sent_at = datetime.now()
                    await channel.save()
                else:
                    log.status = "failed"
                    log.error_message = result.get("error", "")

                await log.save()
                results.append({
                    "channel": channel.channel_name,
                    "success": result["success"],
                    "error": result.get("error")
                })

            except Exception as e:
                log.status = "failed"
                log.error_message = str(e)
                await log.save()
                results.append({
                    "channel": channel.channel_name,
                    "success": False,
                    "error": str(e)
                })

        return results

    async def send_test_notification(self, channel_id: int) -> Dict:
        """
        发送测试通知

        Args:
            channel_id: 渠道ID

        Returns:
            发送结果
        """
        channel = await NotificationChannel.get_or_none(id=channel_id)
        if not channel:
            return {"success": False, "error": "渠道不存在"}

        sender = self.senders.get(channel.channel_type)
        if not sender:
            return {"success": False, "error": "未知的渠道类型"}

        title = "测试通知"
        content = f"这是一条测试通知，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        result = await sender.send(channel.config, title, content)
        return result


# 单例实例
notification_service = NotificationService()