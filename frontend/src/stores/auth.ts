/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginParams, RegisterParams, UserUpdateParams, PasswordUpdateParams } from '@/types/user'
import * as authApi from '@/api/auth'
import router from '@/router'

const TOKEN_KEY = 'stock_policy_token'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<User | null>(null)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 设置Token
  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  // 登录
  async function login(params: LoginParams) {
    const res = await authApi.login(params)
    setToken(res.access_token)
    user.value = res.user
    return res
  }

  // 登出
  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      // 忽略登出错误
    }
    setToken(null)
    user.value = null
    router.push('/login')
  }

  // 获取用户信息
  async function fetchProfile() {
    if (!token.value) return null
    try {
      const res = await authApi.getProfile()
      user.value = res
      return res
    } catch (e) {
      setToken(null)
      return null
    }
  }

  // 更新用户信息
  async function updateProfile(params: UserUpdateParams) {
    const res = await authApi.updateProfile(params)
    user.value = res
    return res
  }

  // 修改密码
  async function updatePassword(params: PasswordUpdateParams) {
    await authApi.updatePassword(params)
  }

  // 注册用户（管理员）
  async function register(params: RegisterParams) {
    return await authApi.register(params)
  }

  // 刷新Token
  async function refreshToken() {
    const res = await authApi.refreshToken()
    setToken(res.access_token)
    return res
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    setToken,
    login,
    logout,
    fetchProfile,
    updateProfile,
    updatePassword,
    register,
    refreshToken
  }
})