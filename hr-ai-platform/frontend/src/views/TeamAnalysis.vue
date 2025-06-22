<template>
  <div class="team-analysis min-h-screen bg-cognitive-background">
    <!-- 頁面標題 -->
    <div class="bg-white shadow-cognitive-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="cognitive-hierarchy-1">
              團隊分析
            </h1>
            <p class="cognitive-hierarchy-4 mt-1">
              深入分析團隊動力、協作模式與整體效能
            </p>
          </div>
          <div class="flex space-x-3">
            <CognitiveButton 
              variant="secondary" 
              size="medium"
              @click="exportTeamReport"
            >
              <span class="mr-2">📊</span>
              匯出報告
            </CognitiveButton>
            <CognitiveButton 
              variant="primary" 
              size="medium"
              :is-loading="isAnalyzing"
              @click="startTeamAnalysis"
            >
              <span class="mr-2">🤝</span>
              開始團隊分析
            </CognitiveButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 團隊選擇區域 -->
      <div class="cognitive-card mb-8">
        <div class="cognitive-card-header">
          <h3 class="cognitive-hierarchy-3">選擇分析團隊</h3>
        </div>
        <div class="cognitive-card-body">
          <CognitiveForm @submit="handleTeamSelect">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="form-group">
                <label class="form-label required">部門團隊</label>
                <select v-model="selectedTeam" class="form-input">
                  <option value="">請選擇團隊</option>
                  <option 
                    v-for="team in teams" 
                    :key="team.id" 
                    :value="team.id"
                  >
                    {{ team.name }} ({{ team.memberCount }}人)
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">分析深度</label>
                <select v-model="analysisDepth" class="form-input">
                  <option value="basic">基礎分析</option>
                  <option value="standard">標準分析</option>
                  <option value="comprehensive">深度分析</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">分析週期</label>
                <select v-model="analysisPeriod" class="form-input">
                  <option value="1month">近1個月</option>
                  <option value="3months">近3個月</option>
                  <option value="6months">近6個月</option>
                  <option value="1year">近1年</option>
                </select>
              </div>
            </div>
            
            <template #actions>
              <CognitiveButton 
                type="submit" 
                variant="primary"
                :disabled="!selectedTeam"
              >
                載入團隊數據
              </CognitiveButton>
            </template>
          </CognitiveForm>
        </div>
      </div>

      <!-- 分析結果區域 -->
      <div v-if="currentTeamAnalysis" class="space-y-8">
        <!-- 團隊概覽 -->
        <div class="cognitive-card">
          <div class="cognitive-card-body">
            <div class="flex items-center justify-between mb-6">
              <div>
                <h2 class="cognitive-hierarchy-2">{{ currentTeamAnalysis.name }}</h2>
                <p class="cognitive-hierarchy-4 text-cognitive-neutral">
                  {{ currentTeamAnalysis.description }}
                </p>
              </div>
              <div class="text-right">
                <div class="text-3xl font-bold text-cognitive-primary">
                  {{ currentTeamAnalysis.overallScore }}
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">團隊評分</div>
              </div>
            </div>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="text-2xl font-bold text-gray-900">
                  {{ currentTeamAnalysis.memberCount }}
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">團隊成員</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-cognitive-success">
                  {{ currentTeamAnalysis.collaborationScore }}%
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">協作效率</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-cognitive-primary">
                  {{ currentTeamAnalysis.productivityScore }}%
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">生產力指數</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-cognitive-warning">
                  {{ currentTeamAnalysis.satisfactionScore }}%
                </div>
                <div class="text-cognitive-sm text-cognitive-neutral">滿意度</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 團隊動力和協作分析 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 協作網絡圖 -->
          <div class="cognitive-card">
            <div class="cognitive-card-header">
              <h3 class="cognitive-hierarchy-3">團隊協作網絡</h3>
            </div>
            <div class="cognitive-card-body">
              <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg mb-4">
                <div class="text-center">
                  <div class="text-4xl mb-2">🕸️</div>
                  <p class="text-cognitive-neutral">協作關係圖</p>
                  <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                    (D3.js 網絡圖)
                  </p>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div class="text-lg font-semibold text-cognitive-primary">
                    {{ currentTeamAnalysis.networkMetrics.density }}%
                  </div>
                  <div class="text-cognitive-sm text-cognitive-neutral">
                    網絡密度
                  </div>
                </div>
                <div>
                  <div class="text-lg font-semibold text-cognitive-success">
                    {{ currentTeamAnalysis.networkMetrics.centrality }}
                  </div>
                  <div class="text-cognitive-sm text-cognitive-neutral">
                    核心節點
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 技能互補分析 -->
          <div class="cognitive-card">
            <div class="cognitive-card-header">
              <h3 class="cognitive-hierarchy-3">技能互補分析</h3>
            </div>
            <div class="cognitive-card-body">
              <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg mb-4">
                <div class="text-center">
                  <div class="text-4xl mb-2">🧩</div>
                  <p class="text-cognitive-neutral">技能互補矩陣</p>
                  <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                    (熱力圖顯示)
                  </p>
                </div>
              </div>
              <div class="space-y-3">
                <div
                  v-for="skill in currentTeamAnalysis.skillGaps"
                  :key="skill.name"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <span class="text-cognitive-sm font-medium">{{ skill.name }}</span>
                  <div class="flex items-center space-x-2">
                    <span 
                      :class="skill.status === 'strong' ? 'text-cognitive-success' : 
                               skill.status === 'weak' ? 'text-cognitive-danger' : 'text-cognitive-warning'"
                      class="text-cognitive-sm"
                    >
                      {{ skill.coverage }}%
                    </span>
                    <span class="text-xs">
                      {{ skill.status === 'strong' ? '✅' : skill.status === 'weak' ? '❌' : '⚠️' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 團隊成員詳細分析 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">團隊成員表現</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="overflow-x-auto">
              <table class="min-w-full">
                <thead>
                  <tr class="border-b border-gray-200">
                    <th class="text-left py-3 px-4 font-medium text-gray-900">成員</th>
                    <th class="text-left py-3 px-4 font-medium text-gray-900">角色</th>
                    <th class="text-center py-3 px-4 font-medium text-gray-900">績效</th>
                    <th class="text-center py-3 px-4 font-medium text-gray-900">協作度</th>
                    <th class="text-center py-3 px-4 font-medium text-gray-900">影響力</th>
                    <th class="text-center py-3 px-4 font-medium text-gray-900">狀態</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="member in currentTeamAnalysis.members"
                    :key="member.id"
                    class="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td class="py-3 px-4">
                      <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 bg-cognitive-primary rounded-full flex items-center justify-center">
                          <span class="text-white text-sm">{{ getInitials(member.name) }}</span>
                        </div>
                        <span class="font-medium">{{ member.name }}</span>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-cognitive-sm text-cognitive-neutral">
                      {{ member.role }}
                    </td>
                    <td class="py-3 px-4 text-center">
                      <div class="flex items-center justify-center">
                        <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            class="bg-cognitive-primary h-2 rounded-full"
                            :style="{ width: `${member.performance * 10}%` }"
                          ></div>
                        </div>
                        <span class="text-cognitive-sm">{{ member.performance }}/10</span>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span 
                        :class="member.collaboration >= 8 ? 'text-cognitive-success' : 
                                 member.collaboration >= 6 ? 'text-cognitive-warning' : 'text-cognitive-danger'"
                        class="font-medium"
                      >
                        {{ member.collaboration }}/10
                      </span>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <div class="flex items-center justify-center space-x-1">
                        <span
                          v-for="star in 5"
                          :key="star"
                          :class="star <= member.influence ? 'text-yellow-400' : 'text-gray-300'"
                        >
                          ⭐
                        </span>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-center">
                      <span
                        :class="{
                          'bg-cognitive-success text-white': member.status === 'excellent',
                          'bg-cognitive-primary text-white': member.status === 'good',
                          'bg-cognitive-warning text-white': member.status === 'average',
                          'bg-cognitive-danger text-white': member.status === 'needs_improvement'
                        }"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ getStatusText(member.status) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- AI 團隊洞察 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">AI 團隊洞察報告</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 class="font-semibold text-cognitive-success mb-3">🌟 團隊優勢</h4>
                <ul class="space-y-2">
                  <li 
                    v-for="strength in currentTeamAnalysis.insights.strengths"
                    :key="strength"
                    class="text-cognitive-sm text-gray-700 flex items-start"
                  >
                    <span class="text-cognitive-success mr-2">•</span>
                    {{ strength }}
                  </li>
                </ul>
              </div>
              <div>
                <h4 class="font-semibold text-cognitive-warning mb-3">⚠️ 風險識別</h4>
                <ul class="space-y-2">
                  <li 
                    v-for="risk in currentTeamAnalysis.insights.risks"
                    :key="risk"
                    class="text-cognitive-sm text-gray-700 flex items-start"
                  >
                    <span class="text-cognitive-warning mr-2">•</span>
                    {{ risk }}
                  </li>
                </ul>
              </div>
              <div>
                <h4 class="font-semibold text-cognitive-primary mb-3">🚀 優化建議</h4>
                <ul class="space-y-2">
                  <li 
                    v-for="suggestion in currentTeamAnalysis.insights.suggestions"
                    :key="suggestion"
                    class="text-cognitive-sm text-gray-700 flex items-start"
                  >
                    <span class="text-cognitive-primary mr-2">•</span>
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 class="font-semibold text-cognitive-primary mb-2">📋 行動計劃</h4>
              <div class="space-y-2">
                <div
                  v-for="(action, index) in currentTeamAnalysis.insights.actionPlan"
                  :key="index"
                  class="flex items-start space-x-3"
                >
                  <span class="flex-shrink-0 w-6 h-6 bg-cognitive-primary text-white rounded-full flex items-center justify-center text-xs">
                    {{ index + 1 }}
                  </span>
                  <div>
                    <p class="text-cognitive-sm font-medium text-gray-900">{{ action.title }}</p>
                    <p class="text-xs text-gray-600">{{ action.description }}</p>
                    <p class="text-xs text-cognitive-neutral mt-1">預計時間: {{ action.timeline }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">🤝</div>
        <h3 class="cognitive-hierarchy-3 text-cognitive-neutral mb-2">
          選擇團隊以開始分析
        </h3>
        <p class="text-cognitive-neutral">
          請從上方選擇要分析的團隊，系統將為您生成深度團隊分析報告
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import CognitiveButton from '@/components/cognitive/CognitiveButton.vue'
import CognitiveForm from '@/components/cognitive/CognitiveForm.vue'

// 應用狀態
const appStore = useAppStore()

// 組件狀態
const isAnalyzing = ref(false)
const selectedTeam = ref('')
const analysisDepth = ref('standard')
const analysisPeriod = ref('3months')
const currentTeamAnalysis = ref(null)

// 模擬團隊數據
const teams = ref([
  { id: '1', name: '前端開發團隊', memberCount: 8, department: '研發部' },
  { id: '2', name: '後端開發團隊', memberCount: 6, department: '研發部' },  
  { id: '3', name: '產品設計團隊', memberCount: 5, department: '設計部' },
  { id: '4', name: '數據分析團隊', memberCount: 4, department: '數據部' },
  { id: '5', name: '營運支援團隊', memberCount: 7, department: '營運部' }
])

// 處理團隊選擇
const handleTeamSelect = (event: Event) => {
  if (!selectedTeam.value) return
  
  isAnalyzing.value = true
  appStore.showInfo('團隊分析中', '正在載入團隊數據並進行深度分析...')
  
  // 模擬API調用
  setTimeout(() => {
    loadTeamAnalysis(selectedTeam.value)
    isAnalyzing.value = false
    appStore.showSuccess('團隊分析完成', '團隊深度分析報告已生成')
  }, 3000)
}

// 載入團隊分析數據
const loadTeamAnalysis = (teamId: string) => {
  const team = teams.value.find(t => t.id === teamId)
  if (!team) return
  
  // 模擬團隊分析數據
  currentTeamAnalysis.value = {
    id: team.id,
    name: team.name,
    description: `${team.department}的核心團隊，負責產品研發和技術創新`,
    memberCount: team.memberCount,
    overallScore: '8.4',
    collaborationScore: 89,
    productivityScore: 85,
    satisfactionScore: 92,
    networkMetrics: {
      density: 76,
      centrality: 3
    },
    skillGaps: [
      { name: '前端技術', coverage: 95, status: 'strong' },
      { name: '後端開發', coverage: 88, status: 'strong' },
      { name: '系統設計', coverage: 72, status: 'average' },
      { name: '項目管理', coverage: 65, status: 'average' },
      { name: '數據分析', coverage: 45, status: 'weak' }
    ],
    members: [
      {
        id: '1',
        name: '張小明',
        role: '技術主管',
        performance: 9.2,
        collaboration: 8.8,
        influence: 5,
        status: 'excellent'
      },
      {
        id: '2', 
        name: '李小華',
        role: '資深工程師',
        performance: 8.6,
        collaboration: 9.1,
        influence: 4,
        status: 'excellent'
      },
      {
        id: '3',
        name: '王小美',
        role: '前端工程師',
        performance: 8.2,
        collaboration: 7.9,
        influence: 3,
        status: 'good'
      },
      {
        id: '4',
        name: '陳小強',
        role: '後端工程師',
        performance: 7.8,
        collaboration: 8.3,
        influence: 3,
        status: 'good'
      },
      {
        id: '5',
        name: '林小莉',
        role: '初級工程師',
        performance: 6.9,
        collaboration: 7.2,
        influence: 2,
        status: 'average'
      }
    ],
    insights: {
      strengths: [
        '團隊技術實力強，核心成員經驗豐富',
        '協作氛圍良好，溝通效率高',
        '學習能力強，能快速適應新技術',
        '項目交付質量穩定'
      ],
      risks: [
        '技術主管工作負荷過重，存在單點風險',
        '初級成員成長速度需要提升',
        '跨團隊協作經驗相對不足'
      ],
      suggestions: [
        '建立技術導師制度，加速初級成員成長',
        '增加跨部門協作項目機會',
        '定期進行技術分享和知識傳承',
        '優化工作分配，避免關鍵人員過度依賴'
      ],
      actionPlan: [
        {
          title: '建立導師制度',
          description: '為初級成員安排經驗豐富的導師，制定個人發展計劃',
          timeline: '2-3週'
        },
        {
          title: '技術知識分享',
          description: '每週安排技術分享會，促進知識交流和團隊學習',
          timeline: '持續進行'
        },
        {
          title: '跨團隊協作',
          description: '安排與其他團隊的聯合項目，拓展協作經驗',
          timeline: '1-2個月'
        }
      ]
    }
  }
}

// 開始團隊分析
const startTeamAnalysis = () => {
  selectedTeam.value = ''
  currentTeamAnalysis.value = null
  appStore.showInfo('準備分析', '請選擇要分析的團隊')
}

// 匯出團隊報告
const exportTeamReport = () => {
  appStore.showInfo('功能開發中', '團隊報告匯出功能將在下個版本提供')
}

// 獲取姓名縮寫
const getInitials = (name: string) => {
  return name.slice(0, 2)
}

// 獲取狀態文字
const getStatusText = (status: string) => {
  const statusMap = {
    excellent: '優秀',
    good: '良好', 
    average: '一般',
    needs_improvement: '待改進'
  }
  return statusMap[status] || status
}

// 初始化
onMounted(() => {
  appStore.showInfo('團隊分析模塊載入完成', '可以開始選擇團隊進行深度分析')
})
</script>

<style scoped>
.team-analysis {
  /* 團隊分析特定樣式 */
}

/* 表格響應式 */
@media (max-width: 768px) {
  .overflow-x-auto table {
    font-size: 0.875rem;
  }
  
  .overflow-x-auto th,
  .overflow-x-auto td {
    padding: 0.5rem 0.25rem;
  }
}

/* 成員卡片動畫 */
.cognitive-card tbody tr {
  transition: background-color 0.2s ease;
}
</style>