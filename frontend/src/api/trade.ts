/**
 * 交易管理相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface Position {
  stock_code: string
  stock_name: string
  quantity: number
  available: number
  cost_price: number
  current_price: number
  profit: number
  profit_rate: number
  market_value: number
  updated_time: string
}

export interface Balance {
  total_asset: number
  available_cash: number
  market_value: number
  frozen_cash: number
  profit_today: number
  profit_total: number
  updated_time: string
}

export interface Trade {
  order_id: string
  stock_code: string
  stock_name: string
  direction: 'buy' | 'sell'
  price: number
  quantity: number
  amount: number
  status: string
  traded_time: string
}

export interface Entrust {
  order_id: string
  stock_code: string
  stock_name: string
  direction: 'buy' | 'sell'
  price: number
  quantity: number
  traded_quantity: number
  status: string
  entrust_time: string
}

export interface TradeStatus {
  is_trade_day: boolean
  is_trade_time: boolean
  trade_session: string
  current_time: string
  current_date: string
  weekday: string
  next_trade_time: string | null
}

export interface TradeRequest {
  stock_code: string
  price: number
  quantity: number
  order_type?: 'limit' | 'market'
}

// ==================== 行情接口 ====================

/** 获取股票行情 */
export async function fetchStockQuote(stockCode: string): Promise<Record<string, any>> {
  return request.get(`/position/quote/${stockCode}`)
}

// ==================== 持仓和资金接口 ====================

/** 获取持仓列表 */
export async function fetchPositions(): Promise<{
  positions: Position[]
  total_market_value: number
  total_profit: number
  count: number
}> {
  return request.get('/position/list')
}

/** 获取资金余额 */
export async function fetchBalance(): Promise<Balance> {
  return request.get('/position/balance')
}

/** 获取今日成交 */
export async function fetchTodayTrades(): Promise<{
  trades: Trade[]
  total: number
}> {
  return request.get('/position/trades/today')
}

/** 获取今日委托 */
export async function fetchTodayEntrusts(): Promise<{
  entrusts: Entrust[]
  total: number
}> {
  return request.get('/position/entrusts/today')
}

// ==================== 交易接口 ====================

/** 买入股票 */
export async function buyStock(data: TradeRequest): Promise<{
  success: boolean
  order_id: string
  message: string
}> {
  return request.post('/position/buy', data)
}

/** 卖出股票 */
export async function sellStock(data: TradeRequest): Promise<{
  success: boolean
  order_id: string
  message: string
}> {
  return request.post('/position/sell', data)
}

/** 撤单 */
export async function cancelOrder(orderId: string): Promise<{
  success: boolean
  message: string
}> {
  return request.post('/position/cancel', { order_id: orderId })
}

/** 获取交易状态 */
export async function fetchTradeStatus(): Promise<TradeStatus> {
  return request.get('/position/trade-status')
}

/** 快捷买入 */
export async function quickBuy(data: TradeRequest): Promise<{
  success: boolean
  order_id: string
  limit_up_price: number
  message: string
}> {
  return request.post('/position/quick-buy', data)
}

/** 快捷卖出 */
export async function quickSell(data: TradeRequest): Promise<{
  success: boolean
  order_id: string
  limit_down_price: number
  message: string
}> {
  return request.post('/position/quick-sell', data)
}