<template>
  <div class="ai-chat-container">
    <div class="chat-header">
      <h2>AI 聊天机器人</h2>
      <p>与AI进行智能对话，获取帮助和建议</p>
    </div>
    
    <!-- 删除开始聊天按钮区域 -->

    <!-- 会话名称输入弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <h3>创建新会话</h3>
        <p>请输入会话名称：</p>
        <input 
          v-model="sessionName" 
          type="text" 
          placeholder="例如：我的AI助手对话"
          class="session-name-input"
          @keydown.enter="confirmStartChat"
          ref="sessionNameInput"
        />
        <div class="dialog-buttons">
          <button @click="closeDialog" class="cancel-btn">取消</button>
          <button @click="confirmStartChat" class="confirm-btn" :disabled="!sessionName.trim() || isStarting">
            <span v-if="!isStarting">确认</span>
            <span v-else>正在创建...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索记录弹窗 -->
    <div v-if="showSearchDialog" class="dialog-overlay" @click="closeSearchDialog">
      <div class="search-dialog-content" @click.stop>
        <h3>AI聊天机器人</h3>
        <div class="search-filters">
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜索问题内容..."
            class="search-input"
            @input="filterRecords"
          />
        </div>
        <div class="records-container">
          <div v-if="loadingRecords" class="loading">加载中...</div>
          <div v-else-if="filteredRecords.length === 0" class="no-records">暂无记录</div>
          <div v-else class="records-list">
            <div 
              v-for="record in filteredRecords" 
              :key="record.id" 
              class="record-item"
              @click="selectRecord(record)"
            >
              <div class="record-header">
                <span class="comment-id">#{{ record.comment_id }}</span>
                <span class="feedback-type" :class="record.feedback_type">
                  {{ getFeedbackTypeText(record.feedback_type) }}
                </span>
              </div>
              <div class="record-question">{{ record.question }}</div>
              <div class="record-time">{{ formatTime(record.created_at) }}</div>
            </div>
          </div>
        </div>
        <div class="dialog-buttons">
          <button @click="closeSearchDialog" class="cancel-btn">关闭</button>
        </div>
      </div>
    </div>

    <!-- 重置聊天确认弹窗 -->
    <div v-if="showResetDialog" class="dialog-overlay" @click="closeResetDialog">
      <div class="reset-dialog-content" @click.stop>
        <div class="reset-dialog-header">
          <div class="reset-icon">🔄</div>
          <h3>重置聊天确认</h3>
        </div>
        <div class="reset-dialog-body">
          <p class="reset-warning">确定要重置聊天吗？</p>
          <p class="reset-description">这将清除所有聊天记录，包括：</p>
          <ul class="reset-list">
            <li>所有用户消息</li>
            <li>所有AI回复</li>
            <li>聊天历史</li>
          </ul>
          <p class="reset-note">重置后将从欢迎消息重新开始。</p>
        </div>
        <div class="reset-dialog-buttons">
          <button @click="closeResetDialog" class="reset-cancel-btn">
            取消
          </button>
          <button @click="confirmReset" class="reset-confirm-btn">
            确定重置
          </button>
        </div>
      </div>
    </div>

    <!-- 历史问题统计弹窗 -->
    <div v-if="showHistoryDialog" class="dialog-overlay" @click="closeHistoryDialog">
      <div class="history-dialog-content" @click.stop>
        <h3>历史问题反馈统计</h3>
        <div class="stats-container">
          <div v-if="loadingStats" class="loading">加载中...</div>
          <div v-else class="stats-content">
            <!-- 统计摘要 -->
            <div class="stats-summary">
              <div class="stat-item good" @click="switchFeedbackType('good')" style="cursor:pointer">
                <div class="stat-number">{{ statsData.goodCount }}</div>
                <div class="stat-label">好评</div>
              </div>
              <div class="stat-item not-satisfied" @click="switchFeedbackType('not satisfied')" style="cursor:pointer">
                <div class="stat-number">{{ statsData.notSatisfiedCount }}</div>
                <div class="stat-label">差评</div>
              </div>
              <div class="stat-item total">
                <div class="stat-number">{{ statsData.totalCount }}</div>
                <div class="stat-label">总计</div>
              </div>
            </div>
            
            <!-- 图表区域 - 已隐藏 -->
            <!-- <div class="charts-section">
              <div class="chart-container">
                <h4>反馈分布饼图</h4>
                <canvas ref="pieChart" width="400" height="400"></canvas>
              </div>
            </div> -->
            
            <!-- 问题列表（好评/差评切换） -->
            <div class="stats-details">
              <h4>{{ selectedFeedbackType === 'good' ? '好评问题列表' : '差评问题列表' }}</h4>
              <div class="detail-list">
                <div v-if="questionsList.length === 0" class="no-questions">
                  暂无{{ selectedFeedbackType === 'good' ? '好评' : '差评' }}问题
                </div>
                <div v-else v-for="question in questionsList" :key="question.id || question.comment_id" class="detail-item">
                  <div class="question-text" @click="viewRecordAnswer(question.comment_id, question.question)">{{ question.question }}</div>
                  <div class="question-info">
                    <span class="comment-id">#{{ question.comment_id }}</span>
                    <span class="feedback-time">{{ formatTime(question.created_at) }}</span>
                  </div>
                  <div v-if="question.answer" class="answer-preview" @click="viewRecordAnswer(question.comment_id, question.question)">
                    <span class="answer-label">answer：</span>{{ truncate(question.answer, 120) }}
                  </div>
                  <!-- 仅在好评列表中显示"设置为标注"按钮 -->
                  <div v-if="selectedFeedbackType === 'good'" class="question-actions">
                    <button 
                      class="annotation-btn" 
                      @click.stop="uploadToAnnotation(question.comment_id)"
                      :disabled="question.uploading"
                    >
                      <span v-if="!question.uploading">设置为标注</span>
                      <span v-else>上传中...</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-buttons">
          <button @click="closeHistoryDialog" class="cancel-btn">关闭</button>
          <button @click="refreshStats" class="refresh-btn">刷新数据</button>
        </div>
      </div>
    </div>
    
    <!-- 聊天界面 -->
    <div class="chat-interface">
      <!-- 聊天头部 -->
      <div class="chat-header-bar">
        <div class="assistant-info">
          <div class="assistant-avatar">
            <div class="avatar-icon">🤖</div>
            <div class="online-indicator"></div>
          </div>
          <div class="assistant-details">
            <h3>AI聊天机器人</h3>
            <span class="status">在线</span>
          </div>
        </div>
        <div class="action-buttons">
          <button class="reset-btn" @click="resetChat" title="重置聊天">
            🔄 重置聊天
          </button>
          <button class="history-btn" @click="showHistoryStats">
            查看历史问题
          </button>
        </div>
      </div>
      
      <!-- 初始界面 -->
      <div v-if="false" class="initial-chat-interface">
        <div class="welcome-content">
          <div class="welcome-icon">💬</div>
          <h3>欢迎使用AI聊天机器人</h3>
          <p>点击"开始聊天"按钮开始与AI进行智能对话</p>
          <div class="welcome-actions">
            <button class="history-btn" @click="showHistoryStats">
              查看历史问题
            </button>
          </div>
        </div>
      </div>
      
      <!-- 聊天消息界面 -->
      <div v-else>
        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesContainer" @wheel="handleWheel">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            :class="['message', message.type]"
          >
            <div class="message-avatar">
              <div class="avatar-icon" v-if="message.type === 'user'">👤</div>
              <div class="avatar-icon" v-else>🤖</div>
            </div>
            <div class="message-content">
              <div class="message-text">
                {{ message.content }}
                <!-- 显示comment_id -->
                <div v-if="message.commentId" class="comment-id">
                  #{{ message.commentId }}
                </div>
              </div>
              <!-- AI消息操作条：仅AI消息展示（首条欢迎语不展示） -->
              <div v-if="message.type === 'ai' && !message.hideActions" class="message-actions">
                <button 
                  class="action-btn like" 
                  :class="{ active: message.feedback === 'like' }"
                  :disabled="message.feedbackSubmitting"
                  @click="handleFeedback(index, 'like')"
                  title="点赞"
                >👍</button>
                <button 
                  class="action-btn dislike" 
                  :class="{ active: message.feedback === 'dislike' }"
                  :disabled="message.feedbackSubmitting"
                  @click="handleFeedback(index, 'dislike')"
                  title="点踩"
                >👎</button>
                <button 
                  class="action-btn copy" 
                  :disabled="message.feedbackSubmitting"
                  @click="copyAnswer(message)"
                  title="复制"
                >📋</button>
              </div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="isLoading" class="message ai">
            <div class="message-avatar">
              <div class="avatar-icon">🤖</div>
            </div>
            <div class="message-content">
              <div class="message-text">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="chat-input-container">
          <div class="input-wrapper">
            <button class="attach-button" title="附件">
              📎
            </button>
            <input
              v-model="inputMessage"
              @keydown.enter.prevent="sendMessage"
              placeholder="Type your message here..."
              class="chat-input"
              :disabled="isLoading"
            />
            <button @click="sendMessage" class="send-button" :disabled="isLoading || !inputMessage.trim()">
              ✈️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIchat',
  data() {
    return {
      chatStarted: true,
      isStarting: false,
      isLoading: false,
      inputMessage: '',
      messages: [],
      sessionId: null,
      chatId: 'workbench', // 不再使用远端聊天助手ID
      showDialog: false,
      sessionName: '',
      userId: 'user_001', // 用户ID，你可以根据实际需求修改
      apiBaseUrl: 'http://127.0.0.1:8000', // API基础URL
      apiKey: '', // 密钥后端保管
      showInput: true,
      showSearchDialog: false,
      searchKeyword: '',
      allRecords: [],
      filteredRecords: [],
      loadingRecords: false,
      showHistoryDialog: false,
      showResetDialog: false,
      loadingStats: false,
      statsData: {
        goodCount: 0,
        notSatisfiedCount: 0,
        totalCount: 0,
        notSatisfiedQuestions: []
      },
      // 列表筛选（默认好评）
      selectedFeedbackType: 'good',
      questionsList: [],
      // 自动刷新定时器
      refreshTimer: null
    }
  },
  methods: {
    // 去除开始/退出按钮逻辑
    
    showSessionNameDialog() {
      this.showDialog = true
      this.sessionName = ''
      this.$nextTick(() => {
        if (this.$refs.sessionNameInput) {
          this.$refs.sessionNameInput.focus()
        }
      })
    },
    
    closeDialog() {
      this.showDialog = false
      this.sessionName = ''
    },
    
    async confirmStartChat() {
      if (!this.sessionName.trim()) return
      this.showDialog = false
      await this.startChat()
    },
    
    async startChat() {
      this.isStarting = true
      try {
        // 直接进入聊天，不再创建远端会话
        this.chatStarted = true
        this.messages.push({
          type: 'ai',
          content: '您好！我是您的AI智能助手，有什么可以帮助您的吗？',
          time: this.getCurrentTime(),
          hideActions: true
        })
      } catch (error) {
        console.error('开始聊天失败:', error)
        alert('开始聊天失败，请稍后重试')
      } finally {
        this.isStarting = false
      }
    },
    
    // 不再需要 createChatSession

    // 搜索记录相关方法
    async showSearchRecords() {
      this.showSearchDialog = true
      this.loadingRecords = true
      try {
        await this.fetchRecords()
      } catch (error) {
        console.error('获取记录失败:', error)
        alert('获取记录失败，请稍后重试')
      } finally {
        this.loadingRecords = false
      }
    },

    async fetchRecords() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/v1/ai-feedback/records`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`)
        }
        
        const result = await response.json()
        // API响应处理
        
        if (result.code === 200 && result.data) {
          // 使用真实的API数据
          this.allRecords = result.data || []
          this.filteredRecords = [...this.allRecords]
        } else {
          throw new Error('API返回数据格式错误')
        }
      } catch (error) {
        console.error('获取记录失败:', error)
        // 如果接口调用失败，使用模拟数据作为fallback
        this.allRecords = this.getMockRecords()
        this.filteredRecords = [...this.allRecords]
      }
    },

    getMockRecords() {
      return [
        {
          id: 1,
          comment_id: 100,
          question: "什么是人工智能？",
          feedback_type: "good",
          created_at: "2024-01-15T10:30:00Z"
        },
        {
          id: 2,
          comment_id: 101,
          question: "如何学习编程？",
          feedback_type: "not satisfied",
          created_at: "2024-01-15T11:45:00Z"
        },
        {
          id: 3,
          comment_id: 102,
          question: "Python和JavaScript有什么区别？",
          feedback_type: "good",
          created_at: "2024-01-15T14:20:00Z"
        }
      ]
    },

    filterRecords() {
      if (!this.searchKeyword.trim()) {
        this.filteredRecords = [...this.allRecords]
      } else {
        this.filteredRecords = this.allRecords.filter(record => 
          record.question.toLowerCase().includes(this.searchKeyword.toLowerCase())
        )
      }
    },

    selectRecord(record) {
      this.messages.push({
        type: 'user',
        content: record.question,
        time: this.getCurrentTime()
      })
      
      this.messages.push({
        type: 'ai',
        content: `这是关于"${record.question}"的历史回复记录。`,
        time: this.getCurrentTime(),
        commentId: record.comment_id
      })
      
      this.closeSearchDialog()
    },

    closeSearchDialog() {
      this.showSearchDialog = false
      this.searchKeyword = ''
    },

    async showHistoryStats() {
      this.showHistoryDialog = true
      this.loadingStats = true
      try {
        await this.fetchHistoryStats()
        
        // 数据加载完成后创建图表，增加延迟确保DOM完全渲染
        // 图表功能已隐藏
        // setTimeout(() => {
        //   this.createCharts()
        // }, 200)
        // 启动自动刷新
        this.startAutoRefresh()
      } catch (error) {
        console.error('获取历史统计失败:', error)
        alert('获取历史统计失败，请稍后重试')
      } finally {
        this.loadingStats = false
      }
    },

    async fetchHistoryStats() {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/v1/ai-feedback/stats`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`)
        }
        
        const result = await response.json()
        // 统计数据API响应处理
        
        if (result.code === 200 && result.data) {
          // 使用真实的API数据
          this.statsData = {
            goodCount: result.data.good_count || 0,
            notSatisfiedCount: result.data.not_satisfied_count || 0,
            totalCount: result.data.total_count || 0,
            notSatisfiedQuestions: result.data.not_satisfied_questions || [],
            goodQuestions: result.data.good_questions || []
          }
          // 初始化为好评列表，直接从数据库读取该类型记录
          this.selectedFeedbackType = 'good'
          await this.fetchQuestionsByType('good')
        } else {
          throw new Error('API返回数据格式错误')
        }
      } catch (error) {
        console.error('获取历史统计失败:', error)
        // 如果接口调用失败，使用模拟数据作为fallback
        this.statsData = this.getMockStats()
      }
    },

    // 切换好评/差评
    async switchFeedbackType(type) {
      if (type !== 'good' && type !== 'not satisfied') return
      this.selectedFeedbackType = type
      await this.fetchQuestionsByType(type)
    },

    // 根据选择应用到 questionsList
    applyQuestionsByType() {
      if (this.selectedFeedbackType === 'good') {
        this.questionsList = [...(this.statsData.goodQuestions || [])]
      } else {
        this.questionsList = [...(this.statsData.notSatisfiedQuestions || [])]
      }
    },

    // 直接从记录接口拉取指定类型的问题列表（数据库反馈）
    async fetchQuestionsByType(type) {
      try {
        const url = `${this.apiBaseUrl}/api/v1/ai-feedback/records?skip=0&limit=100&feedback_type=${encodeURIComponent(type)}`
        const res = await fetch(url)
        if (!res.ok) {
          const txt = await res.text()
          throw new Error(`HTTP ${res.status}: ${txt}`)
        }
        const result = await res.json()
        if (result?.code === 200) {
          const list = Array.isArray(result.data) ? result.data : []
          this.questionsList = list.map(item => ({
            id: item.id,
            comment_id: item.comment_id,
            question: item.question,
            answer: item.answer,
            feedback_type: item.feedback_type,
            created_at: item.created_at
          }))
          // 为缺少answer的项按comment_id补齐
          await this.hydrateAnswersForQuestions()
        } else {
          this.questionsList = []
        }
      } catch (e) {
        console.error('获取问题列表失败:', e)
        this.questionsList = []
      }
    },

    // 批量为差评问题补充 answer 预览
    async hydrateAnswersForQuestions() {
      try {
        const list = this.questionsList || []
        const tasks = list.map(async (q) => {
          if (!q || !q.comment_id || q.answer) return
          const url = `${this.apiBaseUrl}/api/v1/ai-feedback/records?skip=0&limit=1&comment_id=${encodeURIComponent(q.comment_id)}`
          const res = await fetch(url)
          if (!res.ok) return
          const result = await res.json()
          if (result?.code === 200) {
            const data = result.data
            let a = ''
            if (Array.isArray(data) && data.length) {
              const item = data[0]
              a = item.answer || item.content || item.text || ''
            } else if (data && typeof data === 'object') {
              a = data.answer || data.content || data.text || ''
            }
            if (a) q.answer = a
          }
        })
        await Promise.allSettled(tasks)
      } catch (e) {
        console.warn('为问题加载答案预览失败:', e)
      }
    },

    // 简短展示
    truncate(text, len = 120) {
      if (!text) return ''
      return text.length > len ? `${text.slice(0, len)}...` : text
    },

    getMockStats() {
      return {
        goodCount: 15,
        notSatisfiedCount: 3,
        totalCount: 18,
        notSatisfiedQuestions: [
          {
            id: 1,
            comment_id: 101,
            question: "如何学习编程？",
            created_at: "2024-01-15T11:45:00Z"
          },
          {
            id: 2,
            comment_id: 103,
            question: "Python和JavaScript有什么区别？",
            created_at: "2024-01-15T14:20:00Z"
          },
          {
            id: 3,
            comment_id: 105,
            question: "机器学习算法有哪些？",
            created_at: "2024-01-15T16:30:00Z"
          }
        ]
      }
    },

    closeHistoryDialog() {
      this.showHistoryDialog = false
      // 图表功能已隐藏，不销毁图表
      // this.destroyCharts()
      // 停止自动刷新
      this.stopAutoRefresh()
    },

    // 刷新统计数据
    async refreshStats() {
      this.loadingStats = true
      try {
        await this.fetchHistoryStats()
        // 图表功能已隐藏，不更新图表
        // this.updateCharts()
      } catch (error) {
        console.error('刷新统计数据失败:', error)
        alert('刷新失败，请稍后重试')
      } finally {
        this.loadingStats = false
      }
    },

    

    // 启动自动刷新
    startAutoRefresh() {
      // 每30秒自动刷新一次数据
      this.refreshTimer = setInterval(async () => {
        try {
          await this.fetchHistoryStats()
          // 图表功能已隐藏，不更新图表
          // this.updateCharts()
        } catch (error) {
          console.error('自动刷新失败:', error)
        }
      }, 30000) // 30秒
    },



    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer)
        this.refreshTimer = null
      }
    },

    exitChat() {
      // 重置聊天状态，返回到初始界面
      this.chatStarted = false
      this.sessionId = null
      this.messages = []
      this.inputMessage = ''
      this.isLoading = false
      this.isStarting = false
      this.showDialog = false
      this.showSearchDialog = false
      this.sessionName = ''
    },

    getFeedbackTypeText(type) {
      return type === 'good' ? '👍 好评' : '👎 差评'
    },

    formatTime(timeString) {
      const date = new Date(timeString)
      return date.toLocaleString('zh-CN')
    },
    
    async sendMessage() {
      if (!this.inputMessage.trim() || this.isLoading) return
      
      const userMessage = this.inputMessage.trim()
      this.inputMessage = ''
      
      // 添加用户消息
      this.messages.push({
        type: 'user',
        content: userMessage,
        time: this.getCurrentTime()
      })
      
      this.isLoading = true
      this.scrollToBottom()
      
      try {
        const response = await this.sendToAI(userMessage)
        const aiMessage = this.extractAIMessage(response)
        
        if (aiMessage && aiMessage !== '抱歉，我无法理解您的请求，请重新表述。') {
          // 提取comment_id
          const commentId = this.extractCommentId(response)
          this.messages.push({
            type: 'ai',
            content: aiMessage,
            time: this.getCurrentTime(),
            feedback: null,
            feedbackSubmitting: false,
            commentId: commentId
          })

        } else {
          this.messages.push({
            type: 'ai',
            content: '抱歉，我无法理解您的请求，请重新表述。',
            time: this.getCurrentTime()
          })
        }
      } catch (error) {
        console.error('发送消息失败:', error)
        this.messages.push({
          type: 'ai',
          content: '抱歉，我遇到了一些问题，请稍后重试。',
          time: this.getCurrentTime()
        })
      } finally {
        this.isLoading = false
        this.scrollToBottom()
      }
    },
    


    extractCommentId(response) {
      try {
              let commentId = null
      if (response?.data?.comment_id) commentId = response.data.comment_id
      else if (response?.comment_id) commentId = response.comment_id
      else if (Array.isArray(response?.messages)) {
        const last = response.messages[response.messages.length - 1]
        commentId = last?.comment_id || null
      }
        
        return commentId
      } catch (e) {
        console.warn('提取comment_id失败:', e)
        return null
      }
    },

    async handleFeedback(messageIndex, feedbackType) {
      const message = this.messages[messageIndex]
      if (!message || message.type !== 'ai') return
      
            const backendFeedbackType = feedbackType === 'like' ? 'good' : 'not satisfied'
      
      try {
        message.feedbackSubmitting = true
        
        if (message.commentId) {
          const updateUrl = `${this.apiBaseUrl}/api/v1/ai-feedback/${message.commentId}`
          const updateBody = { feedback_type: backendFeedbackType }
          

          
          const updateRes = await fetch(updateUrl, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${this.apiKey}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateBody)
          })
          
          if (updateRes.ok) {
            message.feedback = feedbackType
          } else {
            const txt = await updateRes.text()
            throw new Error(`更新反馈记录失败 HTTP ${updateRes.status}: ${txt}`)
          }
        } else {
          throw new Error('无法获取有效的comment_id')
        }
        
      } catch (err) {
        console.error('提交反馈失败:', err)
        alert('提交反馈失败，请稍后重试')
      } finally {
        message.feedbackSubmitting = false
      }
    },

    async copyAnswer(message) {
      try {
        const text = message?.content || ''
        if (!text) return
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text)
        } else {
          const textarea = document.createElement('textarea')
          textarea.value = text
          textarea.style.position = 'fixed'
          textarea.style.left = '-9999px'
          document.body.appendChild(textarea)
          textarea.focus()
          textarea.select()
          document.execCommand('copy')
          document.body.removeChild(textarea)
        }
        alert('已复制到剪贴板')
      } catch (e) {
        console.error('复制失败:', e)
        alert('复制失败，请手动选择文本复制')
      }
    },
    
    async sendToAI(question) {
      try {
        const response = await fetch(`${this.apiBaseUrl}/api/workbench/run-text`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: question,
            inputs: {},
            response_mode: 'blocking',
            user: this.userId
          })
        })
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }
        
        const result = await response.json()
        return result
      } catch (error) {
        console.error('AI对话接口调用失败:', error)
        throw error
      }
    },
    
    extractAIMessage(response) {
      // 尝试多种可能的响应结构
      const possiblePaths = [
        response?.data?.answer,
        response?.answer,
        response?.data?.content,
        response?.content,
        response?.data?.text,
        response?.text,
        response?.data?.response,
        response?.response,
        response?.result,
        response?.result?.answer,
        response?.result?.content
      ]
      
      // 检查messages数组
      if (response?.messages?.length > 0) {
        const lastMessage = response.messages[response.messages.length - 1]
        possiblePaths.push(
          lastMessage?.data?.answer,
          lastMessage?.content,
          lastMessage?.text
        )
      }
      
      const answer = possiblePaths.find(path => path && typeof path === 'string')
      return answer || '抱歉，我无法理解您的请求，请重新表述。'
    },
    
    getCurrentTime() {
      const now = new Date()
      return now.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.messagesContainer) {
          const container = this.$refs.messagesContainer
          // 使用平滑滚动
          container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
          })
        }
      })
    },
    
    // 处理鼠标滚轮事件
    handleWheel(event) {
      const container = this.$refs.messagesContainer
      if (container) {
        // 确保滚轮事件能正常传递到消息容器
        event.stopPropagation()
      }
    },
    
    // 重置聊天
    resetChat() {
      // 显示自定义确认弹窗
      this.showResetDialog = true
    },
    
    // 关闭重置确认弹窗
    closeResetDialog() {
      this.showResetDialog = false
    },
    
    // 确认重置聊天
    confirmReset() {
      // 清除所有消息
      this.messages = []
      
      // 清空输入框
      this.inputMessage = ''
      
      // 重置加载状态
      this.isLoading = false
      
      // 添加新的欢迎消息
      this.messages.push({
        type: 'ai',
        content: '您好！我是您的AI智能助手，有什么可以帮助您的吗？',
        time: this.getCurrentTime(),
        hideActions: true
      })
      
      // 关闭弹窗
      this.showResetDialog = false
      
      // 滚动到底部
      this.scrollToBottom()
      
      // 显示成功提示
      this.$nextTick(() => {
        // 聊天重置完成
      })
    },

    // 上传到标注平台
    async uploadToAnnotation(commentId) {
      try {
        // 找到对应的问题项并设置上传状态
        const question = this.questionsList.find(q => q.comment_id === commentId)
        if (question) {
          question.uploading = true
        }

        const response = await fetch(`${this.apiBaseUrl}/api/annotations/${commentId}/upload-to-dify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }

        const result = await response.json()
        
        if (result.code === 200) {
          alert('成功上传到标注平台！')
          // 上传成功处理
        } else {
          throw new Error(result.message || '上传失败')
        }
      } catch (error) {
        console.error('上传到标注平台失败:', error)
        alert(`上传失败: ${error.message}`)
      } finally {
        // 重置上传状态
        const question = this.questionsList.find(q => q.comment_id === commentId)
        if (question) {
          question.uploading = false
        }
      }
    }
  },
  mounted() {
    // 进入页面即显示欢迎语
    if (this.messages.length === 0) {
      this.messages.push({
        type: 'ai',
        content: '您好！我是您的AI智能助手，有什么可以帮助您的吗？',
        time: this.getCurrentTime(),
        hideActions: true
      })
    }
    
    // 确保滚动功能正常工作
    this.$nextTick(() => {
      this.scrollToBottom()
    })
  },
  beforeUnmount() {
    // 组件销毁前清理资源
    this.stopAutoRefresh()
  }
}
</script>

<style scoped>
.ai-chat-container {
  max-width: 900px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  position: relative;
  overflow: hidden;
}

.ai-chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
  z-index: 0;
}

.chat-header {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: white;
  padding: 25px;
  text-align: center;
  border-radius: 0 0 25px 25px;
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.chat-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: 600;
}

.chat-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}



/* 聊天界面样式 */
.chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  min-height: 0;
  position: relative;
  z-index: 1;
}

/* 初始界面样式 */
.initial-chat-interface {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.welcome-content {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 100%;
}

.welcome-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.welcome-content h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.welcome-content p {
  margin: 0;
  color: #666;
  font-size: 16px;
  line-height: 1.5;
}

.welcome-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
  justify-content: center;
}

/* 聊天头部 */
.chat-header-bar {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 18px 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.assistant-avatar {
  position: relative;
}

.avatar-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  animation: pulse 2s infinite;
}

.avatar-icon:hover {
  transform: scale(1.1);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 
      0 4px 15px rgba(102, 126, 234, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    box-shadow: 
      0 6px 25px rgba(102, 126, 234, 0.6),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
}

.online-indicator {
  position: absolute;
  bottom: 3px;
  right: 3px;
  width: 14px;
  height: 14px;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.4);
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.7; }
}

.assistant-details h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.assistant-details .status {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  text-shadow: 0 1px 5px rgba(0,0,0,0.2);
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.history-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
}

.history-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.history-btn:hover::before {
  left: 100%;
}

.history-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(0,0,0,0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.reset-btn {
  background: rgba(255, 193, 7, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.4);
  border-radius: 20px;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
}

.reset-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 193, 7, 0.2), transparent);
  transition: left 0.5s;
}

.reset-btn:hover::before {
  left: 100%;
}

.reset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(255, 193, 7, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 193, 7, 0.6);
  background: rgba(255, 193, 7, 0.3);
}

.toggle-input-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 18px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-input-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.status {
  font-size: 12px;
  color: #28a745;
  font-weight: 500;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 25px;
  background: transparent;
  position: relative;
  min-height: 0;
  max-height: calc(100vh - 200px);
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 85%;
  animation: messageSlideIn 0.4s ease-out;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
}

.message.user .avatar-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.message.ai .avatar-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 
    0 4px 15px rgba(240, 147, 251, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.message-content {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  padding: 15px 20px;
  border-radius: 20px;
  position: relative;
  max-width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.message.user .message-content {
  background: rgba(102, 126, 234, 0.3);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 
    0 8px 32px rgba(102, 126, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.message.ai .message-content {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  color: #333;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
  font-size: 15px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.message.user .message-text {
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.comment-id {
  margin-top: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  font-family: 'Courier New', monospace;
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
  display: inline-block;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.message.ai .comment-id {
  color: rgba(0, 0, 0, 0.6);
  background: rgba(0, 0, 0, 0.05);
}

/* AI消息操作条 */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.action-btn {
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  position: relative;
  overflow: hidden;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.3s;
}

.action-btn:hover::before {
  left: 100%;
}

.action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.action-btn.like.active { 
  border-color: rgba(40, 167, 69, 0.6); 
  color: #28a745; 
  background: rgba(40, 167, 69, 0.2);
  box-shadow: 0 0 15px rgba(40, 167, 69, 0.3);
}

.action-btn.dislike.active { 
  border-color: rgba(220, 53, 69, 0.6); 
  color: #dc3545; 
  background: rgba(220, 53, 69, 0.2);
  box-shadow: 0 0 15px rgba(220, 53, 69, 0.3);
}

.action-btn.similar { color: rgba(255, 255, 255, 0.7); }

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 12px 0;
}

.typing-indicator span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: typing 1.4s infinite ease-in-out;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.6;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 输入区域 */
.chat-input-container {
  padding: 20px 25px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 -2px 20px rgba(0,0,0,0.1);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-radius: 30px;
  padding: 12px 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 
    0 8px 32px rgba(102, 126, 234, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.attach-button {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 18px;
  cursor: pointer;
  padding: 10px;
  border-radius: 50%;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.attach-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 10px 15px;
  font-size: 15px;
  outline: none;
  color: white;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.chat-input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.send-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.send-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.send-button:hover::before {
  left: 100%;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 10px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  margin: 5px 0;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 5px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

.chat-messages::-webkit-scrollbar-thumb:active {
  background: rgba(255, 255, 255, 0.8);
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

/* 重置确认弹窗样式 */
.reset-dialog-content {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 0;
  max-width: 450px;
  width: 90%;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: slideIn 0.4s ease-out;
  overflow: hidden;
}

.reset-dialog-header {
  background: rgba(255, 193, 7, 0.2);
  padding: 25px 30px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 193, 7, 0.3);
}

.reset-icon {
  font-size: 40px;
  margin-bottom: 15px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.reset-dialog-header h3 {
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.reset-dialog-body {
  padding: 25px 30px;
}

.reset-warning {
  margin: 0 0 20px 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.reset-description {
  margin: 0 0 15px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.reset-list {
  margin: 0 0 20px 0;
  padding-left: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.6;
}

.reset-list li {
  margin-bottom: 8px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.reset-note {
  margin: 0;
  color: rgba(255, 193, 7, 0.9);
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.reset-dialog-buttons {
  display: flex;
  gap: 15px;
  padding: 20px 30px 25px;
  justify-content: center;
}

.reset-cancel-btn, .reset-confirm-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
  min-width: 100px;
}

.reset-cancel-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.reset-cancel-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.reset-confirm-btn {
  background: linear-gradient(135deg, #ffc107 0%, #ff8f00 100%);
  color: white;
  border: 1px solid rgba(255, 193, 7, 0.3);
  box-shadow: 
    0 4px 15px rgba(255, 193, 7, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.reset-confirm-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.reset-confirm-btn:hover::before {
  left: 100%;
}

.reset-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(255, 193, 7, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dialog-content {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 35px;
  border-radius: 20px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  max-width: 450px;
  width: 90%;
  text-align: center;
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dialog-content h3 {
  margin: 0 0 20px 0;
  color: white;
  font-size: 22px;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dialog-content p {
  margin: 0 0 25px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  text-shadow: 0 1px 5px rgba(0,0,0,0.2);
}

.session-name-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: all 0.3s ease;
  margin-bottom: 25px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.session-name-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.session-name-input:focus {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 
    0 0 20px rgba(102, 126, 234, 0.3),
    inset 0 0 20px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.15);
}

.dialog-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.cancel-btn, .confirm-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.confirm-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.confirm-btn:hover::before {
  left: 100%;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.refresh-btn {
  background: linear-gradient(135deg, #17a2b8 0%, #20c997 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  box-shadow: 
    0 4px 15px rgba(23, 162, 184, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.refresh-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.refresh-btn:hover::before {
  left: 100%;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 20px rgba(23, 162, 184, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.refresh-btn:active {
  transform: translateY(0);
}

/* 搜索记录弹窗样式 */
.search-dialog-content {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 35px;
  max-width: 650px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: slideIn 0.4s ease-out;
}

.search-dialog-content h3 {
  margin: 0 0 25px 0;
  color: white;
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.search-filters {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 15px 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.search-input:focus {
  border-color: rgba(102, 126, 234, 0.6);
  box-shadow: 
    0 0 20px rgba(102, 126, 234, 0.3),
    inset 0 0 20px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.15);
}

.records-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
}

.loading, .no-records {
  text-align: center;
  color: #666;
  padding: 40px 0;
  font-size: 14px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 
    0 4px 15px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.record-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
  box-shadow: 
    0 8px 25px rgba(0,0,0,0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-item .comment-id {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.feedback-type {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.feedback-type.good {
  background: rgba(40, 167, 69, 0.3);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.4);
}

.feedback-type.not\ satisfied {
  background: rgba(220, 53, 69, 0.3);
  color: #dc3545;
  border: 1px solid rgba(220, 53, 69, 0.4);
}

.record-question {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.5;
  margin-bottom: 10px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.record-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* 历史问题统计弹窗样式 */
.history-dialog-content {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 35px;
  max-width: 750px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: slideIn 0.4s ease-out;
}

.history-dialog-content h3 {
  margin: 0 0 25px 0;
  color: white;
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.stats-container {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-summary {
  display: flex;
  justify-content: space-around;
  gap: 25px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.stat-item {
  text-align: center;
  flex: 1;
  padding: 15px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-number {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 10px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.stat-item.good .stat-number {
  color: #28a745;
}

.stat-item.not-satisfied .stat-number {
  color: #dc3545;
}

.stat-item.total .stat-number {
  color: rgba(255, 255, 255, 0.9);
}

.stat-label {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

/* 图表区域样式 */
.charts-section {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.chart-container {
  text-align: center;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}

.chart-container h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.chart-container canvas {
  max-width: 100%;
  height: auto;
}

.stats-details h4 {
  margin: 0 0 20px 0;
  color: white;
  font-size: 18px;
  font-weight: 700;
  text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.detail-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(0,0,0,0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.question-text {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.5;
  margin-bottom: 15px;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.question-info {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-top: 10px;
}

.detail-item .comment-id {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 700;
  font-family: 'Courier New', monospace;
  background: rgba(0, 0, 0, 0.2);
  padding: 4px 8px;
  border-radius: 6px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.feedback-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.no-questions {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  padding: 50px 0;
  font-size: 15px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

/* 问题操作按钮样式 */
.question-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.annotation-btn {
  background: linear-gradient(135deg, #17a2b8 0%, #20c997 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
  box-shadow: 
    0 2px 8px rgba(23, 162, 184, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.annotation-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.3s;
}

.annotation-btn:hover::before {
  left: 100%;
}

.annotation-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 4px 12px rgba(23, 162, 184, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  background: linear-gradient(135deg, #138496 0%, #1e7e34 100%);
}

.annotation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  background: rgba(23, 162, 184, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-chat-container {
    height: 100vh;
    margin: 0;
    max-width: 100%;
  }
  
  .chat-header {
    border-radius: 0;
    padding: 20px 15px;
  }
  
  .chat-header h2 {
    font-size: 20px;
  }
  
  .chat-header p {
    font-size: 13px;
  }
  
  .chat-header-bar {
    padding: 15px 20px;
  }
  
  .assistant-details h3 {
    font-size: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 8px;
  }
  
  .reset-btn, .history-btn {
    font-size: 13px;
    padding: 8px 14px;
  }
  
  .message {
    max-width: 95%;
    gap: 12px;
  }
  
  .message-content {
    padding: 12px 16px;
  }
  
  .message-text {
    font-size: 14px;
  }
  
  .chat-input-container {
    padding: 15px 20px;
  }
  
  .input-wrapper {
    padding: 10px 15px;
  }
  
  .chat-input {
    font-size: 14px;
    padding: 8px 12px;
  }
  
  .send-button {
    width: 38px;
    height: 38px;
    font-size: 16px;
  }
  
  .attach-button {
    padding: 8px;
    font-size: 16px;
  }
  
  .dialog-content, .search-dialog-content, .history-dialog-content {
    padding: 25px 20px;
    margin: 20px;
  }
  
  .reset-dialog-content {
    margin: 20px;
    max-width: calc(100vw - 40px);
  }
  
  .reset-dialog-header {
    padding: 20px 25px 15px;
  }
  
  .reset-icon {
    font-size: 35px;
    margin-bottom: 12px;
  }
  
  .reset-dialog-header h3 {
    font-size: 18px;
  }
  
  .reset-dialog-body {
    padding: 20px 25px;
  }
  
  .reset-warning {
    font-size: 16px;
    margin-bottom: 15px;
  }
  
  .reset-dialog-buttons {
    flex-direction: column;
    gap: 12px;
    padding: 15px 25px 20px;
  }
  
  .reset-cancel-btn, .reset-confirm-btn {
    width: 100%;
    padding: 14px 20px;
  }
  
  .stats-summary {
    flex-direction: column;
    gap: 15px;
  }
  
  .stat-item {
    padding: 12px;
  }
  
  .stat-number {
    font-size: 28px;
  }
}
</style>
