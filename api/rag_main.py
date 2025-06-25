"""
HR智能知識助手 - FastAPI後端主應用
整合RAG、LLM管理、文件處理等核心功能
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import uvicorn
import logging
import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 延遲導入以避免循環依賴
try:
    from agents.rag_knowledge_agent import RAGKnowledgeAgent
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: RAG Agent not available: {e}")
    RAGKnowledgeAgent = None
    RAG_AVAILABLE = False

try:
    from core.llm_manager import llm_manager
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LLM Manager not available: {e}")
    llm_manager = None
    LLM_AVAILABLE = False

try:
    from core.query_analyzer import query_analyzer
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Query Analyzer not available: {e}")
    query_analyzer = None
    ANALYZER_AVAILABLE = False

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(
    title="HR智能知識助手API",
    description="基於RAG的HR智能問答系統",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # 前端開發服務器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全域變數
rag_agent: Optional[RAGKnowledgeAgent] = None

# Pydantic模型
class QueryRequest(BaseModel):
    question: str
    
class QueryResponse(BaseModel):
    answer: str
    confidence_score: float
    source_documents: List[str]
    relevant_chunks: List[str]
    response_time: float
    complexity: str
    
class AnalysisRequest(BaseModel):
    question: str

class AnalysisResponse(BaseModel):
    complexity: str
    suggested_chunks: int
    topics: List[str]
    keywords: List[str]
    confidence_score: float
    reasoning: str

class SystemStatusResponse(BaseModel):
    status: str
    current_model: str
    document_count: int
    available_models: List[str]
    system_info: Dict[str, Any]

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str

# 依賴注入
async def get_rag_agent() -> RAGKnowledgeAgent:
    """獲取RAG智能體實例"""
    global rag_agent
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG系統尚未初始化")
    return rag_agent

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時初始化"""
    global rag_agent
    logger.info("🚀 啟動HR智能知識助手...")
    
    try:
        # 初始化RAG智能體
        rag_agent = RAGKnowledgeAgent(
            vector_store_path="./vector_store"
        )
        
        # 異步初始化
        init_success = await rag_agent.initialize()
        if not init_success:
            logger.error("❌ RAG Agent初始化失敗")
            # 繼續運行，但功能受限
        else:
            logger.info("✅ RAG Agent初始化成功")
        
        # 檢查LLM狀態
        llm_status = llm_manager.get_system_status()
        logger.info(f"📊 LLM狀態: {llm_status}")
        
    except Exception as e:
        logger.error(f"💥 啟動失敗: {e}")
        # 不拋出異常，允許API在降級模式下運行

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時清理資源"""
    logger.info("🛑 正在關閉HR智能知識助手...")

# 健康檢查端點
@app.get("/health")
async def health_check():
    """基本健康檢查"""
    return {"status": "healthy", "service": "hr-ai-assistant"}

@app.get("/health/detailed")
async def detailed_health_check():
    """詳細健康檢查"""
    health_info = {
        "status": "healthy",
        "service": "hr-ai-assistant",
        "rag_agent": "unknown",
        "llm_manager": "unknown"
    }
    
    try:
        # 檢查RAG Agent
        if rag_agent and rag_agent.is_initialized:
            health_info["rag_agent"] = "healthy"
            stats = rag_agent.get_statistics()
            health_info["document_count"] = stats["total_documents"]
        else:
            health_info["rag_agent"] = "not_initialized"
            
        # 檢查LLM Manager
        llm_status = llm_manager.get_system_status()
        health_info["llm_manager"] = "healthy" if llm_status["total_llm_instances"] > 0 else "no_models"
        health_info["available_models"] = llm_status["available_llms"]
        
        from datetime import datetime
        health_info["timestamp"] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
    
    return health_info

# RAG查詢端點
@app.post("/api/rag/query")
async def query_knowledge_base(
    request: QueryRequest,
    agent: RAGKnowledgeAgent = Depends(get_rag_agent)
):
    """智能查詢知識庫"""
    try:
        logger.info(f"📝 收到查詢: {request.question[:50]}...")
        
        # 分析查詢複雜度
        analysis = query_analyzer.analyze_query(request.question)
        logger.info(f"🔍 查詢分析: {analysis.complexity.value}, 建議片段: {analysis.suggested_chunks}")
        
        # 執行RAG查詢
        result = await agent.query(request.question)
        
        # 格式化回應
        response = {
            "success": True,
            "data": {
                "answer": result.answer,
                "confidence_score": result.confidence_score,
                "source_documents": result.source_documents,
                "relevant_chunks": result.relevant_chunks,
                "response_time": result.response_time,
                "complexity": analysis.complexity.value,
                "suggested_chunks": analysis.suggested_chunks,
                "topics": analysis.topics
            }
        }
        
        logger.info(f"✅ 查詢完成，耗時: {result.response_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"❌ 查詢失敗: {e}")
        return {
            "success": False,
            "error": f"查詢處理失敗: {str(e)}"
        }

@app.post("/api/rag/analyze")
async def analyze_query_complexity(request: AnalysisRequest):
    """分析查詢複雜度"""
    try:
        analysis = query_analyzer.analyze_query(request.question)
        
        return {
            "success": True,
            "data": {
                "complexity": analysis.complexity.value,
                "suggested_chunks": analysis.suggested_chunks,
                "topics": analysis.topics,
                "keywords": analysis.keywords,
                "confidence_score": analysis.confidence_score,
                "reasoning": analysis.reasoning
            }
        }
    except Exception as e:
        logger.error(f"查詢分析失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# 文件管理端點
@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    agent: RAGKnowledgeAgent = Depends(get_rag_agent)
):
    """上傳並處理文件"""
    try:
        logger.info(f"📤 上傳文件: {file.filename}")
        
        # 檢查文件類型
        allowed_types = [".pdf", ".doc", ".docx", ".txt", ".md"]
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_types:
            return {
                "success": False,
                "error": f"不支援的文件類型: {file_ext}"
            }
        
        # 保存文件到臨時位置
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / file.filename
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 處理文件
        doc_info = await agent.add_document(str(temp_file_path), file_ext.lstrip('.'))
        
        # 清理臨時文件
        temp_file_path.unlink()
        
        return {
            "success": True,
            "data": {
                "id": doc_info.filename,
                "filename": doc_info.filename,
                "file_type": doc_info.file_type,
                "upload_date": doc_info.upload_date.isoformat(),
                "chunk_count": doc_info.chunk_count,
                "status": doc_info.status,
                "file_size": len(content)
            }
        }
        
    except Exception as e:
        logger.error(f"文件上傳失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/documents/recent")
async def get_recent_documents(
    limit: int = 10,
    agent: RAGKnowledgeAgent = Depends(get_rag_agent)
):
    """獲取最近上傳的文件"""
    try:
        documents = agent.get_document_list()
        
        # 按上傳時間排序並限制數量
        recent_docs = sorted(
            documents, 
            key=lambda x: x.upload_date, 
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "data": [
                {
                    "id": doc.filename,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "upload_date": doc.upload_date.isoformat(),
                    "chunk_count": doc.chunk_count,
                    "status": doc.status,
                    "file_size": 0  # TODO: 實現文件大小追蹤
                }
                for doc in recent_docs
            ]
        }
    except Exception as e:
        logger.error(f"獲取文件列表失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# 系統狀態端點
@app.get("/api/system/status")
async def get_system_status():
    """獲取系統狀態"""
    try:
        # RAG Agent狀態
        rag_stats = rag_agent.get_statistics() if rag_agent else {}
        
        # LLM狀態
        llm_status = llm_manager.get_system_status()
        
        # 模型健康檢查
        model_health = await llm_manager.check_all_models_health()
        
        return {
            "success": True,
            "data": {
                "status": "已就緒" if rag_agent and rag_agent.is_initialized else "初始化中",
                "current_model": llm_status.get("current_llm", "未知"),
                "document_count": rag_stats.get("total_documents", 0),
                "available_models": llm_status.get("available_llms", []),
                "model_health": model_health,
                "system_info": {
                    "total_chunks": rag_stats.get("total_chunks", 0),
                    "vector_store_path": rag_stats.get("vector_store_path", ""),
                    "last_update": rag_stats.get("last_update", "")
                }
            }
        }
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/system/llm-status")
async def get_llm_status():
    """獲取LLM模型狀態"""
    try:
        status = llm_manager.get_system_status()
        health = await llm_manager.check_all_models_health()
        
        return {
            "success": True,
            "data": {
                "system_status": status,
                "model_health": health
            }
        }
    except Exception as e:
        logger.error(f"獲取LLM狀態失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# 聊天會話管理（簡單實現）
@app.get("/api/chat/sessions")
async def get_chat_sessions():
    """獲取聊天會話列表"""
    # TODO: 實現數據庫存儲
    return {
        "success": True,
        "data": []
    }

@app.post("/api/chat/sessions")
async def create_chat_session():
    """創建新的聊天會話"""
    # TODO: 實現數據庫存儲
    return {
        "success": True,
        "data": {
            "id": "temp_session",
            "title": "新對話",
            "created_at": "2024-01-01T00:00:00Z"
        }
    }

# 錯誤處理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全域異常處理"""
    logger.error(f"未處理的異常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "內部服務器錯誤",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    # 開發環境直接運行
    uvicorn.run(
        "rag_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )