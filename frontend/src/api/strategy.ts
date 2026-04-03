/**
 * 策略API封装
 */
import request from '@/utils/request'
import type {
  Strategy,
  StrategyListItem,
  StrategyStats,
  CreateStrategyRequest,
  UpdateStrategyRequest,
  StrategyQueryParams,
  PaginatedResponse
} from '@/types/strategy'

/**
 * 获取策略列表
 */
export function getStrategies(params?: StrategyQueryParams): Promise<PaginatedResponse<StrategyListItem>> {
  return request.get('/v1/strategies', { params })
}

/**
 * 获取策略详情
 */
export function getStrategy(id: number): Promise<Strategy> {
  return request.get(`/v1/strategies/${id}`)
}

/**
 * 创建策略
 */
export function createStrategy(data: CreateStrategyRequest): Promise<{ id: number; name: string }> {
  return request.post('/v1/strategies', data)
}

/**
 * 更新策略
 */
export function updateStrategy(id: number, data: UpdateStrategyRequest): Promise<{ id: number }> {
  return request.put(`/v1/strategies/${id}`, data)
}

/**
 * 删除策略
 */
export function deleteStrategy(id: number): Promise<void> {
  return request.delete(`/v1/strategies/${id}`)
}

/**
 * 更新策略状态
 */
export function updateStrategyStatus(id: number, status: string): Promise<{ id: number; status: string }> {
  return request.put(`/v1/strategies/${id}/status`, { status })
}

/**
 * 获取策略统计
 */
export function getStrategyStats(): Promise<StrategyStats> {
  return request.get('/v1/strategies/stats')
}