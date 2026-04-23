"""
用户认证API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from core.response import success_response, error_response
from core.auth import (
    hash_password, verify_password, create_token,
    get_current_user_required, get_admin_user
)
from schemas.user import (
    UserLogin, UserCreate, UserUpdate, UserPasswordUpdate,
    UserResponse, TokenResponse
)
from models.user import User
from api.v1.captcha import verify_captcha_internal
from services.config import SysConfigService

router = APIRouter(prefix="/api/v1/auth", tags=["用户认证"])
config_service = SysConfigService()


@router.post("/login", response_model=None)
async def login(data: UserLogin):
    """用户登录"""
    # 检查是否启用验证码
    captcha_enabled = await config_service.get_config_value("login_captcha_enabled")
    if captcha_enabled == "true":
        if not data.captcha_id or not data.captcha_code:
            return error_response("请输入验证码", 400)
        if not verify_captcha_internal(data.captcha_id, data.captcha_code):
            return error_response("验证码错误或已过期", 400)

    # 查找用户
    user = await User.get_or_none(username=data.username)
    if not user:
        return error_response("用户名或密码错误", 401)

    # 验证密码
    if not verify_password(data.password, user.password):
        return error_response("用户名或密码错误", 401)

    # 检查状态
    if user.status != "active":
        return error_response("用户已被禁用", 403)

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await user.save()

    # 生成Token
    token = create_token(user.id, user.username, user.role)

    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400,  # 24小时
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "status": user.status,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    })


@router.post("/register", response_model=None)
async def register(data: UserCreate, admin: User = Depends(get_admin_user)):
    """用户注册（仅管理员可调用）"""
    # 检查用户名是否存在
    existing = await User.get_or_none(username=data.username)
    if existing:
        return error_response("用户名已存在", 400)

    # 检查邮箱是否存在
    if data.email:
        existing_email = await User.get_or_none(email=data.email)
        if existing_email:
            return error_response("邮箱已存在", 400)

    # 创建用户
    user = await User.create(
        username=data.username,
        password=hash_password(data.password),
        email=data.email,
        nickname=data.nickname,
        role=data.role
    )

    return success_response({
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at.isoformat()
    })


@router.get("/profile", response_model=None)
async def get_profile(user: User = Depends(get_current_user_required)):
    """获取当前用户信息"""
    return success_response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
        "status": user.status,
        "api_key": user.api_key,
        "qmt_account_id": user.qmt_account_id,
        "qmt_account_name": user.qmt_account_name,
        "qmt_client_path": user.qmt_client_path,
        "qmt_session_id": user.qmt_session_id,
        "qmt_enabled": user.qmt_enabled,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    })


@router.put("/profile", response_model=None)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user_required)
):
    """更新当前用户信息"""
    # 检查邮箱是否被其他用户使用
    if data.email:
        existing = await User.get_or_none(email=data.email)
        if existing and existing.id != user.id:
            return error_response("邮箱已被其他用户使用", 400)

    # 更新字段
    update_data = data.dict(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(user, key, value)
        await user.save()

    return success_response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "updated_at": user.updated_at.isoformat()
    })


@router.put("/password", response_model=None)
async def update_password(
    data: UserPasswordUpdate,
    user: User = Depends(get_current_user_required)
):
    """修改密码"""
    # 验证原密码
    if not verify_password(data.old_password, user.password):
        return error_response("原密码错误", 400)

    # 更新密码
    user.password = hash_password(data.new_password)
    await user.save()

    return success_response(message="密码修改成功")


@router.post("/refresh", response_model=None)
async def refresh_token(user: User = Depends(get_current_user_required)):
    """刷新Token"""
    token = create_token(user.id, user.username, user.role)

    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400
    })


@router.post("/logout", response_model=None)
async def logout(user: User = Depends(get_current_user_required)):
    """登出（客户端清除Token即可）"""
    return success_response(message="登出成功")