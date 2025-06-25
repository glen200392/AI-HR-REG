#!/bin/bash

# HR AI Platform MVP 啟動腳本
echo "🚀 啟動 HR AI Platform MVP"

# 檢查Node.js和npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安裝，請先安裝 Node.js (版本 >= 16)"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安裝，請先安裝 npm"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"

# 函數：檢查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    else
        echo "✅ 端口 $port 可用"
        return 0
    fi
}

# 檢查必要端口
echo "🔍 檢查端口狀態..."
check_port 3001 || echo "   後端端口 3001 被占用，請先停止相關服務"
check_port 5173 || echo "   前端端口 5173 被占用，請先停止相關服務"

# 設置OpenAI API Key (如果未設置)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API Key 未設置"
    echo "   請執行: export OPENAI_API_KEY='your-api-key'"
    echo "   或者程序將使用模擬AI響應"
fi

# 後端設置
echo "🔧 設置後端..."
cd backend

# 檢查後端依賴
if [ ! -d "node_modules" ]; then
    echo "📦 安裝後端依賴..."
    npm install
fi

# 設置環境變數
if [ ! -f ".env" ]; then
    echo "⚙️  創建後端環境配置..."
    cp .env.example .env
    echo "   請編輯 backend/.env 文件設置 OpenAI API Key"
fi

# 啟動後端 (背景執行)
echo "🚀 啟動後端服務 (端口 3001)..."
npm run dev > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "   後端 PID: $BACKEND_PID"

# 等待後端啟動
echo "⏳ 等待後端啟動..."
sleep 5

# 檢查後端是否啟動成功
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✅ 後端啟動成功"
else
    echo "❌ 後端啟動失敗，請檢查 backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 前端設置
echo "🔧 設置前端..."
cd ../frontend

# 檢查前端依賴
if [ ! -d "node_modules" ]; then
    echo "📦 安裝前端依賴..."
    npm install
fi

# 啟動前端
echo "🚀 啟動前端服務 (端口 5173)..."
echo "📱 應用將在 http://localhost:5173 開啟"
echo ""
echo "🎯 MVP 功能說明："
echo "   - ✅ 認知友善的用戶界面"
echo "   - ✅ 真實員工數據管理"  
echo "   - ✅ AI 驅動的員工分析"
echo "   - ✅ AI 驅動的團隊分析"
echo "   - ✅ 分析歷史記錄"
echo "   - ✅ 雙語支援 (中/英)"
echo ""
echo "🤖 AI 功能："
echo "   - OpenAI GPT-4 (需要API Key)"
echo "   - 智能降級到模擬數據"
echo "   - 真實分析與模擬分析對比"
echo ""
echo "⏹️  停止服務: Ctrl+C"
echo "📋 後端日誌: tail -f backend.log"
echo ""

# 啟動前端 (前台執行)
npm run dev

# 清理：當前端停止時，也停止後端
echo "🛑 停止服務..."
kill $BACKEND_PID 2>/dev/null
echo "✅ 服務已停止"