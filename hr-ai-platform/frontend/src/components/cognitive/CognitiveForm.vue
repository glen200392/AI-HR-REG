<template>
  <form
    class="cognitive-form max-w-4xl mx-auto p-cognitive-lg"
    @submit="handleSubmit"
  >
    <!-- 認知負荷指示器 -->
    <div
      v-if="cognitiveLoad.isOverloaded"
      class="mb-cognitive-md p-cognitive-sm bg-cognitive-warning text-white rounded-lg animate-cognitive-fade-in"
    >
      <div class="flex items-center">
        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm">表單較為複雜，建議分步驟填寫</span>
      </div>
    </div>

    <!-- 表單內容插槽 -->
    <div class="space-y-cognitive-lg">
      <slot />
    </div>

    <!-- 進度指示器 -->
    <div class="mt-cognitive-lg">
      <div class="w-full bg-gray-200 rounded-full h-1">
        <div
          class="bg-cognitive-primary h-1 rounded-full transition-all duration-300"
          :style="{ width: `${cognitiveLoad.loadPercentage}%` }"
        ></div>
      </div>
      <div class="mt-2 text-sm text-cognitive-neutral text-center">
        表單完成度: {{ Math.round(cognitiveLoad.loadPercentage) }}%
      </div>
    </div>

    <!-- 提交按鈕插槽 -->
    <div class="mt-cognitive-xl">
      <slot name="actions" />
    </div>
  </form>
</template>

<script setup lang="ts">
import { onMounted, reactive, watch } from 'vue'
import { useCognitiveLoad } from '@/composables/useCognitive'

interface Props {
  maxSections?: number
  onSubmit?: (event: Event) => void
}

interface Emits {
  (e: 'submit', event: Event): void
  (e: 'loadChange', load: number): void
}

// Props 和 Emits
const props = withDefaults(defineProps<Props>(), {
  maxSections: 5
})

const emit = defineEmits<Emits>()

// 認知負荷管理
const cognitiveLoad = useCognitiveLoad()

// 表單狀態
const formState = reactive({
  isValid: false,
  sections: 0,
  completedFields: 0,
  totalFields: 0
})

// 處理表單提交
const handleSubmit = (event: Event) => {
  event.preventDefault()
  
  if (props.onSubmit) {
    props.onSubmit(event)
  }
  
  emit('submit', event)
}

// 分析表單複雜度
const analyzeFormComplexity = () => {
  // 計算表單區塊數量
  const form = event?.target as HTMLFormElement
  if (form) {
    const sections = form.querySelectorAll('.form-section, .cognitive-section')
    const fields = form.querySelectorAll('input, select, textarea')
    
    formState.sections = sections.length
    formState.totalFields = fields.length
    
    // 更新認知負荷
    cognitiveLoad.resetLoad()
    cognitiveLoad.addLoad(Math.min(formState.sections, props.maxSections))
  }
}

// 計算完成進度
const calculateProgress = () => {
  const form = document.querySelector('.cognitive-form') as HTMLFormElement
  if (!form) return
  
  const fields = form.querySelectorAll('input, select, textarea') as NodeListOf<HTMLInputElement>
  let completed = 0
  
  fields.forEach(field => {
    if (field.type === 'checkbox' || field.type === 'radio') {
      if (field.checked) completed++
    } else if (field.value.trim() !== '') {
      completed++
    }
  })
  
  formState.completedFields = completed
  
  // 更新進度百分比
  const percentage = formState.totalFields > 0 
    ? (completed / formState.totalFields) * 100 
    : 0
  
  cognitiveLoad.loadPercentage = percentage
}

// 監聽表單變化
onMounted(() => {
  analyzeFormComplexity()
  
  // 監聽表單輸入變化
  const form = document.querySelector('.cognitive-form')
  if (form) {
    form.addEventListener('input', calculateProgress)
    form.addEventListener('change', calculateProgress)
  }
})

// 監聽認知負荷變化
watch(
  () => cognitiveLoad.currentLoad,
  (newLoad) => {
    emit('loadChange', newLoad)
  }
)

// 暴露方法
defineExpose({
  cognitiveLoad,
  formState,
  analyzeFormComplexity,
  calculateProgress
})
</script>

<style scoped>
.cognitive-form {
  /* 確保表單有適當的視覺層次 */
}

/* 表單區塊樣式 */
:deep(.form-section),
:deep(.cognitive-section) {
  @apply mb-cognitive-lg p-cognitive-lg border border-gray-200 rounded-lg bg-gray-50;
}

/* 表單標題樣式 */
:deep(.form-section-title),
:deep(.cognitive-section-title) {
  @apply text-cognitive-lg font-semibold text-gray-900 mb-cognitive-md flex items-center;
}

/* 表單組樣式 */
:deep(.form-group) {
  @apply mb-cognitive-md;
}

/* 標籤樣式 */
:deep(.form-label) {
  @apply block text-cognitive-sm font-medium text-gray-700 mb-cognitive-sm;
}

/* 輸入框樣式 */
:deep(.form-input) {
  @apply w-full px-cognitive-md py-cognitive-sm border border-gray-300 rounded-md shadow-cognitive-sm focus:ring-cognitive-primary focus:border-cognitive-primary;
}

/* 必填字段標記 */
:deep(.form-label.required::after) {
  content: ' *';
  color: #dc2626;
}
</style>