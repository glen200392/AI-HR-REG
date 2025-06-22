<template>
  <div id="app" class="min-h-screen bg-cognitive-background">
    <!-- 全局載入指示器 -->
    <Transition name="fade">
      <div
        v-if="isLoading"
        class="fixed inset-0 z-50 flex items-center justify-center bg-white bg-opacity-80"
      >
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-cognitive-primary"></div>
          <p class="mt-2 text-cognitive-neutral">載入中...</p>
        </div>
      </div>
    </Transition>

    <!-- 主要應用內容 -->
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>

    <!-- 全局通知系統 -->
    <NotificationContainer />

    <!-- 無障礙跳過連結 -->
    <a
      href="#main-content"
      class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-cognitive-primary text-white px-4 py-2 rounded"
    >
      跳到主要內容
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { useAppStore } from '@/stores/app'
import NotificationContainer from '@/components/ui/NotificationContainer.vue'

// 使用應用狀態
const appStore = useAppStore()
const isLoading = computed(() => appStore.isLoading)

// 初始化應用
appStore.initialize()
</script>

<style scoped>
/* 頁面轉場動畫 */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 淡入淡出動畫 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 視覺上隱藏但對螢幕閱讀器可見 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
</style>