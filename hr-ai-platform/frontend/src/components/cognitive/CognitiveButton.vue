<template>
  <button
    ref="buttonRef"
    :class="buttonClasses"
    :disabled="disabled || isLoading"
    :aria-busy="isLoading"
    :aria-describedby="ariaDescribedBy"
    @click="handleClick"
    @focus="onFocus"
    @blur="onBlur"
  >
    <!-- 載入指示器 -->
    <span v-if="isLoading" class="animate-spin mr-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25"></circle>
        <path d="M4 12a8 8 0 0 1 8-8v8z" fill="currentColor"></path>
      </svg>
    </span>

    <!-- 圖標 (如果有) -->
    <span v-if="icon && !isLoading" class="mr-2" v-html="icon"></span>

    <!-- 按鈕文字 -->
    <span>
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAttention } from '@/composables/useCognitive'

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  isLoading?: boolean
  icon?: string
  cognitiveLoad?: number
  ariaDescribedBy?: string
}

interface Emits {
  (e: 'click', event: MouseEvent): void
  (e: 'focus'): void
  (e: 'blur'): void
}

// Props 和 Emits
const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  isLoading: false,
  cognitiveLoad: 1
})

const emit = defineEmits<Emits>()

// 組件引用
const buttonRef = ref<HTMLButtonElement>()

// 使用認知注意力管理
const attention = useAttention(props.variant === 'primary' ? 'high' : 'normal')

// 計算樣式類
const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex',
    'items-center',
    'justify-center',
    'font-medium',
    'rounded-lg',
    'transition-all',
    'duration-200',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-2',
    'disabled:opacity-50',
    'disabled:cursor-not-allowed'
  ]

  // 尺寸樣式
  const sizeClasses = {
    small: ['px-3', 'py-1.5', 'text-sm'],
    medium: ['px-4', 'py-2', 'text-base'],
    large: ['px-6', 'py-3', 'text-lg']
  }

  // 變體樣式
  const variantClasses = {
    primary: [
      'bg-cognitive-primary',
      'text-white',
      'hover:bg-blue-700',
      'focus:ring-cognitive-primary',
      'shadow-cognitive-sm',
      'hover:shadow-cognitive-md'
    ],
    secondary: [
      'bg-white',
      'text-cognitive-neutral',
      'border',
      'border-gray-300',
      'hover:bg-gray-50',
      'focus:ring-cognitive-neutral'
    ],
    success: [
      'bg-cognitive-success',
      'text-white',
      'hover:bg-green-700',
      'focus:ring-cognitive-success'
    ],
    warning: [
      'bg-cognitive-warning',
      'text-white',
      'hover:bg-orange-700',
      'focus:ring-cognitive-warning'
    ],
    danger: [
      'bg-cognitive-danger',
      'text-white',
      'hover:bg-red-700',
      'focus:ring-cognitive-danger'
    ]
  }

  return [
    ...baseClasses,
    ...sizeClasses[props.size],
    ...variantClasses[props.variant]
  ]
})

// 事件處理
const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.isLoading) {
    attention.focusElement()
    emit('click', event)
  }
}

const onFocus = () => {
  emit('focus')
}

const onBlur = () => {
  emit('blur')
}

// 暴露方法給父組件
defineExpose({
  focus: () => buttonRef.value?.focus(),
  blur: () => buttonRef.value?.blur()
})
</script>