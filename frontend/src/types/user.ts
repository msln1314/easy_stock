/**
 * 用户相关类型定义
 */
export interface User {
  id: number
  username: string
  email?: string
  nickname?: string
  role: 'admin' | 'user'
  status: 'active' | 'disabled'
  last_login?: string
  created_at: string
  updated_at: string
}

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  email?: string
  nickname?: string
  role?: 'admin' | 'user'
}

export interface UserUpdateParams {
  email?: string
  nickname?: string
  status?: 'active' | 'disabled'
}

export interface PasswordUpdateParams {
  old_password: string
  new_password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface AuthState {
  token: string | null
  user: User | null
  isLoggedIn: boolean
}