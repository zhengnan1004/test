import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Success from '@/views/Success.vue'
import CourseEdit from '@/views/CourseEdit.vue'
import TextInput from '@/views/TextInput.vue'
import ContentList from '@/views/ContentList.vue'
import UserProfile from '@/views/UserProfile.vue'
import UserManagement from '@/views/UserManagement.vue'
import Home from '@/views/Home.vue'
import AIchat from '@/views/AIchat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/course-edit',
    name: 'CourseEdit',
    component: CourseEdit,
    meta: { requiresAuth: true }
  },
  {
    path: '/text-input',
    name: 'TextInput',
    component: TextInput,
    meta: { requiresAuth: true }
  },
  {
    path: '/content-list',
    name: 'ContentList',
    component: ContentList,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/ai-chat',
    name: 'AIchat',
    component: AIchat,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/success',
    name: 'Success',
    component: Success,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 如果访问需要认证的页面但未登录，重定向到登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  // 如果已登录用户访问登录页或注册页，重定向到主页面
  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
    return
  }
  
  // 如果有token，验证token有效性
  if (token && to.meta.requiresAuth) {
    try {
      // 检查token是否过期（通过解析JWT的exp字段）
      const tokenPayload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      
      if (tokenPayload.exp < currentTime) {
        // token已过期，清除本地存储并跳转到登录页
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        next('/login')
        return
      }
      
      // 检查管理员权限
      if (to.meta.requiresAdmin) {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        if (user.role !== 'admin') {
          alert('您没有访问此页面的权限')
          next('/')
          return
        }
      }
    } catch (error) {
      // token格式错误，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      next('/login')
      return
    }
  }
  
  // 其他情况正常跳转
  next()
})

export default router 