/**
 * 认证相关API
 */
import request from '@/utils/request'
import type { LoginParams, RegisterParams, UserUpdateParams, PasswordUpdateParams, User, QmtAccountConfig, QmtAccountUpdate } from '@/types/user'

/**
 * 用户登录
 */
export function login(data: LoginParams) {
  return request.post<any, { access_token: string; token_type: string; expires_in: number; user: User }>('/auth/login', data)
}

/**
 * 用户注册（仅管理员可调用）
 */
export function register(data: RegisterParams) {
  return request.post<any, { id: number; username: string; role: string; created_at: string }>('/auth/register', data)
}

/**
 * 获取当前用户信息
 */
export function getProfile() {
  return request.get<any, User>('/auth/profile')
}

/**
 * 更新当前用户信息
 */
export function updateProfile(data: UserUpdateParams) {
  return request.put<any, User>('/auth/profile', data)
}

/**
 * 修改密码
 */
export function updatePassword(data: PasswordUpdateParams) {
  return request.put<any, void>('/auth/password', data)
}

/**
 * 获取用户QMT账户配置
 */
export function getQmtAccount(userId: number) {
  return request.get<any, QmtAccountConfig>(`/users/${userId}/qmt`)
}

/**
 * 更新用户QMT账户配置
 */
export function updateQmtAccount(userId: number, data: QmtAccountUpdate) {
  return request.put<any, { id: number; qmt_account_id: string; qmt_enabled: boolean; message: string }>(`/users/${userId}/qmt`, data)
}

/**
 * 启用QMT交易
 */
export function enableQmt(userId: number) {
  return request.post<any, { message: string }>(`/users/${userId}/qmt/enable`)
}

/**
 * 禁用QMT交易
 */
export function disableQmt(userId: number) {
  return request.post<any, { message: string }>(`/users/${userId}/qmt/disable`)
}

/**
 * 获取用户API Key
 */
export function getApiKey() {
  return request.get<any, { api_key: string; has_api_key: boolean }>('/users/me/api-key')
}

/**
 * 刷新用户API Key
 */
export function refreshApiKey() {
  return request.post<any, { api_key: string; message: string }>('/users/me/api-key/refresh')
}
export function refreshToken() {
  return request.post<any, { access_token: string; token_type: string; expires_in: number }>('/auth/refresh')
}

/**
 * 登出
 */
export function logout() {
  return request.post<any, void>('/auth/logout')
}