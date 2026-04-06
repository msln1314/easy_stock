/**
 * AI交易助手API
 */
import axios from 'axios'

const TOKEN_KEY = 'stock_policy_token'

// ==================== 类型定义 ====================

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  function_called?: string
  function_result?: string
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  role: string
  content: string
  function_called?: string
  function_result?: string
}

// ==================== API接口 ====================

/**
 * 发送消息给AI助手
 */
export async function sendAIMessage(message: string): Promise<ChatResponse> {
  const token = localStorage.getItem(TOKEN_KEY)
  const response = await axios.post('/api/v1/ai/chat', { message }, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    timeout: 60000 // AI响应可能较慢，设置60秒超时
  })

  const { code, data, message: msg } = response.data
  if (code === 200) {
    return data
  }
  throw new Error(msg || '请求失败')
}

/**
 * 获取聊天历史
 */
export async function getChatHistory(limit: number = 50): Promise<{
  messages: ChatMessage[]
  total: number
}> {
  const token = localStorage.getItem(TOKEN_KEY)
  const response = await axios.get('/api/v1/ai/history', {
    params: { limit },
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })

  const { code, data } = response.data
  if (code === 200) {
    return data
  }
  return { messages: [], total: 0 }
}