# 🖥️ HR智能知識助手 - 桌面版架構設計

## 🎯 **技術方案選擇**

### **方案A: Electron + Vue.js (推薦)**
```javascript
優勢:
✅ 跨平台 (Windows/Mac/Linux)
✅ 前端技術複用
✅ 豐富的生態系統
✅ 易於開發和維護

技術棧:
├── Electron (桌面框架)
├── Vue.js 3 (前端界面)
├── FastAPI (內嵌後端)
├── SQLite (本地資料庫)
└── Qwen2.5 (本地LLM)
```

### **方案B: Tauri + Vue.js (輕量)**
```rust
優勢:
✅ 體積更小 (~50MB vs 200MB)
✅ 安全性更高
✅ 性能更好
⚠️ 學習曲線較陡

技術棧:
├── Tauri (Rust桌面框架)
├── Vue.js 3 (前端界面)  
├── Python微服務 (後端)
└── 本地模型整合
```

## 🏗️ **Electron版本架構 (推薦)**

### **📁 項目結構**
```
hr-ai-desktop/
├── 📦 package.json
├── 🔧 electron.js (主進程)
├── 🌐 dist/ (打包後的前端)
├── 🐍 backend/ (內嵌Python服務)
│   ├── main.py (FastAPI)
│   ├── agents/ (RAG智能體)
│   ├── models/ (本地LLM)
│   └── data/ (向量資料庫)
├── 📊 frontend/ (Vue.js源碼)
└── 🔨 build/ (打包配置)
```

### **🔄 應用啟動流程**
```javascript
// electron.js - 主進程
const { app, BrowserWindow, shell } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

class HRAssistantApp {
  constructor() {
    this.pythonProcess = null
    this.mainWindow = null
  }

  async createWindow() {
    // 1. 啟動內嵌Python後端
    await this.startPythonBackend()
    
    // 2. 創建主窗口
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, 'assets/icon.png'),
      titleBarStyle: 'hiddenInset', // macOS樣式
      show: false
    })

    // 3. 載入前端界面
    const isDev = process.env.NODE_ENV === 'development'
    const url = isDev 
      ? 'http://localhost:3000'  // 開發環境
      : `file://${path.join(__dirname, '../dist/index.html')}` // 生產環境

    await this.mainWindow.loadURL(url)
    
    // 4. 等待後端啟動完成
    await this.waitForBackend()
    
    // 5. 顯示窗口
    this.mainWindow.show()
  }

  async startPythonBackend() {
    const pythonPath = this.getPythonPath()
    const scriptPath = path.join(__dirname, 'backend/main.py')
    
    this.pythonProcess = spawn(pythonPath, [scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: path.join(__dirname, 'backend')
    })
    
    console.log('🐍 Python backend starting...')
  }

  getPythonPath() {
    // 內嵌Python解釋器路徑
    if (process.platform === 'win32') {
      return path.join(__dirname, 'python/python.exe')
    } else if (process.platform === 'darwin') {
      return path.join(__dirname, 'python/bin/python')
    } else {
      return path.join(__dirname, 'python/bin/python')
    }
  }

  async waitForBackend() {
    // 檢查後端是否啟動成功
    const maxRetries = 30
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch('http://localhost:8000/health')
        if (response.ok) {
          console.log('✅ Backend ready!')
          return
        }
      } catch (error) {
        // 繼續等待
      }
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    throw new Error('Backend failed to start')
  }
}

// 應用生命週期
app.whenReady().then(() => {
  const hrApp = new HRAssistantApp()
  hrApp.createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
```

## 📦 **打包和分發策略**

### **🔨 打包工具**
```json
{
  "build": {
    "appId": "com.company.hr-assistant",
    "productName": "HR智能知識助手",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "backend/**/*",
      "python/**/*",
      "node_modules/**/*"
    ],
    "mac": {
      "category": "public.app-category.productivity",
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        }
      ]
    },
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ]
    },
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        }
      ]
    }
  }
}
```

### **📥 安裝包規格**

| 平台 | 格式 | 大小預估 | 特色 |
|------|------|----------|------|
| **Windows** | `.exe` 安裝檔 | ~1.5GB | 一鍵安裝，自動更新 |
| **macOS** | `.dmg` 映像檔 | ~1.8GB | 拖拽安裝，原生體驗 |
| **Linux** | `.AppImage` | ~1.6GB | 免安裝執行檔 |

## 🧠 **內嵌LLM策略**

### **模型選擇與優化**
```python
# 模型配置策略
LOCAL_MODELS = {
    "light": {
        "name": "qwen2.5:7b-instruct-q4_0",
        "size": "4.1GB",
        "ram_requirement": "6GB",
        "performance": "快速響應"
    },
    "standard": {
        "name": "qwen2.5:14b-instruct-q4_0", 
        "size": "8.2GB",
        "ram_requirement": "12GB",
        "performance": "平衡性能"
    },
    "premium": {
        "name": "qwen2.5:32b-instruct-q4_0",
        "size": "18GB", 
        "ram_requirement": "24GB",
        "performance": "最佳質量"
    }
}

# 自動檢測硬體配置
def auto_select_model():
    import psutil
    total_ram = psutil.virtual_memory().total / (1024**3)  # GB
    
    if total_ram >= 24:
        return "premium"
    elif total_ram >= 12:
        return "standard"
    else:
        return "light"
```

### **首次啟動流程**
```python
class FirstRunSetup:
    async def setup(self):
        # 1. 檢測系統規格
        system_info = self.detect_system()
        
        # 2. 推薦模型配置
        recommended_model = self.recommend_model(system_info)
        
        # 3. 用戶確認或自定義
        user_choice = await self.show_model_selection(recommended_model)
        
        # 4. 下載並安裝模型
        await self.download_model(user_choice)
        
        # 5. 初始化向量資料庫
        await self.setup_vector_store()
        
        # 6. 完成設置
        self.mark_setup_complete()
```

## 💾 **本地數據存儲**

### **資料庫設計**
```sql
-- 使用SQLite作為本地資料庫
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    content_hash TEXT UNIQUE,
    upload_date DATETIME,
    file_size INTEGER,
    chunk_count INTEGER,
    status TEXT DEFAULT 'processing'
);

CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT,
    created_at DATETIME,
    last_activity DATETIME,
    message_count INTEGER DEFAULT 0
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    user_message TEXT,
    ai_response TEXT,
    timestamp DATETIME,
    response_time REAL,
    model_used TEXT,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
);

CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME
);
```

### **檔案組織結構**
```
用戶資料目錄/
├── 📊 database.sqlite (聊天記錄)
├── 🗄️ vector_store/ (向量資料庫)
├── 📁 documents/ (原始文件)
├── 🤖 models/ (LLM模型)
├── 📋 logs/ (應用日誌)
└── ⚙️ config.json (用戶設定)
```

## 🔧 **用戶界面設計**

### **主界面布局**
```vue
<template>
  <div class="app-container">
    <!-- 標題欄 -->
    <div class="title-bar">
      <div class="title">HR智能知識助手</div>
      <div class="controls">
        <button @click="openSettings">⚙️</button>
        <button @click="minimizeApp">➖</button>
        <button @click="closeApp">❌</button>
      </div>
    </div>

    <!-- 主要內容區 -->
    <div class="main-content">
      <!-- 側邊欄 -->
      <div class="sidebar">
        <div class="model-status">
          <div class="status-indicator" :class="modelStatus"></div>
          <span>{{ currentModel }}</span>
        </div>
        
        <div class="chat-history">
          <h3>對話記錄</h3>
          <div v-for="session in chatSessions" :key="session.id">
            {{ session.name }}
          </div>
        </div>
        
        <div class="document-manager">
          <h3>文件管理</h3>
          <button @click="uploadDocument">📤 上傳文件</button>
          <div class="document-list">
            <!-- 文件列表 -->
          </div>
        </div>
      </div>

      <!-- 聊天區域 -->
      <div class="chat-area">
        <div class="messages">
          <!-- 聊天消息 -->
        </div>
        <div class="input-area">
          <input v-model="userInput" 
                 @keyup.enter="sendMessage"
                 placeholder="請輸入您的HR問題..." />
          <button @click="sendMessage">發送</button>
        </div>
      </div>

      <!-- 分析面板 -->
      <div class="analysis-panel">
        <h3>查詢分析</h3>
        <div class="complexity-indicator">
          複雜度: {{ queryComplexity }}
        </div>
        <div class="source-documents">
          來源文件: {{ sourceDocuments }}
        </div>
      </div>
    </div>
  </div>
</template>
```

## 🚀 **部署和更新策略**

### **自動更新機制**
```javascript
// 檢查更新
const { autoUpdater } = require('electron-updater')

autoUpdater.checkForUpdatesAndNotify()

autoUpdater.on('update-available', () => {
  // 通知用戶有新版本
  dialog.showMessageBox({
    type: 'info',
    title: '發現新版本',
    message: '新版本可用，是否立即下載？',
    buttons: ['是', '稍後']
  })
})
```

### **離線檢測與降級**
```javascript
// 網路狀態檢測
class NetworkManager {
  constructor() {
    this.isOnline = navigator.onLine
    this.setupEventListeners()
  }

  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.notifyNetworkChange('online')
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
      this.notifyNetworkChange('offline')
    })
  }

  notifyNetworkChange(status) {
    // 通知用戶網路狀態變化
    // 離線時禁用雲端功能，確保本地功能正常
  }
}
```

## 📊 **性能優化策略**

### **啟動時間優化**
```javascript
// 延遲載入非關鍵組件
const optimizations = {
  "lazy_load_models": true,      // 懶加載LLM模型
  "preload_chat_ui": true,       // 預載聊天界面
  "background_indexing": true,   // 背景索引文件
  "cache_embeddings": true       // 快取向量嵌入
}
```

### **記憶體使用優化**
```python
# 模型記憶體管理
class ModelManager:
    def __init__(self):
        self.max_memory_usage = 0.7  # 最大使用70%系統記憶體
        self.model_cache_size = 2    # 最多快取2個模型
        
    def load_model_with_memory_check(self, model_name):
        current_usage = psutil.virtual_memory().percent / 100
        if current_usage > self.max_memory_usage:
            self.cleanup_unused_models()
        
        return self.load_model(model_name)
```

## 💡 **發布策略**

### **版本規劃**
- **v1.0 MVP**: 基本聊天 + 文件上傳 (4週)
- **v1.1**: 查詢分析 + 系統監控 (2週)  
- **v1.2**: 性能優化 + 用戶體驗 (2週)
- **v2.0**: 進階功能 + 企業版 (8週)

### **發布渠道**
- 📦 **官方網站下載**
- 🏢 **企業內部分發**
- 💾 **USB隨身碟版本**
- 🔄 **內建自動更新**

這個方案的優勢：
1. **零配置**：下載即用
2. **完全離線**：不依賴網路
3. **數據隱私**：所有資料本地存儲
4. **跨平台**：支援Windows/Mac/Linux
5. **自動更新**：無感升級體驗

要開始實現桌面版嗎？