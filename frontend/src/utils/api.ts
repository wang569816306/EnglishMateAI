import axios from 'axios'

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
    
    return res
  },
  (error) => {
    console.error('Request Error:', error.message)
    
    // 处理401未授权
    if (error.response && error.response.status === 401) {
      // Token过期或无效，清除登录状态
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      
      // 触发重新登录
      window.dispatchEvent(new CustomEvent('auth-expired'))
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
