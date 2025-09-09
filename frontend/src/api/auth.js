import axios from 'axios'
import router from '@/router'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 后端API地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
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
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 使用router进行跳转，避免页面刷新
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

// 登录API
export const loginApi = (credentials) => {
  return api.post('/auth/login', credentials)
}

// 注册API
export const registerApi = (userData) => {
  return api.post('/auth/register', userData)
}

// 获取用户信息API
export const getUserInfoApi = () => {
  return api.get('/auth/me')
}

// 刷新token API
export const refreshTokenApi = () => {
  return api.post('/auth/refresh')
}

// ============== 用户信息管理 ==============
// 获取用户详细信息
export const getUserDetailApi = (userId) => {
  return api.get(`/auth/users/${userId}`)
}

// 更新用户信息
export const updateUserApi = (userId, userData) => {
  return api.put(`/auth/users/${userId}`, userData)
}

// ============== 头像相关 ==============
// 上传头像（multipart/form-data）
export const uploadAvatarApi = (userId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/auth/users/${userId}/avatar`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取头像（返回图片二进制）
export const getAvatarApi = (userId) => {
  return api.get(`/auth/users/${userId}/avatar`, { responseType: 'blob' })
}

// ============== 用户管理API ==============
// 获取用户列表
export const getUserListApi = (params = {}) => {
  return api.get('/auth/users', { params })
}

// 创建新用户
export const createUserApi = (userData) => {
  return api.post('/auth/users', userData)
}

// 删除用户
export const deleteUserApi = (userId) => {
  return api.delete(`/auth/users/${userId}`)
}

// 切换用户状态
export const toggleUserStatusApi = (userId) => {
  return api.patch(`/auth/users/${userId}/toggle-status`)
}

// ============== 文档分类管理 ==============
// 修改文档分类
export const updateDocumentClassificationApi = (difyFileId, classification) => {
  return api.put(`/documents/${difyFileId}/classification`, { classification })
}

export default api 