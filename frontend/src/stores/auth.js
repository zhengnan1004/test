import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, registerApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userInfo = computed(() => user.value)

  // 方法
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      // 使用真实API
      const response = await loginApi(credentials)
      const { access_token: authToken, username, user_id, role } = response.data
      
      // 保存token和用户信息（包含用户ID和角色）
      token.value = authToken
      user.value = { 
        id: user_id || 1, // 如果后端没有返回user_id，使用默认值1
        username,
        role: role || 'user'
      }
      localStorage.setItem('token', authToken)
      localStorage.setItem('user', JSON.stringify({ 
        id: user_id || 1, 
        username,
        role: role || 'user'
      }))
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || err.response?.data?.message || '登录失败，请重试'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      // 使用真实API
      const response = await registerApi(userData)
      
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || err.response?.data?.message || '注册失败，请重试'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const clearError = () => {
    error.value = null
  }

  // 检查token是否过期
  const isTokenExpired = () => {
    if (!token.value) return true
    
    try {
      const tokenPayload = JSON.parse(atob(token.value.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      return tokenPayload.exp < currentTime
    } catch (error) {
      return true
    }
  }

  // 检查并清理过期的token
  const checkAndCleanExpiredToken = () => {
    if (isTokenExpired()) {
      logout()
      return true
    }
    return false
  }

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      // 检查token是否过期
      try {
        const tokenPayload = JSON.parse(atob(savedToken.split('.')[1]))
        const currentTime = Math.floor(Date.now() / 1000)
        
        if (tokenPayload.exp < currentTime) {
          // token已过期，清除本地存储
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          return
        }
        
        // token有效，设置状态
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch (error) {
        // token格式错误，清除本地存储
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }

  return {
    // 状态
    user,
    token,
    loading,
    error,
    
    // 计算属性
    isAuthenticated,
    userInfo,
    
    // 方法
    login,
    register,
    logout,
    clearError,
    isTokenExpired,
    checkAndCleanExpiredToken,
    initializeAuth
  }
}) 