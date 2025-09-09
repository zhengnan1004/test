<template>
  <div class="container">
    <div class="login-card">
      <!-- 注册头部 -->
      <div class="login-header">
        <h1 class="login-title">Register</h1>
        <p class="login-subtitle">创建您的账户，开始您的旅程</p>
      </div>

      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-input"
            :class="{ error: errors.username }"
            placeholder="请输入用户名（至少3个字符）"
            @input="clearError('username')"
            @blur="validateField('username')"
          />
          <div v-if="errors.username" class="error-message">
            {{ errors.username }}
          </div>
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email Address</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            :class="{ error: errors.email }"
            placeholder="请输入邮箱地址"
            @input="clearError('email')"
            @blur="validateField('email')"
          />
          <div v-if="errors.email" class="error-message">
            {{ errors.email }}
          </div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ error: errors.password }"
            placeholder="请输入密码（至少6个字符）"
            @input="clearError('password')"
            @blur="validateField('password')"
          />
          <div v-if="errors.password" class="error-message">
            {{ errors.password }}
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ error: errors.confirmPassword }"
            placeholder="请再次输入密码"
            @input="clearError('confirmPassword')"
            @blur="validateField('confirmPassword')"
          />
          <div v-if="errors.confirmPassword" class="error-message">
            {{ errors.confirmPassword }}
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-container">
            <input
              v-model="form.agreeTerms"
              type="checkbox"
              class="checkbox-input"
              @change="clearError('agreeTerms')"
            />
            <span class="checkbox-label">I agree to the Terms and Conditions</span>
          </label>
          <div v-if="errors.agreeTerms" class="error-message">
            {{ errors.agreeTerms }}
          </div>
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <!-- 错误信息显示 -->
      <div v-if="authStore.error" class="error-message" style="text-align: center; margin-top: 15px;">
        {{ authStore.error }}
      </div>

      <!-- 注册页脚 -->
      <div class="login-footer">
        <div class="signup-link">
          <span>Already have an account? </span>
          <a href="#" @click.prevent="handleLogin">Login now</a>
        </div>
      </div>

      <!-- 社交注册 -->
      <div class="social-login">
        <div class="social-divider">
          <span>或使用以下方式注册</span>
        </div>
        <div class="social-buttons">
          <button class="social-button" @click="handleSocialRegister('wechat')">
            <span>微信</span>
          </button>
          <button class="social-button" @click="handleSocialRegister('qq')">
            <span>QQ</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由和状态管理
const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// 表单验证错误
const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: ''
})

// 响应式数据
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 表单验证
const isFormValid = computed(() => {
  return (
    form.username.trim() && 
    form.email.trim() && 
    form.password.trim() && 
    form.confirmPassword.trim() && 
    form.agreeTerms &&
    !errors.username && 
    !errors.email && 
    !errors.password && 
    !errors.confirmPassword && 
    !errors.agreeTerms
  )
})

// 验证字段
const validateField = (field) => {
  errors[field] = ''
  
  if (field === 'username') {
    if (!form.username.trim()) {
      errors.username = '用户名不能为空'
    } else if (form.username.length < 3) {
      errors.username = '用户名至少3个字符'
    } else if (form.username.length > 50) {
      errors.username = '用户名不能超过50个字符'
    }
  }
  
  if (field === 'email') {
    if (!form.email.trim()) {
      errors.email = '邮箱不能为空'
    } else if (!isValidEmail(form.email)) {
      errors.email = '请输入有效的邮箱地址'
    }
  }
  
  if (field === 'password') {
    if (!form.password.trim()) {
      errors.password = '密码不能为空'
    } else if (form.password.length < 6) {
      errors.password = '密码至少6个字符'
    } else if (form.password.length > 100) {
      errors.password = '密码不能超过100个字符'
    }
  }
  
  if (field === 'confirmPassword') {
    if (!form.confirmPassword.trim()) {
      errors.confirmPassword = '确认密码不能为空'
    } else if (form.password !== form.confirmPassword) {
      errors.confirmPassword = '两次输入的密码不一致'
    }
  }
  
  if (field === 'agreeTerms') {
    if (!form.agreeTerms) {
      errors.agreeTerms = '请同意服务条款'
    }
  }
}

// 邮箱验证
const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 清除错误
const clearError = (field) => {
  errors[field] = ''
  authStore.clearError()
}

// 处理注册
const handleRegister = async () => {
  // 验证所有字段
  validateField('username')
  validateField('email')
  validateField('password')
  validateField('confirmPassword')
  validateField('agreeTerms')
  
  if (!isFormValid.value) {
    return
  }
  
  loading.value = true
  
  try {
    const result = await authStore.register({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password
    })
    
    if (result.success) {
      // 注册成功，跳转到登录页面
      alert('注册成功！请登录您的账户。')
      router.push('/')
    }
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理登录跳转
const handleLogin = () => {
  router.push('/')
}

// 处理社交注册
const handleSocialRegister = (provider) => {
  alert(`${provider}注册功能正在开发中...`)
}

// 组件挂载时初始化
onMounted(() => {
  authStore.initializeAuth()
})
</script>

<style scoped>
/* Checkbox样式已在全局style.css中定义，无需重复 */

.login-form {
  margin-bottom: 20px;
}
</style>
