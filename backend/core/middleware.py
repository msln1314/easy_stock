"""
中间件配置
"""
from fastapi.middleware.cors import CORSMiddleware
from config.settings import CORS_ORIGINS


def setup_middlewares(app):
    """配置中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )