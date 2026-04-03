/**
 * 认证相关API
 */
import request from '@/utils/request'
import type { LoginParams, RegisterParams, UserUpdateParams, PasswordUpdateParams, User } from '@/types/user'

/**
 * 用户登录
 */
export function login(data: LoginParams) {
  return request.post<any, { access_token: string; token_type: string; expires_in: number; user: User }>('/v1/auth/login', data)
}

/**
 * 用户注册（仅管理员可调用）
 */
export function register(data: RegisterParams) {
  return request.post<any, { id: number; username: string; role: string; created_at: string }>('/v1/auth/register', data)
}

/**
 * 获取当前用户信息
 */
export function getProfile() {
  return request.get<any, User>('/v1/auth/profile')
}

/**
 * 更新当前用户信息
 */
export function updateProfile(data: UserUpdateParams) {
  return request.put<any, User>('/v1/auth/profile', data)
}

/**
 * 修改密码
 */
export function updatePassword(data: PasswordUpdateParams) {
  return request.put<any, void>('/v1/auth/password', data)
}

/**
 * 刷新Token
 */
export function refreshToken() {
  return request.post<any, { access_token: string; token_type: string; expires_in: number }>('/v1/auth/refresh')
}

/**
 * 登出
 */
export function logout() {
  return request.post<any, void>('/v1/auth/logout')
}