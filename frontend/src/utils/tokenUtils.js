import router from '@/router'

/**
 * 检查token是否过期
 * @param {string} token - JWT token
 * @returns {boolean} - 是否过期
 */
export const isTokenExpired = (token) => {
  if (!token) return true
  
  try {
    const tokenPayload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    return tokenPayload.exp < currentTime
  } catch (error) {
    return true
  }
}

/**
 * 检查并处理过期的token
 * @returns {boolean} - 是否已过期
 */
export const checkAndHandleExpiredToken = () => {
  const token = localStorage.getItem('token')
  
  if (isTokenExpired(token)) {
    // 清除过期的token
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // 如果不在登录页面，跳转到登录页
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login')
    }
    
    return true
  }
  
  return false
}

/**
 * 获取token剩余有效时间（秒）
 * @param {string} token - JWT token
 * @returns {number} - 剩余秒数，-1表示无效token
 */
export const getTokenRemainingTime = (token) => {
  if (!token) return -1
  
  try {
    const tokenPayload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    const remainingTime = tokenPayload.exp - currentTime
    
    return remainingTime > 0 ? remainingTime : -1
  } catch (error) {
    return -1
  }
}

/**
 * 检查token是否即将过期（默认5分钟内）
 * @param {string} token - JWT token
 * @param {number} warningMinutes - 警告分钟数，默认5分钟
 * @returns {boolean} - 是否即将过期
 */
export const isTokenExpiringSoon = (token, warningMinutes = 5) => {
  const remainingTime = getTokenRemainingTime(token)
  return remainingTime > 0 && remainingTime <= warningMinutes * 60
}

/**
 * 自动刷新token（如果支持的话）
 * @returns {Promise<boolean>} - 是否刷新成功
 */
export const autoRefreshToken = async () => {
  try {
    // 这里可以调用后端的token刷新接口
    // const response = await refreshTokenApi()
    // const newToken = response.data.access_token
    // localStorage.setItem('token', newToken)
    // return true
    
    // 暂时返回false，表示不支持自动刷新
    return false
  } catch (error) {
    console.error('Token刷新失败:', error)
    return false
  }
}
