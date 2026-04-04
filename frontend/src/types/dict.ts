/**
 * 字典相关类型定义
 */
export interface DictType {
  id: number
  code: string
  name: string
  category: 'system' | 'custom' | 'config'
  access_type: 'public' | 'private'
  description?: string
  sort: number
  status: 'active' | 'disabled'
  created_by?: number
  created_at: string
  updated_at: string
}

export interface DictItem {
  id: number
  type_id: number
  code: string
  name: string
  value?: string
  data_type: 'plain' | 'encrypted'
  access_type: 'public' | 'private'
  parent_id?: number
  sort: number
  status: 'active' | 'disabled'
  remark?: string
  decrypted_value?: string
  created_at: string
  updated_at: string
  children?: DictItem[]
}

export interface DictTypeCreateParams {
  code: string
  name: string
  category?: 'system' | 'custom' | 'config'
  access_type?: 'public' | 'private'
  description?: string
  sort?: number
  status?: 'active' | 'disabled'
}

export interface DictTypeUpdateParams {
  name?: string
  category?: 'system' | 'custom' | 'config'
  access_type?: 'public' | 'private'
  description?: string
  sort?: number
  status?: 'active' | 'disabled'
}

export interface DictItemCreateParams {
  type_id: number
  code: string
  name: string
  value?: string
  data_type?: 'plain' | 'encrypted'
  access_type?: 'public' | 'private'
  parent_id?: number
  sort?: number
  status?: 'active' | 'disabled'
  remark?: string
}

export interface DictItemUpdateParams {
  name?: string
  value?: string
  data_type?: 'plain' | 'encrypted'
  access_type?: 'public' | 'private'
  parent_id?: number
  sort?: number
  status?: 'active' | 'disabled'
  remark?: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}