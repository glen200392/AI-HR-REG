/**
 * 國際化配置系統
 * 支援繁體中文和英文雙語
 */

import { createI18n } from 'vue-i18n'
import zhTW from './locales/zh-TW.json'
import enUS from './locales/en-US.json'

// 檢測瀏覽器語言
const getDefaultLocale = (): string => {
  const savedLocale = localStorage.getItem('hr-ai-locale')
  if (savedLocale) {
    return savedLocale
  }
  
  const browserLocale = navigator.language
  if (browserLocale.startsWith('zh')) {
    return 'zh-TW'
  }
  
  return 'en-US'
}

// 創建 i18n 實例
export const i18n = createI18n({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'zh-TW',
  messages: {
    'zh-TW': zhTW,
    'en-US': enUS
  },
  globalInjection: true
})

// 語言切換函數
export const setLocale = (locale: string) => {
  i18n.global.locale.value = locale
  localStorage.setItem('hr-ai-locale', locale)
  document.documentElement.lang = locale
}

// 獲取當前語言
export const getCurrentLocale = () => {
  return i18n.global.locale.value
}

// 支援的語言列表
export const supportedLocales = [
  {
    code: 'zh-TW',
    name: '繁體中文',
    flag: '🇹🇼'
  },
  {
    code: 'en-US', 
    name: 'English',
    flag: '🇺🇸'
  }
]

export default i18n