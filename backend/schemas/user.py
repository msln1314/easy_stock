"""
用户相关Schema定义
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    captcha_id: Optional[str] = Field(None, description="验证码ID")
    captcha_code: Optional[str] = Field(None, description="验证码")


class UserCreate(BaseModel):
    """用户创建"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    role: str = Field(default="user", description="角色: admin/user")


class UserUpdate(BaseModel):
    """用户更新"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    status: Optional[str] = Field(None, description="状态: active/disabled")


class UserPasswordUpdate(BaseModel):
    """密码更新"""
    old_password: str = Field(..., min_length=6, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: Optional[str]
    nickname: Optional[str]
    role: str
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    id: int
    username: str
    email: Optional[str]
    nickname: Optional[str]
    role: str
    status: str
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginResponse(BaseModel):
    """登录响应"""
    code: int = 200
    message: str = "success"
    data: TokenResponse


class PasswordReset(BaseModel):
    """密码重置"""
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class AssignRolesRequest(BaseModel):
    """分配角色请求"""
    role_ids: list[int] = Field(..., description="角色ID列表")