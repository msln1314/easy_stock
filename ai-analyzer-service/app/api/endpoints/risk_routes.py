"""
风险评估 REST API 路由
"""
from fastapi import APIRouter
from typing import List, Optional

from app.models.risk_models import (
    RiskAssessmentRequest,
    PortfolioRiskRequest,
    CompareRiskRequest,
)
from app.services.risk_service import risk_service

router = APIRouter()


@router.post("/assess")
async def assess_risk(request: RiskAssessmentRequest):
    """单只股票风险评估"""
    result = await risk_service.assess_risk(
        stock_code=request.stock_code,
        assessment_type=request.assessment_type,
        model=request.model
    )
    return result.model_dump()


@router.post("/portfolio")
async def portfolio_risk(request: PortfolioRiskRequest):
    """组合风险评估"""
    result = await risk_service.portfolio_risk(
        stock_codes=request.stock_codes,
        weights=request.weights,
        model=request.model
    )
    return result.model_dump()


@router.post("/compare")
async def compare_risk(request: CompareRiskRequest):
    """多股风险对比"""
    result = await risk_service.compare_risk(
        stock_codes=request.stock_codes,
        model=request.model
    )
    return result.model_dump()