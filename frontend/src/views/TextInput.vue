<template>
  <div class="text-page">
    <div class="content-header"></div>
    <div class="card">
      <!-- 用户名输入区域 -->
      <div class="username-input-container">
        <label for="username" class="username-label">用户名</label>
        <input
          id="username"
          v-model="username"
          type="text"
          class="username-input"
          placeholder="请输入用户名"
          required
        />
      </div>

      <!-- 访问权限选择区域 -->
      <div class="access-input-container">
        <label for="access" class="access-label">访问权限</label>
        <select
          id="access"
          v-model="accessType"
          class="access-select"
          required
        >
          <option value="Free">免费 (Free)</option>
          <option value="Paid">付费 (Paid)</option>
        </select>
      </div>

      <!-- File Upload Area -->
      <div class="file-upload-container">
        <div class="upload-hint">
          <p class="upload-hint-title">点击选择文件或拖拽文件到此处</p>
          <p class="upload-hint-sub">支持格式：PDF、DOC、DOCX、TXT、MD</p>
        </div>
        <input
          ref="fileInput"
          type="file"
          class="file-input"
          @change="handleFileChange"
          accept=".pdf,.doc,.docx,.txt,.md"
        />
        <div class="file-upload-area" @click="triggerFileInput">
          <div v-if="!selectedFile" class="file-upload-placeholder">
            <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </div>
          <div v-else class="file-selected">
            <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
            <div class="file-info">
              <p class="file-name">{{ selectedFile.name }}</p>
              <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button type="button" class="remove-file" @click.stop="removeFile">×</button>
          </div>
        </div>
      </div>
      
      <!-- 加载提示 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner-large"></div>
          <p class="loading-text">正在上传文件并进行分析，请稍候...</p>
        </div>
      </div>
      
      <div class="toolbar">
          <span class="count">{{ selectedFile ? selectedFile.name : '未选择文件' }}</span>
          <div class="actions">
            <button class="btn btn-secondary" @click="goBack" :disabled="loading">返回</button>
            <button class="btn btn-secondary" @click="clear" :disabled="loading">清空</button>
            <button class="btn btn-primary" @click="preview" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '上传中...' : '上传并分类' }}
            </button>
          </div>
        </div>

      <!-- 上传结果弹窗 -->
      <div v-if="showPreview" class="result-modal-overlay" @click.self="closeResult">
        <div class="result-modal">
          <div class="result-modal-header">
            <div class="result-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="result-title">上传结果</h3>
            <button class="modal-close-btn" @click="closeResult">×</button>
          </div>
          
          <div class="result-content">
            <div v-if="isSuccess" class="success-message">
              <div class="success-icon">✓</div>
              <span>{{ getSuccessMessage() }}</span>
            </div>
            
            <div class="result-details">
              <div v-for="(value, key) in parsedResult" :key="key" class="detail-item">
                <span class="detail-label">{{ formatLabel(key) }}</span>
                <span class="detail-value">{{ formatValue(key, value) }}</span>
              </div>
            </div>
          </div>
          
          <div class="result-modal-footer">
            <button class="btn btn-primary" @click="closeResult">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const content = ref('')
const showPreview = ref(false)

// File upload state
const fileInput = ref(null)
const selectedFile = ref(null)
const loading = ref(false) // 添加上传加载状态
const username = ref('web_user') // 用户名，默认为 web_user
const accessType = ref('Free') // 访问权限，默认为免费

// 计算属性
const isSuccess = computed(() => {
  try {
    const parsed = JSON.parse(content.value)
    return parsed.code === 200
  } catch {
    return false
  }
})

const parsedResult = computed(() => {
  try {
    const parsed = JSON.parse(content.value)
    const data = parsed.data || {}
    // 过滤掉不需要显示的字段
    const { file_id, workflow_run_id, ...filteredData } = data
    return filteredData
  } catch {
    return {}
  }
})

// 方法
const getSuccessMessage = () => {
  try {
    const parsed = JSON.parse(content.value)
    return parsed.message || '上传成功'
  } catch {
    return '上传完成'
  }
}

const formatLabel = (key) => {
  const labelMap = {
    filename: '文件名',
    classification: '分类结果',
    username: '用户名',
    access: '访问权限',
    upload_time: '上传时间'
  }
  return labelMap[key] || key
}

const formatValue = (key, value) => {
  if (key === 'upload_time' && typeof value === 'number') {
    return new Date(value * 1000).toLocaleString('zh-CN')
  }
  if (key === 'file_id' || key === 'workflow_run_id') {
    return value.substring(0, 8) + '...'
  }
  return value
}

const closeResult = () => {
  showPreview.value = false
  content.value = ''
}

const clear = () => {
  content.value = ''
  selectedFile.value = null
      accessType.value = 'Free' // 重置访问权限为免费
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const preview = async () => {
  if (selectedFile.value) {
    try {
      loading.value = true // 开始上传，设置加载状态
      
      // 创建 FormData 对象
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      formData.append('current_user', username.value || 'web_user') // 使用用户输入的用户名
      formData.append('access', accessType.value) // 添加访问权限信息
      
      // 调用文档上传和分类接口
      const response = await axios.post('http://localhost:8000/api/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // 显示上传结果
      content.value = JSON.stringify(response.data, null, 2)
      showPreview.value = true
      
    } catch (error) {
      let errorMsg = '文件上传失败'
      if (error?.response?.data?.detail) {
        errorMsg = error.response.data.detail
      } else if (error?.message) {
        errorMsg = error.message
      }
      content.value = `错误: ${errorMsg}`
      showPreview.value = true
    } finally {
      loading.value = false // 无论成功失败，都要结束加载状态
    }
  }
}

const goBack = () => {
  router.push('/')
}

// File handling functions
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.text-page {
  min-height: calc(100vh - 70px);
  background: transparent;
  display: flex;
  justify-content: center;
  padding: 16px;
  margin-top: 0;
}

.content-header {
  text-align: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0 0 6px 0;
  color: #333;
}

.page-subtitle {
  margin: 0;
  color: #666;
}

.card {
  width: 100%;
  max-width: 820px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  padding: 20px;
}

/* 用户名输入区域样式 */
.username-input-container {
  margin-bottom: 20px;
}

.username-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.username-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.username-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.username-input::placeholder {
  color: #999;
}

/* 访问权限选择区域样式 */
.access-input-container {
  margin-bottom: 20px;
}

.access-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.access-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
  background-color: white;
  cursor: pointer;
}

.access-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.access-select option {
  padding: 8px;
  font-size: 14px;
}

/* File Upload Styles */
.file-upload-container { position: relative; }
.file-input { position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none; }

.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8px; /* 调整上传区域顶部间距，让提示与上传框贴近 */
}

.file-upload-area:hover { border-color: #4CAF50; background-color: #f0f8f0; }

.file-upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.upload-icon { width: 48px; height: 48px; color: #666; }
.file-upload-placeholder p { margin: 0; color: #666; font-size: 14px; }
.file-types { font-size: 12px !important; color: #999 !important; }

.file-selected { display: flex; align-items: center; gap: 16px; padding: 16px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef; width: 100%; }
.file-icon { width: 32px; height: 32px; color: #4CAF50; flex-shrink: 0; }
.file-info { flex: 1; text-align: left; }
.file-name { margin: 0 0 4px 0; font-weight: 500; color: #333; font-size: 14px; }
.file-size { margin: 0; color: #666; font-size: 12px; }
.remove-file { background: none; border: none; color: #dc3545; font-size: 18px; cursor: pointer; padding: 4px 8px; border-radius: 4px; transition: background-color 0.2s; }
.remove-file:hover { background-color: #f8d7da; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.count { color: #999; }
.actions { display: flex; gap: 10px; }

.btn { padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; }
.btn-primary { background: #4CAF50; color: #fff; }
.btn-primary:hover { background: #45a049; }
.btn-secondary { background: #fff; color: #4CAF50; border: 1px solid #4CAF50; }
.btn-secondary:hover { background: #f0f8f0; }

/* 弹窗及加载样式保持不变 */
.result-modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(4px); }
.result-modal { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; width: 90%; max-width: 600px; max-height: 80vh; overflow-y: auto; color: white; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4); animation: modalSlideIn 0.3s ease-out; }
@keyframes modalSlideIn { from { opacity: 0; transform: translateY(-20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
.result-modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 24px 0 24px; margin-bottom: 20px; }
.result-icon { width: 40px; height: 40px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.result-icon svg { width: 24px; height: 24px; color: white; }
.result-title { margin: 0; font-size: 24px; font-weight: 600; color: white; flex: 1; text-align: center; }
.modal-close-btn { background: none; border: none; color: rgba(255, 255, 255, 0.8); font-size: 28px; cursor: pointer; padding: 4px; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; }
.modal-close-btn:hover { background: rgba(255, 255, 255, 0.1); color: white; }
.result-content { background: rgba(255, 255, 255, 0.1); margin: 0 24px; border-radius: 12px; padding: 20px; backdrop-filter: blur(10px); }
.success-message { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding: 16px; background: rgba(76, 175, 80, 0.2); border-radius: 8px; border-left: 4px solid #4CAF50; }
.success-icon { width: 32px; height: 32px; background: #4CAF50; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: bold; }
.result-details { display: grid; gap: 12px; }
.detail-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 12px 16px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; transition: all 0.3s ease; gap: 16px; }
.detail-item:hover { background: rgba(255, 255, 255, 0.15); transform: translateX(4px); }
.detail-label { font-weight: 500; color: rgba(255, 255, 255, 0.9); font-size: 14px; }
.detail-value { color: white; font-size: 14px; font-weight: 600; text-align: left; max-width: 300px; word-wrap: break-word; white-space: normal; line-height: 1.4; }
.result-modal-footer { padding: 20px 24px 24px 24px; text-align: center; }

/* 加载状态样式 */
.loading-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.loading-content { background: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); }
.loading-spinner-large { width: 50px; height: 50px; border: 4px solid #f3f3f3; border-top: 4px solid #4CAF50; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }
.loading-text { margin: 0; color: #333; font-size: 16px; font-weight: 500; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 按钮加载状态 */
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.loading-spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid #ffffff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; }

/* 提示区域样式 */
.upload-hint { text-align: center; margin-bottom: 10px; }
.upload-hint-title { margin: 0; font-size: 14px; color: #555; }
.upload-hint-sub { margin: 4px 0 0 0; font-size: 12px; color: #888; }
</style>
