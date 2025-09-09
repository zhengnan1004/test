<template>
  <nav class="navigation">
    <div class="nav-container">
      <!-- Logo区域 -->
      <div class="nav-logo">
        <router-link to="/" class="logo-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
          <span class="logo-text">文档管理系统</span>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <div class="nav-menu">

        <router-link 
          to="/content-list" 
          class="nav-item"
          :class="{ active: currentPath === '/content-list' }"
          @click="handleNavigation('/content-list')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"></path>
          </svg>
          <span>文件管理</span>
        </router-link>

        <router-link 
          to="/text-input" 
          class="nav-item"
          :class="{ active: currentPath === '/text-input' }"
          @click="handleNavigation('/text-input')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          <span>文本上传</span>
        </router-link>

        <router-link 
          to="/course-edit" 
          class="nav-item"
          :class="{ active: currentPath === '/course-edit' }"
          @click="handleNavigation('/course-edit')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
          </svg>
          <span>文本生成</span>
        </router-link>

        <router-link 
          to="/ai-chat" 
          class="nav-item"
          :class="{ active: currentPath === '/ai-chat' }"
          @click="handleNavigation('/ai-chat')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>AI对话</span>
        </router-link>

        <router-link 
          to="/user-profile" 
          class="nav-item"
          :class="{ active: currentPath === '/user-profile' }"
          @click="handleNavigation('/user-profile')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <span>用户信息</span>
        </router-link>
      </div>

      <!-- 用户操作区域 -->
      <div class="nav-user">
        <div class="user-info">
          <span class="username">{{ currentUser || '用户' }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16,17 21,12 16,7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          <span>退出</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNavigationStore } from '@/stores/navigation'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const navigationStore = useNavigationStore()

// 获取当前用户信息
const currentUser = computed(() => authStore.user?.username || '用户')

// 获取当前路径
const currentPath = computed(() => route.path)

// 处理退出登录
const handleLogout = () => {
  // 清空导航历史
  navigationStore.clearNavigationHistory()
  
  authStore.logout()
  router.push('/login')
}

// 处理导航点击
const handleNavigation = (path) => {
  navigationStore.setCurrentPath(path)
}

// 组件挂载时设置当前路径
onMounted(() => {
  navigationStore.setCurrentPath(route.path)
})
</script>

<style scoped>
.navigation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

/* Logo样式 */
.nav-logo {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: white;
  font-weight: 700;
  font-size: 1.5rem;
}

.logo-link svg {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 1.3rem;
}

/* 导航菜单样式 */
.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateY(-2px);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: white;
  border-radius: 2px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    width: 0;
    opacity: 0;
  }
  to {
    width: 20px;
    opacity: 1;
  }
}

.nav-item svg {
  width: 20px;
  height: 20px;
}

.nav-item span {
  font-size: 14px;
}

/* 用户操作区域样式 */
.nav-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  color: white;
  font-weight: 500;
  font-size: 14px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.logout-btn svg {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
    height: 60px;
  }

  .logo-text {
    display: none;
  }

  .nav-menu {
    gap: 4px;
  }

  .nav-item {
    padding: 8px 12px;
  }

  .nav-item span {
    display: none;
  }

  .nav-item svg {
    width: 18px;
    height: 18px;
  }

  .username {
    display: none;
  }

  .logout-btn span {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0 12px;
  }

  .nav-menu {
    gap: 2px;
  }

  .nav-item {
    padding: 6px 8px;
  }
}
</style>

