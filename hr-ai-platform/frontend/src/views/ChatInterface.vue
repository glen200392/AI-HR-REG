<template>
  <div class="chat-interface h-screen bg-gray-50 flex">
    <!-- 側邊欄 -->
    <div class="sidebar w-80 bg-white border-r border-gray-200 flex flex-col">
      <!-- 系統狀態 -->
      <div class="status-panel p-4 border-b border-gray-100">
        <div class="flex items-center mb-3">
          <div class="w-3 h-3 rounded-full mr-2" :class="systemStatusColor"></div>
          <span class="text-sm font-medium text-gray-700">{{ systemStatus }}</span>
        </div>
        <div class="text-xs text-gray-500">
          模型: {{ currentModel }}
        </div>
        <div class="text-xs text-gray-500">
          文件: {{ documentCount }} 個
        </div>
      </div>

      <!-- 對話歷史 -->
      <div class="chat-history flex-1 overflow-y-auto">
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-gray-700">對話記錄</h3>
            <button 
              @click="startNewChat"
              class="text-xs text-blue-600 hover:text-blue-800"
            >
              新對話
            </button>
          </div>
          
          <div class="space-y-2">
            <div 
              v-for="session in chatSessions" 
              :key="session.id"
              @click="selectChatSession(session.id)"
              class="p-3 rounded-lg cursor-pointer transition-colors"
              :class="{
                'bg-blue-50 border-blue-200 border': session.id === activeChatId,
                'hover:bg-gray-50': session.id !== activeChatId
              }"
            >
              <div class="text-sm font-medium text-gray-800 truncate">
                {{ session.title || '新對話' }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ formatDate(session.last_activity) }}
              </div>
              <div class="text-xs text-gray-400">
                {{ session.message_count }} 條消息
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件管理 -->
      <div class="document-panel p-4 border-t border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold text-gray-700">文件管理</h3>
          <button 
            @click="openFileUpload"
            class="text-xs text-green-600 hover:text-green-800"
          >
            上傳
          </button>
        </div>
        
        <div class="space-y-2 max-h-32 overflow-y-auto">
          <div 
            v-for="doc in recentDocuments" 
            :key="doc.id"
            class="p-2 bg-gray-50 rounded text-xs"
          >
            <div class="font-medium text-gray-700 truncate">{{ doc.filename }}</div>
            <div class="text-gray-500 flex items-center justify-between">
              <span>{{ doc.status }}</span>
              <span>{{ formatFileSize(doc.file_size) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主聊天區域 -->
    <div class="chat-main flex-1 flex flex-col">
      <!-- 聊天標題欄 -->
      <div class="chat-header p-4 bg-white border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-gray-800">
              HR智能知識助手
            </h2>
            <p class="text-sm text-gray-500">
              基於 {{ currentModel }} • {{ queryComplexity }} 複雜度
            </p>
          </div>
          <div class="flex space-x-2">
            <button 
              @click="clearChat"
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded"
            >
              清空對話
            </button>
            <button 
              @click="openSettings"
              class="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded"
            >
              ⚙️ 設定
            </button>
          </div>
        </div>
      </div>

      <!-- 消息區域 -->
      <div class="messages-area flex-1 overflow-y-auto p-4 space-y-4">
        <!-- 歡迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message text-center py-12">
          <div class="text-6xl mb-4">🤖</div>
          <h3 class="text-xl font-semibold text-gray-700 mb-2">
            歡迎使用HR智能知識助手
          </h3>
          <p class="text-gray-500 mb-6">
            我可以幫您解答人力資源相關問題，分析政策文件，提供專業建議。
          </p>
          <div class="flex flex-wrap justify-center gap-2">
            <button 
              v-for="suggestion in quickSuggestions"
              :key="suggestion"
              @click="sendSuggestion(suggestion)"
              class="px-4 py-2 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <!-- 聊天消息 -->
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="message-group"
        >
          <!-- 用戶消息 -->
          <div class="user-message mb-4">
            <div class="flex justify-end">
              <div class="max-w-xs lg:max-w-md px-4 py-2 bg-blue-600 text-white rounded-lg">
                {{ message.user_message }}
              </div>
            </div>
            <div class="text-right text-xs text-gray-400 mt-1">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>

          <!-- AI回答 -->
          <div class="ai-message mb-4">
            <div class="flex items-start space-x-3">
              <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                🤖
              </div>
              <div class="flex-1">
                <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <div class="prose prose-sm max-w-none">
                    <div v-html="formatMessage(message.ai_response)"></div>
                  </div>
                  
                  <!-- 來源文件 -->
                  <div v-if="message.source_documents && message.source_documents.length > 0" 
                       class="mt-3 pt-3 border-t border-gray-100">
                    <div class="text-xs text-gray-500 mb-2">📄 參考文件:</div>
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="doc in message.source_documents" 
                        :key="doc"
                        class="px-2 py-1 bg-gray-100 text-xs text-gray-600 rounded"
                      >
                        {{ doc }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- 響應時間和信心分數 -->
                  <div class="flex items-center justify-between mt-3 pt-2 border-t border-gray-100 text-xs text-gray-400">
                    <span>響應時間: {{ message.response_time?.toFixed(2) }}s</span>
                    <span v-if="message.confidence_score">
                      信心度: {{ (message.confidence_score * 100).toFixed(0) }}%
                    </span>
                    <span>模型: {{ message.model_used || currentModel }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 載入指示器 -->
        <div v-if="isLoading" class="loading-indicator flex items-start space-x-3">
          <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            🤖
          </div>
          <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div class="flex items-center space-x-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span class="text-sm text-gray-600">{{ loadingMessage }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 輸入區域 -->
      <div class="input-area p-4 bg-white border-t border-gray-200">
        <!-- 查詢分析顯示 -->
        <div v-if="queryAnalysis" class="mb-3 p-2 bg-gray-50 rounded-lg text-xs">
          <div class="flex items-center justify-between">
            <span class="text-gray-600">
              複雜度: <span class="font-medium">{{ queryAnalysis.complexity }}</span>
            </span>
            <span class="text-gray-600">
              建議片段: {{ queryAnalysis.suggested_chunks }} 個
            </span>
          </div>
          <div v-if="queryAnalysis.topics.length > 0" class="mt-1">
            <span class="text-gray-500">主題: </span>
            <span class="text-gray-700">{{ queryAnalysis.topics.join(', ') }}</span>
          </div>
        </div>

        <div class="flex items-end space-x-3">
          <div class="flex-1">
            <textarea
              v-model="userInput"
              @keydown.enter.exact="handleEnterKey"
              @input="analyzeQuery"
              :disabled="isLoading"
              placeholder="請輸入您的HR問題..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="1"
              style="min-height: 44px; max-height: 120px;"
            ></textarea>
          </div>
          <button
            @click="sendMessage"
            :disabled="!userInput.trim() || isLoading"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            發送
          </button>
        </div>
        
        <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>按 Enter 發送，Shift+Enter 換行</span>
          <span v-if="userInput.length > 0">{{ userInput.length }} 字符</span>
        </div>
      </div>
    </div>

    <!-- 文件上傳對話框 -->
    <div v-if="showFileUpload" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-semibold mb-4">上傳文件</h3>
        <div 
          @drop="handleFileDrop"
          @dragover.prevent
          @dragenter.prevent
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
        >
          <div class="text-4xl mb-2">📄</div>
          <p class="text-gray-600 mb-2">拖拽文件到此處或點擊上傳</p>
          <input 
            ref="fileInput"
            type="file" 
            multiple 
            accept=".pdf,.doc,.docx,.txt"
            @change="handleFileSelect"
            class="hidden"
          >
          <button 
            @click="$refs.fileInput.click()"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            選擇文件
          </button>
        </div>
        <div class="flex justify-end space-x-2 mt-4">
          <button 
            @click="showFileUpload = false"
            class="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useCognitive } from '../composables/useCognitive'
import apiService from '../services/api'

// 響應式數據
const userInput = ref('')
const messages = ref([])
const isLoading = ref(false)
const loadingMessage = ref('正在思考中...')
const showFileUpload = ref(false)
const queryAnalysis = ref(null)

// 系統狀態
const systemStatus = ref('已就緒')
const currentModel = ref('Qwen2.5:14B')
const documentCount = ref(0)
const queryComplexity = ref('中等')

// 聊天會話
const chatSessions = ref([])
const activeChatId = ref(null)
const recentDocuments = ref([])

// 認知設計 composable
const { trackAttention, monitorCognitiveLoad } = useCognitive()

// 快速建議
const quickSuggestions = [
  '年假有幾天？',
  '如何處理員工遲到？',
  '績效考核流程是什麼？',
  '勞基法加班規定',
  '員工離職手續'
]

// 計算屬性
const systemStatusColor = computed(() => {
  switch (systemStatus.value) {
    case '已就緒': return 'bg-green-500'
    case '處理中': return 'bg-yellow-500'
    case '錯誤': return 'bg-red-500'
    default: return 'bg-gray-500'
  }
})

// 方法
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  queryAnalysis.value = null
  
  // 添加用戶消息
  messages.value.push({
    user_message: message,
    timestamp: new Date(),
    ai_response: '',
    response_time: 0,
    source_documents: [],
    model_used: currentModel.value
  })
  
  isLoading.value = true
  loadingMessage.value = '正在分析問題...'
  
  try {
    // 追蹤認知負荷
    trackAttention('query_sent')
    
    // 調用API
    const response = await apiService.query(message)
    
    if (response.success) {
      // 更新最後一條消息
      const lastMessage = messages.value[messages.value.length - 1]
      lastMessage.ai_response = response.data.answer
      lastMessage.response_time = response.data.response_time
      lastMessage.source_documents = response.data.source_documents
      lastMessage.confidence_score = response.data.confidence_score
      
      // 更新複雜度
      queryComplexity.value = response.data.complexity || '中等'
    } else {
      throw new Error(response.error || '查詢失敗')
    }
  } catch (error) {
    console.error('查詢錯誤:', error)
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.ai_response = `抱歉，查詢過程中發生錯誤：${error.message}`
    lastMessage.response_time = 0
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const sendSuggestion = (suggestion: string) => {
  userInput.value = suggestion
  sendMessage()
}

const analyzeQuery = async () => {
  if (!userInput.value.trim()) {
    queryAnalysis.value = null
    return
  }
  
  try {
    const response = await apiService.analyzeQuery(userInput.value)
    if (response.success) {
      queryAnalysis.value = response.data
    }
  } catch (error) {
    console.warn('查詢分析失敗:', error)
  }
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (!event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const clearChat = () => {
  messages.value = []
  queryAnalysis.value = null
}

const startNewChat = () => {
  clearChat()
  activeChatId.value = null
}

const selectChatSession = (sessionId: string) => {
  activeChatId.value = sessionId
  // TODO: 載入聊天記錄
}

const openFileUpload = () => {
  showFileUpload.value = true
}

const openSettings = () => {
  // TODO: 開啟設定對話框
}

const handleFileSelect = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

const handleFileDrop = (event: DragEvent) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (files) {
    uploadFiles(Array.from(files))
  }
}

const uploadFiles = async (files: File[]) => {
  showFileUpload.value = false
  
  for (const file of files) {
    try {
      loadingMessage.value = `正在上傳 ${file.name}...`
      isLoading.value = true
      
      const response = await apiService.uploadDocument(file)
      if (response.success) {
        recentDocuments.value.unshift(response.data)
        documentCount.value++
      }
    } catch (error) {
      console.error('文件上傳失敗:', error)
    } finally {
      isLoading.value = false
    }
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    const messagesArea = document.querySelector('.messages-area')
    if (messagesArea) {
      messagesArea.scrollTop = messagesArea.scrollHeight
    }
  })
}

const formatMessage = (message: string) => {
  // 簡單的Markdown渲染
  return message
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatDate = (date: string | Date) => {
  const d = new Date(date)
  const now = new Date()
  const diffInHours = (now.getTime() - d.getTime()) / (1000 * 60 * 60)
  
  if (diffInHours < 24) {
    return d.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
  } else {
    return d.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' })
  }
}

const formatTime = (date: string | Date) => {
  return new Date(date).toLocaleTimeString('zh-TW', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 生命週期
onMounted(async () => {
  // 初始化系統狀態
  try {
    const statusResponse = await apiService.getSystemStatus()
    if (statusResponse.success) {
      systemStatus.value = statusResponse.data.status
      currentModel.value = statusResponse.data.current_model
      documentCount.value = statusResponse.data.document_count
    }
  } catch (error) {
    console.warn('無法獲取系統狀態:', error)
    systemStatus.value = '離線模式'
  }
  
  // 載入聊天記錄
  try {
    const sessionsResponse = await apiService.getChatSessions()
    if (sessionsResponse.success) {
      chatSessions.value = sessionsResponse.data
    }
  } catch (error) {
    console.warn('無法載入聊天記錄:', error)
  }
  
  // 載入最近文件
  try {
    const documentsResponse = await apiService.getRecentDocuments()
    if (documentsResponse.success) {
      recentDocuments.value = documentsResponse.data
    }
  } catch (error) {
    console.warn('無法載入文件列表:', error)
  }
  
  // 監控認知負荷
  monitorCognitiveLoad()
})
</script>

<style scoped>
.chat-interface {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.messages-area {
  scroll-behavior: smooth;
}

.prose {
  line-height: 1.6;
}

.sidebar {
  min-width: 320px;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    max-width: 300px;
  }
}

/* 自定義滾動條 */
.messages-area::-webkit-scrollbar,
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track,
.chat-history::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-area::-webkit-scrollbar-thumb,
.chat-history::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb:hover,
.chat-history::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 載入動畫 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 響應式設計 */
@media (max-width: 1024px) {
  .chat-interface {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
}
</style>