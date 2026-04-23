"""
MCP配置API接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from core.response import success_response
from core.auth import get_admin_user
from services.mcp_config import mcp_config_service
from schemas.mcp_config import McpConfigCreate, McpConfigUpdate

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP配置管理"])


@router.post("/", summary="创建MCP配置")
async def create_mcp_config(
    data: McpConfigCreate,
    admin=Depends(get_admin_user)
):
    """创建MCP服务配置（管理员权限）"""
    try:
        config = await mcp_config_service.create_config(data)
        return success_response({
            "id": config.id,
            "service_name": config.service_name,
            "service_url": config.service_url,
            "enabled": config.enabled,
            "message": "创建成功"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", summary="获取MCP配置列表")
async def get_mcp_configs(
    enabled: Optional[bool] = Query(None, description="是否启用"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    admin=Depends(get_admin_user)
):
    """获取MCP配置列表（管理员权限）"""
    result = await mcp_config_service.get_configs(enabled, keyword, page, page_size)
    return success_response(result)


@router.get("/{config_id}", summary="获取单个MCP配置")
async def get_mcp_config(
    config_id: int,
    admin=Depends(get_admin_user)
):
    """获取单个MCP配置（管理员权限）"""
    config = await mcp_config_service.get_config(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response({
        "id": config.id,
        "service_name": config.service_name,
        "service_url": config.service_url,
        "enabled": config.enabled,
        "description": config.description
    })


@router.put("/{config_id}", summary="更新MCP配置")
async def update_mcp_config(
    config_id: int,
    data: McpConfigUpdate,
    admin=Depends(get_admin_user)
):
    """更新MCP配置（管理员权限）"""
    config = await mcp_config_service.update_config(config_id, data)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response({
        "id": config.id,
        "service_name": config.service_name,
        "message": "更新成功"
    })


@router.delete("/{config_id}", summary="删除MCP配置")
async def delete_mcp_config(
    config_id: int,
    admin=Depends(get_admin_user)
):
    """删除MCP配置（管理员权限）"""
    success = await mcp_config_service.delete_config(config_id)
    if not success:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response({"message": "删除成功"})


@router.get("/keys/{service_name}", summary="获取服务API Key")
async def get_service_api_key(
    service_name: str,
    admin=Depends(get_admin_user)
):
    """获取指定服务的API Key（管理员权限，返回解密后的值）"""
    config = await mcp_config_service.get_config_value(service_name)
    if not config:
        raise HTTPException(status_code=404, detail="服务配置不存在")
    return success_response(config)