/**
 * ETF轮动策略相关类型定义
 */

// ========== ETF池相关 ==========

export interface EtfPool {
  id: number
  name: string
  code: string
  sector: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EtfPoolCreate {
  name: string
  code: string
  sector: string
  is_active?: boolean
}

export interface EtfPoolUpdate {
  name?: string
  sector?: string
  is_active?: boolean
}

// ========== 轮动策略相关 ==========

export interface RotationStrategy {
  id: number
  name: string
  description?: string
  slope_period: number
  rsrs_period: number
  rsrs_z_window: number
  rsrs_buy_threshold: number
  rsrs_sell_threshold: number
  ma_period: number
  hold_count: number
  rebalance_freq: string
  execute_mode: string
  status: string
  created_at: string
  updated_at: string
}

export interface RotationStrategyListItem {
  id: number
  name: string
  description?: string
  slope_period: number
  rsrs_period: number
  hold_count: number
  rebalance_freq: string
  execute_mode: string
  execute_mode_display: string
  status: string
  status_display: string
  created_at: string
  updated_at: string
}

export interface RotationStrategyCreate {
  name: string
  description?: string
  slope_period?: number
  rsrs_period?: number
  rsrs_z_window?: number
  rsrs_buy_threshold?: number
  rsrs_sell_threshold?: number
  ma_period?: number
  hold_count?: number
  rebalance_freq?: string
  execute_mode?: string
}

export interface RotationStrategyUpdate {
  name?: string
  description?: string
  slope_period?: number
  rsrs_period?: number
  status?: string
}

export interface RotationStrategyStats {
  total: number
  by_status: {
    running: number
    paused: number
    stopped: number
  }
  by_execute_mode: {
    simulate: number
    alert: number
  }
}

// ========== ETF评分相关 ==========

export interface EtfScore {
  etf_code: string
  etf_name: string
  sector: string
  momentum_score: number | null
  slope_value: number | null
  r_squared: number | null
  rsrs_z_score: number | null
  close_price: number | null
  ma_value: number | null
  rank: number | null
}

export interface ScoreResponse {
  trade_date: string
  strategy_name: string
  scores: EtfScore[]
}

// ========== 轮动信号相关 ==========

export interface RotationSignal {
  id: number
  signal_date: string
  signal_type: string
  signal_type_display: string
  etf_code: string
  etf_name: string
  action: string
  action_display: string
  score: number | null
  rsrs_z: number | null
  price: number | null
  reason: string | null
  is_executed: boolean
  created_at: string
}

export interface SignalGenerateResponse {
  generated_count: number
  signals: RotationSignal[]
}

// ========== 回测相关 ==========

export interface BacktestRequest {
  start_date: string
  end_date: string
  initial_capital?: number
}

export interface BacktestResult {
  id: number
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number | null
  total_return: number | null
  annual_return: number | null
  max_drawdown: number | null
  win_rate: number | null
  trade_count: number | null
  sharpe_ratio: number | null
  calmar_ratio: number | null
  benchmark_return: number | null
  excess_return: number | null
  created_at: string
}

// ========== 查询参数 ==========

export interface EtfPoolQueryParams {
  sector?: string
  is_active?: boolean
  keyword?: string
}

export interface RotationStrategyQueryParams {
  status?: string
  execute_mode?: string
  keyword?: string
}

export interface SignalQueryParams {
  signal_type?: string
  limit?: number
}