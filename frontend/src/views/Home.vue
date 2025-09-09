<template>
  <div class="home-page">
    <div class="hero-section">
      <h1 class="hero-title">欢迎使用文档管理系统</h1>
      <p class="hero-subtitle">高效管理您的文档，智能分类，快速检索</p>
      <div class="hero-actions">
        <button class="refresh-btn" @click="refreshData" :disabled="loading">
          <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
          </svg>
          <div v-else class="loading-spinner"></div>
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
        <span class="last-update">最后更新: {{ lastUpdateTime }}</span>
      </div>
    </div>

    <div class="features-grid">
      <div class="feature-card" @click="navigateTo('/content-list')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"></path>
          </svg>
        </div>
        <h3 class="feature-title">文件管理</h3>
        <p class="feature-description">查看、下载、删除已上传的文档，支持筛选和分页</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ stats.totalFiles }}</strong> 总文件
          </span>
          <span class="stat-item">
            <strong>{{ stats.classifiedFiles }}</strong> 已分类
          </span>
        </div>
        <div class="feature-hint">点击进入文件管理</div>
      </div>

      <div class="feature-card" @click="navigateTo('/text-input')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        </div>
        <h3 class="feature-title">文本上传</h3>
        <p class="feature-description">上传文档文件，系统自动进行分类和知识库同步</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ stats.uploadedFiles }}</strong> 已上传
          </span>
          <span class="stat-item">
            <strong>{{ stats.failedFiles }}</strong> 失败
          </span>
        </div>
        <div class="feature-hint">点击上传新文档</div>
      </div>

      <div class="feature-card" @click="navigateTo('/course-edit')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
          </svg>
        </div>
        <h3 class="feature-title">文本生成</h3>
        <p class="feature-description">基于工作流自动生成课程内容和相关文档</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ stats.workflowRuns }}</strong> 工作流
          </span>
        </div>
        <div class="feature-hint">点击生成新内容</div>
      </div>

      <div class="feature-card" @click="navigateTo('/user-profile')">
        <div class="feature-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <h3 class="feature-title">用户信息</h3>
        <p class="feature-description">管理账户信息、查看统计数据、修改密码等</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ userInfo.username }}</strong> 用户
          </span>
        </div>
        <div class="feature-hint">点击查看用户信息</div>
      </div>
    </div>

    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <button class="action-btn primary" @click="navigateTo('/text-input')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"></path>
          </svg>
          上传新文档
        </button>
        <button class="action-btn secondary" @click="navigateTo('/content-list')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"></path>
          </svg>
          查看文档列表
        </button>
        <button class="action-btn secondary" @click="navigateTo('/course-edit')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
          </svg>
          生成新内容
        </button>
      </div>
    </div>

    <div class="recent-activity">
      <h2 class="section-title">最近活动</h2>
      <div class="activity-list">
        <div v-if="recentDocuments.length === 0" class="no-activity">
          <p>暂无最近活动</p>
        </div>
        <div v-else v-for="doc in recentDocuments" :key="doc.id" class="activity-item">
          <div class="activity-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
          </div>
          <div class="activity-content">
            <div class="activity-title">{{ doc.filename }}</div>
            <div class="activity-meta">
              <span class="activity-time">{{ formatDate(doc.upload_time) }}</span>
              <span class="activity-status" :class="getStatusClass(doc.status)">
                {{ getStatusText(doc.status) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const stats = ref({
  totalFiles: 0,
  uploadedFiles: 0,
  classifiedFiles: 0,
  failedFiles: 0,
  workflowRuns: 0
})

const userInfo = ref({
  username: '用户'
})

const recentDocuments = ref([])

// 加载状态
const loading = ref(false)
// 最后更新时间
const lastUpdateTime = ref('N/A')

// 方法
const navigateTo = (path) => {
  router.push(path)
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '未知'
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const getStatusClass = (status) => {
  const statusMap = {
    'uploaded': 'status-uploaded',
    'classified': 'status-classified',
    'classification_failed': 'status-failed'
  }
  return statusMap[status] || 'status-unknown'
}

const getStatusText = (status) => {
  const statusMap = {
    'uploaded': '已上传',
    'classified': '已分类',
    'classification_failed': '分类失败'
  }
  return statusMap[status] || '未知状态'
}

const loadStats = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/documents', {
      params: { limit: 1000 }
    })
    
    if (response.data.code === 200) {
      const documents = response.data.data.documents
      stats.value.totalFiles = documents.length
      stats.value.uploadedFiles = documents.filter(d => d.status === 'uploaded').length
      stats.value.classifiedFiles = documents.filter(d => d.status === 'classified').length
      stats.value.failedFiles = documents.filter(d => d.status === 'classification_failed').length
      
      // 获取最近5个文档
      recentDocuments.value = documents.slice(0, 5)
      lastUpdateTime.value = new Date().toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadStats()
}

// 组件挂载时加载数据
onMounted(() => {
  // 设置用户信息
  userInfo.value.username = authStore.user?.username || '用户'
  
  // 加载统计数据
  loadStats()
  
  // 模拟工作流运行次数
  stats.value.workflowRuns = Math.floor(Math.random() * 10) + 5
})
</script>

<style scoped>
.home-page {
  min-height: calc(100vh - 70px);
  background: transparent;
  padding: 16px;
  margin-top: 0;
}

.hero-section {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px 16px;
  background: rgba(255,255,255,0.85);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  backdrop-filter: blur(6px);
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #333;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 1.1rem;
  margin: 0;
  color: #666;
  max-width: 600px;
  margin: 0 auto;
}

.hero-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
  justify-content: center;
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.loading-spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.last-update {
  font-size: 14px;
  color: #666;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.feature-card {
  background: rgba(255,255,255,0.92);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.feature-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #333;
}

.feature-description {
  color: #666;
  margin: 0 0 20px 0;
  line-height: 1.6;
}

.feature-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 14px;
  color: #667eea;
}

.stat-item strong {
  color: #333;
}

.feature-hint {
  font-size: 0.9rem;
  color: #999;
  margin-top: 15px;
  text-align: center;
}

.quick-actions {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #333;
  text-align: center;
}

.actions-grid {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 160px;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.action-btn.secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.action-btn.secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-4px);
}

.action-btn svg {
  width: 20px;
  height: 20px;
}

.recent-activity {
  max-width: 800px;
  margin: 0 auto;
}

.activity-list {
  background: rgba(255,255,255,0.92);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
}

.no-activity {
  text-align: center;
  padding: 40px;
  color: #666;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
}

.activity-icon svg {
  width: 20px;
  height: 20px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.activity-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.activity-time {
  font-size: 14px;
  color: #666;
}

.activity-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-uploaded {
  background: #fff3e0;
  color: #f57c00;
}

.status-classified {
  background: #e8f5e8;
  color: #388e3c;
}

.status-failed {
  background: #ffebee;
  color: #d32f2f;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-page {
    padding: 12px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-actions {
    flex-direction: column;
    gap: 12px;
  }

  .refresh-btn {
    width: 100%;
    max-width: 280px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .actions-grid {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 280px;
  }
}

@media (max-width: 480px) {
  .home-page {
    padding: 8px;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .hero-section {
    padding: 16px 8px;
    margin-bottom: 24px;
  }
  
  .features-grid {
    gap: 12px;
  }
  
  .feature-card {
    padding: 16px;
  }
  
  .action-btn {
    padding: 12px 20px;
    font-size: 14px;
  }
}
</style>

