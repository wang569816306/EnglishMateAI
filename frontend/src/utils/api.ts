import axios from 'axios'
import { message } from 'ant-design-vue'

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/ai',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 如果返回的code不是200，说明有错误
    if (res.code !== 200) {
      console.error('API Error:', res.msg)
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    
    // ✅ 返回 data 字段，而不是整个响应对象
    return res.data
  },
  (error) => {
    console.error('Request Error:', error.message)
    
    // 处理401未授权
    if (error.response && error.response.status === 401) {
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      
      if (isLoginRequest) {
        // 登录接口 401 = 密码错误，直接抛出，由调用方处理
        return Promise.reject(Object.assign(error, { isLoginError: true }))
      }
      
      // 其他接口 401 = Token过期或无效，清除登录状态
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      
      // 使用antd提示
      message.error('登录过期，请重新登录')
      
      // 触发重新登录事件
      window.dispatchEvent(new CustomEvent('auth-expired'))
      
      return Promise.reject(new Error('登录过期，请重新登录'))
    }
    
    // 其他错误提示
    const errorMsg = error.response?.data?.msg || error.message || '请求失败'
    message.error(errorMsg)
    
    return Promise.reject(error)
  }
)

export default apiClient
