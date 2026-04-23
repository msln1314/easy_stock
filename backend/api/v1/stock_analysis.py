"""
AI股票分析API接口
"""
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from core.response import success_response
from core.auth import get_current_user
from services.stock_analysis import stock_analysis_service
from models.stock_analysis import AnalysisType, AnalysisStatus


router = APIRouter(prefix="/api/v1/stock-analysis", tags=["AI股票分析"])


# ==================== Schemas ====================

class CreateAnalysisRequest(BaseModel):
    """创建分析请求"""
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    request_prompt: Optional[str] = Field(None, description="分析请求/问题，不填则根据分析类型自动生成")
    analysis_type: str = Field(
        default="comprehensive",
        description="分析类型: fundamental/technical/comprehensive/industry/sentiment/risk"
    )
    stock_data: Optional[dict] = Field(None, description="股票数据（可选）")


class AnalysisReportResponse(BaseModel):
    """分析报告响应"""
    id: int
    stock_code: str
    stock_name: str
    analysis_type: str
    analysis_type_display: str
    status: str
    status_display: str
    request_prompt: str
    summary: Optional[str] = None
    fundamental_analysis: Optional[str] = None
    technical_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None
    recommendation: Optional[str] = None
    full_report: Optional[str] = None
    rating: Optional[int] = None
    tags: Optional[list] = None
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class AnalysisHistoryResponse(BaseModel):
    """分析历史响应"""
    items: list
    total: int
    page: int
    page_size: int


# ==================== API接口 ====================

@router.post("/create", summary="创建AI分析报告")
async def create_analysis(
    request: CreateAnalysisRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """
    创建AI股票分析报告（后台异步执行）

    支持的分析类型：
    - fundamental: 基本面分析
    - technical: 技术面分析
    - comprehensive: 综合分析（默认）
    - industry: 行业分析
    - sentiment: 情绪分析
    - risk: 风险分析
    """
    # 验证分析类型
    try:
        analysis_type = AnalysisType(request.analysis_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"无效的分析类型，可选值: {[t.value for t in AnalysisType]}"
        )

    # 如果未提供分析请求，根据分析类型生成默认请求
    request_prompt = request.request_prompt
    if not request_prompt:
        type_prompts = {
            "fundamental": f"请对{request.stock_name}({request.stock_code})进行基本面分析，包括财务状况、盈利能力、成长性等方面",
            "technical": f"请对{request.stock_name}({request.stock_code})进行技术面分析，包括价格走势、关键技术指标、支撑阻力位等",
            "comprehensive": f"请对{request.stock_name}({request.stock_code})进行全面分析，包括基本面、技术面、风险和投资建议",
            "industry": f"请分析{request.stock_name}({request.stock_code})所在行业的发展趋势、竞争格局和公司行业地位",
            "sentiment": f"请分析{request.stock_name}({request.stock_code})的市场情绪和投资者预期",
            "risk": f"请对{request.stock_name}({request.stock_code})进行风险评估，识别主要风险因素并提出应对建议",
        }
        request_prompt = type_prompts.get(request.analysis_type, f"请分析{request.stock_name}({request.stock_code})的投资价值")

    # 获取股票数据（如果未提供，可以尝试获取）
    stock_data = request.stock_data or {}

    # 创建待处理状态的报告记录
    report = await stock_analysis_service.create_pending_report(
        stock_code=request.stock_code,
        stock_name=request.stock_name,
        request_prompt=request_prompt,
        analysis_type=analysis_type,
        user_id=user.id if user else None,
    )

    # 后台异步执行分析
    background_tasks.add_task(
        stock_analysis_service.run_analysis_task,
        report_id=report.id,
        stock_data=stock_data,
    )

    return success_response({
        "id": report.id,
        "status": report.status,
        "status_display": report.status_display,
        "message": "分析任务已创建，正在后台处理中",
    })


@router.get("/report/{report_id}", summary="获取分析报告详情")
async def get_analysis_report(report_id: int, user=Depends(get_current_user)):
    """
    获取指定分析报告的详细内容
    """
    report = await stock_analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    return success_response({
        "id": report.id,
        "stock_code": report.stock_code,
        "stock_name": report.stock_name,
        "analysis_type": report.analysis_type,
        "analysis_type_display": report.analysis_type_display,
        "status": report.status,
        "status_display": report.status_display,
        "request_prompt": report.request_prompt,
        "summary": report.summary,
        "fundamental_analysis": report.fundamental_analysis,
        "technical_analysis": report.technical_analysis,
        "risk_analysis": report.risk_analysis,
        "recommendation": report.recommendation,
        "full_report": report.full_report,
        "rating": report.rating,
        "tags": report.tags,
        "model_name": report.model_name,
        "tokens_used": report.tokens_used,
        "duration_ms": report.duration_ms,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None,
        "error_message": report.error_message,
    })


@router.get("/history", summary="获取分析历史列表")
async def get_analysis_history(
    stock_code: Optional[str] = Query(None, description="股票代码筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user=Depends(get_current_user)
):
    """
    获取分析报告历史列表

    支持按股票代码、状态筛选
    """
    # 转换状态
    analysis_status = None
    if status:
        try:
            analysis_status = AnalysisStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的状态值，可选值: {[s.value for s in AnalysisStatus]}"
            )

    offset = (page - 1) * page_size
    reports = await stock_analysis_service.get_report_history(
        stock_code=stock_code,
        user_id=user.id if user else None,
        status=analysis_status,
        limit=page_size,
        offset=offset,
    )

    # 获取总数（简化处理）
    total = len(reports)

    items = [
        {
            "id": r.id,
            "stock_code": r.stock_code,
            "stock_name": r.stock_name,
            "analysis_type": r.analysis_type,
            "analysis_type_display": r.analysis_type_display,
            "status": r.status,
            "status_display": r.status_display,
            "request_prompt": r.request_prompt[:100] + "..." if r.request_prompt and len(r.request_prompt) > 100 else r.request_prompt,
            "summary": r.summary[:200] + "..." if r.summary and len(r.summary) > 200 else r.summary,
            "rating": r.rating,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        }
        for r in reports
    ]

    return success_response({
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.delete("/report/{report_id}", summary="删除分析报告")
async def delete_analysis_report(report_id: int, user=Depends(get_current_user)):
    """
    删除指定分析报告
    """
    success = await stock_analysis_service.delete_report(
        report_id=report_id,
        user_id=user.id if user else None,
    )

    if not success:
        raise HTTPException(status_code=404, detail="报告不存在或无权限删除")

    return success_response({"message": "报告删除成功"})


@router.get("/statistics", summary="获取分析统计")
async def get_analysis_statistics(user=Depends(get_current_user)):
    """
    获取分析报告统计数据

    包括总数量、平均耗时、各类型分布等
    """
    stats = await stock_analysis_service.get_statistics(user_id=user.id if user else None)

    return success_response(stats)


@router.get("/conversations/{report_id}", summary="获取报告对话历史")
async def get_report_conversations(report_id: int, user=Depends(get_current_user)):
    """
    获取报告的AI对话历史记录
    """
    # 先检查报告是否存在
    report = await stock_analysis_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    conversations = await stock_analysis_service.get_conversations(report_id)

    items = [
        {
            "id": c.id,
            "role": c.role,
            "content": c.content,
            "tokens_used": c.tokens_used,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in conversations
    ]

    return success_response({"items": items, "total": len(items)})