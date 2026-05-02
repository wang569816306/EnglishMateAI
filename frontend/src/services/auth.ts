import apiClient from '../utils/api'

export interface RegisterData {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface LoginData {
  username: string
  password: string
}

export interface AuthResponse {
  user: {
    id: number
    username: string
    email: string
    full_name?: string
    avatar_url?: string
  }
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name?: string
  avatar_url?: string
}

/**
 * 用户注册
 */
export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await apiClient.post('/auth/register', {
    username: data.username,
    email: data.email,
    password: data.password,
    full_name: data.full_name || data.username // 如果没有提供full_name，使用username
  })
  return response.data
}

/**
 * 用户登录
 */
export const login = async (data: LoginData): Promise<AuthResponse> => {
  const response = await apiClient.post('/auth/login', {
    username: data.username,
    password: data.password
  })
  return response.data
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async (): Promise<UserInfo> => {
  const response = await apiClient.get('/auth/me')
  return response.data
}

/**
 * 刷新Token
 */
export const refreshToken = async (refreshToken: string): Promise<{access_token: string, token_type: string, expires_in: number}> => {
  const response = await apiClient.post('/auth/refresh', {
    refresh_token: refreshToken
  })
  return response.data
}

/**
 * 修改密码
 */
export const changePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
  await apiClient.post('/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword
  })
}

/**
 * 登出
 */
export const logout = async (): Promise<void> => {
  try {
    await apiClient.post('/auth/logout')
  } finally {
    // 无论成功与否，都清除本地存储
    clearAuth()
  }
}

/**
 * 保存认证信息到localStorage
 */
export const saveAuth = (authData: AuthResponse) => {
  localStorage.setItem('access_token', authData.access_token)
  localStorage.setItem('refresh_token', authData.refresh_token)
  localStorage.setItem('user_info', JSON.stringify(authData.user))
}

/**
 * 清除认证信息
 */
export const clearAuth = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_info')
}

/**
 * 获取当前用户信息（从localStorage）
 */
export const getCachedUserInfo = (): UserInfo | null => {
  const userInfo = localStorage.getItem('user_info')
  return userInfo ? JSON.parse(userInfo) : null
}

/**
 * 检查是否已登录
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token')
}
