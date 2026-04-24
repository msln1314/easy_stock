# backend/qmt-service/app/api/router.py
from fastapi import APIRouter, Depends

from app.api.endpoints import trade_routes, position_routes, quote_routes, factor_routes
from app.mcp.router import mcp_router
from app.core.auth import verify_api_key

api_router = APIRouter(dependencies=[Depends(verify_api_key)])

api_router.include_router(trade_routes.router, prefix="/trade", tags=["trade"])
api_router.include_router(position_routes.router, prefix="/position", tags=["position"])
api_router.include_router(quote_routes.router, prefix="/quote", tags=["quote"])
api_router.include_router(factor_routes.router, prefix="/factor", tags=["factor"])
api_router.include_router(mcp_router, tags=["mcp"])