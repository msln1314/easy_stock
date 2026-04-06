/**
 * 角色相关类型定义
 */

/** 角色状态 */
export type RoleStatus = 'active' | 'inactive'

/** 角色基础接口 */
export interface RoleBase {
  name: string
  code: string
  description?: string
  status: RoleStatus
}

/** 角色创建请求 */
export interface RoleCreate extends RoleBase {
  menu_ids?: number[]
}

/** 角色更新请求 */
export interface RoleUpdate {
  name?: string
  code?: string
  description?: string
  status?: RoleStatus
}

/** 角色响应 */
export interface RoleResponse extends RoleBase {
  id: number
  created_at: string
  updated_at: string
}

/** 角色列表响应 */
export interface RoleListResponse {
  id: number
  name: string
  code: string
  description?: string
  status: RoleStatus
  created_at: string
}

/** 角色详情响应（含菜单） */
export interface RoleWithMenusResponse extends RoleBase {
  id: number
  menu_ids: number[]
  created_at: string
  updated_at: string
}

/** 分配菜单请求 */
export interface AssignMenusRequest {
  menu_ids: number[]
}

/** 角色列表查询参数 */
export interface RoleQueryParams {
  status?: RoleStatus
  keyword?: string
  page?: number
  pageSize?: number
}