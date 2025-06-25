# HR AI 人才生態系統平台

## 🌟 項目概述

基於認知神經科學的智能人才分析平台，整合多模型AI技術，提供深度的員工和團隊分析洞察。

## 🏗️ 技術架構

- **前端**: Vue.js 3 + TypeScript + Vite + Tailwind CSS
- **狀態管理**: Pinia
- **測試**: Vitest + Vue Test Utils  
- **國際化**: Vue-i18n (zh-TW, en-US)
- **設計系統**: 認知友善設計原則

## 📋 功能特色

### 🧠 認知友善設計
- Miller's Law 合規 (7±2 項目限制)
- 注意力管理和認知負荷監控
- 無障礙功能 (WCAG 2.1 合規)
- 減少動畫偏好支援

### 📊 核心功能
- **儀表板**: 綜合數據視圖和快速統計
- **個人分析**: 深度員工能力、績效與發展潛力分析
- **團隊分析**: 團隊動力、協作模式與整體效能分析
- **AI 洞察**: 智能建議和預測分析

## 🚀 快速開始

### 環境需求
- Node.js >= 16.0
- npm >= 8.0

### 1. 安裝依賴
\`\`\`bash
cd /Users/tsunglunho/hr-ai-platform/frontend
npm install
\`\`\`

### 2. 啟動開發服務器
\`\`\`bash
npm run dev
\`\`\`

### 3. 訪問應用
打開瀏覽器訪問: http://localhost:5173

## 🧪 測試

### 運行單元測試
\`\`\`bash
npm run test
\`\`\`

### 運行測試覆蓋率
\`\`\`bash
npm run test:coverage
\`\`\`

### 類型檢查
\`\`\`bash
npm run type-check
\`\`\`

## 🏗️ 構建

### 開發構建
\`\`\`bash
npm run build
\`\`\`

### 預覽構建結果
\`\`\`bash
npm run preview
\`\`\`

## 📁 項目結構

\`\`\`
frontend/
├── src/
│   ├── components/          # 可重用組件
│   │   └── cognitive/       # 認知設計組件
│   ├── composables/         # Vue 組合式函數
│   ├── i18n/               # 國際化配置
│   ├── stores/             # Pinia 狀態管理
│   ├── views/              # 頁面組件
│   ├── assets/css/         # 全局樣式
│   └── router/             # 路由配置
├── tests/                  # 測試配置
└── public/                 # 靜態資源
\`\`\`

## 🎨 設計系統

### 認知色彩系統
- **Primary**: #2563eb (認知主色)
- **Success**: #059669 (成功狀態)
- **Warning**: #d97706 (警告狀態)
- **Danger**: #dc2626 (錯誤狀態)

### 認知間距系統
- **XS**: 0.25rem (4px)
- **SM**: 0.5rem (8px)  
- **MD**: 1rem (16px)
- **LG**: 1.5rem (24px)
- **XL**: 2rem (32px)

## 🔧 開發指南

### 組件開發
- 使用 TypeScript 嚴格模式
- 遵循 Composition API 模式
- 實現認知友善設計原則
- 包含完整的單元測試

### 測試策略  
- 單元測試: 70% 覆蓋率
- 組件測試: Vue Test Utils
- 認知功能測試: 專門的可用性測試

### 國際化
- 支援繁體中文 (zh-TW) 和英文 (en-US)
- 使用 Vue-i18n 進行本地化
- 所有文字內容需要翻譯

## 📚 API 文檔

### 認知組件 API

#### CognitiveButton
\`\`\`vue
<CognitiveButton 
  variant="primary|secondary|success|warning|danger"
  size="small|medium|large"
  :disabled="boolean"
  :is-loading="boolean"
  @click="handleClick"
>
  按鈕文字
</CognitiveButton>
\`\`\`

#### CognitiveForm
\`\`\`vue
<CognitiveForm 
  :max-sections="number"
  @submit="handleSubmit"
  @load-change="handleLoadChange"
>
  <template #default>
    <!-- 表單內容 -->
  </template>
  <template #actions>
    <!-- 操作按鈕 -->
  </template>
</CognitiveForm>
\`\`\`

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支: \`git checkout -b feature/new-feature\`
3. 提交變更: \`git commit -m 'Add new feature'\`
4. 推送分支: \`git push origin feature/new-feature\`
5. 創建 Pull Request

## 📄 授權

MIT License

## 🙋‍♂️ 支援

如需幫助，請聯繫項目維護者或提交 Issue。

---

🤖 Generated with [Claude Code](https://claude.ai/code)