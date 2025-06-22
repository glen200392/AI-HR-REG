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

// 應用狀態
const appStore = useAppStore()

// 組件狀態
const isAnalyzing = ref(false)
const selectedEmployee = ref('')
const analysisType = ref('comprehensive')
const timeRange = ref('6months')
const currentAnalysis = ref(null)

// 模擬員工數據
const employees = ref([
  { id: '1', name: '張小明', position: '前端工程師', department: '研發部' },
  { id: '2', name: '李小華', position: '產品經理', department: '產品部' },
  { id: '3', name: '王小美', position: 'UI設計師', department: '設計部' },
  { id: '4', name: '陳小強', position: '後端工程師', department: '研發部' },
  { id: '5', name: '林小莉', position: '數據分析師', department: '數據部' }
])

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

// 處理員工選擇
const handleEmployeeSelect = (event: Event) => {
  if (!selectedEmployee.value) return
  
  isAnalyzing.value = true
  appStore.showInfo('開始分析', '正在載入員工數據並進行AI分析...')
  
  // 模擬API調用
  setTimeout(() => {
    loadEmployeeAnalysis(selectedEmployee.value)
    isAnalyzing.value = false
    appStore.showSuccess('分析完成', '員工分析報告已生成')
  }, 2000)
}

// 載入員工分析數據
const loadEmployeeAnalysis = (employeeId: string) => {
  const employee = employees.value.find(e => e.id === employeeId)
  if (!employee) return
  
  // 模擬分析數據
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
    }
  }
}

// 開始新分析
const startAnalysis = () => {
  // 重置選擇
  selectedEmployee.value = ''
  currentAnalysis.value = null
  appStore.showInfo('準備開始', '請選擇要分析的員工')
}

// 切換分析歷史
const toggleAnalysisHistory = () => {
  appStore.showInfo('功能開發中', '分析歷史功能將在下個版本提供')
}

// 獲取姓名縮寫
const getInitials = (name: string) => {
  return name.slice(0, 2)
}

// 初始化
onMounted(() => {
  appStore.showInfo('個人分析模塊載入完成', '可以開始選擇員工進行分析')
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