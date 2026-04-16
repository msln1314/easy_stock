"""
日志配置
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)


# 初始化日志
setup_logging()
logger = get_logger(__name__)