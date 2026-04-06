"""
角色业务逻辑服务
"""
from typing import Optional, List
from models.role import Role
from models.role_menu import RoleMenu
from models.user_role import UserRole
from schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse,
    RoleListResponse, RoleWithMenusResponse
)


class RoleService:
    """角色服务"""

    async def create_role(self, data: RoleCreate) -> Role:
        """创建角色"""
        role = await Role.create(
            name=data.name,
            code=data.code,
            description=data.description,
            status=data.status
        )

        # 分配菜单
        if data.menu_ids:
            for menu_id in data.menu_ids:
                await RoleMenu.create(role_id=role.id, menu_id=menu_id)

        return role

    async def get_role(self, role_id: int) -> Optional[Role]:
        """获取单个角色"""
        return await Role.get_or_none(id=role_id)

    async def get_role_by_code(self, code: str) -> Optional[Role]:
        """根据编码获取角色"""
        return await Role.get_or_none(code=code)

    async def get_role_with_menus(self, role_id: int) -> Optional[RoleWithMenusResponse]:
        """获取角色详情（含菜单ID）"""
        role = await Role.get_or_none(id=role_id)
        if not role:
            return None

        role_menus = await RoleMenu.filter(role_id=role_id).all()
        menu_ids = [rm.menu_id for rm in role_menus]

        return RoleWithMenusResponse(
            id=role.id,
            name=role.name,
            code=role.code,
            description=role.description,
            status=role.status,
            menu_ids=menu_ids,
            created_at=role.created_at,
            updated_at=role.updated_at
        )

    async def get_roles(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ):
        """获取角色列表"""
        query = Role.all()
        if status:
            query = query.filter(status=status)
        if keyword:
            query = query.filter(name__icontains=keyword)

        total = await query.count()
        roles = await query.offset((page - 1) * page_size).limit(page_size).all()

        items = [RoleListResponse(
            id=r.id,
            name=r.name,
            code=r.code,
            description=r.description,
            status=r.status,
            created_at=r.created_at
        ) for r in roles]

        return {"total": total, "page": page, "page_size": page_size, "items": items}

    async def get_all_roles(self) -> List[RoleListResponse]:
        """获取所有角色（下拉选择用）"""
        roles = await Role.filter(status="active").all()
        return [RoleListResponse(
            id=r.id,
            name=r.name,
            code=r.code,
            description=r.description,
            status=r.status,
            created_at=r.created_at
        ) for r in roles]

    async def update_role(self, role_id: int, data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        role = await Role.get_or_none(id=role_id)
        if not role:
            return None

        update_data = data.dict(exclude_unset=True)
        if update_data:
            await Role.filter(id=role_id).update(**update_data)

        return await Role.get(id=role_id)

    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        role = await Role.get_or_none(id=role_id)
        if not role:
            return False

        # 检查是否有用户使用该角色
        user_count = await UserRole.filter(role_id=role_id).count()
        if user_count > 0:
            return False  # 有用户使用不允许删除

        # 删除角色菜单关联
        await RoleMenu.filter(role_id=role_id).delete()
        await role.delete()
        return True

    async def assign_menus(self, role_id: int, menu_ids: List[int]) -> bool:
        """分配菜单权限"""
        role = await Role.get_or_none(id=role_id)
        if not role:
            return False

        # 删除原有菜单关联
        await RoleMenu.filter(role_id=role_id).delete()

        # 创建新的菜单关联
        for menu_id in menu_ids:
            await RoleMenu.create(role_id=role_id, menu_id=menu_id)

        return True