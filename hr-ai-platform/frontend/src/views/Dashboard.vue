<template>
  <div class="dashboard min-h-screen bg-cognitive-background">
    <!-- 頁面標題 -->
    <div class="bg-white shadow-cognitive-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="cognitive-hierarchy-1">
              AI 人才分析儀表板
            </h1>
            <p class="cognitive-hierarchy-4 mt-1">
              綜合視圖：團隊績效與人才洞察
            </p>
          </div>
          <div class="flex space-x-3">
            <CognitiveButton variant="secondary" size="medium">
              <span class="mr-2">📊</span>
              匯出報告
            </CognitiveButton>
            <CognitiveButton variant="primary" size="medium">
              <span class="mr-2">🔍</span>
              開始分析
            </CognitiveButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 快速統計卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div
          v-for="(stat, index) in quickStats"
          :key="index"
          class="cognitive-card hover:shadow-cognitive-md transition-shadow duration-200"
        >
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center"
                  :class="stat.bgColor"
                >
                  <span class="text-white text-lg">{{ stat.icon }}</span>
                </div>
              </div>
              <div class="ml-4">
                <p class="text-cognitive-sm text-cognitive-neutral">{{ stat.label }}</p>
                <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
              </div>
            </div>
            <div class="mt-4">
              <div class="flex items-center text-cognitive-sm">
                <span
                  :class="stat.trend > 0 ? 'text-cognitive-success' : 'text-cognitive-danger'"
                  class="flex items-center"
                >
                  <span class="mr-1">{{ stat.trend > 0 ? '↗' : '↘' }}</span>
                  {{ Math.abs(stat.trend) }}%
                </span>
                <span class="text-cognitive-neutral ml-1">較上月</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要圖表區域 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- 團隊績效趨勢 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">團隊績效趨勢</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="text-4xl mb-2">📈</div>
                <p class="text-cognitive-neutral">績效趨勢圖表</p>
                <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                  (整合 Chart.js 後顯示)
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 人才技能分佈 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">人才技能分佈</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div class="text-center">
                <div class="text-4xl mb-2">🎯</div>
                <p class="text-cognitive-neutral">技能雷達圖</p>
                <p class="text-cognitive-sm text-cognitive-neutral mt-1">
                  (整合 Chart.js 後顯示)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 近期活動和建議 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- 近期活動 -->
        <div class="lg:col-span-2 cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">近期分析活動</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="space-y-4">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors duration-200"
              >
                <div
                  class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
                  :class="activity.bgColor"
                >
                  <span class="text-white text-sm">{{ activity.icon }}</span>
                </div>
                <div class="flex-1">
                  <p class="text-cognitive-sm font-medium text-gray-900">
                    {{ activity.title }}
                  </p>
                  <p class="text-cognitive-sm text-cognitive-neutral">
                    {{ activity.description }}
                  </p>
                  <p class="text-xs text-cognitive-neutral mt-1">
                    {{ activity.timestamp }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI 建議 -->
        <div class="cognitive-card">
          <div class="cognitive-card-header">
            <h3 class="cognitive-hierarchy-3">AI 智能建議</h3>
          </div>
          <div class="cognitive-card-body">
            <div class="space-y-4">
              <div
                v-for="suggestion in aiSuggestions"
                :key="suggestion.id"
                class="p-3 border border-gray-200 rounded-lg hover:border-cognitive-primary transition-colors duration-200"
              >
                <div class="flex items-start space-x-2">
                  <span class="text-lg">{{ suggestion.icon }}</span>
                  <div class="flex-1">
                    <p class="text-cognitive-sm font-medium text-gray-900">
                      {{ suggestion.title }}
                    </p>
                    <p class="text-xs text-cognitive-neutral mt-1">
                      {{ suggestion.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import CognitiveButton from '@/components/cognitive/CognitiveButton.vue'

// 應用狀態
const appStore = useAppStore()

// 快速統計數據
const quickStats = ref([
  {
    label: '總員工數',
    value: '156',
    trend: 8,
    icon: '👥',
    bgColor: 'bg-cognitive-primary'
  },
  {
    label: '平均績效分數',
    value: '8.2',
    trend: 12.5,
    icon: '⭐',
    bgColor: 'bg-cognitive-success'
  },
  {
    label: '待優化領域',
    value: '5',
    trend: -15,
    icon: '📊',
    bgColor: 'bg-cognitive-warning'
  },
  {
    label: '本月分析次數',
    value: '32',
    trend: 22,
    icon: '🔍',
    bgColor: 'bg-cognitive-primary'
  }
])

// 近期活動
const recentActivities = ref([
  {
    id: 1,
    title: '團隊協作能力分析完成',
    description: '研發團隊的協作模式分析報告已生成',
    timestamp: '2小時前',
    icon: '🤝',
    bgColor: 'bg-cognitive-success'
  },
  {
    id: 2,
    title: '員工技能評估更新',
    description: '15名員工的技能檔案已更新',
    timestamp: '4小時前',
    icon: '📈',
    bgColor: 'bg-cognitive-primary'
  },
  {
    id: 3,
    title: '績效預測模型訓練',
    description: 'AI模型使用最新數據重新訓練',
    timestamp: '1天前',
    icon: '🤖',
    bgColor: 'bg-cognitive-warning'
  }
])

// AI 建議
const aiSuggestions = ref([
  {
    id: 1,
    title: '提升團隊溝通',
    description: '建議增加跨部門協作機會',
    icon: '💬'
  },
  {
    id: 2,
    title: '技能培訓計劃',
    description: '識別出3個關鍵技能需要加強',
    icon: '🎓'
  },
  {
    id: 3,
    title: '人才保留策略',
    description: '高價值員工離職風險預警',
    icon: '🛡️'
  }
])

// 初始化儀表板
onMounted(() => {
  appStore.showInfo('儀表板載入完成', '歡迎回到 AI 人才分析平台')
})
</script>

<style scoped>
.dashboard {
  /* 儀表板特定樣式 */
}

/* 響應式調整 */
@media (max-width: 768px) {
  .grid-cols-4 {
    @apply grid-cols-2;
  }
  
  .lg\:col-span-2 {
    @apply col-span-1;
  }
}
</style>