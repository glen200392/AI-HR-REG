import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由定義
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: {
      title: '儀表板',
      requiresAuth: false // MVP 階段暫不需要登入
    }
  },
  {
    path: '/employee-analysis',
    name: 'employee-analysis',
    component: () => import('@/views/analysis/EmployeeAnalysisView.vue'),
    meta: {
      title: '員工分析',
      requiresAuth: false
    }
  },
  {
    path: '/team-analysis',
    name: 'team-analysis',
    component: () => import('@/views/analysis/TeamAnalysisView.vue'),
    meta: {
      title: '團隊分析',
      requiresAuth: false
    }
  },
  {
    path: '/batch-analysis',
    name: 'batch-analysis',
    component: () => import('@/views/analysis/BatchAnalysisView.vue'),
    meta: {
      title: '批量分析',
      requiresAuth: false
    }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/history/HistoryView.vue'),
    meta: {
      title: '分析記錄',
      requiresAuth: false
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/settings/SettingsView.vue'),
    meta: {
      title: '系統設定',
      requiresAuth: false
    }
  },
  // 404 頁面
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/error/NotFoundView.vue'),
    meta: {
      title: '頁面不存在'
    }
  }
]

// 創建路由實例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 返回儲存的位置或滾動到頂部
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守衛
router.beforeEach((to, from, next) => {
  // 設置頁面標題
  if (to.meta.title) {
    document.title = `${to.meta.title} - HR AI 平台`
  }

  // 檢查認證狀態 (Phase 2 才會啟用)
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
  }

  next()
})

// 路由錯誤處理
router.onError((error) => {
  console.error('Router error:', error)
  // TODO: 發送錯誤到監控系統
})

export default router