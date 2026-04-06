"""
认证工具模块
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt

from config.settings import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from models.user import User

# 密码加密上下文
# 支持 bcrypt 和 bcrypt_sha256，兼容已有密码
# bcrypt_sha256 用于新密码，bcrypt 用于验证旧密码
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
    bcrypt_sha256__default_rounds=12,
    bcrypt__default_rounds=12
)

# Bearer认证方案
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_token(user_id: int, username: str, role: str, expire_minutes: Optional[int] = None) -> str:
    """创建JWT Token"""
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes or JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    """获取当前用户（依赖注入）"""
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的Token"
        )

    user_id = payload.get("user_id")
    user = await User.get_or_none(id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """获取当前用户（必须登录）"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录"
        )
    return user


async def get_admin_user(
    user: User = Depends(get_current_user_required)
) -> User:
    """获取管理员用户（仅管理员可访问）"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return user