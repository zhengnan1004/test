<template>
  <div class="user-management-page">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-subtitle">管理系统中的所有用户账户</p>
    </div>

    <div class="management-content">
      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="search-section">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索用户名或邮箱..." 
            class="search-input"
            @input="filterUsers"
          />
          <button class="btn btn-primary" @click="filterUsers">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            搜索
          </button>
        </div>
        <button class="btn btn-primary" @click="showAddUserModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          添加用户
        </button>
      </div>

      <!-- 用户列表 -->
      <div class="users-table-container">
        <table class="users-table">
          <thead>
            <tr>
                             <th>ID</th>
               <th>用户名</th>
               <th>邮箱</th>
               <th>角色</th>
               <th>状态</th>
               <th>创建时间</th>
               <th>最后登录</th>
               <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
              <td>{{ user.id }}</td>
              <td>
                <div class="user-info">
                  <div class="user-avatar">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <span>{{ user.username }}</span>
                </div>
              </td>
                             <td>{{ user.email }}</td>
               <td>
                 <span :class="['role-badge', user.role === 'admin' ? 'admin' : 'user']">
                   {{ user.role === 'admin' ? '管理员' : '用户' }}
                 </span>
               </td>
               <td>
                 <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                   {{ user.is_active ? '启用' : '禁用' }}
                 </span>
               </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ formatDate(user.last_login) }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn btn-sm btn-outline" @click="editUser(user)" title="编辑">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline" 
                    @click="toggleUserStatus(user)"
                    :title="user.is_active ? '禁用' : '启用'"
                  >
                    <svg v-if="user.is_active" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                      <line x1="9" y1="9" x2="15" y2="15"></line>
                      <line x1="15" y1="9" x2="9" y2="15"></line>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <polyline points="20,6 9,17 4,12"></polyline>
                    </svg>
                  </button>
                  <button 
                    class="btn btn-sm btn-danger" 
                    @click="deleteUser(user)"
                    title="删除"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <polyline points="3,6 5,6 21,6"></polyline>
                      <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- 空状态 -->
        <div v-if="filteredUsers.length === 0" class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <h3>暂无用户</h3>
          <p>{{ searchQuery ? '没有找到匹配的用户' : '还没有用户数据' }}</p>
        </div>
      </div>
    </div>

    <!-- 添加用户弹窗 -->
    <div v-if="showAddUserModal" class="modal-overlay" @click.self="showAddUserModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加用户</h3>
          <button class="modal-close" @click="showAddUserModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="new-username">用户名</label>
            <input 
              id="new-username"
              v-model="newUser.username" 
              type="text" 
              class="form-input"
              placeholder="输入用户名"
            />
          </div>
          
          <div class="form-group">
            <label for="new-email">邮箱</label>
            <input 
              id="new-email"
              v-model="newUser.email" 
              type="email" 
              class="form-input"
              placeholder="输入邮箱"
            />
          </div>
          
                     <div class="form-group">
             <label for="new-password">密码</label>
             <input 
               id="new-password"
               v-model="newUser.password" 
               type="password" 
               class="form-input"
               placeholder="输入密码"
             />
           </div>
           
           <div class="form-group">
             <label for="new-role">角色</label>
             <select 
               id="new-role"
               v-model="newUser.role" 
               class="form-input"
             >
               <option value="user">用户</option>
               <option value="admin">管理员</option>
             </select>
           </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="newUser.is_active" 
                type="checkbox" 
                class="checkbox-input"
              />
              <span class="checkbox-text">启用账户</span>
            </label>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddUserModal = false">取消</button>
          <button class="btn btn-primary" @click="addUser" :disabled="addingUser">
            {{ addingUser ? '添加中...' : '添加用户' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <div v-if="showEditUserModal" class="modal-overlay" @click.self="showEditUserModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑用户</h3>
          <button class="modal-close" @click="showEditUserModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="edit-username">用户名</label>
            <input 
              id="edit-username"
              v-model="editingUser.username" 
              type="text" 
              class="form-input"
              placeholder="输入用户名"
            />
          </div>
          
          <div class="form-group">
            <label for="edit-email">邮箱</label>
            <input 
              id="edit-email"
              v-model="editingUser.email" 
              type="email" 
              class="form-input"
              placeholder="输入邮箱"
            />
          </div>
          
                     <div class="form-group">
             <label for="edit-password">新密码（留空则不修改）</label>
             <input 
               id="edit-password"
               v-model="editingUser.password" 
               type="password" 
               class="form-input"
               placeholder="输入新密码"
             />
           </div>
           
           <div class="form-group">
             <label for="edit-role">角色</label>
             <select 
               id="edit-role"
               v-model="editingUser.role" 
               class="form-input"
             >
               <option value="user">用户</option>
               <option value="admin">管理员</option>
             </select>
           </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="editingUser.is_active" 
                type="checkbox" 
                class="checkbox-input"
              />
              <span class="checkbox-text">启用账户</span>
            </label>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showEditUserModal = false">取消</button>
          <button class="btn btn-primary" @click="updateUser" :disabled="updatingUser">
            {{ updatingUser ? '更新中...' : '更新用户' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getUserListApi, createUserApi, updateUserApi, deleteUserApi, toggleUserStatusApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const users = ref([])
const searchQuery = ref('')
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const addingUser = ref(false)
const updatingUser = ref(false)

// 新用户表单
const newUser = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
})

// 编辑用户表单
const editingUser = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true
})

// 过滤后的用户列表
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query)
  )
})

// 获取所有用户
const fetchUsers = async () => {
  try {
    const response = await getUserListApi()
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    alert('获取用户列表失败：' + (error?.response?.data?.detail || error?.message || '未知错误'))
  }
}

// 过滤用户
const filterUsers = () => {
  // 这里可以添加额外的过滤逻辑
}

// 添加用户
const addUser = async () => {
  if (!newUser.username || !newUser.email || !newUser.password) {
    alert('请填写所有必填字段')
    return
  }
  
  addingUser.value = true
  try {
    const response = await createUserApi(newUser)
    
    // 重新获取用户列表
    await fetchUsers()
    
    // 重置表单
    newUser.username = ''
    newUser.email = ''
    newUser.password = ''
    newUser.role = 'user'
    newUser.is_active = true
    
    showAddUserModal.value = false
    alert('用户添加成功！')
  } catch (error) {
    console.error('添加用户失败:', error)
    alert('添加用户失败：' + (error?.response?.data?.detail || error?.message || '未知错误'))
  } finally {
    addingUser.value = false
  }
}

// 编辑用户
const editUser = (user) => {
  editingUser.id = user.id
  editingUser.username = user.username
  editingUser.email = user.email
  editingUser.password = ''
  editingUser.role = user.role
  editingUser.is_active = user.is_active
  showEditUserModal.value = true
}

// 更新用户
const updateUser = async () => {
  if (!editingUser.username || !editingUser.email) {
    alert('请填写所有必填字段')
    return
  }
  
  updatingUser.value = true
  try {
    const response = await updateUserApi(editingUser.id, editingUser)
    
    // 重新获取用户列表
    await fetchUsers()
    
    showEditUserModal.value = false
    alert('用户更新成功！')
  } catch (error) {
    console.error('更新用户失败:', error)
    alert('更新用户失败：' + (error?.response?.data?.detail || error?.message || '未知错误'))
  } finally {
    updatingUser.value = false
  }
}

// 切换用户状态
const toggleUserStatus = async (user) => {
  const action = user.is_active ? '禁用' : '启用'
  if (!confirm(`确定要${action}用户 "${user.username}" 吗？`)) {
    return
  }
  
  try {
    await toggleUserStatusApi(user.id)
    
    // 重新获取用户列表
    await fetchUsers()
    
    alert(`用户${action}成功！`)
  } catch (error) {
    console.error(`${action}用户失败:`, error)
    alert(`${action}用户失败：` + (error?.response?.data?.detail || error?.message || '未知错误'))
  }
}

// 删除用户
const deleteUser = async (user) => {
  if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可恢复！`)) {
    return
  }
  
  try {
    await deleteUserApi(user.id)
    
    // 重新获取用户列表
    await fetchUsers()
    
    alert('用户删除成功！')
  } catch (error) {
    console.error('删除用户失败:', error)
    alert('删除用户失败：' + (error?.response?.data?.detail || error?.message || '未知错误'))
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '从未登录'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '无效日期'
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

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management-page {
  min-height: calc(100vh - 70px);
  background: transparent;
  padding: 16px;
  margin-top: 0;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #333;
}

.page-subtitle {
  font-size: 1.1rem;
  margin: 0;
  color: #666;
}

.management-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
}

.search-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  min-width: 300px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
  transform: translateY(-2px);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.users-table td {
  font-size: 14px;
  color: #333;
}

.user-row:hover {
  background: #f8f9fa;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: #d1ecf1;
  color: #0c5460;
}

.role-badge.user {
  background: #e2e3e5;
  color: #383d41;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state svg {
  margin-bottom: 16px;
  color: #ccc;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

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

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Checkbox样式已在全局style.css中定义，无需重复 */

.checkbox-text {
  font-size: 14px;
  color: #333;
}

.modal-footer {
  padding: 20px 24px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .user-management-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .action-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-section {
    flex-direction: column;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .users-table th,
  .users-table td {
    padding: 12px 8px;
    font-size: 12px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
  
  .btn-sm {
    padding: 4px 8px;
  }
}
</style>
