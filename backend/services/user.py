"""
用户管理服务
"""
from typing import Optional, List
from models.user import User
from models.user_role import UserRole
from schemas.user import UserCreate, UserUpdate, UserListResponse
import bcrypt


def hash_password(password: str) -> str:
    """加密密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class UserService:
    """用户服务"""

    async def create_user(self, data: UserCreate) -> User:
        """创建用户"""
        user = await User.create(
            username=data.username,
            password=hash_password(data.password),
            email=data.email,
            nickname=data.nickname,
            role=data.role,
            status="active"
        )
        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        """获取单个用户"""
        return await User.get_or_none(id=user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return await User.get_or_none(username=username)

    async def get_users(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ):
        """获取用户列表"""
        query = User.all()
        if role:
            query = query.filter(role=role)
        if status:
            query = query.filter(status=status)
        if keyword:
            query = query.filter(username__icontains=keyword)

        total = await query.count()
        users = await query.offset((page - 1) * page_size).limit(page_size).all()

        items = [UserListResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            nickname=u.nickname,
            role=u.role,
            status=u.status,
            last_login=u.last_login,
            created_at=u.created_at
        ) for u in users]

        return {"total": total, "page": page, "page_size": page_size, "items": items}

    async def get_all_users(self) -> List[UserListResponse]:
        """获取所有用户"""
        users = await User.filter(status="active").all()
        return [UserListResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            nickname=u.nickname,
            role=u.role,
            status=u.status,
            last_login=u.last_login,
            created_at=u.created_at
        ) for u in users]

    async def update_user(self, user_id: int, data: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return None

        update_data = data.dict(exclude_unset=True)
        if update_data:
            await User.filter(id=user_id).update(**update_data)

        return await User.get(id=user_id)

    async def update_password(self, user_id: int, new_password: str) -> bool:
        """更新密码"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return False

        user.password = hash_password(new_password)
        await user.save()
        return True

    async def reset_password(self, user_id: int, new_password: str) -> bool:
        """重置密码（管理员操作）"""
        return await self.update_password(user_id, new_password)

    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return False

        # 不能删除admin用户
        if user.username == "admin":
            return False

        # 删除用户角色关联
        await UserRole.filter(user_id=user_id).delete()
        await user.delete()
        return True

    async def assign_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """分配角色"""
        user = await User.get_or_none(id=user_id)
        if not user:
            return False

        # 删除原有角色关联
        await UserRole.filter(user_id=user_id).delete()

        # 创建新的角色关联
        for role_id in role_ids:
            await UserRole.create(user_id=user_id, role_id=role_id)

        return True

    async def get_user_role_ids(self, user_id: int) -> List[int]:
        """获取用户的角色ID列表"""
        user_roles = await UserRole.filter(user_id=user_id).all()
        return [ur.role_id for ur in user_roles]