"""
日志配置
"""
import logging
import sys
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """获取 logger 实例"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(settings.LOG_LEVEL)
    return logger