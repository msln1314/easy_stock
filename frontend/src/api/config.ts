/**
 * 系统配置API
 */
import request from '@/utils/request'
import type {
  SysConfig,
  SysConfigCreateParams,
  SysConfigUpdateParams,
  PaginatedResponse
} from '@/types/config'

/**
 * 获取系统配置列表
 */
export function getConfigs(params?: {
  category?: string
  access_type?: string
  keyword?: string
  page?: number
  page_size?: number
}) {
  return request.get<any, PaginatedResponse<SysConfig>>('/v1/configs', { params })
}

/**
 * 获取公开配置（无需认证）
 */
export function getPublicConfigs() {
  return request.get<any, Record<string, string>>('/v1/configs/public')
}

/**
 * 按类别获取配置
 */
export function getConfigsByCategory(category: 'basic' | 'security' | 'notification' | 'ai') {
  return request.get<any, SysConfig[]>(`/v1/configs/category/${category}`)
}

/**
 * 获取单个配置详情
 */
export function getConfig(key: string) {
  return request.get<any, SysConfig>(`/v1/configs/${key}`)
}

/**
 * 创建系统配置（仅管理员）
 */
export function createConfig(data: SysConfigCreateParams) {
  return request.post<any, SysConfig>('/v1/configs', data)
}

/**
 * 更新系统配置（仅管理员）
 */
export function updateConfig(key: string, data: SysConfigUpdateParams) {
  return request.put<any, SysConfig>(`/v1/configs/${key}`, data)
}

/**
 * 删除系统配置（仅管理员）
 */
export function deleteConfig(key: string) {
  return request.delete<any, void>(`/v1/configs/${key}`)
}

/**
 * 批量更新配置值（仅管理员）
 */
export function batchUpdateConfigs(configs: Record<string, string>) {
  return request.post<any, void>('/v1/configs/batch', configs)
}