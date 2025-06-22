/**
 * 認知友善設計組合式函數
 * 基於認知神經科學的UI交互邏輯
 */

import { ref, reactive, onMounted, onUnmounted } from 'vue'

// 認知設計常數
export const COGNITIVE_CONSTANTS = {
  // 工作記憶限制 (Miller's Law: 7±2)
  MAX_VISIBLE_ITEMS: 7,
  
  // 注意力持續時間 (基於神經科學研究)
  ATTENTION_SPAN_MS: 8000,
  
  // 認知時間系統
  TIMING: {
    micro: 100,      // 即時反饋
    quick: 300,      // 快速轉場
    normal: 500,     // 標準動畫
    slow: 1000       // 重要狀態變化
  }
}

/**
 * 注意力管理 Hook
 * 基於注意力研究，管理用戶注意力分配
 */
export function useAttention(priority: 'high' | 'normal' | 'low' = 'normal') {
  const isVisible = ref(false)
  const isFocused = ref(false)
  const elementRef = ref<HTMLElement>()

  let observer: IntersectionObserver | null = null

  onMounted(() => {
    if (elementRef.value) {
      observer = new IntersectionObserver(
        ([entry]) => {
          isVisible.value = entry.isIntersecting
        },
        { threshold: 0.1 }
      )
      observer.observe(elementRef.value)
    }
  })

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  const focusElement = () => {
    if (elementRef.value) {
      elementRef.value.focus()
      isFocused.value = true
    }
  }

  const priorityLevel = priority === 'high' ? 1 : priority === 'low' ? 3 : 2

  return {
    elementRef,
    isVisible,
    isFocused,
    focusElement,
    priority: priorityLevel
  }
}

/**
 * 認知負荷管理 Hook
 * 基於認知負荷理論，動態管理界面複雜度
 */
export function useCognitiveLoad() {
  const state = reactive({
    currentLoad: 0,
    maxLoad: COGNITIVE_CONSTANTS.MAX_VISIBLE_ITEMS,
    loadPercentage: 0
  })

  const addLoad = (amount = 1) => {
    state.currentLoad = Math.min(state.currentLoad + amount, state.maxLoad)
    updatePercentage()
  }

  const removeLoad = (amount = 1) => {
    state.currentLoad = Math.max(state.currentLoad - amount, 0)
    updatePercentage()
  }

  const resetLoad = () => {
    state.currentLoad = 0
    updatePercentage()
  }

  const updatePercentage = () => {
    state.loadPercentage = (state.currentLoad / state.maxLoad) * 100
  }

  const isOverloaded = () => state.currentLoad >= state.maxLoad

  return {
    ...state,
    addLoad,
    removeLoad,
    resetLoad,
    isOverloaded: isOverloaded()
  }
}

/**
 * 漸進披露 Hook
 * 基於信息架構理論，管理內容的漸進顯示
 */
export function useProgressiveDisclosure(steps: string[]) {
  const state = reactive({
    currentStep: 0,
    completedSteps: new Set<number>(),
    totalSteps: steps.length
  })

  const nextStep = () => {
    if (state.currentStep < state.totalSteps - 1) {
      state.currentStep += 1
    }
  }

  const prevStep = () => {
    if (state.currentStep > 0) {
      state.currentStep -= 1
    }
  }

  const goToStep = (step: number) => {
    if (step >= 0 && step < state.totalSteps) {
      state.currentStep = step
    }
  }

  const completeStep = (step = state.currentStep) => {
    state.completedSteps.add(step)
  }

  const isStepCompleted = (step: number) => {
    return state.completedSteps.has(step)
  }

  const progressPercentage = () => {
    return (state.completedSteps.size / state.totalSteps) * 100
  }

  return {
    ...state,
    nextStep,
    prevStep,
    goToStep,
    completeStep,
    isStepCompleted,
    progressPercentage: progressPercentage()
  }
}

/**
 * 無障礙功能 Hook
 * 提供鍵盤導航和螢幕閱讀器支援
 */
export function useAccessibility() {
  const isKeyboardNavigation = ref(false)

  onMounted(() => {
    // 檢測鍵盤導航
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        isKeyboardNavigation.value = true
      }
    }

    const handleMouseDown = () => {
      isKeyboardNavigation.value = false
    }

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    })
  })

  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', 'polite')
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.textContent = message

    document.body.appendChild(announcement)

    setTimeout(() => {
      document.body.removeChild(announcement)
    }, 1000)
  }

  const trapFocus = (element: HTMLElement) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus()
          event.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus()
          event.preventDefault()
        }
      }
    }

    element.addEventListener('keydown', handleTabKey)

    return () => {
      element.removeEventListener('keydown', handleTabKey)
    }
  }

  return {
    isKeyboardNavigation,
    announceToScreenReader,
    trapFocus
  }
}

/**
 * 認知動畫 Hook
 * 基於認知科學的動畫和轉場管理
 */
export function useCognitiveAnimation() {
  const prefersReducedMotion = ref(false)

  onMounted(() => {
    // 檢測用戶是否偏好減少動畫
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    prefersReducedMotion.value = mediaQuery.matches

    const handleChange = (event: MediaQueryListEvent) => {
      prefersReducedMotion.value = event.matches
    }

    mediaQuery.addEventListener('change', handleChange)

    onUnmounted(() => {
      mediaQuery.removeEventListener('change', handleChange)
    })
  })

  const getAnimationDuration = (type: keyof typeof COGNITIVE_CONSTANTS.TIMING) => {
    return prefersReducedMotion.value ? 0 : COGNITIVE_CONSTANTS.TIMING[type]
  }

  const createFadeTransition = (duration = COGNITIVE_CONSTANTS.TIMING.normal) => {
    if (prefersReducedMotion.value) return {}

    return {
      enterActiveClass: 'transition-opacity duration-300 ease-in-out',
      leaveActiveClass: 'transition-opacity duration-300 ease-in-out',
      enterFromClass: 'opacity-0',
      leaveToClass: 'opacity-0'
    }
  }

  const createSlideTransition = (
    direction: 'up' | 'down' | 'left' | 'right' = 'up',
    duration = COGNITIVE_CONSTANTS.TIMING.normal
  ) => {
    if (prefersReducedMotion.value) return {}

    const transforms = {
      up: 'translateY(20px)',
      down: 'translateY(-20px)',
      left: 'translateX(20px)',
      right: 'translateX(-20px)'
    }

    return {
      enterActiveClass: 'transition-all duration-500 ease-out',
      leaveActiveClass: 'transition-all duration-300 ease-in',
      enterFromClass: `opacity-0 transform ${transforms[direction]}`,
      leaveToClass: `opacity-0 transform ${transforms[direction]}`
    }
  }

  return {
    prefersReducedMotion,
    getAnimationDuration,
    createFadeTransition,
    createSlideTransition
  }
}