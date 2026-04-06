import request from '@/utils/request'

// 分析类型
export type AnalysisType = 'fundamental' | 'technical' | 'comprehensive' | 'industry' | 'sentiment' | 'risk'

// 分析状态
export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed'

// 分析报告接口
export interface AnalysisReport {
  id: number
  stock_code: string
  stock_name: string
  analysis_type: AnalysisType
  analysis_type_display: string
  status: AnalysisStatus
  status_display: string
  request_prompt: string
  summary?: string
  fundamental_analysis?: string
  technical_analysis?: string
  risk_analysis?: string
  recommendation?: string
  full_report?: string
  rating?: number
  tags?: string[]
  model_name?: string
  tokens_used?: number
  duration_ms?: number
  created_at: string
  completed_at?: string
  error_message?: string
}

// 分析历史列表项
export interface AnalysisHistoryItem {
  id: number
  stock_code: string
  stock_name: string
  analysis_type: AnalysisType
  analysis_type_display: string
  status: AnalysisStatus
  status_display: string
  request_prompt: string
  summary?: string
  rating?: number
  created_at: string
  completed_at?: string
}

// 创建分析请求
export interface CreateAnalysisRequest {
  stock_code: string
  stock_name: string
  request_prompt: string
  analysis_type?: AnalysisType
  stock_data?: Record<string, unknown>
}

// 对话记录
export interface AnalysisConversation {
  id: number
  role: 'user' | 'assistant'
  content: string
  tokens_used?: number
  created_at: string
}

// 分析统计
export interface AnalysisStatistics {
  total_count: number
  avg_duration_ms: number
  avg_tokens: number
  analysis_types: Record<AnalysisType, number>
  stocks_analyzed: number
}

/**
 * 创建AI分析报告
 */
export function createAnalysis(data: CreateAnalysisRequest) {
  return request.post<{
    id: number
    status: AnalysisStatus
    status_display: string
    message: string
  }>('/api/v1/stock-analysis/create', data)
}

/**
 * 获取分析报告详情
 */
export function getAnalysisReport(reportId: number) {
  return request.get<AnalysisReport>(`/api/v1/stock-analysis/report/${reportId}`)
}

/**
 * 获取分析历史列表
 */
export function getAnalysisHistory(params?: {
  stock_code?: string
  status?: AnalysisStatus
  page?: number
  page_size?: number
}) {
  return request.get<{
    items: AnalysisHistoryItem[]
    total: number
    page: number
    page_size: number
  }>('/api/v1/stock-analysis/history', { params })
}

/**
 * 删除分析报告
 */
export function deleteAnalysisReport(reportId: number) {
  return request.delete<{ message: string }>(`/api/v1/stock-analysis/report/${reportId}`)
}

/**
 * 获取分析统计
 */
export function getAnalysisStatistics() {
  return request.get<AnalysisStatistics>('/api/v1/stock-analysis/statistics')
}

/**
 * 获取报告对话历史
 */
export function getReportConversations(reportId: number) {
  return request.get<{
    items: AnalysisConversation[]
    total: number
  }>(`/api/v1/stock-analysis/conversations/${reportId}`)
}