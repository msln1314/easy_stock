import request from '@/utils/request'

export interface StockQuote {
  stock_code: string
  stock_name: string
  current_price: number
  change_percent: number
  change_amount: number
  volume: number
  high: number
  low: number
  update_time: string
}

export interface StrategyExecution {
  id: number
  strategy_name: string
  stock_code: string
  signal_type: string
  execution_status: string
  position_size: number
  executed_at: string
}

export interface Position {
  stock_code: string
  stock_name: string
  position_size: number
  cost_price: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_percent: number
}

export interface PerformanceMetrics {
  total_return: number
  win_rate: number
  max_drawdown: number
  sharpe_ratio: number
  total_trades: number
  profit_trades: number
  loss_trades: number
}

export interface PerformanceChartData {
  dates: string[]
  values: number[]
}

export interface SystemStatus {
  api_status: string
  data_sync_status: string
  uptime: number
  cpu_usage: number
  memory_usage: number
  last_update: string
}

export interface Alert {
  id: number
  alert_type: string
  alert_level: string
  title: string
  content: string
  is_resolved: boolean
  created_at: string
}

export interface IndexQuote {
  code: string
  name: string
  price: number
  change: number
  change_amount: number
  pre_close: number
  open: number
  high: number
  low: number
  volume: number
  amount: number
  updated_time: string
}

export interface DashboardData {
  quotes: StockQuote[]
  strategies: StrategyExecution[]
  positions: Position[]
  performance: PerformanceMetrics
  performanceChart: PerformanceChartData
  systemStatus: SystemStatus
  alerts: Alert[]
}

// 获取所有大屏数据（聚合接口）
export async function fetchDashboardData(): Promise<DashboardData> {
  const [quotes, strategies, positions, performance, performanceChart, systemStatus, alerts] = await Promise.all([
    fetchQuotes(),
    fetchStrategies(),
    fetchPositions(),
    fetchPerformance(),
    fetchPerformanceChart(30),
    fetchSystemStatus(),
    fetchAlerts()
  ])

  return {
    quotes,
    strategies,
    positions,
    performance,
    performanceChart,
    systemStatus,
    alerts
  }
}

// 获取股票行情
export async function fetchQuotes(limit = 20): Promise<StockQuote[]> {
  return request.get('/dashboard/quotes', { params: { limit } })
}

// 获取策略执行
export async function fetchStrategies(): Promise<StrategyExecution[]> {
  return request.get('/dashboard/strategies')
}

// 获取持仓列表（从qmt-service）
export async function fetchPositions(): Promise<Position[]> {
  const data = await request.get('/v1/position/list')
  // 转换字段名称以适配前端展示
  return data.positions?.map((p: any) => ({
    stock_code: p.stock_code,
    stock_name: p.stock_name,
    position_size: p.quantity,
    cost_price: p.cost_price,
    current_price: p.current_price,
    market_value: p.market_value,
    profit_loss: p.profit,
    profit_percent: p.profit_rate
  })) || []
}

// 获取资金余额
export async function fetchBalance(): Promise<{
  total_asset: number
  available_cash: number
  market_value: number
  frozen_cash: number
  profit_today: number
  profit_total: number
}> {
  return request.get('/v1/position/balance')
}

// 获取业绩指标
export async function fetchPerformance(): Promise<PerformanceMetrics> {
  return request.get('/dashboard/performance')
}

// 获取收益曲线
export async function fetchPerformanceChart(days = 30): Promise<PerformanceChartData> {
  return request.get('/dashboard/performance/chart', { params: { days } })
}

// 获取系统状态
export async function fetchSystemStatus(): Promise<SystemStatus> {
  return request.get('/dashboard/system/status')
}

// 获取告警列表
export async function fetchAlerts(level?: string): Promise<Alert[]> {
  return request.get('/dashboard/alerts', { params: { level } })
}

// 解决告警
export async function resolveAlert(id: number): Promise<void> {
  return request.put(`/dashboard/alerts/${id}/resolve`)
}

// 获取主要指数行情（从qmt-service）
export async function fetchIndexQuotes(): Promise<IndexQuote[]> {
  const data = await request.get('/v1/position/indexes')
  return data.indexes || []
}