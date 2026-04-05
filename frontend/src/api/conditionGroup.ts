/**
 * 组合条件 API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface ConditionGroup {
  id: number
  group_key: string
  group_name: string
  logic_type: 'AND' | 'OR'
  priority: string
  is_enabled: boolean
  parent_id: number | null
  description: string | null
  condition_count: number
  subgroup_count: number
  created_at: string
  updated_at: string
}

export interface ConditionGroupTreeNode {
  id: number
  group_key: string
  group_name: string
  logic_type: 'AND' | 'OR'
  priority: string
  is_enabled: boolean
  description: string | null
  conditions: ConditionItem[]
  subgroups: ConditionGroupTreeNode[]
}

export interface ConditionItem {
  item_id?: number
  condition_id: number
  condition_key: string
  condition_name: string
  priority: string
  sort_order?: number
}

export interface CreateGroupParams {
  group_name: string
  logic_type: 'AND' | 'OR'
  parent_id?: number
  priority?: string
  description?: string
  condition_ids?: number[]
}

export interface UpdateGroupParams {
  group_name?: string
  logic_type?: 'AND' | 'OR'
  priority?: string
  is_enabled?: boolean
  description?: string
}

// ==================== API 函数 ====================

/** 获取组合条件列表 */
export async function fetchConditionGroups(parentId?: number): Promise<ConditionGroup[]> {
  const params = parentId !== undefined ? { parent_id: parentId } : {}
  return request.get('/warning/groups', { params })
}

/** 获取组合条件树 */
export async function fetchConditionGroupTree(): Promise<ConditionGroupTreeNode[]> {
  return request.get('/warning/groups/tree')
}

/** 获取单个组合条件详情 */
export async function fetchConditionGroup(id: number): Promise<ConditionGroupTreeNode> {
  return request.get(`/warning/groups/${id}`)
}

/** 创建组合条件 */
export async function createConditionGroup(data: CreateGroupParams): Promise<{ id: number; group_key: string }> {
  return request.post('/warning/groups', data)
}

/** 更新组合条件 */
export async function updateConditionGroup(id: number, data: UpdateGroupParams): Promise<void> {
  return request.put(`/warning/groups/${id}`, data)
}

/** 删除组合条件 */
export async function deleteConditionGroup(id: number): Promise<void> {
  return request.delete(`/warning/groups/${id}`)
}

/** 添加条件项 */
export async function addConditionItem(groupId: number, conditionId: number, sortOrder?: number): Promise<{ id: number }> {
  return request.post(`/warning/groups/${groupId}/items`, { condition_id: conditionId, sort_order: sortOrder })
}

/** 移除条件项 */
export async function removeConditionItem(groupId: number, itemId: number): Promise<void> {
  return request.delete(`/warning/groups/${groupId}/items/${itemId}`)
}

/** 创建子分组 */
export async function createSubgroup(parentId: number, data: CreateGroupParams): Promise<{ id: number; group_key: string }> {
  return request.post(`/warning/groups/${parentId}/subgroups`, data)
}