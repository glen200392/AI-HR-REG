# 高質量HR AI助手

一個專注於內容質量和易用性的HR人工智能分析工具。

## ✨ 核心特色

- **多LLM支持**: OpenAI、Claude、Groq、Ollama本地模型
- **專業HR分析**: 基於15年HR經驗的專業提示模板
- **質量保證**: 自動評估和改進分析質量
- **繁體中文**: 完整支援台灣HR術語和職場文化
- **即插即用**: 5分鐘內完成安裝和使用

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 最小安裝（使用備用回應）
pip install python-dotenv

# 基本安裝（支持Ollama本地模型）
pip install requests python-dotenv

# 完整安裝（支持所有LLM）
pip install -r simple_requirements.txt
```

### 2. 配置LLM（可選）

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"
export LLM_PROVIDER="openai"

# Claude
export ANTHROPIC_API_KEY="your-api-key" 
export LLM_PROVIDER="claude"

# Ollama（本地運行）
export LLM_PROVIDER="ollama"
export OLLAMA_MODEL="llama2:13b"

# Groq
export GROQ_API_KEY="your-api-key"
export LLM_PROVIDER="groq"
```

### 3. 立即使用

```bash
# 分析員工
python hr_ai_quality.py analyze-employee examples/employee_sample.json

# 分析團隊  
python hr_ai_quality.py analyze-team examples/team_sample.json

# 指定輸出文件
python hr_ai_quality.py analyze-employee examples/employee_sample.json --output-file result.json

# 使用特定模型
python hr_ai_quality.py analyze-employee examples/employee_sample.json --provider ollama --model llama2:13b
```

## 📊 支持的LLM提供商

| 提供商 | 推薦模型 | 優勢 | 成本 |
|--------|----------|------|------|
| **OpenAI** | gpt-4, gpt-3.5-turbo | 最佳中文理解 | 中等 |
| **Claude** | claude-3-sonnet | 專業分析能力 | 中等 |
| **Groq** | mixtral-8x7b | 超快響應速度 | 低 |
| **Ollama** | llama2:13b, mistral:7b | 完全免費本地運行 | 免費 |

## 💡 使用示例

### 員工分析示例

```json
{
  "id": "emp_001",
  "name": "王小明",
  "department": "軟體工程部",
  "role": "資深軟體工程師", 
  "experience_years": 6,
  "skills": {
    "Python": 0.9,
    "領導能力": 0.7,
    "溝通協調": 0.8
  },
  "performance_score": 0.88
}
```

### 分析結果示例

```json
{
  "employee_name": "王小明",
  "analysis_timestamp": "2024-01-15T10:30:00",
  "detailed_analysis": "## 人才特質評估\n\n王小明展現出優秀的技術能力...",
  "quality_assessment": {
    "quality_score": 0.85,
    "is_acceptable": true,
    "feedback": []
  },
  "llm_provider": "openai",
  "model_used": "gpt-4"
}
```

## 🎯 質量保證機制

### 自動質量評估

- **內容長度**: 確保分析詳細完整
- **結構化程度**: 檢查格式和組織
- **專業術語**: 驗證HR專業用詞
- **可執行性**: 評估建議的實用性

### 質量改進流程

1. **初次生成**: LLM產生分析內容
2. **質量評估**: 自動評分和反饋
3. **智能改進**: 低質量內容自動重新生成
4. **最終輸出**: 確保質量達標

## 🔧 進階配置

### 環境變量

```bash
# LLM配置
export LLM_PROVIDER="openai"              # LLM提供商
export LLM_TEMPERATURE="0.7"              # 創造性參數
export OPENAI_MODEL="gpt-4"               # 指定模型

# 質量控制
export QUALITY_THRESHOLD="0.6"            # 質量閾值
export MAX_RETRY_ATTEMPTS="2"             # 最大重試次數

# Ollama配置（本地模型）
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama2:13b"
```

### 命令行選項

```bash
python hr_ai_quality.py --help

# 常用選項
--provider {openai,claude,groq,ollama}     # 指定LLM提供商
--model MODEL_NAME                         # 指定模型名稱
--quality-threshold 0.8                    # 設定質量閾值
--output-file results.json                 # 輸出文件
```

## 📈 性能對比

| 架構 | 代碼行數 | 內存使用 | 啟動時間 | 分析質量 |
|------|----------|----------|----------|----------|
| **簡化版** | ~400行 | <50MB | 2秒 | ⭐⭐⭐⭐⭐ |
| 原複雜版 | 2500+行 | >500MB | 30秒+ | ⭐⭐⭐ |

## 🛠️ 本地模型推薦

使用Ollama運行本地模型，完全免費且隱私保護：

```bash
# 安裝Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下載推薦模型
ollama pull llama2:13b        # 最佳平衡
ollama pull mistral:7b        # 速度優先
ollama pull codellama:7b      # 技術分析
```

## 🚨 故障排除

### 常見問題

1. **No module named 'openai'**
   ```bash
   pip install openai
   ```

2. **Ollama連接失敗**
   ```bash
   # 確保Ollama服務運行
   ollama serve
   ```

3. **API密鑰錯誤**
   ```bash
   # 檢查環境變量
   echo $OPENAI_API_KEY
   ```

4. **分析質量不佳**
   ```bash
   # 提高質量閾值
   python hr_ai_quality.py analyze-employee data.json --quality-threshold 0.8
   ```

## 📝 開發指南

### 擴展分析模板

```python
# 在 HRPromptTemplates 類中添加新模板
@staticmethod
def custom_analysis_prompt(data):
    return "您的自定義分析提示..."
```

### 添加新的LLM提供商

```python
# 在 LLMProvider 枚舉中添加
NEW_PROVIDER = "new_provider"

# 在 HighQualityLLMClient 中實現
def _setup_new_provider(self):
    # 實現設置邏輯
    pass
```

## 📄 授權條款

MIT License - 可自由使用、修改和分發

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. Fork本專案
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟Pull Request

---

**讓HR分析變得簡單而專業！** 🎯