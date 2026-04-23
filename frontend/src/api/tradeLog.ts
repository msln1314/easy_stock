/**
 * 交易日志API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface TradeLog {
  id: number
  action_type: 'buy' | 'sell' | 'cancel' | 'query' | 'sync'
  stock_code: string
  stock_name: string
  strategy_key: string | null
  order_id: string | null
  price: number | null
  quantity: number | null
  amount: number | null
  result: 'success' | 'failed' | 'pending'
  message: string
  request_data: Record<string, any> | null
  response_data: Record<string, any> | null
  created_at: string
}

export interface TradeLogSummary {
  date: string
  total_trades: number
  buy_count: number
  sell_count: number
  success_count: number
  failed_count: number
  total_amount: number
}

export interface TradeStats {
  total_trades: number
  today_trades: number
  success_rate: number
  buy_count: number
  sell_count: number
  cancel_count: number
}

// ==================== 日志查询接口 ====================

/** 获取交易日志列表 */
export async function getTradeLogs(params?: {
  action_type?: string
  stock_code?: string
  strategy_key?: string
  result?: string
  order_id?: string
  start_date?: string
  end_date?: string
  limit?: number
  offset?: number
}): Promise<{
  logs: TradeLog[]
  total: number
}> {
  return request.get('/trade-log/list', { params })
}

/** 获取日志统计 */
export async function getTradeLogStats(params?: {
  start_date?: string
  end_date?: string
}): Promise<TradeStats> {
  return request.get('/trade-log/stats', { params })
}

/** 获取日志汇总 */
export async function getTradeLogSummary(params?: {
  start_date?: string
  end_date?: string
}): Promise<{
  summaries: TradeLogSummary[]
  total: number
}> {
  return request.get('/trade-log/summary', { params })
}

/** 导出交易日志 */
export async function exportTradeLogs(params?: {
  start_date?: string
  end_date?: string
  action_type?: string
}): Promise<Blob> {
  return request.get('/trade-log/export', { params, responseType: 'blob' })
}