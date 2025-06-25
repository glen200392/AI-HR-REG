<template>
  <div class="employee-analysis min-h-screen bg-cognitive-background">
    <!-- 頁面標題 -->
    <div class="bg-white shadow-cognitive-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="cognitive-hierarchy-1">
              個人分析
            </h1>
            <p class="cognitive-hierarchy-4 mt-1">
              深度分析個別員工的能力、績效與發展潛力
            </p>
          </div>
          <div class="flex space-x-3">
            <CognitiveButton 
              variant="secondary" 
              size="medium"
              @click="toggleAnalysisHistory"
            >
              <span class="mr-2">📋</span>
              歷史記錄
            </CognitiveButton>
            <CognitiveButton 
              variant="primary" 
              size="medium"
              :is-loading="isAnalyzing"
              @click="startAnalysis"
            >
              <span class="mr-2">🔍</span>
              開始新分析
            </CognitiveButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 員工選擇區域 -->
      <div class="cognitive-card mb-8">
        <div class="cognitive-card-header">
          <h3 class="cognitive-hierarchy-3">選擇分析對象</h3>
        </div>
        <div class="cognitive-card-body">
          <CognitiveForm @submit="handleEmployeeSelect">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="form-group">
                <label class="form-label required">員工姓名</label>
                <select v-model="selectedEmployee" class="form-input">
                  <option value="">請選擇員工</option>
                  <option 
                    v-for="employee in employees" 
                    :key="employee.id" 
                    :value="employee.id"
                  >
                    {{ employee.name }} - {{ employee.position }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">分析類型</label>
                <select v-model="analysisType" class="form-input">
                  <option value="comprehensive">綜合分析</option>
                  <option value="performance">績效分析</option>
                  <option value="skills">技能評估</option>
                  <option value="potential">潛力評估</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">時間範圍</label>
                <select v-model="timeRange" class="form-input">
                  <option value="3months">近3個月</option>
                  <option value="6months">近6個月</option>
                  <option value="1year">近1年</option>
                  <option value="all">全部時間</option>
                </select>
              </div>
            </div>
            
            <template #actions>
              <CognitiveButton 
                type="submit" 
                variant="primary"
                :disabled="!selectedEmployee"
              >
                載入分析資料
              </CognitiveButton>
            </template>
          </CognitiveForm>
        </div>
      </div>

      <!-- 分析結果區域 -->
      <div v-if="currentAnalysis" class="space-y-8">
        <!-- 員工基本資訊 -->
        <div class="cognitive-card">
          <div class="cognitive-card-body">
            <div class="flex items-center space-x-6">
              <div class="w-20 h-20 bg-cognitive-primary rounded-full flex items-center justify-center">
                <span class="text-white text-2xl">{{ getInitials(currentAnalysis.name) }}</span>
              </div>
              <div class="flex-1">
                <h2 class="cognitive-hierarchy-2">{{ currentAnalysis.name }}</h2>
                <p class="cognitive-hierarchy-4 text-cognitive-neutral">
                  {{ currentAnalysis.position }} • {{ currentAnalysis.department }}
                </p>
                <div class="flex items-center mt-2 space-x-4">
                  <span class="text-cognitive-sm text-cognitive-neutral">
                    入職時間: {{ currentAnalysis.joinDate }}
                  </span>
                  <span class="text-cognitive-sm text-cognitive-neutral">
                    工作年資: {{ currentAnalysis.experience }}年
                  </span>
                </div>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold text-cognitive-primary">
                  {{ currentAnalysis.overallScore }}
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">總體評分</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 核心指標 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="metric in coreMetrics"
            :key="metric.key"
            class="cognitive-card"
          >
            <div class="cognitive-card-body text-center">
              <div class="text-2xl mb-2">{{ metric.icon }}</div>
              <div class="text-2xl font-bold text-gray-900 mb-1">
                {{ metric.value }}
              </div>
              <div class="text-cognitive-sm text-cognitive-neutral mb-3">
                {{ metric.label }}
              </div>
              <div class="cognitive-progress">
                <div 
                  class="cognitive-progress-bar"
                  :style="{ width: `${metric.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 技能雷達圖和詳細分析 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 技能評估 -->
          <div class="cognitive-card">
            <div class="cognitive-card-header">
              <h3 class="cognitive-hierarchy-3">技能評估</h3>
            </div>
            <div class="cognitive-card-body">
              <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg mb-4">
                <div class="text-center">
                  <div class="text-4xl mb-2">🎯</div>
                  <p class="text-cognitive-neutral">技能雷達圖</p>
                  <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                    (整合圖表組件後顯示)
                  </p>
                </div>
              </div>
              <div class="space-y-3">
                <div
                  v-for="skill in currentAnalysis.skills"
                  :key="skill.name"
                  class="flex items-center justify-between"
                >
                  <span class="text-cognitive-sm font-medium">{{ skill.name }}</span>
                  <div class="flex items-center space-x-2">
                    <div class="w-20 bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-cognitive-primary h-2 rounded-full"
                        :style="{ width: `${skill.level * 20}%` }"
                      ></div>
                    </div>
                    <span class="text-cognitive-sm text-cognitive-neutral w-8">
                      {{ skill.level }}/5
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 績效趨勢 -->
          <div class="cognitive-card">
            <div class="cognitive-card-header">
              <h3 class="cognitive-hierarchy-3">績效趨勢</h3>
            </div>
            <div class="cognitive-card-body">
              <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg mb-4">
                <div class="text-center">
                  <div class="text-4xl mb-2">📈</div>
                  <p class="text-cognitive-neutral">績效趨勢圖</p>
                  <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                    (整合圖表組件後顯示)
                  </p>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center">
                  <div class="text-lg font-semibold text-cognitive-success">
                    {{ currentAnalysis.performanceTrend.improvement }}%
                  </div>
                  <div class="text-cognitive-sm text-cognitive-neutral">
                    績效提升
                  </div>
                </div>
                <div class="text-center">
                  <div class="text-lg font-semibold text-cognitive-primary">
                    {{ currentAnalysis.performanceTrend.consistency }}%
                  </div>
                  <div class="text-cognitive-sm text-cognitive-neutral">
                    表現一致性
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI 分析報告 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">AI 深度分析報告</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="font-semibold text-cognitive-success mb-3">✨ 優勢領域</h4>
                <ul class="space-y-2">
                  <li 
                    v-for="strength in currentAnalysis.aiInsights.strengths"
                    :key="strength"
                    class="text-cognitive-sm text-gray-700 flex items-start"
                  >
                    <span class="text-cognitive-success mr-2">•</span>
                    {{ strength }}
                  </li>
                </ul>
              </div>
              <div>
                <h4 class="font-semibold text-cognitive-warning mb-3">🎯 改進建議</h4>
                <ul class="space-y-2">
                  <li 
                    v-for="suggestion in currentAnalysis.aiInsights.improvements"
                    :key="suggestion"
                    class="text-cognitive-sm text-gray-700 flex items-start"
                  >
                    <span class="text-cognitive-warning mr-2">•</span>
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 class="font-semibold text-cognitive-primary mb-2">💡 發展建議</h4>
              <p class="text-cognitive-sm text-gray-700">
                {{ currentAnalysis.aiInsights.developmentPlan }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="cognitive-hierarchy-3 text-cognitive-neutral mb-2">
          選擇員工以開始分析
        </h3>
        <p class="text-cognitive-neutral">
          請從上方選擇要分析的員工，系統將為您生成詳細的分析報告
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import CognitiveButton from '@/components/cognitive/CognitiveButton.vue'
import CognitiveForm from '@/components/cognitive/CognitiveForm.vue'
import { apiService, type EmployeeAnalysisRequest } from '@/services/api'

// 應用狀態
const appStore = useAppStore()

// 組件狀態
const isAnalyzing = ref(false)
const isLoading = ref(false)
const selectedEmployee = ref('')
const analysisType = ref<'comprehensive' | 'performance' | 'skills' | 'potential'>('comprehensive')
const timeRange = ref<'3months' | '6months' | '1year' | 'all'>('6months')
const currentAnalysis = ref<any>(null)
const apiConnected = ref(false)

// 員工數據
const employees = ref<any[]>([])

// 核心指標計算
const coreMetrics = computed(() => {
  if (!currentAnalysis.value) return []
  
  const analysis = currentAnalysis.value
  return [
    {
      key: 'performance',
      label: '績效指標',
      value: analysis.performanceScore,
      percentage: (analysis.performanceScore / 10) * 100,
      icon: '🎯'
    },
    {
      key: 'skills',
      label: '技能水平',
      value: analysis.skillsScore,
      percentage: (analysis.skillsScore / 10) * 100,
      icon: '🛠️'
    },
    {
      key: 'potential',
      label: '發展潛力',
      value: analysis.potentialScore,
      percentage: (analysis.potentialScore / 10) * 100,
      icon: '🚀'
    }
  ]
})

// 載入員工列表
const loadEmployees = async () => {
  try {
    isLoading.value = true
    const result = await apiService.getEmployees()
    
    if (result.success && result.data) {
      employees.value = result.data
      console.log('✅ 員工列表載入成功:', employees.value.length)
    } else {
      throw new Error(result.error || '載入員工列表失敗')
    }
  } catch (error) {
    console.error('❌ 載入員工列表失敗:', error)
    appStore.showWarning('載入失敗', '無法載入員工列表，使用模擬數據')
    
    // 降級到模擬數據
    employees.value = [
      { id: '1', name: '張小明', position: '前端工程師', department: '研發部' },
      { id: '2', name: '李小華', position: '產品經理', department: '產品部' },
      { id: '3', name: '王小美', position: 'UI設計師', department: '設計部' },
      { id: '4', name: '陳小強', position: '後端工程師', department: '研發部' },
      { id: '5', name: '林小莉', position: '數據分析師', department: '數據部' }
    ]
  } finally {
    isLoading.value = false
  }
}

// 處理員工選擇 - 使用真實API
const handleEmployeeSelect = async (event: Event) => {
  if (!selectedEmployee.value) return
  
  isAnalyzing.value = true
  appStore.showInfo('開始AI分析', '正在使用人工智慧進行深度分析，請稍候...')
  
  try {
    // 準備分析參數
    const analysisParams: EmployeeAnalysisRequest = {
      analysisType: analysisType.value,
      timeRange: timeRange.value,
      recentPerformance: "持續穩定表現，近期項目完成度高",
      feedback: "同事評價積極，溝通協作能力強",
      projectContribution: "在團隊項目中貢獻突出，技術能力獲得認可"
    }

    console.log('🚀 開始AI分析:', selectedEmployee.value, analysisParams)

    // 調用真實的AI分析API
    const result = await apiService.analyzeEmployee(selectedEmployee.value, analysisParams)
    
    if (result.success && result.data) {
      // 轉換API響應為前端顯示格式
      currentAnalysis.value = transformAnalysisResult(result.data)
      
      const sourceText = result.data.metadata?.source === 'openai' ? 'OpenAI GPT-4' : 
                        result.data.metadata?.source === 'mock' ? '模擬AI' : 'AI分析'
      
      appStore.showSuccess('AI分析完成', `已使用${sourceText}生成智能分析報告`)
      
      console.log('✅ AI分析完成:', result.data.metadata)
    } else {
      throw new Error(result.error || '分析失敗')
    }
  } catch (error) {
    console.error('❌ AI分析失敗:', error)
    appStore.showError('分析失敗', apiService.handleAPIError(error))
    
    // 降級到模擬數據
    loadEmployeeAnalysisFallback(selectedEmployee.value)
  } finally {
    isAnalyzing.value = false
  }
}

// 轉換AI分析結果為前端格式
const transformAnalysisResult = (result: any) => {
  const { employee, analysis, metadata } = result
  
  return {
    id: employee.id,
    name: employee.name,
    position: employee.position,
    department: employee.department,
    joinDate: employee.joinDate || '2022-01-01',
    experience: employee.experience || 2,
    overallScore: analysis.overallScore?.toString() || '8.0',
    performanceScore: analysis.performanceScore || analysis.overallScore || 8.0,
    skillsScore: analysis.skillsScore || analysis.overallScore * 0.9 || 7.5,
    potentialScore: analysis.potentialScore || analysis.overallScore * 1.1 || 8.5,
    skills: employee.skills?.map((skill: string, index: number) => ({
      name: skill,
      level: Math.min(5, Math.max(1, Math.round((analysis.skillsScore || 8) * 0.6) + (index % 2)))
    })) || [
      { name: '專業技能', level: 4 },
      { name: '溝通協作', level: 4 },
      { name: '學習能力', level: 5 }
    ],
    performanceTrend: {
      improvement: Math.round(((analysis.performanceScore || analysis.overallScore) - 7) * 5),
      consistency: Math.round((analysis.performanceScore || analysis.overallScore) * 10)
    },
    aiInsights: {
      strengths: analysis.strengths || ["表現良好", "具備發展潛力"],
      improvements: analysis.improvements || ["持續學習", "加強專業技能"],
      developmentPlan: analysis.developmentPlan || "建議制定個人發展計劃，持續提升專業能力。"
    },
    metadata: {
      source: metadata?.source || 'unknown',
      analyzedAt: metadata?.analyzedAt || new Date().toISOString(),
      analysisId: metadata?.analysisId
    }
  }
}

// 降級到模擬數據的員工分析
const loadEmployeeAnalysisFallback = (employeeId: string) => {
  const employee = employees.value.find(e => e.id === employeeId)
  if (!employee) return
  
  currentAnalysis.value = {
    id: employee.id,
    name: employee.name,
    position: employee.position,
    department: employee.department,
    joinDate: '2022-03-15',
    experience: 3,
    overallScore: '8.6',
    performanceScore: 8.8,
    skillsScore: 8.2,
    potentialScore: 9.0,
    skills: [
      { name: 'JavaScript', level: 4 },
      { name: 'Vue.js', level: 5 },
      { name: '團隊協作', level: 4 },
      { name: '問題解決', level: 3 },
      { name: '學習能力', level: 5 }
    ],
    performanceTrend: {
      improvement: 15,
      consistency: 87
    },
    aiInsights: {
      strengths: [
        '技術學習能力強，能快速掌握新技術',
        '代碼質量高，注重細節和最佳實踐',
        '團隊協作積極，善於溝通和分享知識'
      ],
      improvements: [
        '可加強在複雜問題分析和系統設計方面的能力',
        '建議參與更多跨部門項目以拓展視野',
        '可考慮承擔技術導師角色，提升領導力'
      ],
      developmentPlan: '建議在接下來的6個月內，重點發展系統架構設計能力，同時可以考慮參與技術分享和團隊培訓，既能提升個人影響力，也能為團隊發展做出貢獻。'
    },
    metadata: {
      source: 'fallback',
      analyzedAt: new Date().toISOString()
    }
  }
  
  appStore.showInfo('使用模擬數據', '已生成模擬分析報告')
}

// 開始新分析
const startAnalysis = () => {
  selectedEmployee.value = ''
  currentAnalysis.value = null
  appStore.showInfo('準備開始', '請選擇要分析的員工')
}

// 查看分析歷史
const toggleAnalysisHistory = async () => {
  if (!selectedEmployee.value) {
    appStore.showWarning('請先選擇員工', '需要先選擇員工才能查看分析歷史')
    return
  }

  try {
    const result = await apiService.getEmployeeHistory(selectedEmployee.value, 5)
    if (result.success && result.data?.length > 0) {
      appStore.showSuccess('歷史記錄', `找到 ${result.data.length} 條分析記錄`)
      console.log('📚 分析歷史:', result.data)
    } else {
      appStore.showInfo('暫無歷史', '該員工暫無分析歷史記錄')
    }
  } catch (error) {
    console.error('❌ 獲取歷史失敗:', error)
    appStore.showError('載入失敗', '無法載入分析歷史')
  }
}

// 檢查API連接
const checkAPIConnection = async () => {
  try {
    apiConnected.value = await apiService.testConnection()
    if (apiConnected.value) {
      console.log('✅ 後端API連接正常')
    } else {
      console.warn('⚠️ 後端API連接失敗，將使用模擬數據')
    }
  } catch (error) {
    console.error('❌ API連接檢查失敗:', error)
    apiConnected.value = false
  }
}

// 獲取姓名縮寫
const getInitials = (name: string) => {
  return name.slice(0, 2)
}

// 初始化
onMounted(async () => {
  console.log('🚀 初始化員工分析模塊')
  
  // 檢查API連接
  await checkAPIConnection()
  
  // 載入員工列表
  await loadEmployees()
  
  const statusMessage = apiConnected.value 
    ? '個人分析模塊載入完成，AI功能已就緒' 
    : '個人分析模塊載入完成，使用模擬數據模式'
  
  appStore.showInfo('模塊就緒', statusMessage)
})
</script>

<style scoped>
.employee-analysis {
  /* 員工分析特定樣式 */
}

/* 分析卡片動畫 */
.cognitive-card {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>