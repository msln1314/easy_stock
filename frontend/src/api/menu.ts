/**
 * 菜单管理API
 */
import request from '@/utils/request'
import type {
  MenuCreate,
  MenuUpdate,
  MenuTreeResponse,
  MenuListResponse,
  UserMenuResponse
} from '@/types/menu'

/**
 * 获取菜单树形列表
 */
export function getMenuTree() {
  return request.get<any, MenuTreeResponse[]>('/v1/menus')
}

/**
 * 获取所有菜单（扁平列表）
 */
export function getAllMenus() {
  return request.get<any, MenuListResponse[]>('/v1/menus/all')
}

/**
 * 获取当前用户菜单
 */
export function getUserMenus() {
  return request.get<any, UserMenuResponse[]>('/v1/menus/user')
}

/**
 * 获取菜单详情
 */
export function getMenu(menuId: number) {
  return request.get<any, MenuTreeResponse>(`/v1/menus/${menuId}`)
}

/**
 * 创建菜单
 */
export function createMenu(data: MenuCreate) {
  return request.post<any, MenuTreeResponse>('/v1/menus', data)
}

/**
 * 更新菜单
 */
export function updateMenu(menuId: number, data: MenuUpdate) {
  return request.put<any, MenuTreeResponse>(`/v1/menus/${menuId}`, data)
}

/**
 * 删除菜单
 */
export function deleteMenu(menuId: number) {
  return request.delete<any, void>(`/v1/menus/${menuId}`)
}