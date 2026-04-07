"""
FastAPI应用入口（集成通知功能）
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger

from config.database import init_db, close_db
from config.settings import APP_NAME, APP_VERSION, DEBUG
from core.middleware import setup_middlewares
from core.exceptions import AppException, NotFoundException
from core.response import error_response
from core.ap_scheduler import SchedulerUtil
from api.v1.strategy import router as strategy_router
from api.v1.warning import router as warning_router
from api.v1.indicator import router as indicator_router
from api.v1.scheduler import router as scheduler_router
from api.v1.auth import router as auth_router
from api.v1.dict import router as dict_router
from api.v1.config import router as config_router
from api.v1.monitor import router as monitor_router
from api.v1.notification import router as notification_router
from api.v1.captcha import router as captcha_router
from api.v1.menu import router as menu_router
from api.v1.condition_group import router as condition_group_router
from api.v1.ai_trade import router as ai_trade_router
from api.v1.stock_analysis import router as stock_analysis_router
from api.v1.role import router as role_router
from api.v1.user import router as user_router
from api.v1.factor_screen import router as factor_screen_router
from api.v1.stock_pick import router as stock_pick_router
from api.v1.trade_log import router as trade_log_router
from api.v1.position import router as position_router
from api.v1.red_line import router as red_line_router

# 配置日志
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="7 days",
    level="INFO" if not DEBUG else "DEBUG"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    # 启动调度器
    logger.info("正在启动计划任务调度器...")
    await SchedulerUtil.init_system_scheduler()
    logger.info("计划任务调度器启动完成")

    yield

    # 关闭调度器
    logger.info("正在关闭计划任务调度器...")
    await SchedulerUtil.close_system_scheduler()
    logger.info("计划任务调度器已关闭")

    # 关闭时清理资源
    logger.info("正在关闭数据库连接...")
    await close_db()
    logger.info("应用已关闭")


# 创建应用
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="股票交易策略管理系统（支持多渠道通知）",
    lifespan=lifespan
)

# 配置中间件
setup_middlewares(app)

# 注册异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.code if exc.code < 500 else 400,
        content=error_response(exc.message, exc.code)
    )

@app.exception_handler(NotFoundException)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=error_response(exc.message, 404)
    )

# 注册路由
app.include_router(strategy_router)
app.include_router(warning_router)
app.include_router(indicator_router)
app.include_router(scheduler_router)
app.include_router(auth_router)
app.include_router(dict_router)
app.include_router(config_router)
app.include_router(monitor_router)
app.include_router(notification_router)
app.include_router(captcha_router)
app.include_router(menu_router)
app.include_router(condition_group_router)
app.include_router(ai_trade_router)
app.include_router(stock_analysis_router)
app.include_router(role_router)
app.include_router(user_router)
app.include_router(factor_screen_router)
app.include_router(stock_pick_router)
app.include_router(trade_log_router)
app.include_router(position_router)
app.include_router(red_line_router)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{APP_NAME}",
        "version": APP_VERSION,
        "docs": "/docs",
        "features": ["预警监控", "多渠道通知"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8030,
        reload=DEBUG
    )