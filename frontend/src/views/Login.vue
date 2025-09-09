<template>
  <div class="container">
    <div class="login-card">
      <!-- 登录头部 -->
      <div class="login-header">
        <h1 class="login-title">Login</h1>
        <p class="login-subtitle">欢迎回来，请登录您的账户</p>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-input"
            :class="{ error: errors.username }"
            placeholder="请输入用户名"
            @input="clearError('username')"
            @blur="validateField('username')"
          />
          <div v-if="errors.username" class="error-message">
            {{ errors.username }}
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
            placeholder="请输入密码"
            @input="clearError('password')"
            @blur="validateField('password')"
          />
          <div v-if="errors.password" class="error-message">
            {{ errors.password }}
          </div>
        </div>

        <div class="form-group">
          <label for="captcha" class="form-label">Verification Code</label>
          <div class="captcha-container">
            <input
              id="captcha"
              v-model="form.captcha"
              type="text"
              class="form-input captcha-input"
              :class="{ error: errors.captcha }"
              placeholder="请输入验证码"
              @input="clearError('captcha')"
              @blur="validateField('captcha')"
            />
            <div class="captcha-display" @click="generateCaptcha">
              <span class="captcha-text">{{ captchaText }}</span>
              <div class="captcha-refresh">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 4v6h-6M1 20v-6h6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                </svg>
              </div>
            </div>
          </div>
          <div v-if="errors.captcha" class="error-message">
            {{ errors.captcha }}
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-container">
            <input
              v-model="form.rememberMe"
              type="checkbox"
              class="checkbox-input"
            />
            <span class="checkbox-label">Remember me</span>
          </label>
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <!-- 错误信息显示 -->
      <div v-if="authStore.error" class="error-message" style="text-align: center; margin-top: 15px;">
        {{ authStore.error }}
      </div>

      <!-- 登录页脚 -->
      <div class="login-footer">
        <a href="#" class="forgot-password" @click.prevent="handleForgotPassword">
          Forgot password?
        </a>
        <div class="signup-link">
          <span>Don't have an account? </span>
          <a href="#" @click.prevent="handleSignup">Signup now</a>
        </div>
      </div>

      <!-- 社交登录 -->
      <div class="social-login">
        <div class="social-divider">
          <span>或使用以下方式登录</span>
        </div>
        <div class="social-buttons">
          <button class="social-button" @click="handleSocialLogin('wechat')">
            <span>微信</span>
          </button>
          <button class="social-button" @click="handleSocialLogin('qq')">
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
  password: '',
  captcha: '',
  rememberMe: false
})

// 表单验证错误
const errors = reactive({
  username: '',
  password: '',
  captcha: ''
})

// 验证码相关
const captchaText = ref('')
const correctCaptcha = ref('')

// 响应式数据
const loading = computed(() => authStore.loading)
const showPassword = ref(false)

// 表单验证
const isFormValid = computed(() => {
  return form.username.trim() && form.password.trim() && form.captcha.trim() && !errors.username && !errors.password && !errors.captcha
})

// 验证字段
const validateField = (field) => {
  errors[field] = ''
  
  if (field === 'username') {
    if (!form.username.trim()) {
      errors.username = '用户名不能为空'
    } else if (form.username.length < 3) {
      errors.username = '用户名至少3个字符'
    }
  }
  
  if (field === 'password') {
    if (!form.password.trim()) {
      errors.password = '密码不能为空'
    } else if (form.password.length < 6) {
      errors.password = '密码至少6个字符'
    }
  }
  
  if (field === 'captcha') {
    if (!form.captcha.trim()) {
      errors.captcha = '验证码不能为空'
    } else if (form.captcha.toLowerCase() !== correctCaptcha.value.toLowerCase()) {
      errors.captcha = '验证码错误'
    }
  }
}

// 生成验证码
const generateCaptcha = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaText.value = result
  correctCaptcha.value = result
  form.captcha = '' // 清空验证码输入
  clearError('captcha')
}

// 清除错误
const clearError = (field) => {
  errors[field] = ''
  authStore.clearError()
}

// 处理登录
const handleLogin = async () => {
  // 验证所有字段
  validateField('username')
  validateField('password')
  validateField('captcha')
  
  if (!isFormValid.value) {
    return
  }
  
  // 验证验证码
  if (form.captcha.toLowerCase() !== correctCaptcha.value.toLowerCase()) {
    errors.captcha = '验证码错误'
    return
  }
  
  try {
    const result = await authStore.login({
      username: form.username.trim(),
      password: form.password
    })
    
    if (result.success) {
      // 登录成功，直接跳转到文档列表页面
              router.push('/')
    }
  } catch (error) {
    console.error('登录失败:', error)
  }
}

// 处理忘记密码
const handleForgotPassword = () => {
  alert('忘记密码功能正在开发中...')
}

// 处理注册
const handleSignup = () => {
  router.push('/register')
}

// 处理社交登录
const handleSocialLogin = (provider) => {
  alert(`${provider}登录功能正在开发中...`)
}

// 组件挂载时初始化
onMounted(() => {
  authStore.initializeAuth()
  generateCaptcha() // 生成初始验证码
})
</script>

<style scoped>
/* Checkbox样式已在全局style.css中定义，无需重复 */

.login-form {
  margin-bottom: 20px;
}

/* 验证码样式 */
.captcha-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-display {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 120px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.captcha-display:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.captcha-display::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.captcha-display:hover::before {
  left: 100%;
}

.captcha-text {
  font-family: 'Courier New', monospace;
  font-size: 20px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 3px;
  user-select: none;
  position: relative;
  z-index: 1;
}

.captcha-refresh {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.captcha-display:hover .captcha-refresh {
  color: white;
  transform: rotate(180deg);
}

/* 添加一些干扰线效果 */
.captcha-display::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%),
    linear-gradient(-45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%);
  pointer-events: none;
}
</style> 