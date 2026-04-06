/**
 * 选股策略相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface StockPickStrategy {
  id: number
  strategy_key: string
  strategy_name: string
  strategy_type: string
  strategy_type_display: string
  description?: string
  strategy_config: Record<string, any>
  duration_days: number
  generate_time: string
  advance_days: number
  is_active: boolean
  auto_generate: boolean
  total_generated: number
  success_rate?: number
  created_at?: string
}

export interface StrategyTrackRecord {
  id: number
  strategy_id: number
  strategy_key: string
  stock_code: string
  stock_name: string
  generate_date: string
  target_date: string
  pool_type: 'today' | 'tomorrow'
  anomaly_type: string
  anomaly_type_display: string
  duration_days: number
  effective_time: string
  expire_time: string
  confidence: number
  confidence_reason?: string
  status: string
  status_display: string
  entry_price?: number
  exit_price?: number
  max_return?: number
  actual_return?: number
  is_active: boolean
  created_at?: string
}

export interface ExecutionLog {
  id: number
  strategy_id: number
  strategy_key: string
  execution_date: string
  pool_type: string
  status: string
  stocks_found: number
  stocks_saved: number
  error_message?: string
  started_at: string
  finished_at?: string
  created_at?: string
}

// ==================== 选股策略接口 ====================

/** 获取选股策略列表 */
export async function fetchStockPickStrategies(params?: {
  strategy_type?: string
  is_active?: boolean
}): Promise<StockPickStrategy[]> {
  return request.get('/stock-pick/strategies', { params })
}

/** 创建选股策略 */
export async function createStockPickStrategy(data: {
  strategy_key: string
  strategy_name: string
  strategy_type?: string
  description?: string
  strategy_config: Record<string, any>
  duration_days?: number
  generate_time?: string
  advance_days?: number
  auto_generate?: boolean
}): Promise<{ id: number }> {
  return request.post('/stock-pick/strategies', data)
}

/** 更新选股策略 */
export async function updateStockPickStrategy(id: number, data: {
  strategy_name?: string
  description?: string
  strategy_config?: Record<string, any>
  duration_days?: number
  generate_time?: string
  advance_days?: number
  is_active?: boolean
  auto_generate?: boolean
}): Promise<void> {
  return request.put(`/stock-pick/strategies/${id}`, data)
}

/** 删除选股策略 */
export async function deleteStockPickStrategy(id: number): Promise<void> {
  return request.delete(`/stock-pick/strategies/${id}`)
}

/** 执行策略 */
export async function executeStrategy(id: number): Promise<{
  strategy_id: number
  strategy_name: string
  message: string
}> {
  return request.post(`/stock-pick/strategies/${id}/execute`)
}

// ==================== 追踪异动池接口 ====================

/** 获取追踪异动池 */
export async function fetchTrackPool(params?: {
  strategy_id?: number
  pool_type?: string
  status?: string
  target_date?: string
  limit?: number
}): Promise<StrategyTrackRecord[]> {
  return request.get('/stock-pick/track-pool', { params })
}

/** 获取今日股池 */
export async function fetchTodayPool(): Promise<StrategyTrackRecord[]> {
  return request.get('/stock-pick/track-pool/today')
}

/** 获取明日股池 */
export async function fetchTomorrowPool(): Promise<StrategyTrackRecord[]> {
  return request.get('/stock-pick/track-pool/tomorrow')
}

/** 创建追踪记录 */
export async function createTrackRecord(data: {
  strategy_id: number
  stock_code: string
  stock_name?: string
  target_date: string
  pool_type?: string
  anomaly_type: string
  confidence?: number
  anomaly_data?: Record<string, any>
  confidence_reason?: string
}): Promise<{ id: number }> {
  return request.post('/stock-pick/track-pool', data)
}

/** 批量创建追踪记录 */
export async function batchCreateTrackRecords(records: {
  strategy_id: number
  stock_code: string
  stock_name?: string
  target_date: string
  pool_type?: string
  anomaly_type: string
  confidence?: number
  anomaly_data?: Record<string, any>
  confidence_reason?: string
}[]): Promise<{ created: number }> {
  return request.post('/stock-pick/track-pool/batch', records)
}

/** 更新追踪记录 */
export async function updateTrackRecord(id: number, data: {
  status?: string
  entry_price?: number
  exit_price?: number
  max_return?: number
  actual_return?: number
  verify_note?: string
}): Promise<void> {
  return request.put(`/stock-pick/track-pool/${id}`, data)
}

/** 删除追踪记录 */
export async function deleteTrackRecord(id: number): Promise<void> {
  return request.delete(`/stock-pick/track-pool/${id}`)
}

// ==================== 执行日志接口 ====================

/** 获取执行日志 */
export async function fetchExecutionLogs(params?: {
  strategy_id?: number
  limit?: number
}): Promise<ExecutionLog[]> {
  return request.get('/stock-pick/execution-logs', { params })
}