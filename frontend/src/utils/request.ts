/**
 * Axios请求封装
 */
import axios, { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'

const TOKEN_KEY = 'stock_policy_token'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message, data } = response.data

    if (code === 200) {
      return data
    } else {
      // 业务错误 - 在控制台输出，不使用useMessage
      console.error('请求失败:', message || '未知错误')
      return Promise.reject(new Error(message || '请求失败'))
    }
  },
  (error: AxiosError) => {
    // 网络错误或服务器错误
    console.error('网络错误:', error.message)

    // 401 未授权，跳转登录页
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      // 延迟跳转
      setTimeout(() => {
        window.location.href = '/login'
      }, 1000)
    }

    return Promise.reject(error)
  }
)

export default request