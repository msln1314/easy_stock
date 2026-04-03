/**
 * 策略相关类型定义
 */

// 指标类型
export interface Indicator {
  id?: number
  indicator_type: string  // MA, MACD, RSI, KDJ, BOLL
  parameters: Record<string, any>
}

// 信号类型
export interface Signal {
  id?: number
  signal_type: 'buy' | 'sell'
  condition_type: string  // indicator_cross, threshold, custom
  condition_config: Record<string, any>
  priority?: number
}

// 风控配置
export interface RiskConfig {
  id?: number
  stop_profit_type?: string  // fixed_percent, dynamic, trailing
  stop_profit_value?: number
  stop_loss_type?: string    // fixed_percent, dynamic
  stop_loss_value?: number
  max_position?: number
}

// 策略主类型
export interface Strategy {
  id: number
  name: string
  description?: string
  execute_mode: 'auto' | 'alert' | 'simulate'
  status: 'running' | 'paused' | 'stopped'
  indicators: Indicator[]
  signals: Signal[]
  risk?: RiskConfig
  created_at: string
  updated_at: string
}

// 策略列表项
export interface StrategyListItem {
  id: number
  name: string
  description?: string
  execute_mode: string
  status: string
  created_at: string
  updated_at: string
}

// 分页响应
export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

// 统计信息
export interface StrategyStats {
  total: number
  by_execute_mode: {
    auto: number
    alert: number
    simulate: number
  }
  by_status: {
    running: number
    paused: number
    stopped: number
  }
}

// 创建请求
export interface CreateStrategyRequest {
  name: string
  description?: string
  execute_mode: string
  status: string
  indicators: Indicator[]
  signals: Signal[]
  risk?: RiskConfig
}

// 更新请求
export interface UpdateStrategyRequest {
  name?: string
  description?: string
  execute_mode?: string
  status?: string
  indicators?: Indicator[]
  signals?: Signal[]
  risk?: RiskConfig
}

// 列表查询参数
export interface StrategyQueryParams {
  execute_mode?: string
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}

// 指标类型选项
export const INDICATOR_TYPES = [
  { label: '均线 (MA)', value: 'MA' },
  { label: 'MACD指标', value: 'MACD' },
  { label: '相对强弱指数 (RSI)', value: 'RSI' },
  { label: 'KDJ指标', value: 'KDJ' },
  { label: '布林带 (BOLL)', value: 'BOLL' }
]

// 执行模式选项
export const EXECUTE_MODE_OPTIONS = [
  { label: '自动交易', value: 'auto' },
  { label: '信号提醒', value: 'alert' },
  { label: '模拟运行', value: 'simulate' }
]

// 状态选项
export const STATUS_OPTIONS = [
  { label: '运行中', value: 'running' },
  { label: '已暂停', value: 'paused' },
  { label: '已停止', value: 'stopped' }
]

// 止盈类型选项
export const STOP_PROFIT_TYPE_OPTIONS = [
  { label: '固定百分比', value: 'fixed_percent' },
  { label: '动态止盈', value: 'dynamic' },
  { label: '移动止盈', value: 'trailing' }
]

// 止损类型选项
export const STOP_LOSS_TYPE_OPTIONS = [
  { label: '固定百分比', value: 'fixed_percent' },
  { label: '动态止损', value: 'dynamic' }
]