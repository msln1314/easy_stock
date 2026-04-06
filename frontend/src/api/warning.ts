/**
 * 预警相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface WarningCondition {
  id: number
  condition_key: string
  condition_name: string
  indicator_key: string
  indicator_key2?: string
  period: string
  condition_rule: string
  priority: 'critical' | 'warning' | 'info'
  is_enabled: boolean
  description?: string
}

export interface WarningStock {
  id: number
  stock_code: string
  stock_name: string
  price: number
  change_percent: number
  condition_name: string
  warning_level: 'critical' | 'warning' | 'info'
  trigger_time: string
  trigger_value: Record<string, any>
  is_handled: boolean
  handle_action?: string
}

export interface IndicatorInfo {
  id: number
  indicator_key: string
  indicator_name: string
  category: string
  parameters: Record<string, any>
  output_fields: Record<string, any>
  is_builtin: boolean
}

// ==================== 指标库接口 ====================

/** 获取指标库列表 */
export async function fetchIndicators(): Promise<IndicatorInfo[]> {
  return request.get('/warning/indicators')
}

// ==================== 预警条件接口 ====================

/** 获取预警条件列表 */
export async function fetchWarningConditions(): Promise<WarningCondition[]> {
  return request.get('/warning/conditions')
}

/** 创建预警条件 */
export async function createWarningCondition(data: Partial<WarningCondition>): Promise<{ id: number }> {
  return request.post('/warning/conditions', data)
}

/** 更新预警条件 */
export async function updateWarningCondition(id: number, data: { is_enabled?: boolean; priority?: string }): Promise<void> {
  return request.put(`/warning/conditions/${id}`, data)
}

/** 初始化预置预警条件 */
export async function initWarningConditions(): Promise<void> {
  return request.post('/warning/conditions/init')
}

/** 创建自定义预警条件 */
export async function createCustomCondition(data: {
  condition_name: string
  description?: string
  priority: string
  rule_type: string
  indicator_key: string
  indicator_params: Record<string, any>
  rule_config: Record<string, any>
}): Promise<{ id: number }> {
  return request.post('/warning/conditions/custom', data)
}

// ==================== 预警股票池接口 ====================

/** 获取预警股票池 */
export async function fetchWarningStocks(params?: {
  level?: string
  handled?: boolean
  limit?: number
}): Promise<WarningStock[]> {
  return request.get('/warning/stocks', { params })
}

/** 处理预警股票 */
export async function handleWarningStock(id: number, action: 'IGNORE' | 'SELL' | 'WATCH'): Promise<void> {
  return request.put(`/warning/stocks/${id}/handle`, { action })
}

/** 删除预警记录 */
export async function deleteWarningStock(id: number): Promise<void> {
  return request.delete(`/warning/stocks/${id}`)
}

/** 清理已处理的预警记录 */
export async function clearHandledStocks(): Promise<void> {
  return request.delete('/warning/stocks')
}