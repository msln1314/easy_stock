"""
模型管理 REST API 路由
"""
from fastapi import APIRouter

from app.services.model_service import model_service

router = APIRouter()


@router.get("/list")
async def get_model_list():
    """获取支持的模型列表"""
    result = model_service.get_available_models()
    return result.model_dump()


@router.get("/current")
async def get_current_model():
    """获取当前使用的模型"""
    result = model_service.get_current_model()
    return result.model_dump()


@router.post("/switch")
async def switch_model(provider: str, model: str = None):
    """切换模型"""
    result = model_service.switch_model(provider, model)
    return result.model_dump()


@router.get("/status")
async def check_status():
    """检查各 Provider 状态"""
    result = model_service.check_status()
    return result.model_dump()