import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'

// CSS 導入
import './assets/css/main.css'

// 創建應用實例
const app = createApp(App)

// 使用 Pinia 狀態管理
app.use(createPinia())

// 使用路由
app.use(router)

// 使用國際化
app.use(i18n)

// 全局錯誤處理
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
  // TODO: 發送錯誤到監控系統
}

// 全局警告處理 (開發環境)
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, vm, trace) => {
    console.warn('Global warning:', msg)
    console.warn('Warning trace:', trace)
  }
}

// 掛載應用
app.mount('#app')