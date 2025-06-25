# 🚀 HR智能知識助手 - 快速使用指南

## ⚡ **一鍵啟動 (推薦)**

```bash
# 1. 安裝所有依賴
python install.py

# 2. 啟動應用
python start.py
```

## 📋 **手動安裝步驟**

### **1. 環境要求**
- Python 3.8+
- Node.js 16+
- 8GB+ RAM

### **2. 安裝依賴**
```bash
# Python依賴
pip install -r requirements.txt

# 前端依賴  
cd hr-ai-platform/frontend
npm install
cd ../..

# 安裝Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Windows: 下載 https://ollama.ai/download
```

### **3. 下載AI模型**
```bash
# 啟動Ollama
ollama serve

# 另開終端下載模型
ollama pull qwen2.5:7b    # 輕量版 (4GB)
# 或
ollama pull qwen2.5:14b   # 標準版 (8GB)
```

### **4. 啟動服務**
```bash
# 終端1: 後端API
cd api
python rag_main.py

# 終端2: 前端界面  
cd hr-ai-platform/frontend
npm run dev
```

### **5. 開始使用**
- 打開瀏覽器：http://localhost:5173
- 上傳HR文件 (PDF、Word、TXT)
- 開始智能問答！

## 🎯 **使用示例**

### **上傳文件**
1. 點擊左側 "上傳" 按鈕
2. 選擇HR相關文件 (勞基法、公司政策等)
3. 等待處理完成

### **智能問答**
```
Q: "員工請病假超過30天，薪資如何計算？"
A: 根據勞基法第59條規定...
   [來源: 勞基法.pdf, 第23頁]
```

## 🛠️ **故障排除**

### **常見問題**
- **Ollama連接失敗**: 確認ollama serve運行中
- **前端404錯誤**: 檢查後端API是否在8000端口運行
- **模型下載慢**: 可以先使用較小的qwen2.5:7b模型

### **檢查服務狀態**
```bash
# 檢查後端
curl http://localhost:8000/health

# 檢查Ollama
ollama list

# 檢查前端
curl http://localhost:5173
```

## 🎊 **完成！**

現在你有一個完全本地運行的HR智能知識助手了！