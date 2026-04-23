/**
 * MCP配置API
 */
import request from '@/utils/request'
import type { McpConfig, McpConfigCreateParams } from '@/types/mcpConfig'

export interface McpConfig {
  id: number
  service_name: string
  service_url: string
  api_key: string | null
  enabled: boolean
  description: string | null
  created_at: string
  updated_at: string
}

export interface McpConfigCreateParams {
  service_name: string
  service_url: string
  api_key?: string
  enabled?: boolean
  description?: string
}

export interface McpConfigListResponse {
  total: number
  items: McpConfig[]
}

/**
 * 获取MCP配置列表
 */
export async function getMcpConfigs(params?: {
  enabled?: boolean
  keyword?: string
  page?: number
  page_size?: number
}): Promise<McpConfigListResponse> {
  const response = await request.get('/mcp', { params })
  return response.data
}

/**
 * 获取单个MCP配置
 */
export async function getMcpConfig(id: number): Promise<McpConfig> {
  const response = await request.get(`/mcp/${id}`)
  return response.data
}

/**
 * 创建MCP配置
 */
export async function createMcpConfig(data: McpConfigCreateParams): Promise<McpConfig> {
  const response = await request.post('/mcp', data)
  return response.data
}

/**
 * 更新MCP配置
 */
export async function updateMcpConfig(id: number, data: Partial<McpConfigCreateParams>): Promise<McpConfig> {
  const response = await request.put(`/mcp/${id}`, data)
  return response.data
}

/**
 * 删除MCP配置
 */
export async function deleteMcpConfig(id: number): Promise<void> {
  await request.delete(`/mcp/${id}`)
}

/**
 * 获取服务API Key
 */
export async function getServiceApiKey(serviceName: string): Promise<{ service_name: string; service_url: string; api_key: string }> {
  const response = await request.get(`/mcp/keys/${serviceName}`)
  return response.data
}