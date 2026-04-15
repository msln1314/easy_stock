/**
 * ETF池API封装
 */
import request from '@/utils/request'
import type { EtfPool, EtfPoolCreate, EtfPoolUpdate, EtfPoolQueryParams } from '@/types/etfRotation'

/**
 * 获取ETF池列表
 */
export function getEtfPoolList(params?: EtfPoolQueryParams): Promise<EtfPool[]> {
  return request.get('/etf-pool', { params })
}

/**
 * 获取ETF详情
 */
export function getEtfDetail(id: number): Promise<EtfPool> {
  return request.get(`/etf-pool/${id}`)
}

/**
 * 添加ETF到池中
 */
export function addEtf(data: EtfPoolCreate): Promise<EtfPool> {
  return request.post('/etf-pool', data)
}

/**
 * 更新ETF配置
 */
export function updateEtf(id: number, data: EtfPoolUpdate): Promise<EtfPool> {
  return request.put(`/etf-pool/${id}`, data)
}

/**
 * 删除ETF
 */
export function deleteEtf(id: number): Promise<void> {
  return request.delete(`/etf-pool/${id}`)
}

/**
 * 切换ETF启用状态
 */
export function toggleEtfStatus(id: number): Promise<{ id: number; is_active: boolean }> {
  return request.put(`/etf-pool/${id}/toggle`)
}