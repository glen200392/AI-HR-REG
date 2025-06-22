/**
 * 應用全局狀態管理
 * 管理應用級別的狀態和設定
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface AppNotification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  duration?: number
  actions?: Array<{
    label: string
    action: () => void
  }>
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-TW' | 'en-US'
  reducedMotion: boolean
  highContrast: boolean
  fontSize: 'small' | 'medium' | 'large'
  cognitiveAssistance: boolean
}

export const useAppStore = defineStore('app', () => {
  // 狀態
  const isLoading = ref(false)
  const isOnline = ref(navigator.onLine)
  const notifications = ref<AppNotification[]>([])
  const settings = ref<AppSettings>({
    theme: 'light',
    language: 'zh-TW',
    reducedMotion: false,
    highContrast: false,
    fontSize: 'medium',
    cognitiveAssistance: true
  })

  // 計算屬性
  const hasNotifications = computed(() => notifications.value.length > 0)
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.actions)
  )

  // 動作
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const addNotification = (notification: Omit<AppNotification, 'id'>) => {
    const id = Date.now().toString()
    const newNotification: AppNotification = {
      id,
      duration: 5000,
      ...notification
    }
    
    notifications.value.push(newNotification)

    // 自動移除通知
    if (newNotification.duration && newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    settings.value = { ...settings.value, ...newSettings }
    saveSettings()
  }

  const saveSettings = () => {
    try {
      localStorage.setItem('hr-ai-settings', JSON.stringify(settings.value))
    } catch (error) {
      console.warn('無法保存設定到本地存儲:', error)
    }
  }

  const loadSettings = () => {
    try {
      const saved = localStorage.getItem('hr-ai-settings')
      if (saved) {
        const parsedSettings = JSON.parse(saved) as AppSettings
        settings.value = { ...settings.value, ...parsedSettings }
      }
    } catch (error) {
      console.warn('無法從本地存儲載入設定:', error)
    }
  }

  const applyTheme = () => {
    const { theme } = settings.value
    const root = document.documentElement
    
    if (theme === 'auto') {
      // 跟隨系統主題
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.toggle('dark', prefersDark)
    } else {
      root.classList.toggle('dark', theme === 'dark')
    }
  }

  const applyAccessibilitySettings = () => {
    const { reducedMotion, highContrast, fontSize } = settings.value
    const root = document.documentElement

    // 應用動畫偏好
    if (reducedMotion) {
      root.style.setProperty('--animation-duration', '0.01ms')
    } else {
      root.style.removeProperty('--animation-duration')
    }

    // 應用高對比度
    root.classList.toggle('high-contrast', highContrast)

    // 應用字體大小
    root.classList.remove('font-small', 'font-medium', 'font-large')
    root.classList.add(`font-${fontSize}`)
  }

  const initialize = async () => {
    setLoading(true)
    
    try {
      // 載入設定
      loadSettings()
      
      // 應用主題和無障礙設定
      applyTheme()
      applyAccessibilitySettings()
      
      // 監聽網路狀態
      window.addEventListener('online', () => {
        isOnline.value = true
        addNotification({
          type: 'success',
          title: '網路連線恢復',
          message: '您的網路連線已恢復正常'
        })
      })
      
      window.addEventListener('offline', () => {
        isOnline.value = false
        addNotification({
          type: 'warning',
          title: '網路連線中斷',
          message: '您目前處於離線狀態，部分功能可能無法使用'
        })
      })

      // 監聽系統主題變化
      if (settings.value.theme === 'auto') {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        mediaQuery.addEventListener('change', applyTheme)
      }

      // 歡迎訊息
      addNotification({
        type: 'info',
        title: '歡迎使用 HR AI 平台',
        message: '開始您的智能人才分析之旅',
        duration: 3000
      })
      
    } catch (error) {
      console.error('應用初始化失敗:', error)
      addNotification({
        type: 'error',
        title: '初始化失敗',
        message: '應用初始化過程中發生錯誤，請重新整理頁面'
      })
    } finally {
      setLoading(false)
    }
  }

  const showSuccess = (title: string, message: string) => {
    addNotification({ type: 'success', title, message })
  }

  const showWarning = (title: string, message: string) => {
    addNotification({ type: 'warning', title, message })
  }

  const showError = (title: string, message: string) => {
    addNotification({ type: 'error', title, message })
  }

  const showInfo = (title: string, message: string) => {
    addNotification({ type: 'info', title, message })
  }

  return {
    // 狀態
    isLoading,
    isOnline,
    notifications,
    settings,
    
    // 計算屬性
    hasNotifications,
    unreadNotifications,
    
    // 動作
    setLoading,
    addNotification,
    removeNotification,
    clearNotifications,
    updateSettings,
    saveSettings,
    loadSettings,
    applyTheme,
    applyAccessibilitySettings,
    initialize,
    
    // 便利方法
    showSuccess,
    showWarning,
    showError,
    showInfo
  }
})