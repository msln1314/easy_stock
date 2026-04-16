"""
FastAPI 主应用 - factor-service

提供 REST API 和 MCP 双接口支持
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger
from app.api.router import api_router
from app.mcp_server import mcp_server

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"Starting {settings.PROJECT_NAME} on port {settings.SERVICE_PORT}")

    # 启动 MCP HTTP app
    # Note: FastMCP provides separate HTTP app for SSE transport
    yield

    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="因子选股服务 - 提供技术指标计算、因子筛选、评分计算、回测验证功能",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应配置具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 REST API 路由
    app.include_router(api_router, prefix="/api/v1")

    # 健康检查接口
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "port": settings.SERVICE_PORT
        }

    # 根接口
    @app.get("/")
    async def root():
        """服务根路径"""
        return {
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "mcp": "/mcp",
            "health": "/health"
        }

    # MCP SSE 接口 - 挂载 FastMCP HTTP app
    # FastMCP 使用 SSE (Server-Sent Events) 传输
    app.mount("/mcp", mcp_server.http_app())

    logger.info("FastAPI app created with MCP support")
    return app


# 创建应用实例
app = create_app()