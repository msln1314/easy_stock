/**
 * 选股策略相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

/** 指标库项 */
export interface IndicatorItem {
  id: number
  indicator_key: string
  indicator_name: string
  category: string
  description?: string
  params?: IndicatorParam[]
  output_fields?: IndicatorOutputField[]
  default_output?: string
  usage_guide?: string
  signal_interpretation?: Record<string, string>
}

/** 指标参数定义 */
export interface IndicatorParam {
  key: string
  name: string
  type: string
  default?: any
  min?: number
  max?: number
  required?: boolean
  desc?: string
  options?: string[]
}

/** 指标输出字段 */
export interface IndicatorOutputField {
  key: string
  name: string
  type: string
  desc?: string
}

/** 策略条件 */
export interface StrategyCondition {
  id: string
  type: 'indicator' | 'quote' | 'threshold'
  indicator_key?: string
  params?: Record<string, any>
  output_field?: string
  operator: string
  value?: any
  value_type?: 'number' | 'indicator' | 'quote_field'
  value_indicator_key?: string
  value_output_field?: string
  value_field?: string
  field?: string  // quote类型条件使用的字段
}

/** 策略配置 */
export interface StrategyConfig {
  indicators: Array<{
    indicator_key: string
    params?: Record<string, any>
    output_field?: string
  }>
  conditions: StrategyCondition[]
  logic?: 'AND' | 'OR'
}

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
  stocks_found: number
  stocks: any[]
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

// ==================== 指标库接口 ====================

/** 获取指标库列表 */
export async function fetchIndicators(params?: {
  category?: string
  search?: string
}): Promise<IndicatorItem[]> {
  return request.get('/stock-pick/indicators', { params })
}

/** 获取指标详情 */
export async function fetchIndicatorDetail(indicatorKey: string): Promise<IndicatorItem> {
  return request.get(`/stock-pick/indicators/${indicatorKey}`)
}

// ==================== 选股接口 ====================

/** 快速选股 */
export async function quickScreening(data: {
  strategy_config: StrategyConfig
  stock_pool?: string[]
}): Promise<{
  total: number
  stocks: Array<{
    stock_code: string
    stock_name: string
    passed: boolean
    confidence: number
    matched_conditions: any[]
    indicator_values: Record<string, any>
    current_price: number
    change_percent: number
  }>
}> {
  return request.post('/stock-pick/screening', data)
}