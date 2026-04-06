"""
菜单业务逻辑服务
"""
from typing import Optional, List, Dict
from models.menu import Menu
from models.role_menu import RoleMenu
from models.user_role import UserRole
from schemas.menu import (
    MenuCreate, MenuUpdate, MenuResponse,
    MenuTreeResponse, MenuListResponse, UserMenuResponse
)


class MenuService:
    """菜单服务"""

    async def create_menu(self, data: MenuCreate) -> Menu:
        """创建菜单"""
        menu = await Menu.create(
            parent_id=data.parent_id,
            name=data.name,
            path=data.path,
            component=data.component,
            icon=data.icon,
            sort=data.sort,
            visible=data.visible,
            status=data.status,
            menu_type=data.menu_type,
            permission=data.permission
        )
        return menu

    async def get_menu(self, menu_id: int) -> Optional[Menu]:
        """获取单个菜单"""
        return await Menu.get_or_none(id=menu_id)

    async def get_all_menus(self) -> List[MenuListResponse]:
        """获取所有菜单（扁平列表）"""
        menus = await Menu.all().order_by('sort', 'id')
        return [MenuListResponse(
            id=m.id,
            parent_id=m.parent_id,
            name=m.name,
            path=m.path,
            icon=m.icon,
            sort=m.sort,
            visible=m.visible,
            status=m.status,
            menu_type=m.menu_type,
            permission=m.permission,
            created_at=m.created_at
        ) for m in menus]

    async def get_menu_tree(self) -> List[MenuTreeResponse]:
        """获取菜单树形结构"""
        menus = await Menu.filter(status="active").order_by('sort', 'id').all()

        # 构建树形结构
        menu_map: Dict[int, MenuTreeResponse] = {}
        root_menus: List[MenuTreeResponse] = []

        for m in menus:
            tree_item = MenuTreeResponse(
                id=m.id,
                parent_id=m.parent_id,
                name=m.name,
                path=m.path,
                component=m.component,
                icon=m.icon,
                sort=m.sort,
                visible=m.visible,
                status=m.status,
                menu_type=m.menu_type,
                permission=m.permission,
                children=[],
                created_at=m.created_at,
                updated_at=m.updated_at
            )
            menu_map[m.id] = tree_item

        for m in menus:
            tree_item = menu_map[m.id]
            if m.parent_id and m.parent_id in menu_map:
                menu_map[m.parent_id].children.append(tree_item)
            else:
                root_menus.append(tree_item)

        return root_menus

    async def get_user_menus(self, user_id: int) -> List[UserMenuResponse]:
        """获取用户菜单（根据角色权限）"""
        # 获取用户所有角色
        user_roles = await UserRole.filter(user_id=user_id).all()
        role_ids = [ur.role_id for ur in user_roles]

        if not role_ids:
            return []

        # 获取角色关联的菜单ID
        role_menus = await RoleMenu.filter(role_id__in=role_ids).all()
        menu_ids = list(set([rm.menu_id for rm in role_menus]))

        if not menu_ids:
            return []

        # 获取菜单
        menus = await Menu.filter(
            id__in=menu_ids,
            status="active",
            visible=True
        ).order_by('sort', 'id').all()

        # 构建树形结构
        menu_map: Dict[int, UserMenuResponse] = {}
        root_menus: List[UserMenuResponse] = []

        for m in menus:
            if m.menu_type == "button":
                continue  # 按钮类型不加入菜单树
            menu_item = UserMenuResponse(
                id=m.id,
                parent_id=m.parent_id,
                name=m.name,
                path=m.path,
                icon=m.icon,
                sort=m.sort,
                menu_type=m.menu_type,
                children=[]
            )
            menu_map[m.id] = menu_item

        for m in menus:
            if m.menu_type == "button":
                continue
            menu_item = menu_map[m.id]
            if m.parent_id and m.parent_id in menu_map:
                menu_map[m.parent_id].children.append(menu_item)
            else:
                root_menus.append(menu_item)

        return root_menus

    async def update_menu(self, menu_id: int, data: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        menu = await Menu.get_or_none(id=menu_id)
        if not menu:
            return None

        update_data = data.dict(exclude_unset=True)
        if update_data:
            await Menu.filter(id=menu_id).update(**update_data)

        return await Menu.get(id=menu_id)

    async def delete_menu(self, menu_id: int) -> bool:
        """删除菜单"""
        menu = await Menu.get_or_none(id=menu_id)
        if not menu:
            return False

        # 检查是否有子菜单
        children = await Menu.filter(parent_id=menu_id).count()
        if children > 0:
            return False  # 有子菜单不允许删除

        # 删除角色菜单关联
        await RoleMenu.filter(menu_id=menu_id).delete()
        await menu.delete()
        return True