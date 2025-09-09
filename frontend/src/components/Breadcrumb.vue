<template>
  <nav class="breadcrumb" v-if="breadcrumbs.length > 1">
    <div class="breadcrumb-container">
      <div class="breadcrumb-list">
        <router-link
          v-for="(item, index) in breadcrumbs"
          :key="item.path"
          :to="item.path"
          class="breadcrumb-item"
          :class="{ 
            'active': index === breadcrumbs.length - 1,
            'clickable': index !== breadcrumbs.length - 1
          }"
          @click="handleBreadcrumbClick(item.path)"
        >
          <svg v-if="item.icon === 'home'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9,22 9,12 15,12 15,22"></polyline>
          </svg>
          <svg v-else-if="item.icon === 'file-text'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
          </svg>
          <svg v-else-if="item.icon === 'upload'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17,8 12,3 7,8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <svg v-else-if="item.icon === 'star'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
          </svg>
          <svg v-else-if="item.icon === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
          </svg>
          
          <span class="breadcrumb-text">{{ item.title }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useNavigationStore } from '@/stores/navigation'

const navigationStore = useNavigationStore()

// 获取面包屑数据
const breadcrumbs = computed(() => navigationStore.getBreadcrumbs())

// 处理面包屑点击
const handleBreadcrumbClick = (path) => {
  navigationStore.setCurrentPath(path)
}
</script>

<style scoped>
.breadcrumb {
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e9ecef;
  padding: 12px 0;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.breadcrumb-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: #6c757d;
  font-size: 14px;
  transition: all 0.3s ease;
  position: relative;
}

.breadcrumb-item svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.breadcrumb-text {
  white-space: nowrap;
}

.breadcrumb-item.clickable {
  cursor: pointer;
  color: #667eea;
}

.breadcrumb-item.clickable:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #5a6fd8;
  transform: translateY(-1px);
}

.breadcrumb-item.active {
  color: #495057;
  font-weight: 500;
  background: rgba(102, 126, 234, 0.05);
}

.breadcrumb-item:not(:last-child)::after {
  content: '/';
  margin-left: 8px;
  color: #dee2e6;
  font-weight: 300;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .breadcrumb-container {
    padding: 0 16px;
  }
  
  .breadcrumb-item {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .breadcrumb-item svg {
    width: 14px;
    height: 14px;
  }
  
  .breadcrumb-text {
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
