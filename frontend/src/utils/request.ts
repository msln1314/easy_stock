/**
 * Axios请求封装
 */
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { useMessage } from 'naive-ui'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message, data } = response.data

    if (code === 200) {
      return data
    } else {
      // 业务错误
      const msg = useMessage()
      msg.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    }
  },
  (error: AxiosError) => {
    // 网络错误或服务器错误
    const msg = useMessage()
    const errorMessage = error.response?.data?.message || error.message || '网络错误'
    msg.error(errorMessage)
    return Promise.reject(error)
  }
)

export default request