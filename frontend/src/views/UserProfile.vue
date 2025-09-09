<template>
  <div class="user-profile-page">
    <div class="profile-header">
      <h1 class="page-title">用户信息</h1>
      <p class="page-subtitle">管理您的账户信息和设置</p>
    </div>

    <div class="profile-content">
      <!-- 用户基本信息卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <div class="avatar-section">
            <div class="avatar" @click="triggerSelectAvatar" title="点击更换头像">
              <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" />
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <input ref="avatarInput" type="file" accept="image/*" class="hidden-input" @change="onSelectAvatar" />
            </div>
            <div class="user-details">
              <h2 class="user-name">{{ userInfo.username || '用户名' }}</h2>
              <p class="user-email">{{ userInfo.email || 'user@example.com' }}</p>
              <div class="avatar-actions">
                <button class="btn btn-outline" @click="downloadAvatar" :disabled="!avatarUrl">下载头像</button>
                <span v-if="uploading" class="uploading-tip">上传中...</span>
              </div>
            </div>
          </div>
          <button class="edit-btn" @click="editMode = !editMode">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            {{ editMode ? '取消' : '编辑' }}
          </button>
        </div>

        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">用户ID</label>
              <div class="info-value">{{ userInfo.id || '未获取' }}</div>
            </div>
            
            <div class="info-item">
              <label class="info-label">用户名</label>
              <div v-if="!editMode" class="info-value">{{ userInfo.username || '未设置' }}</div>
              <input v-else v-model="editForm.username" type="text" class="info-input" />
            </div>

            <div class="info-item">
              <label class="info-label">邮箱</label>
              <div v-if="!editMode" class="info-value">{{ userInfo.email || '未设置' }}</div>
              <input v-else v-model="editForm.email" type="email" class="info-input" />
            </div>

            <div class="info-item">
              <label class="info-label">注册时间</label>
              <div class="info-value">{{ formatDate(userInfo.created_at) }}</div>
            </div>

            
          </div>

          <div v-if="editMode" class="edit-actions">
            <button class="btn btn-primary" @click="saveChanges" :disabled="saving">
              {{ saving ? '保存中...' : '保存更改' }}
            </button>
            <button class="btn btn-secondary" @click="cancelEdit">取消</button>
          </div>
        </div>
      </div>

      <!-- 账户统计卡片 -->
      <div class="stats-card">
        <h3 class="stats-title">账户统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalFiles }}</div>
            <div class="stat-label">总文件数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.uploadedFiles }}</div>
            <div class="stat-label">已上传</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.classifiedFiles }}</div>
            <div class="stat-label">已分类</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.failedFiles }}</div>
            <div class="stat-label">分类失败</div>
          </div>
        </div>
      </div>

      <!-- 安全设置卡片 -->
      <div class="security-card">
        <h3 class="security-title">安全设置</h3>
        <div class="security-options">
          <div class="security-item">
            <div class="security-info">
              <h4>修改密码</h4>
              <p>定期更新密码以确保账户安全</p>
            </div>
            <button class="btn btn-outline" @click="showChangePassword = true">
              修改密码
            </button>
          </div>

          <div class="security-item">
            <div class="security-info">
              <h4>登录历史</h4>
              <p>查看最近的登录活动</p>
            </div>
            <button class="btn btn-outline" @click="showLoginHistory = true">
              查看历史
            </button>
          </div>

          <div class="security-item">
            <div class="security-info">
              <h4>管理员界面</h4>
              <p>访问系统管理功能</p>
            </div>
            <button class="btn btn-outline" @click="showAdminPanel = true">
              进入管理
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click.self="showChangePassword = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="modal-close" @click="showChangePassword = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="current-password">当前密码</label>
            <input 
              id="current-password"
              v-model="passwordForm.currentPassword" 
              type="password" 
              class="form-input"
              placeholder="输入当前密码"
            />
          </div>
          
          <div class="form-group">
            <label for="new-password">新密码</label>
            <input 
              id="new-password"
              v-model="passwordForm.newPassword" 
              type="password" 
              class="form-input"
              placeholder="输入新密码"
            />
          </div>
          
          <div class="form-group">
            <label for="confirm-password">确认新密码</label>
            <input 
              id="confirm-password"
              v-model="passwordForm.confirmPassword" 
              type="password" 
              class="form-input"
              placeholder="再次输入新密码"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showChangePassword = false">取消</button>
          <button class="btn btn-primary" @click="changePassword" :disabled="changingPassword">
            {{ changingPassword ? '修改中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 管理员界面弹窗 -->
    <div v-if="showAdminPanel" class="modal-overlay" @click.self="showAdminPanel = false">
      <div class="modal-content admin-modal">
        <div class="modal-header">
          <h3>管理员界面</h3>
          <button class="modal-close" @click="showAdminPanel = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="admin-options">
            <div class="admin-option" @click="navigateToUserManagement">
              <div class="admin-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <div class="admin-info">
                <h4>用户管理</h4>
                <p>管理系统用户账户</p>
              </div>
            </div>

            <div class="admin-option" @click="navigateToSystemSettings">
              <div class="admin-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1 1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
              </div>
              <div class="admin-info">
                <h4>系统设置</h4>
                <p>配置系统参数</p>
              </div>
            </div>

            <div class="admin-option" @click="navigateToLogs">
              <div class="admin-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10,9 9,9 8,9"></polyline>
                </svg>
              </div>
              <div class="admin-info">
                <h4>系统日志</h4>
                <p>查看系统运行日志</p>
              </div>
            </div>

            <div class="admin-option" @click="navigateToAnalytics">
              <div class="admin-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 20V10"></path>
                  <path d="M12 20V4"></path>
                  <path d="M6 20v-6"></path>
                </svg>
              </div>
              <div class="admin-info">
                <h4>数据分析</h4>
                <p>查看系统使用统计</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAdminPanel = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getAvatarApi, uploadAvatarApi, updateUserApi, getUserDetailApi } from '@/api/auth'

const authStore = useAuthStore()
const router = useRouter()

// 响应式数据
const editMode = ref(false)
const saving = ref(false)
const uploading = ref(false)
const showChangePassword = ref(false)
const changingPassword = ref(false)
const showAdminPanel = ref(false)

// 用户信息（从后端API获取真实数据）
const userInfo = ref({
  id: null,
  username: '',
  email: '',
  created_at: null,
  last_login: null
})

// 头像url（blob）
const avatarUrl = ref('')
const avatarInput = ref(null)

// 编辑表单
const editForm = reactive({
  username: '',
  email: ''
})

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 统计数据
const stats = ref({
  totalFiles: 0,
  uploadedFiles: 0,
  classifiedFiles: 0,
  failedFiles: 0
})

// 从后端API获取用户详细信息
const loadUserInfo = async () => {
  if (authStore.user?.id) {
    try {
      const response = await getUserDetailApi(authStore.user.id)
      const userData = response.data
      
      userInfo.value = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        created_at: userData.created_at,
        last_login: userData.last_login
      }
      
      // 初始化编辑表单
      editForm.username = userInfo.value.username
      editForm.email = userInfo.value.email
      
      // 检查是否有缓存的头像状态
      const avatarStatus = localStorage.getItem(`avatar_${userData.id}`)
      if (avatarStatus === 'loaded' || avatarStatus === 'uploaded') {
        // 如果有缓存状态，立即加载头像
        await loadAvatar()
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果API调用失败，使用store中的基本信息
      if (authStore.user) {
        userInfo.value = {
          id: authStore.user.id,
          username: authStore.user.username,
          email: authStore.user.email || '',
          created_at: new Date().toISOString(),
          last_login: new Date().toISOString()
        }
        editForm.username = userInfo.value.username
        editForm.email = userInfo.value.email
        
        // 检查缓存的头像状态
        const avatarStatus = localStorage.getItem(`avatar_${authStore.user.id}`)
        if (avatarStatus === 'loaded' || avatarStatus === 'uploaded') {
          await loadAvatar()
        }
      }
    }
  }
}

// 监听store中用户信息的变化
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    loadUserInfo()
  }
}, { immediate: true })

const triggerSelectAvatar = () => {
  avatarInput.value?.click()
}

const onSelectAvatar = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    uploading.value = true
    await uploadAvatarApi(userInfo.value.id, file)
    await loadAvatar() // 上传成功后刷新头像
    
    // 保存头像状态到localStorage，确保刷新后不丢失
    localStorage.setItem(`avatar_${userInfo.value.id}`, 'uploaded')
  } catch (err) {
    alert('头像上传失败：' + (err?.response?.data?.detail || err.message))
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

const loadAvatar = async () => {
  if (!userInfo.value.id) {
    // 用户ID未获取，跳过头像加载
    return
  }
  
  try {
    // 开始加载头像
    const res = await getAvatarApi(userInfo.value.id)
    const blob = res.data
    
    // 创建新的blob URL
    if (avatarUrl.value) {
      URL.revokeObjectURL(avatarUrl.value) // 释放旧的URL
    }
    
    avatarUrl.value = URL.createObjectURL(blob)
    // 头像加载成功
    
    // 保存头像状态
    localStorage.setItem(`avatar_${userInfo.value.id}`, 'loaded')
  } catch (err) {
    // 头像加载失败
    // 未设置头像时忽略
    avatarUrl.value = ''
    localStorage.removeItem(`avatar_${userInfo.value.id}`)
  }
}

const downloadAvatar = async () => {
  if (!avatarUrl.value) return
  try {
    const res = await getAvatarApi(userInfo.value.id)
    const blob = res.data
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'avatar.png'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert('下载失败')
  }
}

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '未知'
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const saveChanges = async () => {
  saving.value = true
  try {
    // 调用后端API保存更改
    const updateData = {}
    if (editForm.username !== userInfo.value.username) {
      updateData.username = editForm.username
    }
    if (editForm.email !== userInfo.value.email) {
      updateData.email = editForm.email
    }
    
    if (Object.keys(updateData).length === 0) {
      alert('没有需要保存的更改')
      return
    }
    
    const response = await updateUserApi(userInfo.value.id, updateData)
    
    // 更新本地数据
    userInfo.value.username = response.data.username
    userInfo.value.email = response.data.email
    
    // 更新store中的用户信息
    if (authStore.user) {
      authStore.user.username = response.data.username
      authStore.user.email = response.data.email
    }
    
    editMode.value = false
    alert('保存成功！')
  } catch (error) {
    const errorMsg = error?.response?.data?.detail || error?.message || '保存失败，请重试'
    alert('保存失败：' + errorMsg)
  } finally {
    saving.value = false
  }
}

const cancelEdit = () => {
  editMode.value = false
  editForm.username = userInfo.value.username
  editForm.email = userInfo.value.email
}

const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.newPassword.length < 6) {
    alert('新密码长度至少6位')
    return
  }
  
  changingPassword.value = true
  try {
    // 调用后端API修改密码
    await updateUserApi(userInfo.value.id, {
      password: passwordForm.newPassword
    })
    
    showChangePassword.value = false
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    alert('密码修改成功！')
  } catch (error) {
    const errorMsg = error?.response?.data?.detail || error?.message || '密码修改失败，请重试'
    alert('密码修改失败：' + errorMsg)
  } finally {
    changingPassword.value = false
  }
}

// 管理员界面导航方法
const navigateToUserManagement = () => {
  showAdminPanel.value = false
  // 检查用户是否有管理员权限
  if (authStore.user?.role === 'admin') {
    // 跳转到用户管理页面
    router.push('/user-management')
  } else {
    alert('您没有访问用户管理的权限')
  }
}

const navigateToSystemSettings = () => {
  showAdminPanel.value = false
  // 检查用户是否有管理员权限
  if (authStore.user?.role === 'admin') {
    // 这里可以跳转到系统设置页面
    alert('系统设置功能开发中...')
    // router.push('/admin/settings') // 如果存在系统设置页面
  } else {
    alert('您没有访问系统设置的权限')
  }
}

const navigateToLogs = () => {
  showAdminPanel.value = false
  // 检查用户是否有管理员权限
  if (authStore.user?.role === 'admin') {
    // 这里可以跳转到系统日志页面
    alert('系统日志功能开发中...')
    // router.push('/admin/logs') // 如果存在系统日志页面
  } else {
    alert('您没有访问系统日志的权限')
  }
}

const navigateToAnalytics = () => {
  showAdminPanel.value = false
  // 检查用户是否有管理员权限
  if (authStore.user?.role === 'admin') {
    // 这里可以跳转到数据分析页面
    alert('数据分析功能开发中...')
    // router.push('/admin/analytics') // 如果存在数据分析页面
  } else {
    alert('您没有访问数据分析的权限')
  }
}

// 组件挂载时初始化数据
onMounted(async () => {
  // 用户信息和头像会在watch中自动加载，这里只需要初始化统计数据
  stats.value = {
    totalFiles: 25,
    uploadedFiles: 20,
    classifiedFiles: 18,
    failedFiles: 2
  }
})
</script>

<style scoped>
.user-profile-page { min-height: calc(100vh - 70px); background: transparent; padding: 16px; margin-top: 0; }
.profile-header { text-align: center; margin-bottom: 32px; }
.page-title { font-size: 2.5rem; font-weight: 700; margin: 0 0 8px 0; color: #333; }
.page-subtitle { font-size: 1.1rem; margin: 0; color: #666; }
.profile-content { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
.profile-card { background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden; }
.card-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; display: flex; justify-content: space-between; align-items: center; color: white; }
.avatar-section { display: flex; align-items: center; gap: 16px; }
.avatar { width: 80px; height: 80px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid rgba(255, 255, 255, 0.3); overflow: hidden; cursor: pointer; }
.avatar img { width: 100%; height: 100%; object-fit: cover; }
.hidden-input { display: none; }
.avatar-actions { margin-top: 6px; display: flex; gap: 8px; }
.uploading-tip { color: #ffd; font-size: 12px; }
.user-details h2 { margin: 0 0 4px 0; font-size: 1.8rem; font-weight: 600; }
.user-details p { margin: 0; opacity: 0.9; font-size: 1rem; word-break: break-all; white-space: normal; }
.user-email { overflow-wrap: break-word; word-wrap: break-word; max-width: 200px; }
.edit-btn { display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 8px; color: white; cursor: pointer; transition: all 0.3s ease; font-size: 14px; font-weight: 500; }
.edit-btn:hover { background: rgba(255, 255, 255, 0.3); transform: translateY(-2px); }
.card-body { padding: 24px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 24px; }
.info-item { display: flex; flex-direction: column; gap: 8px; }
.info-label { font-weight: 600; color: #666; font-size: 14px; }
.info-value { color: #333; font-size: 16px; padding: 8px 0; }
.info-input { padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; transition: border-color 0.3s ease; }
.info-input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
.edit-actions { display: flex; gap: 12px; justify-content: flex-end; }
.stats-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
.stats-title { margin: 0 0 20px 0; font-size: 1.5rem; color: #333; font-weight: 600; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; }
.stat-item { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 12px; transition: transform 0.3s ease; }
.stat-item:hover { transform: translateY(-4px); }
.stat-number { font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 8px; }
.stat-label { color: #666; font-size: 14px; font-weight: 500; }
.security-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
.security-title { margin: 0 0 20px 0; font-size: 1.5rem; color: #333; font-weight: 600; }
.security-options { display: flex; flex-direction: column; gap: 16px; }
.security-item { display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; }
.security-info h4 { margin: 0 0 4px 0; color: #333; font-size: 16px; font-weight: 600; }
.security-info p { margin: 0; color: #666; font-size: 14px; }
.btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.3s ease; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover:not(:disabled) { background: #5a6fd8; transform: translateY(-2px); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #5a6268; transform: translateY(-2px); }
.btn-outline { background: transparent; color: #667eea; border: 1px solid #667eea; }
.btn-outline:hover { background: #667eea; color: white; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-content { background: white; border-radius: 16px; width: 90%; max-width: 500px; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 24px 0 24px; border-bottom: 1px solid #eee; }
.modal-header h3 { margin: 0; color: #333; font-size: 20px; }
.modal-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; padding: 4px; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; }
.modal-close:hover { background: #f5f5f5; color: #666; }
.modal-body { padding: 24px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
.form-input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; transition: border-color 0.3s ease; }
.form-input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
.modal-footer { padding: 20px 24px 24px 24px; display: flex; gap: 12px; justify-content: flex-end; border-top: 1px solid #eee; }

/* 管理员界面样式 */
.admin-modal {
  max-width: 700px;
}

.admin-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.admin-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.admin-option:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.admin-icon {
  width: 48px;
  height: 48px;
  background: #667eea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.admin-icon svg {
  width: 24px;
  height: 24px;
}

.admin-info h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.admin-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
@media (max-width: 768px) {
  .user-profile-page { padding: 16px; }
  .page-title { font-size: 2rem; }
  .card-header { flex-direction: column; gap: 16px; text-align: center; }
  .info-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .security-item { flex-direction: column; gap: 16px; text-align: center; }
  .edit-actions { flex-direction: column; }
  
  /* 管理员界面响应式 */
  .admin-options {
    grid-template-columns: 1fr;
  }
  
  .admin-option {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .admin-modal {
    max-width: 95%;
  }
}
</style>
