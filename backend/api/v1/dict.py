"""
字典管理API路由
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends
from core.response import success_response, error_response
from core.auth import get_current_user_required
from schemas.dict import (
    DictTypeCreate, DictTypeUpdate, DictTypeResponse,
    DictItemCreate, DictItemUpdate, DictItemResponse
)
from services.dict import DictTypeService, DictItemService
from models.user import User
from models.dict_item import DictItem

router = APIRouter(prefix="/api/v1/dict", tags=["字典管理"])
type_service = DictTypeService()
item_service = DictItemService()


# ==================== 字典类型 API ====================

@router.get("/types", response_model=None)
async def get_dict_types(
    category: Optional[str] = Query(None, description="类别筛选: system/custom/config"),
    access_type: Optional[str] = Query(None, description="访问类型筛选: public/private"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    user: User = Depends(get_current_user_required)
):
    """获取字典类型列表"""
    result = await type_service.get_dict_types(
        category=category,
        access_type=access_type,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return success_response(result.dict())


@router.get("/types/{type_id}", response_model=None)
async def get_dict_type_detail(
    type_id: int,
    user: User = Depends(get_current_user_required)
):
    """获取字典类型详情"""
    dict_type = await type_service.get_dict_type(type_id)
    if not dict_type:
        return error_response("字典类型不存在", 404)

    return success_response({
        "id": dict_type.id,
        "code": dict_type.code,
        "name": dict_type.name,
        "category": dict_type.category,
        "access_type": dict_type.access_type,
        "description": dict_type.description,
        "sort": dict_type.sort,
        "status": dict_type.status,
        "created_by": dict_type.created_by,
        "created_at": dict_type.created_at.isoformat(),
        "updated_at": dict_type.updated_at.isoformat()
    })


@router.post("/types", response_model=None)
async def create_dict_type(
    data: DictTypeCreate,
    user: User = Depends(get_current_user_required)
):
    """创建字典类型"""
    # 检查编码是否已存在
    existing = await type_service.get_dict_type_by_code(data.code)
    if existing:
        return error_response("字典类型编码已存在", 400)

    dict_type = await type_service.create_dict_type(data, user.id)
    return success_response({
        "id": dict_type.id,
        "code": dict_type.code,
        "name": dict_type.name,
        "created_at": dict_type.created_at.isoformat()
    })


@router.put("/types/{type_id}", response_model=None)
async def update_dict_type(
    type_id: int,
    data: DictTypeUpdate,
    user: User = Depends(get_current_user_required)
):
    """更新字典类型"""
    dict_type = await type_service.update_dict_type(type_id, data)
    if not dict_type:
        return error_response("字典类型不存在", 404)

    return success_response({
        "id": dict_type.id,
        "code": dict_type.code,
        "name": dict_type.name,
        "updated_at": dict_type.updated_at.isoformat()
    })


@router.delete("/types/{type_id}", response_model=None)
async def delete_dict_type(
    type_id: int,
    user: User = Depends(get_current_user_required)
):
    """删除字典类型"""
    success = await type_service.delete_dict_type(type_id)
    if not success:
        return error_response("字典类型不存在", 404)
    return success_response(message="删除成功")


# ==================== 字典项 API ====================

@router.get("/types/{code}/items", response_model=None)
async def get_dict_items_by_type_code(
    code: str,
    user: User = Depends(get_current_user_required)
):
    """根据类型编码获取字典项（公开类型无需认证）"""
    dict_type = await type_service.get_dict_type_by_code(code)
    if not dict_type:
        return error_response("字典类型不存在", 404)

    # 私有类型需要认证
    if dict_type.access_type == "private" and not user:
        return error_response("无权访问私有字典", 403)

    # 管理员可查看解密值
    include_decrypted = user.role == "admin" if user else False
    items = await item_service.get_dict_items_by_type(code, include_decrypted)

    return success_response([item.dict() for item in items])


@router.get("/items", response_model=None)
async def get_dict_items(
    type_id: Optional[int] = Query(None, description="字典类型ID"),
    parent_id: Optional[int] = Query(None, description="父级ID"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    user: User = Depends(get_current_user_required)
):
    """获取字典项列表"""
    result = await item_service.get_dict_items(
        type_id=type_id,
        parent_id=parent_id,
        status=status,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return success_response(result.dict())


@router.get("/items/{item_id}", response_model=None)
async def get_dict_item_detail(
    item_id: int,
    user: User = Depends(get_current_user_required)
):
    """获取字典项详情"""
    dict_item = await item_service.get_dict_item(item_id)
    if not dict_item:
        return error_response("字典项不存在", 404)

    # 管理员可查看解密值
    decrypted_value = None
    if user.role == "admin" and dict_item.data_type == "encrypted" and dict_item.value:
        from utils.crypto import aes_decrypt
        decrypted_value = aes_decrypt(dict_item.value)

    return success_response({
        "id": dict_item.id,
        "type_id": dict_item.type_id,
        "code": dict_item.code,
        "name": dict_item.name,
        "value": dict_item.value,
        "data_type": dict_item.data_type,
        "parent_id": dict_item.parent_id,
        "sort": dict_item.sort,
        "status": dict_item.status,
        "remark": dict_item.remark,
        "decrypted_value": decrypted_value,
        "created_at": dict_item.created_at.isoformat(),
        "updated_at": dict_item.updated_at.isoformat()
    })


@router.post("/items", response_model=None)
async def create_dict_item(
    data: DictItemCreate,
    user: User = Depends(get_current_user_required)
):
    """创建字典项"""
    # 检查类型是否存在
    dict_type = await type_service.get_dict_type(data.type_id)
    if not dict_type:
        return error_response("字典类型不存在", 404)

    # 检查编码是否已存在
    existing = await DictItem.get_or_none(type_id=data.type_id, code=data.code)
    if existing:
        return error_response("字典项编码已存在", 400)

    dict_item = await item_service.create_dict_item(data)
    return success_response({
        "id": dict_item.id,
        "type_id": dict_item.type_id,
        "code": dict_item.code,
        "name": dict_item.name,
        "created_at": dict_item.created_at.isoformat()
    })


@router.put("/items/{item_id}", response_model=None)
async def update_dict_item(
    item_id: int,
    data: DictItemUpdate,
    user: User = Depends(get_current_user_required)
):
    """更新字典项"""
    dict_item = await item_service.update_dict_item(item_id, data)
    if not dict_item:
        return error_response("字典项不存在", 404)

    return success_response({
        "id": dict_item.id,
        "code": dict_item.code,
        "name": dict_item.name,
        "updated_at": dict_item.updated_at.isoformat()
    })


@router.delete("/items/{item_id}", response_model=None)
async def delete_dict_item(
    item_id: int,
    user: User = Depends(get_current_user_required)
):
    """删除字典项"""
    success = await item_service.delete_dict_item(item_id)
    if not success:
        return error_response("字典项不存在或存在子项", 404)
    return success_response(message="删除成功")


@router.get("/items/tree", response_model=None)
async def get_dict_items_tree(
    type_id: int = Query(..., description="字典类型ID"),
    user: User = Depends(get_current_user_required)
):
    """获取字典项树形结构"""
    include_decrypted = user.role == "admin"
    tree = await item_service.get_dict_items_tree(type_id, include_decrypted)
    return success_response([item.dict() for item in tree])