<template>
  <div v-if="showWarning" class="token-warning">
    <div class="warning-content">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <p>您的登录会话即将过期，请及时保存工作内容。</p>
        <p class="countdown">剩余时间: {{ formatTime(remainingTime) }}</p>
      </div>
      <div class="warning-actions">
        <button @click="extendSession" class="extend-btn">延长会话</button>
        <button @click="dismissWarning" class="dismiss-btn">忽略</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getTokenRemainingTime, isTokenExpiringSoon } from '@/utils/tokenUtils'
import router from '@/router'

const authStore = useAuthStore()
const showWarning = ref(false)
const remainingTime = ref(0)
let checkInterval = null
let countdownInterval = null

// 检查token状态
const checkTokenStatus = () => {
  const token = localStorage.getItem('token')
  if (!token) return
  
  const timeLeft = getTokenRemainingTime(token)
  const isExpiringSoon = isTokenExpiringSoon(token, 5) // 5分钟内过期
  
  if (isExpiringSoon && timeLeft > 0) {
    remainingTime.value = timeLeft
    showWarning.value = true
    startCountdown()
  } else {
    showWarning.value = false
    stopCountdown()
  }
}

// 启动每秒递减的倒计时，确保实时刷新
const startCountdown = () => {
  if (countdownInterval) return
  countdownInterval = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value = remainingTime.value - 1
    }
  }, 1000)
}

const stopCountdown = () => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
}

// 延长会话（重新登录）
const extendSession = () => {
  showWarning.value = false
  // 清除当前token，跳转到登录页
  authStore.logout()
  router.push('/login')
}

// 忽略警告
const dismissWarning = () => {
  showWarning.value = false
}

// 格式化时间
const formatTime = (seconds) => {
  if (seconds <= 0) return '0分钟'
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes === 0) {
    return `${remainingSeconds}秒`
  } else if (remainingSeconds === 0) {
    return `${minutes}分钟`
  } else {
    return `${minutes}分${remainingSeconds}秒`
  }
}

onMounted(() => {
  // 立即检查一次
  checkTokenStatus()
  
  // 每5秒重新校正一次（避免计时漂移）
  checkInterval = setInterval(checkTokenStatus, 5000)
})

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
  stopCountdown()
})
</script>

<style scoped>
.token-warning {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
  color: white;
  padding: 20px;
  max-width: 400px;
  animation: slideIn 0.3s ease-out;
}

.warning-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.warning-icon {
  font-size: 24px;
  text-align: center;
}

.warning-text {
  text-align: center;
}

.warning-text p {
  margin: 5px 0;
  font-size: 14px;
  line-height: 1.4;
}

.countdown {
  font-weight: bold;
  font-size: 16px;
  color: #fff3cd;
}

.warning-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.extend-btn, .dismiss-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.extend-btn {
  background: #28a745;
  color: white;
}

.extend-btn:hover {
  background: #218838;
  transform: translateY(-1px);
}

.dismiss-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.dismiss-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .token-warning {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .warning-actions {
    flex-direction: column;
  }
}
</style>
