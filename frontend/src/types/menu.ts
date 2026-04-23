/**
 * 菜单相关类型定义
 */

/** 菜单类型 */
export type MenuType = 'directory' | 'menu' | 'button'

/** 菜单状态 */
export type MenuStatus = 'active' | 'inactive'

/** 菜单基础接口 */
export interface MenuBase {
  parent_id?: number
  name: string
  path: string
  component?: string
  icon?: string
  sort: number
  visible: boolean
  status: MenuStatus
  menu_type: MenuType
  permission?: string
}

/** 菜单创建请求 */
export interface MenuCreate extends MenuBase {}

/** 菜单更新请求 */
export interface MenuUpdate {
  parent_id?: number
  name?: string
  path?: string
  component?: string
  icon?: string
  sort?: number
  visible?: boolean
  status?: MenuStatus
  menu_type?: MenuType
  permission?: string
}

/** 菜单响应 */
export interface MenuResponse extends MenuBase {
  id: number
  created_at: string
  updated_at: string
}

/** 菜单树形响应 */
export interface MenuTreeResponse extends MenuBase {
  id: number
  children: MenuTreeResponse[]
  created_at: string
  updated_at: string
}

/** 菜单列表响应（扁平） */
export interface MenuListResponse {
  id: number
  parent_id?: number
  name: string
  path: string
  icon?: string
  sort: number
  visible: boolean
  status: MenuStatus
  menu_type: MenuType
  permission?: string
  created_at: string
}

/** 用户菜单响应（用于前端路由） */
export interface UserMenuResponse {
  id: number
  parent_id?: number
  name: string
  path: string
  component?: string
  icon?: string
  sort: number
  menu_type: MenuType
  is_external: boolean
  external_url?: string
  link_target: string
  children: UserMenuResponse[]
}