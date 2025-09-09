import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { useAuthStore } from './stores/auth'
import { checkAndHandleExpiredToken } from './utils/tokenUtils'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 在应用挂载前初始化认证状态
const authStore = useAuthStore()
authStore.initializeAuth()

// 设置全局token检查定时器（每分钟检查一次）
setInterval(() => {
  checkAndHandleExpiredToken()
}, 60000)

// 页面可见性变化时检查token
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    checkAndHandleExpiredToken()
  }
})

app.mount('#app') 