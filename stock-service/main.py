"""
股票分析服务启动入口
"""
import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST or "0.0.0.0",
        port=settings.SERVICE_PORT or 8008,
        reload=False
    )