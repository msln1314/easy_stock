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
  return request.get('/api/dashboard/quotes', { params: { limit } })
}

// 获取策略执行
export async function fetchStrategies(): Promise<StrategyExecution[]> {
  return request.get('/api/dashboard/strategies')
}

// 获取持仓列表
export async function fetchPositions(): Promise<Position[]> {
  return request.get('/api/dashboard/positions')
}

// 获取业绩指标
export async function fetchPerformance(): Promise<PerformanceMetrics> {
  return request.get('/api/dashboard/performance')
}

// 获取收益曲线
export async function fetchPerformanceChart(days = 30): Promise<PerformanceChartData> {
  return request.get('/api/dashboard/performance/chart', { params: { days } })
}

// 获取系统状态
export async function fetchSystemStatus(): Promise<SystemStatus> {
  return request.get('/api/dashboard/system/status')
}

// 获取告警列表
export async function fetchAlerts(level?: string): Promise<Alert[]> {
  return request.get('/api/dashboard/alerts', { params: { level } })
}

// 解决告警
export async function resolveAlert(id: number): Promise<void> {
  return request.put(`/api/dashboard/alerts/${id}/resolve`)
}