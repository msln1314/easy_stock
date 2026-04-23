/**
 * 角色管理API
 */
import request from '@/utils/request'
import type {
  RoleCreate,
  RoleUpdate,
  RoleListResponse,
  RoleWithMenusResponse,
  AssignMenusRequest,
  RoleQueryParams
} from '@/types/role'

interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

/**
 * 获取角色列表
 */
export function getRoles(params?: RoleQueryParams) {
  return request.get<any, PaginatedResponse<RoleListResponse>>('/roles', { params })
}

/**
 * 获取所有角色（下拉选择用）
 */
export function getAllRoles() {
  return request.get<any, RoleListResponse[]>('/roles/all')
}

/**
 * 获取角色详情（含菜单ID）
 */
export function getRole(roleId: number) {
  return request.get<any, RoleWithMenusResponse>(`/roles/${roleId}`)
}

/**
 * 创建角色
 */
export function createRole(data: RoleCreate) {
  return request.post<any, RoleWithMenusResponse>('/roles', data)
}

/**
 * 更新角色
 */
export function updateRole(roleId: number, data: RoleUpdate) {
  return request.put<any, RoleWithMenusResponse>(`/roles/${roleId}`, data)
}

/**
 * 删除角色
 */
export function deleteRole(roleId: number) {
  return request.delete<any, void>(`/roles/${roleId}`)
}

/**
 * 分配菜单权限
 */
export function assignMenus(roleId: number, data: AssignMenusRequest) {
  return request.put<any, void>(`/roles/${roleId}/menus`, data)
}