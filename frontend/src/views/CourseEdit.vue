<template>
  <div class="course-edit-container">
    <div class="content-header">
      <h1 class="page-title">文本生成</h1>
      <p class="page-subtitle">基于工作流自动生成课程内容和相关文档</p>
    </div>
    <div class="course-edit-form">
      <!-- Form Fields -->
      <form @submit.prevent="handleSubmit" class="form-content">
        <!-- Course Title -->
        <div class="form-group">
          <label for="courseTitle" class="form-label">Course Title</label>
          <input
            id="courseTitle"
            v-model="formData.title"
            type="text"
            class="form-input"
            placeholder="Enter course title..."
            required
            :disabled="loading"
          />
        </div>

        <!-- Course Description -->
        <div class="form-group">
          <label for="courseDescription" class="form-label">Course Description</label>
          <textarea
            id="courseDescription"
            v-model="formData.description"
            class="form-textarea"
            placeholder="Enter course description..."
            rows="4"
            required
            :disabled="loading"
          ></textarea>
        </div>

        <!-- Visibility Options -->
        <div class="form-group">
          <label class="form-label">Visibility</label>
          <div class="radio-group">
            <label class="radio-option">
              <input
                type="radio"
                v-model="formData.visibility"
                value="draft"
                class="radio-input"
                :disabled="loading"
              />
              <span class="radio-label">Draft - Only visible to you</span>
            </label>
            <label class="radio-option">
              <input
                type="radio"
                v-model="formData.visibility"
                value="published"
                class="radio-input"
                :disabled="loading"
              />
              <span class="radio-label">Published - Visible to enrolled students</span>
            </label>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-message">
          <div class="loading-spinner"></div>
          <div>正在启动工作流，请稍候...</div>
          <div class="loading-note">生成过程中请勿关闭页面或刷新</div>
        </div>

        <!-- Action Buttons -->
        <div class="button-group">
          <button type="button" class="btn btn-history" @click="openHistoryModal" :disabled="loading">
            {{ loading ? '处理中...' : '历史生成' }}
          </button>
          <button type="submit" class="btn btn-continue" :disabled="loading">
            {{ loading ? 'Processing...' : '生成文本' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Result Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">结果</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <pre class="modal-content">{{ modalContent }}</pre>
        </div>
        <div class="modal-footer">
          <button class="btn btn-history" @click="downloadText(formData.title || 'generated', modalContent)">下载为TXT</button>
          <button class="btn btn-continue" @click="closeModal">确定</button>
        </div>
      </div>
    </div>

    <!-- History Modal -->
    <div v-if="showHistoryModal" class="modal-overlay" @click.self="closeHistoryModal">
      <div class="modal-card history-modal">
        <div class="modal-header">
          <h3 class="modal-title">历史生成记录</h3>
          <button class="modal-close" @click="closeHistoryModal">×</button>
        </div>
        <div class="modal-body">
          <div v-if="historyLoading" class="loading-message">
            正在加载历史记录...
          </div>
          <div v-else-if="historyError" class="error-message">
            {{ historyError }}
          </div>
          <div v-else-if="courseHistory.length === 0" class="empty-message">
            暂无历史生成记录
          </div>
          <div v-else class="history-list">
            <div v-for="course in courseHistory" :key="course.id" class="history-item">
              <div class="history-header">
                <h4 class="course-title">{{ course.course_title }}</h4>
                <span class="course-visibility" :class="course.visibility">
                  {{ course.visibility === 'draft' ? '草稿' : '已发布' }}
                </span>
              </div>
              <div class="course-description">
                <strong>描述：</strong>{{ course.course_description }}
              </div>
              <div class="course-text">
                <strong>生成内容：</strong>
                <!-- 发布状态或已解锁的草稿：展示内容 -->
                <div v-if="course.visibility === 'published' || unlockedDraftMap[course.id]" class="generated-text">
                  {{ course.generated_text }}
                  <div style="margin-top:8px;text-align:right">
                    <button class="btn btn-history" @click="downloadCourseText(course)">下载TXT</button>
                  </div>
                </div>
                <!-- 草稿且未解锁：展示密码输入 -->
                <div v-else class="draft-locked">
                  <div class="locked-tip">该内容为草稿，输入密钥后查看</div>
                  <div class="unlock-row">
                    <input
                      :id="'pwd-'+course.id"
                      type="password"
                      class="unlock-input"
                      placeholder="输入密钥："
                      v-model="passwordInputs[course.id]"
                      @keyup.enter="verifyDraft(course)"
                    />
                    <button class="btn btn-continue unlock-btn" @click="verifyDraft(course)">验证</button>
                  </div>
                  <div v-if="passwordErrors[course.id]" class="error-message small">{{ passwordErrors[course.id] }}</div>
                </div>
              </div>
              <div class="course-meta">
                <span class="username">用户：{{ course.username }}</span>
                <span class="created-time">创建时间：{{ formatDate(course.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-continue" @click="closeHistoryModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

// 获取认证状态
const authStore = useAuthStore()

// Form data
const formData = reactive({
  title: '',
  description: '',
  visibility: 'draft'
})

// Loading state
const loading = ref(false)

// Modal state
const showModal = ref(false)
const modalContent = ref('')

// History modal state
const showHistoryModal = ref(false)
const courseHistory = ref([])
const historyLoading = ref(false)
const historyError = ref('')

// 草稿密钥相关状态（密钥由后端校验）
const unlockedDraftMap = reactive({}) // { [courseId]: true }
const passwordInputs = reactive({})   // { [courseId]: 'xxx' }
const passwordErrors = reactive({})   // { [courseId]: '错误' }

// 计算属性：获取当前用户名
const currentUsername = computed(() => authStore.userInfo?.username || 'anonymous')

// 页面离开确认
const beforeUnloadHandler = (e) => {
  if (loading.value) {
    e.preventDefault()
    e.returnValue = '正在生成内容，确定要离开吗？'
    return '正在生成内容，确定要离开吗？'
  }
}

function extractTextFromResult(result) {
  try {
    const data = result?.data ?? result ?? {}
    if (typeof data === 'string') return data
    if (typeof data.text === 'string') return data.text
    if (data.outputs && typeof data.outputs.text === 'string') return data.outputs.text
    if (data.message && typeof data.message === 'string') return data.message
    // 兜底：展示完整对象
    return JSON.stringify(result, null, 2)
  } catch (e) {
    return JSON.stringify(result, null, 2)
  }
}

// 验证草稿密钥（后端校验）
const verifyDraft = async (course) => {
  const input = passwordInputs[course.id] || ''
  passwordErrors[course.id] = ''
  try {
    const form = new FormData()
    form.append('secret', input)
    const resp = await axios.post('http://localhost:8000/api/courses/draft/verify', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (resp.data && resp.data.code === 200) {
      unlockedDraftMap[course.id] = true
      passwordErrors[course.id] = ''
    } else {
      passwordErrors[course.id] = resp.data?.message || '密钥错误，请重试'
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '验证失败'
    passwordErrors[course.id] = msg
  }
}

// Form handlers
const handleSubmit = async () => {
  try {
    loading.value = true

    // 创建FormData对象来发送数据
    const formDataToSend = new FormData()
    formDataToSend.append('title', formData.title)
    formDataToSend.append('description', formData.description)
    formDataToSend.append('visibility', formData.visibility)
    formDataToSend.append('current_user', currentUsername.value)

    const response = await axios.post('http://localhost:8000/api/course/workflow', formDataToSend, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 从后端响应中提取可读文本
    const text = extractTextFromResult(response.data)
    modalContent.value = text
    showModal.value = true

    // 如果成功，清空表单
    if (response.data.success) {
      formData.title = ''
      formData.description = ''
      formData.visibility = 'draft'
    }

  } catch (error) {
    let msg = '提交失败'
    if (error?.response?.data?.detail) msg = error.response.data.detail
    else if (error?.message) msg = error.message
    modalContent.value = msg
    showModal.value = true
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showModal.value = false
}

// 下载任意文本为TXT
const downloadText = (baseName, text) => {
  try {
    const content = typeof text === 'string' ? text : JSON.stringify(text, null, 2)
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const safe = (baseName || 'generated').replace(/[^\w\u4e00-\u9fa5\-]+/g, '_')
    a.href = url
    a.download = `${safe}.txt`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('下载失败', e)
  }
}

const downloadCourseText = (course) => {
  const name = course?.course_title || 'generated'
  const text = course?.generated_text || ''
  downloadText(name, text)
}

// 显示历史记录弹窗
const openHistoryModal = () => {
  showHistoryModal.value = true
  loadCourseHistory()
}

// 关闭历史记录弹窗
const closeHistoryModal = () => {
  showHistoryModal.value = false
  courseHistory.value = []
  historyError.value = ''
}

// 加载课程历史记录
const loadCourseHistory = async () => {
  try {
    historyLoading.value = true
    historyError.value = ''
    
    // 调用后端API获取课程列表
    const response = await axios.get('http://localhost:8000/api/courses', {
      params: {
        username: currentUsername.value,
        limit: 50 // 限制返回50条记录
      }
    })
    
    if (response.data.code === 200) {
      courseHistory.value = response.data.data.courses || []
    } else {
      historyError.value = response.data.message || '获取历史记录失败'
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    historyError.value = error?.response?.data?.detail || error?.message || '网络错误，请重试'
  } finally {
    historyLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// 生命周期钩子
onMounted(() => {
  window.addEventListener('beforeunload', beforeUnloadHandler)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})
</script>

<style scoped>
.course-edit-container {
  min-height: calc(100vh - 70px);
  background-color: transparent;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  margin-top: 0;
}

.content-header {
  text-align: center;
  margin-bottom: 16px;
}

.page-title { font-size: 2.2rem; font-weight: 700; margin: 0 0 6px 0; color: #333; }
.page-subtitle { margin: 0; color: #666; }

.course-edit-form {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 30px;
  width: 100%;
  max-width: 600px;
}

/* Form Content */
.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.form-input,
.form-textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

/* Radio Group */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.radio-label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

/* Loading Message */
.loading-message {
  text-align: center;
  color: #666;
  padding: 20px;
  background-color: #f0f8ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e3f2fd;
  border-top: 3px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-note {
  font-size: 12px;
  color: #999;
  font-style: normal;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Button Group */
.button-group {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #ccc !important;
  color: #666 !important;
}

.form-input:disabled,
.form-textarea:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.radio-input:disabled + .radio-label {
  color: #999;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: white;
  color: #4CAF50;
  border: 1px solid #4CAF50;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #f0f8f0;
}

.btn-continue {
  background-color: #4CAF50;
  color: white;
}

.btn-continue:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-history {
  background-color: #2196F3;
  color: white;
}

.btn-history:hover {
  background-color: #1976D2;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: min(820px, 92vw);
  max-height: 80vh;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  margin: 0;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.modal-body {
  padding: 16px;
  overflow: auto;
}

.modal-content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

/* Responsive Design */
@media (max-width: 768px) {
  .course-edit-container {
    padding: 10px;
  }
  
  .course-edit-form {
    padding: 20px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

/* 追加一个链接样式按钮，用于路由跳转 */
.btn-cancel-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border-radius: 4px;
  border: 1px solid #4CAF50;
  color: #4CAF50;
  text-decoration: none;
  background: #fff;
}
.btn-cancel-link:hover { background: #f0f8f0; }
.btn-cancel-link.disabled { pointer-events: none; opacity: .6; }

/* History Modal Styles */
.history-modal {
  width: min(900px, 95vw);
  max-height: 85vh;
}

.history-list {
  max-height: 60vh;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background-color: #fafafa;
}

.history-item:last-child {
  margin-bottom: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.course-title {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.course-visibility {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.course-visibility.draft {
  background-color: #ffeb3b;
  color: #f57f17;
}

.course-visibility.published {
  background-color: #4caf50;
  color: white;
}

.course-description {
  margin-bottom: 12px;
  color: #666;
  font-size: 14px;
}

.course-text {
  margin-bottom: 12px;
}

.generated-text {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  margin-top: 8px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.course-meta {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 12px;
}

.error-message {
  color: #f44336;
  text-align: center;
  padding: 20px;
  background-color: #ffebee;
  border-radius: 4px;
}

.empty-message {
  color: #666;
  text-align: center;
  padding: 40px 20px;
  font-style: italic;
}

/* 新增解锁区域样式 */
.draft-locked {
  margin-top: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
}

.locked-tip {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.unlock-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.unlock-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.unlock-btn {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.unlock-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.unlock-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #ccc !important;
  color: #666 !important;
}

.error-message.small {
  padding: 8px;
  font-size: 12px;
  margin-top: 6px;
}
</style>
