"""
RAG Knowledge Agent - HR智能知識助手
基於檢索增強生成技術，提供精準的HR知識查詢服務
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path

# LangChain imports for RAG
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 文檔處理
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

import io
import sys
import os

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent


@dataclass
class DocumentInfo:
    """文件資訊"""
    filename: str
    file_type: str
    upload_date: datetime
    content_preview: str
    chunk_count: int
    status: str  # 'processed', 'processing', 'failed'


@dataclass
class QueryResult:
    """查詢結果"""
    question: str
    answer: str
    confidence_score: float
    source_documents: List[str]
    relevant_chunks: List[str]
    response_time: float


class RAGKnowledgeAgent(BaseAgent):
    """
    RAG智能知識助手
    
    功能：
    1. 文件上傳和處理
    2. 向量化存儲
    3. 智能檢索
    4. 生成回答
    """
    
    def __init__(self, 
                 vector_store_path: str = "./vector_store"):
        super().__init__("RAGKnowledgeAgent")
        
        self.vector_store_path = Path(vector_store_path)
        self.vector_store_path.mkdir(exist_ok=True)
        
        # LLM管理器會自動初始化
        self.llm_manager = llm_manager
        self.embeddings = None  # 將在初始化時設定
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "。", "！", "？", ";", "：", " ", ""]
        )
        
        # 向量資料庫
        self.vector_store = None
        self.qa_chain = None
        
        # 已處理文件記錄
        self.processed_documents: List[DocumentInfo] = []
        
        # 初始化標記
        self.is_initialized = False
        
        self.logger.info(f"RAG Knowledge Agent created with vector store at {vector_store_path}")
    
    async def initialize(self) -> bool:
        """異步初始化RAG Agent"""
        try:
            # 初始化LLM管理器
            llm_init_success = await self.llm_manager.initialize()
            if not llm_init_success:
                self.logger.warning("LLM Manager initialization failed, but continuing...")
            
            # 獲取embedding模型
            self.embeddings = self.llm_manager.get_current_embedding()
            if not self.embeddings:
                self.logger.error("No embedding model available")
                return False
            
            # 初始化向量存儲
            self._initialize_vector_store()
            self._setup_qa_chain()
            
            self.is_initialized = True
            self.logger.info("✅ RAG Knowledge Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG Agent: {e}")
            return False
    
    def _initialize_vector_store(self):
        """初始化向量資料庫"""
        try:
            # 嘗試載入現有的向量資料庫
            if (self.vector_store_path / "chroma.sqlite3").exists():
                self.vector_store = Chroma(
                    persist_directory=str(self.vector_store_path),
                    embedding_function=self.embeddings
                )
                self.logger.info("Loaded existing vector store")
            else:
                # 創建空的向量資料庫
                self.vector_store = Chroma(
                    persist_directory=str(self.vector_store_path),
                    embedding_function=self.embeddings
                )
                self.logger.info("Created new vector store")
        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _setup_qa_chain(self):
        """設置問答鏈"""
        # HR專用的提示模板
        hr_prompt_template = """
        你是一個專業的HR智能助手，專門協助解答人力資源相關問題。
        請根據以下提供的資料來回答問題，如果資料中沒有相關信息，請誠實說明。
        
        相關資料：
        {context}
        
        問題：{question}
        
        請提供：
        1. 直接明確的答案
        2. 相關的法規或政策依據（如有）
        3. 實務操作建議（如適用）
        4. 注意事項或風險提醒（如需要）
        
        回答：
        """
        
        prompt = PromptTemplate(
            template=hr_prompt_template,
            input_variables=["context", "question"]
        )
        
        if self.vector_store:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 4}  # 檢索最相關的4個文件片段
                ),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
    
    async def add_document(self, 
                          file_path: str, 
                          file_type: str = "auto") -> DocumentInfo:
        """
        添加文件到知識庫
        
        Args:
            file_path: 文件路徑
            file_type: 文件類型 (pdf, txt, docx, auto)
            
        Returns:
            DocumentInfo: 處理結果信息
        """
        start_time = datetime.now()
        
        try:
            # 讀取文件內容
            content = await self._extract_text_from_file(file_path, file_type)
            
            if not content.strip():
                raise ValueError("文件內容為空")
            
            # 分割文本
            documents = self.text_splitter.create_documents([content])
            
            # 添加元數據
            filename = Path(file_path).name
            for doc in documents:
                doc.metadata.update({
                    "source": filename,
                    "upload_date": start_time.isoformat(),
                    "file_type": file_type
                })
            
            # 向向量資料庫添加文件
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            
            # 記錄文件信息
            doc_info = DocumentInfo(
                filename=filename,
                file_type=file_type,
                upload_date=start_time,
                content_preview=content[:200] + "..." if len(content) > 200 else content,
                chunk_count=len(documents),
                status="processed"
            )
            
            self.processed_documents.append(doc_info)
            
            self.logger.info(f"Successfully processed document: {filename} ({len(documents)} chunks)")
            return doc_info
            
        except Exception as e:
            self.logger.error(f"Failed to process document {file_path}: {e}")
            return DocumentInfo(
                filename=Path(file_path).name,
                file_type=file_type,
                upload_date=start_time,
                content_preview="",
                chunk_count=0,
                status="failed"
            )
    
    async def _extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """從文件中提取文本"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 自動檢測文件類型
        if file_type == "auto":
            file_type = file_path.suffix.lower().lstrip('.')
        
        if file_type in ["txt", "md"]:
            return file_path.read_text(encoding="utf-8")
        elif file_type == "pdf":
            # TODO: 添加PDF處理邏輯
            return "PDF處理功能待實現"
        elif file_type in ["doc", "docx"]:
            # TODO: 添加Word處理邏輯
            return "Word處理功能待實現"
        else:
            raise ValueError(f"不支援的文件類型: {file_type}")
    
    async def query(self, question: str) -> QueryResult:
        """
        查詢知識庫
        
        Args:
            question: 問題
            
        Returns:
            QueryResult: 查詢結果
        """
        start_time = datetime.now()
        
        try:
            if not self.qa_chain:
                raise ValueError("QA鏈未初始化")
            
            # 執行查詢
            result = self.qa_chain({"query": question})
            
            # 計算回應時間
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 提取來源文件
            source_docs = []
            relevant_chunks = []
            
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_docs.append(doc.metadata.get("source", "未知來源"))
                    relevant_chunks.append(doc.page_content[:100] + "...")
            
            # 簡單的信心評分 (基於答案長度和來源數量)
            confidence_score = min(0.9, len(result["result"]) / 200 + len(source_docs) * 0.1)
            
            query_result = QueryResult(
                question=question,
                answer=result["result"],
                confidence_score=confidence_score,
                source_documents=list(set(source_docs)),  # 去重
                relevant_chunks=relevant_chunks,
                response_time=response_time
            )
            
            self.logger.info(f"Query processed in {response_time:.2f}s: {question[:50]}...")
            return query_result
            
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            return QueryResult(
                question=question,
                answer=f"抱歉，查詢過程中發生錯誤：{str(e)}",
                confidence_score=0.0,
                source_documents=[],
                relevant_chunks=[],
                response_time=(datetime.now() - start_time).total_seconds()
            )
    
    def get_document_list(self) -> List[DocumentInfo]:
        """獲取已處理的文件列表"""
        return self.processed_documents.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取知識庫統計信息"""
        total_docs = len(self.processed_documents)
        successful_docs = len([d for d in self.processed_documents if d.status == "processed"])
        total_chunks = sum(d.chunk_count for d in self.processed_documents if d.status == "processed")
        
        return {
            "total_documents": total_docs,
            "successful_documents": successful_docs,
            "failed_documents": total_docs - successful_docs,
            "total_chunks": total_chunks,
            "vector_store_path": str(self.vector_store_path),
            "last_update": max([d.upload_date for d in self.processed_documents], 
                              default=datetime.now()).isoformat() if self.processed_documents else None
        }
    
    async def clear_knowledge_base(self):
        """清空知識庫"""
        try:
            # 刪除向量資料庫
            if self.vector_store_path.exists():
                import shutil
                shutil.rmtree(self.vector_store_path)
            
            # 重新初始化
            self._initialize_vector_store()
            self._setup_qa_chain()
            
            # 清空記錄
            self.processed_documents.clear()
            
            self.logger.info("Knowledge base cleared successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to clear knowledge base: {e}")
            raise
