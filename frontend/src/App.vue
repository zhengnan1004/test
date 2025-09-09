<template>
  <div id="app">
    <Navigation v-if="showNavigation" />
    <router-view />
    <TokenExpiryWarning />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navigation from '@/components/Navigation.vue'
import TokenExpiryWarning from '@/components/TokenExpiryWarning.vue'

// 在登录和注册页面不显示导航栏
const route = useRoute()
const authStore = useAuthStore()

const showNavigation = computed(() => {
  return !['login', 'register'].includes(route.name)
})

// 组件挂载时确保认证状态已初始化
onMounted(() => {
  // 如果localStorage中有token但store中没有用户信息，重新初始化
  if (localStorage.getItem('token') && !authStore.user) {
    authStore.initializeAuth()
  }
})
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

/* 全局样式优化 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

/* 隐藏垂直滚动条但保留滚动功能（全局） */
html, body {
  -ms-overflow-style: none; /* IE/旧版Edge */
  scrollbar-width: none;    /* Firefox */
}
html::-webkit-scrollbar,
body::-webkit-scrollbar {
  width: 0 !important;      /* WebKit */
  height: 0 !important;
}

/* 优化滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 