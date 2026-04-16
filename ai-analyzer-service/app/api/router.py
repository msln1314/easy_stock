"""
API 路由聚合
"""
from fastapi import APIRouter

from app.api.endpoints import trend_routes, risk_routes, advice_routes, model_routes

api_router = APIRouter()

api_router.include_router(trend_routes.router, prefix="/trend", tags=["trend"])
api_router.include_router(risk_routes.router, prefix="/risk", tags=["risk"])
api_router.include_router(advice_routes.router, prefix="/advice", tags=["advice"])
api_router.include_router(model_routes.router, prefix="/model", tags=["model"])