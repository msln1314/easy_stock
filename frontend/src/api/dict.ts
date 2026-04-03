/**
 * 字典管理API
 */
import request from '@/utils/request'
import type {
  DictType,
  DictItem,
  DictTypeCreateParams,
  DictTypeUpdateParams,
  DictItemCreateParams,
  DictItemUpdateParams,
  PaginatedResponse
} from '@/types/dict'

// ==================== 字典类型 API ====================

/**
 * 获取字典类型列表
 */
export function getDictTypes(params?: {
  category?: string
  access_type?: string
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}) {
  return request.get<any, PaginatedResponse<DictType>>('/v1/dict/types', { params })
}

/**
 * 获取字典类型详情
 */
export function getDictType(typeId: number) {
  return request.get<any, DictType>(`/v1/dict/types/${typeId}`)
}

/**
 * 创建字典类型
 */
export function createDictType(data: DictTypeCreateParams) {
  return request.post<any, DictType>('/v1/dict/types', data)
}

/**
 * 更新字典类型
 */
export function updateDictType(typeId: number, data: DictTypeUpdateParams) {
  return request.put<any, DictType>(`/v1/dict/types/${typeId}`, data)
}

/**
 * 删除字典类型
 */
export function deleteDictType(typeId: number) {
  return request.delete<any, void>(`/v1/dict/types/${typeId}`)
}

// ==================== 字典项 API ====================

/**
 * 根据类型编码获取字典项
 */
export function getDictItemsByTypeCode(code: string) {
  return request.get<any, DictItem[]>(`/v1/dict/types/${code}/items`)
}

/**
 * 获取字典项列表
 */
export function getDictItems(params?: {
  type_id?: number
  parent_id?: number
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}) {
  return request.get<any, PaginatedResponse<DictItem>>('/v1/dict/items', { params })
}

/**
 * 获取字典项详情
 */
export function getDictItem(itemId: number) {
  return request.get<any, DictItem>(`/v1/dict/items/${itemId}`)
}

/**
 * 创建字典项
 */
export function createDictItem(data: DictItemCreateParams) {
  return request.post<any, DictItem>('/v1/dict/items', data)
}

/**
 * 更新字典项
 */
export function updateDictItem(itemId: number, data: DictItemUpdateParams) {
  return request.put<any, DictItem>(`/v1/dict/items/${itemId}`, data)
}

/**
 * 删除字典项
 */
export function deleteDictItem(itemId: number) {
  return request.delete<any, void>(`/v1/dict/items/${itemId}`)
}

/**
 * 获取字典项树形结构
 */
export function getDictItemsTree(typeId: number) {
  return request.get<any, DictItem[]>('/v1/dict/items/tree', { params: { type_id: typeId } })
}