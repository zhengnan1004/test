<template>
  <div class="content-list-page">
    <div class="content-header">
      <h1 class="page-title">文档列表</h1>
      <p class="page-subtitle">查看所有已上传和分类的文档</p>
    </div>

    <!-- 筛选和搜索区域 -->
    <div class="filter-section">
      <div class="filter-controls">
        <div class="filter-group">
          <label for="username-filter" class="filter-label">用户名</label>
          <input
            id="username-filter"
            v-model="filters.username"
            type="text"
            class="filter-input"
            placeholder="输入用户名筛选"
            @input="handleFilterChange"
          />
        </div>
        
        <div class="filter-group">
          <label for="filename-filter" class="filter-label">文件名</label>
          <input
            id="filename-filter"
            v-model="filters.filename"
            type="text"
            class="filter-input"
            placeholder="输入文件名筛选"
            @input="handleFilterChange"
          />
        </div>

        <button class="refresh-btn" @click="loadDocuments">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载文档列表...</p>
    </div>

    <!-- 文档列表 -->
    <div v-else-if="documents.length > 0" class="documents-grid">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="document-card"
        :class="getStatusClass(doc.status)"
      >
        <div class="card-header">
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
          </div>
          <div class="status-badge" :class="getStatusClass(doc.status)">
            {{ getStatusText(doc.status) }}
          </div>
        </div>

        <div class="card-content">
          <h3 class="document-title" :title="doc.filename">
            {{ truncateFilename(doc.filename) }}
          </h3>
          
          <div class="document-info">
            <div class="info-item">
              <span class="info-label">用户名:</span>
              <span class="info-value">{{ doc.username }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">分类:</span>
              <span 
                class="info-value classification clickable"
                @click="editClassification(doc)"
                :title="doc.classification || '未分类'"
              >
                {{ doc.classification || '未分类' }}
              </span>
            </div>
            
            <div class="info-item">
              <span class="info-label">访问权限:</span>
              <span class="info-value">{{ formatAccess(doc.access) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">上传时间:</span>
              <span class="info-value">{{ formatDate(doc.upload_time) }}</span>
            </div>
          </div>
        </div>

                 <div class="card-actions">
           <button
             v-if="doc.file_path"
             class="action-btn download-btn"
             @click="handleProtectedAction('download', doc)"
             title="下载文件"
           >
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
               <polyline points="7,10 12,15 17,10"></polyline>
               <line x1="12" y1="15" x2="12" y2="3"></line>
             </svg>
             下载
           </button>
           
           <button
             class="action-btn view-btn"
             @click="handleProtectedAction('view', doc)"
             title="查看原文"
           >
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
               <circle cx="12" cy="12" r="3"></circle>
             </svg>
             查看
           </button>

           <button
             class="action-btn update-btn"
             @click="handleProtectedAction('update', doc)"
             title="更新文件"
           >
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M23 4v6h-6M1 20v-6h6M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
             </svg>
             更新
           </button>
           
           <button
             class="action-btn delete-btn"
             @click="handleProtectedAction('delete', doc)"
             title="删除文件"
           >
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>
             </svg>
             删除
           </button>
         </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14,2 14,8 20,8"></polyline>
        </svg>
      </div>
      <h3>暂无文档</h3>
      <p>还没有上传任何文档，或者筛选条件过于严格</p>
    </div>

    <!-- 分页控件 -->
    <div v-if="total > 0" class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
        (共 {{ total }} 条记录)
      </span>
      
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>

         <!-- 删除确认弹窗 -->
     <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
       <div class="modal-content delete-modal">
         <div class="modal-header">
           <h3>确认删除</h3>
           <button class="modal-close" @click="closeDeleteModal">×</button>
         </div>
         
         <div class="modal-body">
           <div class="delete-warning">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
             </svg>
             <p>确定要删除文件 <strong>"{{ documentToDelete.filename }}"</strong> 吗？</p>
             <p class="warning-text">此操作将永久删除该文件，无法恢复！</p>
           </div>
         </div>
         
         <div class="modal-footer">
           <button class="btn btn-secondary" @click="closeDeleteModal">取消</button>
           <button class="btn btn-danger" @click="deleteDocument" :disabled="deleting">
             {{ deleting ? '删除中...' : '确认删除' }}
           </button>
         </div>
       </div>
     </div>

    <!-- 文档详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
     <div class="modal-content">
       <div class="modal-header">
         <h3>文档详情</h3>
         <button class="modal-close" @click="closeDetailModal">×</button>
       </div>
       
       <div class="modal-body">
         <div class="detail-item">
           <span class="detail-label">ID:</span>
           <span class="detail-value">{{ selectedDocument.id }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">文件名:</span>
           <span class="detail-value">{{ selectedDocument.filename }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">用户名:</span>
           <span class="detail-value">{{ selectedDocument.username }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">分类结果:</span>
           <span class="detail-value">{{ selectedDocument.classification || '未分类' }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">状态:</span>
           <span class="detail-value">{{ getStatusText(selectedDocument.status) }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">访问权限:</span>
           <span class="detail-value">{{ selectedDocument.access || 'Free' }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">上传时间:</span>
           <span class="detail-value">{{ formatDate(selectedDocument.upload_time) }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">创建时间:</span>
           <span class="detail-value">{{ formatDate(selectedDocument.created_at) }}</span>
         </div>
         <div class="detail-item">
           <span class="detail-label">文件路径:</span>
           <span class="detail-value">{{ selectedDocument.file_path || '未保存' }}</span>
         </div>
       </div>
       
       <div class="modal-footer">
         <button class="btn btn-secondary" @click="closeDetailModal">关闭</button>
         <button
           v-if="selectedDocument.file_path"
           class="btn btn-primary"
           @click="downloadDocument(selectedDocument.dify_file_id)"
         >
           下载文件
         </button>
       </div>
     </div>
   </div>

    <!-- 预览弹窗（文本/内嵌PDF） -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreview">
      <div class="modal-content" role="dialog" aria-modal="true" @click.stop style="max-width:900px; width:90vw; max-height:85vh;">
        <div class="modal-header">
          <h3>文件原文预览</h3>
          <button type="button" class="modal-close" @click.stop.prevent="closePreview">×</button>
        </div>
        <div class="modal-body" style="height:70vh; overflow:auto;">
          <template v-if="previewMode==='text'">
            <pre style="white-space:pre-wrap;word-break:break-word;">{{ previewText }}</pre>
          </template>
          <template v-else-if="previewMode==='pdf'">
            <iframe :src="previewUrl" type="application/pdf" style="width:100%;height:100%;border:none;"></iframe>
          </template>
          <template v-else>
            <div>该文件类型暂不支持内嵌预览，已在新窗口打开或请下载查看。</div>
          </template>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" @click.stop.prevent="closePreview">关闭</button>
        </div>
      </div>
    </div>

    <!-- 付费文档密钥验证弹窗 -->
    <div v-if="showPaidKeyModal" class="modal-overlay" @click.self="closePaidKeyModal">
      <div class="modal-content paid-key-modal">
        <div class="modal-header">
          <h3>付费文档访问验证</h3>
          <button class="modal-close" @click="closePaidKeyModal">×</button>
        </div>
        
        <div class="modal-body">
                     <div class="paid-warning">
             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
             </svg>
             <p>该文档为付费内容，需要输入访问密钥才能修改分类</p>
           </div>
          
          <div class="form-group">
            <label for="paid-key-input" class="form-label">访问密钥</label>
            <input
              id="paid-key-input"
              v-model="paidKeyInput"
              type="password"
              class="form-input"
              placeholder="请输入访问密钥"
              @keyup.enter="verifyPaidKey"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePaidKeyModal">取消</button>
          <button 
            class="btn btn-primary" 
            @click="verifyPaidKey"
            :disabled="!paidKeyInput.trim()"
          >
            验证密钥
          </button>
        </div>
      </div>
    </div>

    <!-- 分类编辑弹窗 -->
    <div v-if="showClassificationModal" class="modal-overlay" @click.self="closeClassificationModal">
      <div class="modal-content classification-modal">
        <div class="modal-header">
          <h3>修改文档分类</h3>
          <button class="modal-close" @click="closeClassificationModal">×</button>
        </div>
        
        <div class="modal-body">
          <div class="edit-form">
            <div class="form-group">
              <label for="classification-input" class="form-label">文件名</label>
              <div class="filename-display">{{ documentToEdit.filename }}</div>
            </div>
            
            <div class="form-group">
              <label for="classification-input" class="form-label">当前分类</label>
              <div class="current-classification">{{ documentToEdit.classification || '未分类' }}</div>
            </div>
            
            <div class="form-group">
              <label for="classification-input" class="form-label">新分类</label>
              <input
                id="classification-input"
                v-model="editingClassificationValue"
                type="text"
                class="form-input"
                placeholder="请输入新的分类名称"
                maxlength="255"
                @keyup.enter="saveClassification"
              />
              <div class="form-help">分类名称不能为空，建议使用标准分类格式</div>
              
              <!-- 常用分类选项 -->
              <div class="common-classifications">
                <div class="classification-tags">
                  <span class="tag-label">常用分类：</span>
                  <button
                    v-for="tag in commonClassifications"
                    :key="tag"
                    class="classification-tag"
                    @click="selectClassification(tag)"
                  >
                    {{ tag }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeClassificationModal">取消</button>
          <button 
            class="btn btn-primary" 
            @click="saveClassification" 
            :disabled="!editingClassificationValue.trim() || editingClassificationValue.trim() === (documentToEdit.classification || '')"
          >
            保存分类
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api, { updateDocumentClassificationApi } from '@/api/auth'

// 响应式数据
const documents = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const showDetailModal = ref(false)
const selectedDocument = ref({})
const showDeleteModal = ref(false)
const documentToDelete = ref({})
const deleting = ref(false)

// 新增：分类编辑相关状态
const editingClassification = ref(null)
const editingClassificationValue = ref('')
const showClassificationModal = ref(false)
const documentToEdit = ref({})

// 新增：付费文档密钥验证状态
const showPaidKeyModal = ref(false)
const paidKeyInput = ref('')
const pendingClassificationEdit = ref(null)

// 常用分类选项
const commonClassifications = [
  '官方文档：法规政策',
  '官方文档：技术标准',
  '官方文档：管理办法',
  '学术论文：技术研究',
  '学术论文：应用分析',
  '学术论文：综述报告',
  '企业文档：技术文档',
  '企业文档：产品说明',
  '企业文档：培训材料',
  '其他文档'
]

// 新增：付费访问密钥输入
const showSecretPrompt = ref(false)
const secretInput = ref('')
const pendingAction = ref(null)
const pendingDoc = ref(null)

// 预览弹窗状态
const showPreviewModal = ref(false)
const previewMode = ref('text') // 'text' | 'pdf' | 'other'
const previewText = ref('')
const previewUrl = ref('')

// 筛选条件
const filters = reactive({
  username: '',
  filename: ''
})

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 方法
const loadDocuments = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params = {
      skip,
      limit: pageSize.value
    }
    
    if (filters.username) params.username = filters.username
    if (filters.filename) params.filename = filters.filename
    
    const response = await api.get('/documents', { params })
    
    if (response.data.code === 200) {
      documents.value = response.data.data.documents
      total.value = response.data.data.total
    } else {
      console.error('获取文档列表失败:', response.data.message)
    }
  } catch (error) {
    console.error('请求失败:', error)
    // 如果是401错误，API拦截器会自动处理跳转
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadDocuments()
}

const changePage = (page) => {
  currentPage.value = page
  loadDocuments()
}

// 新增：统一入口，先判断是否需要密钥
const handleProtectedAction = async (action, doc) => {
  if (doc?.access === 'PAID') {
    // 弹出输入框
    const key = window.prompt('该文档为付费内容，请输入访问密钥：')
    if (!key) return
    try {
      const form = new FormData()
      form.append('secret', key)
      const verify = await api.post('/paid/verify', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (verify?.data?.code !== 200) {
        alert('密钥不正确')
        return
      }
    } catch (e) {
      alert(e?.response?.data?.detail || '密钥验证失败')
      return
    }
  }

  // 执行动作
  if (action === 'view') {
    viewDocument(doc)
  } else if (action === 'download') {
    downloadDocument(doc.dify_file_id)
  } else if (action === 'delete') {
    confirmDelete(doc)
  } else if (action === 'update') {
    updateDocument(doc)
  }
}

// 预览原文
const viewDocument = async (doc) => {
  try {
    // 尝试以文本方式获取
    const isTxt = /\.txt$/i.test(doc.filename)
    const isPdf = /\.pdf$/i.test(doc.filename)

    if (isTxt) {
      // 直接读取纯文本
      const resp = await api.get(`/documents/${doc.dify_file_id}/text`)
      const text = resp?.data?.data?.text || ''
      previewMode.value = 'text'
      previewText.value = text
      showPreviewModal.value = true
      return
    }

    if (isPdf) {
      const resp = await api.get(`/documents/${doc.dify_file_id}/download`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }))
      previewMode.value = 'pdf'
      previewUrl.value = url
      showPreviewModal.value = true
      return
    }

    // docx 也尝试转为纯文本在线预览
    const isDocx = /\.docx$/i.test(doc.filename)
    if (isDocx) {
      const resp = await api.get(`/documents/${doc.dify_file_id}/text`)
      if (resp?.data?.data?.text) {
        previewMode.value = 'text'
        previewText.value = resp.data.data.text
        showPreviewModal.value = true
        return
      }
    }

    // 其他类型：提示下载查看
    await downloadDocument(doc.dify_file_id)
  } catch (e) {
    console.error('预览失败:', e)
    alert('预览失败，请稍后重试或下载查看')
  }
}

// 关闭预览
function closePreview() {
  try {
    showPreviewModal.value = false
  } finally {
    previewText.value = ''
    if (previewUrl.value) {
      try { URL.revokeObjectURL(previewUrl.value) } catch (e) {}
      previewUrl.value = ''
    }
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedDocument.value = {}
}

const confirmDelete = (doc) => {
  documentToDelete.value = doc
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  documentToDelete.value = {}
}

const deleteDocument = async () => {
  if (!documentToDelete.value.dify_file_id) return
  
  deleting.value = true
  try {
    const response = await api.delete(
      `/documents/${documentToDelete.value.dify_file_id}`
    )
    
    if (response.data.code === 200) {
      // 删除成功，关闭弹窗并刷新列表
      closeDeleteModal()
      await loadDocuments()
      alert('文件删除成功！')
    } else {
      alert('删除失败：' + response.data.message)
    }
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败，请稍后重试')
  } finally {
    deleting.value = false
  }
}

const downloadDocument = async (difyFileId) => {
  try {
    const response = await api.get(
      `/documents/${difyFileId}/download`,
      { responseType: 'blob' }
    )
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'document')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败，请稍后重试')
  }
}

// 更新文档文件
const updateDocument = async (doc) => {
  try {
    // 选择新文件
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.txt,.doc,.docx,.pdf'
    input.onchange = async (e) => {
      const file = e.target.files && e.target.files[0]
      if (!file) return

      try {
        const form = new FormData()
        form.append('file', file)
        if (doc.access) form.append('access', doc.access)

        // 询问是否走 Dify
        const useDify = window.confirm('是否上传到 Dify 并重新分类？(取消则仅本地替换)')
        if (useDify) form.append('via_dify', 'true')

        const resp = await api.put(`/documents/${doc.dify_file_id}/replace`, form, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        if (resp?.data?.code === 200) {
          alert('文件更新成功！')
          loadDocuments()
        } else {
          alert(resp?.data?.message || '文件更新失败')
        }
      } catch (err) {
        console.error('更新失败:', err)
        alert(err?.response?.data?.detail || '更新失败，请稍后重试')
      }
    }
    input.click()
  } catch (e) {
    console.error(e)
  }
}

// 分类编辑相关方法
const editClassification = (doc) => {
  // 检查文档权限
  if (doc.access === 'Paid' || doc.access === 'PAID') {
    // 付费文档，需要先验证密钥
    pendingClassificationEdit.value = doc
    showPaidKeyModal.value = true
    return
  }
  
  // 免费文档，直接打开编辑弹窗
  openClassificationEdit(doc)
}

// 打开分类编辑弹窗
const openClassificationEdit = (doc) => {
  documentToEdit.value = doc
  editingClassificationValue.value = doc.classification || ''
  showClassificationModal.value = true
}

const closeClassificationModal = () => {
  showClassificationModal.value = false
  documentToEdit.value = {}
  editingClassificationValue.value = ''
}

// 付费文档密钥验证相关方法
const verifyPaidKey = () => {
  const key = paidKeyInput.value.trim()
  
  if (!key) {
    alert('请输入访问密钥')
    return
  }
  
  if (key === 'paid123') {
    // 密钥正确，先保存文档引用，然后关闭密钥弹窗，最后打开分类编辑弹窗
    const docToEdit = pendingClassificationEdit.value
    closePaidKeyModal()
    if (docToEdit) {
      openClassificationEdit(docToEdit)
    }
  } else {
    alert('密钥不正确，无法编辑此文档的分类')
    closePaidKeyModal()
  }
}

const closePaidKeyModal = () => {
  showPaidKeyModal.value = false
  paidKeyInput.value = ''
  // 清空待编辑的文档引用
  pendingClassificationEdit.value = null
}

const selectClassification = (classification) => {
  editingClassificationValue.value = classification
}

const saveClassification = async () => {
  const newClassification = editingClassificationValue.value.trim()
  if (!newClassification) {
    alert('分类名称不能为空')
    return
  }
  
  if (newClassification === (documentToEdit.value.classification || '')) {
    alert('分类名称没有变化')
    return
  }
  
  try {
    const response = await updateDocumentClassificationApi(
      documentToEdit.value.dify_file_id,
      newClassification
    )
    
    if (response.data.code === 200) {
      // 更新成功，关闭弹窗并刷新列表
      closeClassificationModal()
      await loadDocuments()
      alert('文档分类更新成功！')
    } else {
      alert('分类更新失败：' + response.data.message)
    }
  } catch (error) {
    console.error('分类更新失败:', error)
    if (error.response?.status === 401) {
      alert('登录已过期，请重新登录')
    } else if (error.response?.status === 403) {
      alert('没有权限修改此文档的分类')
    } else if (error.response?.status === 404) {
      alert('文档不存在')
    } else {
      alert('分类更新失败，请稍后重试')
    }
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

const truncateFilename = (filename) => {
  if (filename.length > 30) {
    return filename.substring(0, 30) + '...'
  }
  return filename
}

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
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateString
  }
}

// 格式化访问权限，统一显示格式
const formatAccess = (access) => {
  if (!access) return 'Free'
  
  // 统一转换为首字母大写的格式
  const accessStr = String(access).toLowerCase()
  
  if (accessStr === 'free') return 'Free'
  if (accessStr === 'paid') return 'Paid'
  if (accessStr === 'restricted') return 'Restricted'
  
  // 其他情况，首字母大写
  return accessStr.charAt(0).toUpperCase() + accessStr.slice(1)
}

// 组件挂载时加载数据
onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.content-list-page {
  min-height: calc(100vh - 70px);
  background: transparent;
  padding: 16px;
  overflow: visible;
  margin-top: 0;
}

.content-header {
  text-align: center;
  margin-bottom: 32px;
  color: #333;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-subtitle {
  font-size: 1.1rem;
  margin: 0;
  opacity: 0.9;
}

.filter-section {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
}

.filter-controls {
  display: flex;
  gap: 20px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  color: #495057;
  font-weight: 500;
  font-size: 14px;
}

.filter-input,
.filter-select {
  padding: 10px 16px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  background: white;
  color: #495057;
  font-size: 14px;
  min-width: 200px;
}

.filter-input::placeholder {
  color: #6c757d;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #667eea;
  border: 1px solid #667eea;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: #495057;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.document-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #ddd;
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.document-card.status-uploaded {
  border-left-color: #ff9800;
}

.document-card.status-classified {
  border-left-color: #4caf50;
}

.document-card.status-failed {
  border-left-color: #f44336;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.file-icon {
  width: 40px;
  height: 40px;
  color: #667eea;
}

.file-icon svg {
  width: 100%;
  height: 100%;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.status-uploaded {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.status-classified {
  background: #e8f5e8;
  color: #388e3c;
}

.status-badge.status-failed {
  background: #ffebee;
  color: #d32f2f;
}

.card-content {
  margin-bottom: 20px;
}

.document-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.document-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.info-value {
  color: #333;
  font-size: 14px;
  text-align: right;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.classification {
  color: #667eea;
  font-weight: 500;
}

.clickable {
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 2px 6px;
  border-radius: 4px;
}

.clickable:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #5a6fd8;
  transform: translateY(-1px);
}

.clickable:active {
  transform: translateY(0);
}

.card-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.download-btn {
  background: #4caf50;
  color: white;
}

.download-btn:hover {
  background: #45a049;
  transform: translateY(-2px);
}

.view-btn {
  background: #667eea;
  color: white;
}

.view-btn:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
  transform: translateY(-2px);
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #495057;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  opacity: 0.7;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
}

.empty-state p {
  margin: 0;
  opacity: 0.8;
  font-size: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 16px;
  border: 1px solid #e9ecef;
}

.page-btn {
  padding: 10px 20px;
  background: #667eea;
  border: 1px solid #667eea;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #495057;
  font-size: 14px;
  font-weight: 500;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-overlay * { pointer-events: auto; }

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 4px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f5f5f5;
  color: #666;
}

.modal-body {
  padding: 24px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
}

.detail-value {
  color: #333;
  text-align: right;
  max-width: 300px;
  word-break: break-word;
}

.modal-footer {
  padding: 20px 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.btn-danger:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* 删除弹窗样式 */
.delete-modal {
  max-width: 500px;
}

/* 分类编辑弹窗样式 */
.classification-modal {
  max-width: 500px;
}

/* 付费密钥验证弹窗样式 */
.paid-key-modal {
  max-width: 500px;
}

.paid-warning {
  text-align: center;
  padding: 20px 0;
}

.paid-warning svg {
  width: 48px;
  height: 48px;
  color: #ffc107;
  margin-bottom: 16px;
}

.paid-warning p {
  margin: 8px 0;
  color: #333;
}

.paid-warning .warning-text {
  color: #667eea !important;
  font-weight: 600;
  font-size: 14px;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.form-input {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-help {
  font-size: 12px;
  color: #6c757d;
  margin-top: 4px;
}

.filename-display,
.current-classification {
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  color: #495057;
  font-size: 14px;
  word-break: break-word;
}

.common-classifications {
  margin-top: 12px;
}

.classification-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-label {
  font-size: 12px;
  color: #6c757d;
  margin-right: 8px;
}

.classification-tag {
  padding: 6px 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 16px;
  color: #495057;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.classification-tag:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateY(-1px);
}

.delete-warning {
  text-align: center;
  padding: 20px 0;
}

.delete-warning svg {
  width: 48px;
  height: 48px;
  color: #ffc107;
  margin-bottom: 16px;
}

.delete-warning p {
  margin: 8px 0;
  color: #333;
}

.warning-text {
  color: #dc3545 !important;
  font-weight: 600;
  font-size: 14px;
}

/* 滚动条样式 */
.content-list-page::-webkit-scrollbar {
  width: 8px;
}

.content-list-page::-webkit-scrollbar-track {
  background: #f1f3f4;
  border-radius: 4px;
}

.content-list-page::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.content-list-page::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 平滑滚动 */
.content-list-page {
  scroll-behavior: smooth;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-list-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-input,
  .filter-select {
    min-width: auto;
  }
  
  .documents-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
