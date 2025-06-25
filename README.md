# 🤖 HR智能知識助手 - RAG系統

> 基於RAG (Retrieval-Augmented Generation) 技術的HR智能問答系統  
> 支援本地LLM部署，完全私有化的企業HR知識管理解決方案

## ✨ 核心功能

- 🧠 **智能RAG問答** - 基於企業文件的精準回答
- 📚 **文件知識庫** - 支援PDF、Word、TXT等格式上傳
- 🤖 **本地LLM** - Ollama + Qwen2.5，完全離線運行
- 🎯 **HR專業優化** - 針對HR領域的查詢分析與回答
- 💻 **現代化界面** - Vue.js 3 響應式設計
- 🔒 **數據安全** - 本地部署，數據不出企業

## 🚀 快速開始

### 一鍵啟動
```bash
# 安裝依賴
python install.py

# 啟動系統
python start.py
```

### 訪問應用
- **主界面**: http://localhost:5173
- **API文檔**: http://localhost:8000/docs

## 📁 項目結構

```
├── agents/                    # AI智能體
│   ├── rag_knowledge_agent.py # RAG知識智能體
│   └── base_agent.py         # 智能體基類
├── core/                     # 核心模組
│   ├── llm_manager.py        # LLM模型管理
│   ├── query_analyzer.py     # 查詢分析器
│   └── rag_engine.py         # RAG引擎
├── api/                      # 後端API
│   └── rag_main.py          # FastAPI主應用
├── hr-ai-platform/frontend/ # 前端應用
│   ├── src/views/           # Vue組件
│   └── src/services/        # API服務
├── install.py               # 自動安裝腳本
├── start.py                 # 一鍵啟動腳本
└── requirements.txt         # Python依賴
```

## 🛠️ 技術架構

### 後端技術棧
- **FastAPI** - 現代化API框架
- **LangChain** - RAG框架
- **ChromaDB** - 向量數據庫
- **Ollama** - 本地LLM服務
- **Sentence Transformers** - 文本嵌入

### 前端技術棧
- **Vue.js 3** - 現代前端框架
- **TypeScript** - 類型安全
- **Tailwind CSS** - 現代化樣式
- **Axios** - HTTP客戶端

### AI模型
- **Qwen2.5 (7B/14B)** - 主力本地模型
- **OpenAI GPT** - 雲端備援模型
- **自動降級機制** - 確保服務穩定性

## 💼 HR使用場景

### 政策查詢
```
Q: "員工年假有幾天？"
A: 根據勞基法第38條規定，工作滿1年者，特休假7日...
   [來源: 勞基法.pdf, 第38條]
```

### 流程指導
```
Q: "如何處理員工離職手續？"
A: 離職手續包含以下步驟：1. 提交離職申請...
   [來源: 員工手冊.docx, 第42頁]
```

### 法規遵循
```
Q: "加班費如何計算？"
A: 依勞基法第24條，延長工作時間之工資計算...
   [來源: 薪資管理辦法.pdf]
```

## 📋 安裝需求

### 系統要求
- **Python 3.8+**
- **Node.js 16+**
- **8GB+ RAM** (推薦16GB)
- **10GB+ 硬碟空間** (模型存儲)

### 支援平台
- macOS (推薦)
- Linux Ubuntu/CentOS
- Windows 10/11

## 🔧 配置選項

### LLM模型選擇
```python
# 本地模型 (推薦)
qwen2.5:7b    # 輕量版，4GB RAM
qwen2.5:14b   # 標準版，8GB RAM  
qwen2.5:32b   # 專業版，16GB RAM

# 雲端備援
gpt-4o-mini   # OpenAI
claude-3      # Anthropic
```

### 檢索配置
```python
# 根據查詢複雜度動態調整
簡單查詢: 2個文件片段
中等查詢: 4個文件片段  
複雜查詢: 6個文件片段
專家查詢: 8個文件片段
```

## 🚨 故障排除

### 常見問題

**Ollama連接失敗**
```bash
# 啟動Ollama服務
ollama serve

# 檢查模型
ollama list
```

**前端無法訪問**
```bash
# 檢查後端狀態
curl http://localhost:8000/health

# 重新安裝前端依賴
cd hr-ai-platform/frontend
npm install
```

**模型下載緩慢**
```bash
# 使用較小模型
ollama pull qwen2.5:7b

# 或使用國內鏡像源
export OLLAMA_HOST=xxx
```

## 📈 性能優化

### 硬體建議
- **CPU**: 8核心+ (M1/M2/Intel i7+)
- **RAM**: 16GB+ (模型加載)
- **存儲**: SSD (向量數據庫性能)
- **GPU**: 可選，加速推理

### 軟體優化
- 使用適合的模型大小
- 調整檢索片段數量
- 啟用結果緩存
- 定期清理向量數據庫

## 🔒 安全考量

### 數據安全
- ✅ 完全本地部署
- ✅ 無數據外傳
- ✅ 企業級隱私保護
- ✅ 支援VPN環境

### 訪問控制
- 基於角色的權限管理
- API金鑰認證
- 操作日誌記錄
- 敏感數據遮罩

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

### 開發環境
```bash
# 克隆專案
git clone https://github.com/glen200392/AI-HR-REG.git

# 安裝開發依賴
pip install -r requirements-dev.txt
npm install

# 運行測試
pytest
npm test
```

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 文件

## 🙋‍♂️ 支援與反饋

- **GitHub Issues**: 技術問題回報
- **Email**: glen200392@gmail.com
- **文檔**: 詳見項目Wiki

---

**🎯 讓AI為你的HR工作賦能！**