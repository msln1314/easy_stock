"""
中间件配置
"""
import traceback
import logging
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import CORS_ORIGINS

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """全局异常处理中间件"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # 打印完整的错误堆栈
            error_traceback = traceback.format_exc()
            logger.error(f"请求异常: {request.method} {request.url}\n{error_traceback}")

            # 控制台也打印
            print(f"\n{'='*60}")
            print(f"请求异常: {request.method} {request.url}")
            print(f"{'='*60}")
            print(error_traceback)
            print(f"{'='*60}\n")

            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "message": f"服务器内部错误: {str(e)}",
                    "data": None,
                    "traceback": error_traceback.split('\n')[-10:]  # 返回最后10行堆栈
                }
            )


def setup_middlewares(app):
    """配置中间件"""
    # 全局异常处理中间件（要在最外层）
    app.add_middleware(ExceptionHandlerMiddleware)

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )