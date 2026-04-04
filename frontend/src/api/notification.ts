/**
 * 通知配置相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface NotificationChannel {
  id: number
  channel_type: string
  channel_name: string
  is_enabled: boolean
  config: Record<string, any>
  warning_levels: string[]
  monitor_types: string[]
  rate_limit_minutes: number
  last_sent_at?: string
  remark?: string
  created_at?: string
}

export interface ChannelTypeOption {
  value: string
  label: string
  config_fields: string[]
}

export interface NotificationLog {
  id: number
  warning_id?: number
  stock_code: string
  stock_name?: string
  title: string
  content: string
  warning_level: string
  condition_name?: string
  channel_id: number
  channel_type: string
  channel_name: string
  status: 'pending' | 'sent' | 'failed'
  error_message?: string
  sent_at?: string
  created_at: string
}

export interface NotificationStats {
  channel_stats: { channel_type: string; count: number }[]
  status_stats: { status: string; count: number }[]
  level_stats: { warning_level: string; count: number }[]
  days: number
}

// ==================== 通知渠道接口 ====================

/** 获取通知渠道列表 */
export async function fetchNotificationChannels(params?: {
  channel_type?: string
  is_enabled?: boolean
}): Promise<NotificationChannel[]> {
  return request.get('/notification/channels', { params })
}

/** 获取可用的渠道类型列表 */
export async function fetchChannelTypes(): Promise<ChannelTypeOption[]> {
  return request.get('/notification/channels/types')
}

/** 创建通知渠道 */
export async function createNotificationChannel(data: {
  channel_type: string
  channel_name: string
  config: Record<string, any>
  warning_levels?: string[]
  monitor_types?: string[]
  rate_limit_minutes?: number
  remark?: string
}): Promise<{ id: number }> {
  return request.post('/notification/channels', data)
}

/** 更新通知渠道 */
export async function updateNotificationChannel(id: number, data: {
  channel_name?: string
  config?: Record<string, any>
  is_enabled?: boolean
  warning_levels?: string[]
  monitor_types?: string[]
  rate_limit_minutes?: number
  remark?: string
}): Promise<void> {
  return request.put(`/notification/channels/${id}`, data)
}

/** 删除通知渠道 */
export async function deleteNotificationChannel(id: number): Promise<void> {
  return request.delete(`/notification/channels/${id}`)
}

/** 测试通知渠道 */
export async function testNotificationChannel(id: number): Promise<void> {
  return request.post(`/notification/channels/${id}/test`)
}

// ==================== 通知记录接口 ====================

/** 获取通知记录列表 */
export async function fetchNotificationLogs(params?: {
  stock_code?: string
  warning_level?: string
  channel_type?: string
  status?: string
  limit?: number
}): Promise<NotificationLog[]> {
  return request.get('/notification/logs', { params })
}

/** 获取通知统计 */
export async function fetchNotificationStats(days?: number): Promise<NotificationStats> {
  return request.get('/notification/logs/stats', { params: { days } })
}

/** 清理旧通知记录 */
export async function clearNotificationLogs(days?: number): Promise<{ deleted_count: number }> {
  return request.delete('/notification/logs', { params: { days } })
}