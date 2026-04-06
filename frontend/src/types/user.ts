/**
 * 用户相关类型定义
 */

/** 用户状态 */
export type UserStatus = 'active' | 'disabled'

/** 用户角色 */
export type UserRole = 'admin' | 'user'

/** 用户列表响应 */
export interface UserListResponse {
  id: number
  username: string
  email?: string
  nickname?: string
  role: UserRole
  status: UserStatus
  last_login?: string
  created_at: string
}

/** 用户详情响应（含角色） */
export interface UserWithRolesResponse {
  id: number
  username: string
  email?: string
  nickname?: string
  role: UserRole
  status: UserStatus
  last_login?: string
  role_ids: number[]
  created_at: string
  updated_at: string
}

/** 用户创建请求 */
export interface UserCreate {
  username: string
  password: string
  email?: string
  nickname?: string
  role?: UserRole
}

/** 用户更新请求 */
export interface UserUpdate {
  email?: string
  nickname?: string
  status?: UserStatus
}

/** 密码重置请求 */
export interface PasswordReset {
  new_password: string
}

/** 分配角色请求 */
export interface AssignRolesRequest {
  role_ids: number[]
}

/** 用户列表查询参数 */
export interface UserQueryParams {
  role?: UserRole
  status?: UserStatus
  keyword?: string
  page?: number
  pageSize?: number
}