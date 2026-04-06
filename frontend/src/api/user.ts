/**
 * 用户管理API
 */
import request from '@/utils/request'
import type {
  UserListResponse,
  UserWithRolesResponse,
  UserCreate,
  UserUpdate,
  PasswordReset,
  AssignRolesRequest,
  UserQueryParams
} from '@/types/user'

interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

/**
 * 获取用户列表
 */
export function getUsers(params?: UserQueryParams) {
  return request.get<any, PaginatedResponse<UserListResponse>>('/v1/users', { params })
}

/**
 * 获取所有用户（下拉选择用）
 */
export function getAllUsers() {
  return request.get<any, UserListResponse[]>('/v1/users/all')
}

/**
 * 获取用户详情
 */
export function getUser(userId: number) {
  return request.get<any, UserWithRolesResponse>(`/v1/users/${userId}`)
}

/**
 * 创建用户
 */
export function createUser(data: UserCreate) {
  return request.post<any, UserWithRolesResponse>('/v1/users', data)
}

/**
 * 更新用户
 */
export function updateUser(userId: number, data: UserUpdate) {
  return request.put<any, UserWithRolesResponse>(`/v1/users/${userId}`, data)
}

/**
 * 删除用户
 */
export function deleteUser(userId: number) {
  return request.delete<any, void>(`/v1/users/${userId}`)
}

/**
 * 重置密码
 */
export function resetPassword(userId: number, data: PasswordReset) {
  return request.put<any, void>(`/v1/users/${userId}/password`, data)
}

/**
 * 分配角色
 */
export function assignRoles(userId: number, data: AssignRolesRequest) {
  return request.put<any, void>(`/v1/users/${userId}/roles`, data)
}