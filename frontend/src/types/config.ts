/**
 * 系统配置相关类型定义
 */
export interface SysConfig {
  id: number
  key: string
  value: string
  category: 'basic' | 'security' | 'notification'
  data_type: 'plain' | 'encrypted'
  access_type: 'public' | 'private'
  description?: string
  decrypted_value?: string
  created_at: string
  updated_at: string
}

export interface SysConfigCreateParams {
  key: string
  value: string
  category?: 'basic' | 'security' | 'notification'
  data_type?: 'plain' | 'encrypted'
  access_type?: 'public' | 'private'
  description?: string
}

export interface SysConfigUpdateParams {
  value?: string
  category?: 'basic' | 'security' | 'notification'
  data_type?: 'plain' | 'encrypted'
  access_type?: 'public' | 'private'
  description?: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}