/**
 * 交易红线API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface RedLine {
  id: number
  rule_key: string
  rule_name: string
  rule_type: string
  description: string
  rule_config: Record<string, any>
  severity: 'critical' | 'warning' | 'info'
  is_enabled: boolean
  effective_from: string | null
  effective_to: string | null
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: number
  rule_key: string
  rule_name: string
  stock_code: string
  stock_name: string
  action_type: string
  original_value: any
  audit_result: string
  audit_message: string
  created_at: string
}

export interface RedLineSwitch {
  enabled: boolean
}

// ==================== 红线开关接口 ====================

/** 获取红线开关状态 */
export async function getRedLineSwitch(): Promise<RedLineSwitch> {
  return request.get('/v1/red-line/switch')
}

/** 设置红线开关状态 */
export async function setRedLineSwitch(enabled: boolean): Promise<RedLineSwitch> {
  return request.put('/v1/red-line/switch', { enabled })
}

// ==================== 红线规则接口 ====================

/** 获取红线规则列表 */
export async function getRedLines(): Promise<{
  rules: RedLine[]
  total: number
}> {
  return request.get('/v1/red-line/rules')
}

/** 获取单个红线规则 */
export async function getRedLine(ruleKey: string): Promise<RedLine> {
  return request.get(`/v1/red-line/rules/${ruleKey}`)
}

/** 创建红线规则 */
export async function createRedLine(data: Partial<RedLine>): Promise<RedLine> {
  return request.post('/v1/red-line/rules', data)
}

/** 更新红线规则 */
export async function updateRedLine(ruleKey: string, data: Partial<RedLine>): Promise<RedLine> {
  return request.put(`/v1/red-line/rules/${ruleKey}`, data)
}

/** 删除红线规则 */
export async function deleteRedLine(ruleKey: string): Promise<{ success: boolean }> {
  return request.delete(`/v1/red-line/rules/${ruleKey}`)
}

/** 批量更新红线状态 */
export async function batchUpdateRedLineStatus(ruleKeys: string[], is_enabled: boolean): Promise<{ updated: number }> {
  return request.put('/v1/red-line/rules/batch/status', { rule_keys: ruleKeys, is_enabled })
}

/** 初始化预置红线 */
export async function initPresetRedLines(): Promise<{ synced: number; total: number }> {
  return request.post('/v1/red-line/rules/init')
}

/** 获取审计日志 */
export async function getAuditLogs(params?: {
  rule_key?: string
  stock_code?: string
  audit_result?: string
  start_date?: string
  end_date?: string
  limit?: number
  offset?: number
}): Promise<{
  logs: AuditLog[]
  total: number
}> {
  return request.get('/v1/red-line/audit-logs', { params })
}

// ==================== 测试接口 ====================

export interface AuditTestRequest {
  stock_code: string
  price: number
  quantity: number
}

export interface AuditTestResult {
  passed: boolean
  audit_result: string
  failed_rules: Array<{
    rule_key: string
    rule_name: string
    reason: string
    value?: number
    limit?: number
  }>
  warning_rules: Array<{
    rule_key: string
    rule_name: string
    reason: string
  }>
  reject_reason?: string
  audit_details: Record<string, any>
  stock_code: string
  stock_name: string
  price: number
  quantity: number
  amount: number
}

/** 测试红线校验 */
export async function testRedLineAudit(data: AuditTestRequest): Promise<AuditTestResult> {
  return request.post('/v1/position/audit', data)
}