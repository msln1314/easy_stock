# backend/qmt-service/app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.qmt_client import QMTClientManager
from app.core.auth import init_api_keys
from app.mcp_server import mcp_server

# Get MCP HTTP app with its lifespan
mcp_http_app = mcp_server.http_app()

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - combines MCP lifespan"""
    # 启动时
    logger.info(f"正在启动 {settings.PROJECT_NAME}...")

    # 初始化因子库（仅内存缓存，不使用数据库）
    from app.services.factor_service import factor_service
    await factor_service.init_factors()
    logger.info(f"因子库加载完成，共 {len(factor_service._factor_cache)} 个因子")

    # 从 Backend 同步 API Keys
    from app.core.auth import init_api_keys, sync_api_keys_from_backend
    api_keys = await sync_api_keys_from_backend()
    if api_keys:
        init_api_keys(api_keys)
        logger.info(f"已从 Backend 同步 {len(api_keys)} 个 API Key")
    else:
        # 开发模式添加默认 key
        if settings.DEBUG:
            from app.core.auth import init_api_keys
            default_keys = [{"api_key": "dev_api_key_2024", "user_id": 0, "qmt_account_id": "dev"}]
            init_api_keys(default_keys)
            logger.warning("开发模式: 使用默认 API Key")
        else:
            logger.warning("未同步到任何 API Key，请检查 Backend 连接")

    # 连接QMT
    connected = await QMTClientManager.initialize()
    if connected:
        logger.info("QMT客户端连接成功")
    else:
        logger.warning("QMT客户端未连接，使用模拟模式")

    # Start MCP lifespan
    async with mcp_http_app.lifespan(app):
        logger.info("MCP Server started")
        yield
        logger.info("MCP Server stopped")

    # 关闭时
    logger.info("正在关闭服务...")
    await QMTClientManager.close()
    logger.info("服务已关闭")


# API tags
tags_metadata = [
    {"name": "trade", "description": "交易执行接口"},
    {"name": "position", "description": "持仓管理接口"},
    {"name": "quote", "description": "行情数据接口"},
    {"name": "factor", "description": "因子选股接口"},
    {"name": "mcp", "description": "MCP接口（供AI调用）"},
]

# 创建应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="QMT量化交易服务，提供交易执行、持仓管理等功能",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": settings.PROJECT_NAME,
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
        "qmt_status": "connected" if QMTClientManager.is_connected() else "mock"
    }


@app.get("/health", tags=["root"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "qmt": QMTClientManager.get_status()
    }