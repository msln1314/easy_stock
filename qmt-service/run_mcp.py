# backend/qmt-service/run_mcp.py
"""
MCP Server 独立启动入口

仅启动 MCP 服务，不启动 FastAPI REST API。
"""
import asyncio
import logging

from app.core.config import settings
from app.core.qmt_client import QMTClientManager
from app.services.factor_service import factor_service
from app.mcp_server import mcp_server

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """启动 MCP Server"""
    logger.info("正在启动 MCP Server...")

    # 初始化因子库
    await factor_service.init_factors()
    logger.info(f"因子库加载完成，共 {len(factor_service._factor_cache)} 个因子")

    # 连接 QMT
    connected = await QMTClientManager.initialize()
    if connected:
        logger.info("QMT客户端连接成功")
    else:
        logger.warning("QMT客户端未连接，使用模拟模式")

    # 运行 MCP HTTP server
    logger.info(f"MCP Server 运行在 http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/mcp")
    await mcp_server.run_http_async(
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT
    )

    # 关闭
    await QMTClientManager.close()
    logger.info("服务已关闭")


if __name__ == "__main__":
    asyncio.run(main())