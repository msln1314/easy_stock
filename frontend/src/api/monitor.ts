/**
 * 监控股票池相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface MonitorStock {
  id: number
  stock_code: string
  stock_name: string
  monitor_type: 'hold' | 'watch'
  conditions: string[]
  is_active: boolean
  last_check_time?: string
  last_price?: number
  change_percent?: number
  remark?: string
  created_at?: string
}

export interface WarningConditionOption {
  condition_key: string
  condition_name: string
  indicator_key: string
  period: string
  priority: string
  description?: string
}

// ==================== 监控股票接口 ====================

/** 获取监控股票列表 */
export async function fetchMonitorStocks(params?: {
  monitor_type?: string
  is_active?: boolean
}): Promise<MonitorStock[]> {
  return request.get('/monitor/stocks', { params })
}

/** 添加监控股票 */
export async function addMonitorStock(data: {
  stock_code: string
  stock_name?: string
  monitor_type?: string
  conditions?: string[]
  remark?: string
}): Promise<{ id: number }> {
  return request.post('/monitor/stocks', data)
}

/** 批量添加监控股票 */
export async function batchAddMonitorStocks(stocks: {
  stock_code: string
  stock_name?: string
  monitor_type?: string
  conditions?: string[]
  remark?: string
}[]): Promise<{ added: number; skipped: number }> {
  return request.post('/monitor/stocks/batch', { stocks })
}

/** 更新监控股票 */
export async function updateMonitorStock(id: number, data: {
  stock_name?: string
  monitor_type?: string
  conditions?: string[]
  is_active?: boolean
  remark?: string
}): Promise<void> {
  return request.put(`/monitor/stocks/${id}`, data)
}

/** 删除监控股票 */
export async function deleteMonitorStock(id: number): Promise<void> {
  return request.delete(`/monitor/stocks/${id}`)
}

/** 检测单只股票 */
export async function checkSingleStock(id: number): Promise<{
  success: boolean
  stock_code: string
  stock_name: string
  triggered_count: number
  warnings: any[]
}> {
  return request.post(`/monitor/stocks/${id}/check`)
}

/** 检测所有股票 */
export async function checkAllStocks(): Promise<{
  success: boolean
  checked: number
  triggered: number
  message: string
}> {
  return request.post('/monitor/stocks/check-all')
}

/** 获取可用预警条件 */
export async function fetchAvailableConditions(): Promise<WarningConditionOption[]> {
  return request.get('/monitor/conditions')
}

/** 模糊搜索股票 */
export async function searchStocks(keyword: string): Promise<{stock_code: string, stock_name: string}[]> {
  return request.get('/monitor/stocks/search', { params: { keyword } })
}