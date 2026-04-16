"""
API 路由聚合
"""
from fastapi import APIRouter

from app.api.endpoints import indicator_routes, factor_routes, backtest_routes

api_router = APIRouter()

api_router.include_router(indicator_routes.router, prefix="/indicator", tags=["indicator"])
api_router.include_router(factor_routes.router, prefix="/factor", tags=["factor"])
api_router.include_router(backtest_routes.router, prefix="/backtest", tags=["backtest"])