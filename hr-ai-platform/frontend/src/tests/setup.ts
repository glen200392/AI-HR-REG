/**
 * 測試環境設定
 * 配置 Vitest 測試環境和全局設定
 */

import { beforeAll, afterAll, afterEach } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { i18n } from '@/i18n'

// 全局測試設定
beforeAll(() => {
  // 設定 Vue Test Utils 全局配置
  config.global.plugins = [createPinia(), i18n]
  
  // 模擬 localStorage
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    },
    writable: true,
  })

  // 模擬 matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })

  // 模擬 IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }))

  // 模擬 navigator
  Object.defineProperty(window.navigator, 'onLine', {
    writable: true,
    value: true,
  })

  Object.defineProperty(window.navigator, 'language', {
    writable: true,
    value: 'zh-TW',
  })
})

// 每個測試後清理
afterEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
})

// 測試結束後清理
afterAll(() => {
  vi.restoreAllMocks()
})