import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNavigationStore = defineStore('navigation', () => {
  // 当前页面路径
  const currentPath = ref('/')
  
  // 导航历史
  const navigationHistory = ref([])
  
  // 页面标题映射
  const pageTitles = {
    '/': '首页 - 文档管理系统',
    '/content-list': '文件管理 - 文档管理系统',
    '/text-input': '文本上传 - 文档管理系统',
    '/course-edit': '文本生成 - 文档管理系统',
    '/user-profile': '用户信息 - 文档管理系统'
  }
  
  // 页面描述映射
  const pageDescriptions = {
    '/': '高效管理您的文档，智能分类，快速检索',
    '/content-list': '查看、下载、删除已上传的文档，支持筛选和分页',
    '/text-input': '上传文档文件，系统自动进行分类和知识库同步',
    '/course-edit': '基于工作流自动生成课程内容和相关文档',
    '/user-profile': '管理账户信息、查看统计数据、修改密码等'
  }
  
  // 计算属性：当前页面标题
  const currentPageTitle = computed(() => pageTitles[currentPath.value] || '文档管理系统')
  
  // 计算属性：当前页面描述
  const currentPageDescription = computed(() => pageDescriptions[currentPath.value] || '')
  
  // 计算属性：当前页面是否激活
  const isPageActive = computed(() => (path) => currentPath.value === path)
  
  // 设置当前路径
  const setCurrentPath = (path) => {
    currentPath.value = path
    addToHistory(path)
    updatePageTitle()
  }
  
  // 添加到导航历史
  const addToHistory = (path) => {
    const timestamp = Date.now()
    const historyItem = {
      path,
      timestamp,
      title: pageTitles[path] || '未知页面'
    }
    
    // 避免重复添加相同路径
    const existingIndex = navigationHistory.value.findIndex(item => item.path === path)
    if (existingIndex !== -1) {
      navigationHistory.value.splice(existingIndex, 1)
    }
    
    navigationHistory.value.unshift(historyItem)
    
    // 限制历史记录数量
    if (navigationHistory.value.length > 10) {
      navigationHistory.value = navigationHistory.value.slice(0, 10)
    }
  }
  
  // 更新页面标题
  const updatePageTitle = () => {
    document.title = currentPageTitle.value
  }
  
  // 获取导航历史
  const getNavigationHistory = () => {
    return navigationHistory.value
  }
  
  // 清空导航历史
  const clearNavigationHistory = () => {
    navigationHistory.value = []
  }
  
  // 获取面包屑导航
  const getBreadcrumbs = () => {
    const breadcrumbs = []
    
    // 添加首页
    breadcrumbs.push({
      path: '/',
      title: '首页',
      icon: 'home'
    })
    
    // 如果不是首页，添加当前页面
    if (currentPath.value !== '/') {
      const currentPage = Object.entries(pageTitles).find(([path]) => path === currentPath.value)
      if (currentPage) {
        breadcrumbs.push({
          path: currentPage[0],
          title: currentPage[1].split(' - ')[0],
          icon: getPageIcon(currentPage[0])
        })
      }
    }
    
    return breadcrumbs
  }
  
  // 获取页面图标
  const getPageIcon = (path) => {
    const iconMap = {
      '/': 'home',
      '/content-list': 'file-text',
      '/text-input': 'upload',
      '/course-edit': 'star',
      '/user-profile': 'user'
    }
    return iconMap[path] || 'file'
  }
  
  return {
    currentPath,
    navigationHistory,
    currentPageTitle,
    currentPageDescription,
    isPageActive,
    setCurrentPath,
    addToHistory,
    updatePageTitle,
    getNavigationHistory,
    clearNavigationHistory,
    getBreadcrumbs,
    getPageIcon
  }
})
