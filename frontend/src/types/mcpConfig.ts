/**
 * MCP配置类型定义
 */
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