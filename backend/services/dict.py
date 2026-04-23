"""
字典业务逻辑服务
"""
from typing import Optional, List, Dict
from tortoise.expressions import Q
from models.dict_type import DictType
from models.dict_item import DictItem
from schemas.dict import (
    DictTypeCreate, DictTypeUpdate, DictTypeResponse,
    DictTypeListResponse, DictTypePaginatedResponse,
    DictItemCreate, DictItemUpdate, DictItemResponse,
    DictItemListResponse, DictItemPaginatedResponse, DictItemTreeResponse
)
from utils.crypto import aes_encrypt, aes_decrypt


class DictTypeService:
    """字典类型服务"""

    async def create_dict_type(self, data: DictTypeCreate, user_id: Optional[int] = None) -> DictType:
        """创建字典类型"""
        dict_type = await DictType.create(
            code=data.code,
            name=data.name,
            category=data.category,
            access_type=data.access_type,
            description=data.description,
            sort=data.sort,
            status=data.status,
            created_by=user_id
        )
        return dict_type

    async def get_dict_type(self, type_id: int) -> Optional[DictType]:
        """获取单个字典类型"""
        return await DictType.get_or_none(id=type_id)

    async def get_dict_type_by_code(self, code: str) -> Optional[DictType]:
        """根据编码获取字典类型"""
        return await DictType.get_or_none(code=code)

    async def get_dict_types(
        self,
        category: Optional[str] = None,
        access_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> DictTypePaginatedResponse:
        """获取字典类型列表"""
        query = DictType.all()
        if category:
            query = query.filter(category=category)
        if access_type:
            query = query.filter(access_type=access_type)
        if status:
            query = query.filter(status=status)
        if keyword:
            query = query.filter(Q(name__icontains=keyword) | Q(code__icontains=keyword))

        total = await query.count()
        dict_types = await query.order_by('sort', '-created_at').offset((page - 1) * page_size).limit(page_size).all()

        return DictTypePaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[DictTypeListResponse(
                id=dt.id,
                code=dt.code,
                name=dt.name,
                category=dt.category,
                access_type=dt.access_type,
                sort=dt.sort,
                status=dt.status,
                created_at=dt.created_at
            ) for dt in dict_types]
        )

    async def update_dict_type(self, type_id: int, data: DictTypeUpdate) -> Optional[DictType]:
        """更新字典类型"""
        dict_type = await DictType.get_or_none(id=type_id)
        if not dict_type:
            return None

        update_data = data.dict(exclude_unset=True)
        if update_data:
            await DictType.filter(id=type_id).update(**update_data)

        return await DictType.get_or_none(id=type_id)

    async def delete_dict_type(self, type_id: int) -> bool:
        """删除字典类型（同时删除关联字典项）"""
        dict_type = await DictType.get_or_none(id=type_id)
        if not dict_type:
            return False

        # 删除关联的字典项
        await DictItem.filter(type_id=type_id).delete()
        await dict_type.delete()
        return True


class DictItemService:
    """字典项服务"""

    async def create_dict_item(self, data: DictItemCreate) -> DictItem:
        """创建字典项"""
        # 加密处理
        value = data.value
        if data.data_type == "encrypted" and value:
            value = aes_encrypt(value)

        dict_item = await DictItem.create(
            type_id=data.type_id,
            code=data.code,
            name=data.name,
            value=value,
            data_type=data.data_type,
            parent_id=data.parent_id,
            sort=data.sort,
            status=data.status,
            remark=data.remark
        )
        return dict_item

    async def get_dict_item(self, item_id: int) -> Optional[DictItem]:
        """获取单个字典项"""
        return await DictItem.get_or_none(id=item_id)

    async def get_dict_items_by_type(
        self,
        type_code: str,
        include_decrypted: bool = False
    ) -> List[DictItemResponse]:
        """根据类型编码获取字典项"""
        dict_type = await DictType.get_or_none(code=type_code)
        if not dict_type:
            return []

        items = await DictItem.filter(
            type_id=dict_type.id,
            status="active"
        ).order_by('sort', 'id').all()

        result = []
        for item in items:
            decrypted_value = None
            if include_decrypted and item.data_type == "encrypted" and item.value:
                decrypted_value = aes_decrypt(item.value)

            result.append(DictItemResponse(
                id=item.id,
                type_id=item.type_id,
                code=item.code,
                name=item.name,
                value=item.value,
                data_type=item.data_type,
                parent_id=item.parent_id,
                sort=item.sort,
                status=item.status,
                remark=item.remark,
                created_at=item.created_at,
                updated_at=item.updated_at,
                decrypted_value=decrypted_value
            ))

        return result

    async def get_dict_items_tree(
        self,
        type_id: int,
        include_decrypted: bool = False
    ) -> List[DictItemTreeResponse]:
        """获取字典项树形结构"""
        items = await DictItem.filter(type_id=type_id).order_by('sort', 'id').all()

        # 构建树形结构
        item_map: Dict[int, DictItemTreeResponse] = {}
        root_items: List[DictItemTreeResponse] = []

        for item in items:
            decrypted_value = None
            if include_decrypted and item.data_type == "encrypted" and item.value:
                decrypted_value = aes_decrypt(item.value)

            tree_item = DictItemTreeResponse(
                id=item.id,
                type_id=item.type_id,
                code=item.code,
                name=item.name,
                value=item.value,
                data_type=item.data_type,
                parent_id=item.parent_id,
                sort=item.sort,
                status=item.status,
                children=[]
            )
            item_map[item.id] = tree_item

        # 构建父子关系
        for item in items:
            tree_item = item_map[item.id]
            if item.parent_id and item.parent_id in item_map:
                item_map[item.parent_id].children.append(tree_item)
            else:
                root_items.append(tree_item)

        return root_items

    async def get_dict_items(
        self,
        type_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> DictItemPaginatedResponse:
        """获取字典项列表"""
        query = DictItem.all()
        if type_id:
            query = query.filter(type_id=type_id)
        if parent_id is not None:
            query = query.filter(parent_id=parent_id)
        if status:
            query = query.filter(status=status)
        if keyword:
            query = query.filter(Q(name__icontains=keyword) | Q(code__icontains=keyword))

        total = await query.count()
        items = await query.order_by('sort', '-created_at').offset((page - 1) * page_size).limit(page_size).all()

        return DictItemPaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[DictItemListResponse(
                id=it.id,
                type_id=it.type_id,
                code=it.code,
                name=it.name,
                value=it.value,
                data_type=it.data_type,
                parent_id=it.parent_id,
                sort=it.sort,
                status=it.status,
                created_at=it.created_at
            ) for it in items]
        )

    async def update_dict_item(self, item_id: int, data: DictItemUpdate) -> Optional[DictItem]:
        """更新字典项"""
        dict_item = await DictItem.get_or_none(id=item_id)
        if not dict_item:
            return None

        update_data = data.dict(exclude_unset=True)

        # 处理加密
        if 'value' in update_data and 'data_type' in update_data:
            if update_data['data_type'] == "encrypted" and update_data['value']:
                update_data['value'] = aes_encrypt(update_data['value'])
        elif 'value' in update_data and dict_item.data_type == "encrypted":
            if update_data['value']:
                update_data['value'] = aes_encrypt(update_data['value'])

        if update_data:
            await DictItem.filter(id=item_id).update(**update_data)

        return await DictItem.get_or_none(id=item_id)

    async def delete_dict_item(self, item_id: int) -> bool:
        """删除字典项"""
        dict_item = await DictItem.get_or_none(id=item_id)
        if not dict_item:
            return False

        # 检查是否有子项
        children = await DictItem.filter(parent_id=item_id).count()
        if children > 0:
            return False  # 有子项不允许删除

        await dict_item.delete()
        return True