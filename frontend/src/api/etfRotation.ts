/**
 * ETF轮动策略API封装
 */
import request from '@/utils/request'
import type {
  RotationStrategy,
  RotationStrategyListItem,
  RotationStrategyCreate,
  RotationStrategyUpdate,
  RotationStrategyStats,
  RotationStrategyQueryParams,
  ScoreResponse,
  RotationSignal,
  SignalGenerateResponse,
  SignalQueryParams,
  BacktestRequest,
  BacktestResult
} from '@/types/etfRotation'

/**
 * 获取轮动策略列表
 */
export function getRotationStrategies(params?: RotationStrategyQueryParams): Promise<RotationStrategyListItem[]> {
  return request.get('/rotation-strategies', { params })
}

/**
 * 获取策略统计
 */
export function getRotationStrategyStats(): Promise<RotationStrategyStats> {
  return request.get('/rotation-strategies/stats')
}

/**
 * 获取策略详情
 */
export function getRotationStrategy(id: number): Promise<RotationStrategy> {
  return request.get(`/rotation-strategies/${id}`)
}

/**
 * 创建轮动策略
 */
export function createRotationStrategy(data: RotationStrategyCreate): Promise<{ id: number; name: string }> {
  return request.post('/rotation-strategies', data)
}

/**
 * 更新策略
 */
export function updateRotationStrategy(id: number, data: RotationStrategyUpdate): Promise<{ id: number }> {
  return request.put(`/rotation-strategies/${id}`, data)
}

/**
 * 更新策略状态
 */
export function updateRotationStrategyStatus(id: number, status: string): Promise<{ id: number; status: string }> {
  return request.put(`/rotation-strategies/${id}/status`, { status })
}

/**
 * 获取最新ETF评分排名
 */
export function getLatestScores(id: number): Promise<ScoreResponse> {
  return request.get(`/rotation-strategies/${id}/scores/latest`)
}

/**
 * 获取信号记录
 */
export function getSignals(id: number, params?: SignalQueryParams): Promise<RotationSignal[]> {
  return request.get(`/rotation-strategies/${id}/signals`, { params })
}

/**
 * 手动生成信号
 */
export function generateSignals(id: number): Promise<SignalGenerateResponse> {
  return request.post(`/rotation-strategies/${id}/signals/generate`)
}

/**
 * 运行回测
 */
export function runBacktest(id: number, data: BacktestRequest): Promise<{ backtest_id: number; status: string }> {
  return request.post(`/rotation-strategies/${id}/backtest`, data)
}

/**
 * 获取回测结果
 */
export function getBacktestResult(id: number, backtestId: number): Promise<BacktestResult> {
  return request.get(`/rotation-strategies/${id}/backtest/${backtestId}`)
}