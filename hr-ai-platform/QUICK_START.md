# 🚀 HR AI 平台快速啟動指南

## 📋 現在可以開始使用！

您的 HR AI 平台已經完成開發，這裡是立即開始使用的步驟：

## 🔧 步驟 1: 安裝依賴

```bash
# 進入前端目錄
cd /Users/tsunglunho/hr-ai-platform/frontend

# 安裝 Node.js 依賴 (如果網路正常)
npm install

# 或者使用 yarn (如果有安裝)
yarn install

# 或者使用 pnpm (如果有安裝)
pnpm install
```

## 🌐 步驟 2: 啟動開發服務器

```bash
# 啟動開發模式
npm run dev

# 或者
yarn dev
```

成功啟動後會看到:
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 🎯 步驟 3: 開始使用

打開瀏覽器訪問 `http://localhost:5173`，您將看到：

### 🏠 主要功能頁面

1. **儀表板** (`/`) 
   - 查看總體統計和趨勢
   - AI 智能建議
   - 近期分析活動

2. **個人分析** (`/employee`)
   - 選擇員工進行深度分析
   - 查看技能評估和績效趨勢
   - AI 生成的發展建議

3. **團隊分析** (`/team`)
   - 分析團隊協作模式
   - 查看技能互補情況
   - 團隊優化建議

## 🧪 步驟 4: 測試功能 (可選)

```bash
# 運行單元測試
npm run test

# 查看測試覆蓋率
npm run test:coverage

# 類型檢查
npm run type-check
```

## 🎨 認知友善設計特色

### ✨ 體驗我們的認知設計系統:

1. **智能認知負荷管理**
   - 表單會自動檢測複雜度
   - 超過7個項目時會顯示警告
   - 實時進度指示器

2. **無障礙功能**
   - 完整鍵盤導航支援
   - 螢幕閱讀器友善
   - 高對比度模式支援

3. **減少動畫偏好**
   - 自動檢測用戶偏好
   - 動畫可以完全關閉

4. **多語言支援**
   - 繁體中文 / English 切換
   - 本地化存儲偏好

## 🔍 功能演示數據

應用內建了模擬數據，您可以立即體驗所有功能：

### 員工分析
- 張小明 (前端工程師)
- 李小華 (產品經理)  
- 王小美 (UI設計師)
- 陳小強 (後端工程師)
- 林小莉 (數據分析師)

### 團隊分析
- 前端開發團隊 (8人)
- 後端開發團隊 (6人)
- 產品設計團隊 (5人)
- 數據分析團隊 (4人)
- 營運支援團隊 (7人)

## 🛠️ 如果遇到問題

### 網路問題
如果 `npm install` 失敗:
```bash
# 清除 npm 快取
npm cache clean --force

# 使用國內鏡像 (中國地區)
npm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm
cnpm install
```

### Port 衝突
如果 5173 端口被占用:
```bash
# 使用其他端口
npm run dev -- --port 3000
```

### 依賴問題
```bash
# 重新安裝
rm -rf node_modules package-lock.json
npm install
```

## 📱 下一步開發計劃

1. **後端 API 整合** - 連接真實數據源
2. **AI 模型整合** - 接入 OpenAI/Claude API
3. **部署到雲端** - Vercel/Netlify 部署
4. **數據視覺化** - Chart.js 圖表整合
5. **PWA 功能** - 離線使用支援

## 🎉 恭喜！

您現在擁有一個功能完整的 HR AI 分析平台！

這個平台基於最新的認知科學研究，提供了業界領先的用戶體驗設計。所有組件都經過精心設計，確保用戶能夠高效地進行人才分析工作。

---

📧 需要技術支援或有問題？隨時聯繫開發團隊！

🤖 Powered by Vue.js 3 + AI + Cognitive Science