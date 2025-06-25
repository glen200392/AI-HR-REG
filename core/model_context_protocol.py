from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import asyncio
import json
from loguru import logger

class ContextWindow(BaseModel):
    """上下文窗口定義"""
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    source: str
    timestamp: str

class ModelContext(BaseModel):
    """模型上下文管理"""
    primary_context: List[ContextWindow]
    secondary_context: List[ContextWindow]
    global_context: Dict[str, Any]
    max_context_length: int = 4096

class MCPManager:
    """Model Context Protocol 管理器"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.context_cache = {}
        self.active_contexts = {}
    
    async def initialize_vector_store(self, documents: List[Document]):
        """初始化向量存儲"""
        self.vector_store = Chroma(
            collection_name="hr_knowledge",
            embedding_function=self.embeddings
        )
        await self.vector_store.aadd_documents(documents)
    
    async def create_context(self, 
                           query: str, 
                           context_type: str,
                           additional_metadata: Optional[Dict] = None) -> ModelContext:
        """創建查詢上下文"""
        try:
            # 獲取相關文檔
            relevant_docs = await self.vector_store.asimilarity_search_with_relevance_scores(
                query, k=5
            )
            
            # 創建上下文窗口
            primary_windows = [
                ContextWindow(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    relevance_score=score,
                    source=doc.metadata.get('source', 'unknown'),
                    timestamp=doc.metadata.get('timestamp', '')
                )
                for doc, score in relevant_docs if score > 0.7
            ]
            
            secondary_windows = [
                ContextWindow(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    relevance_score=score,
                    source=doc.metadata.get('source', 'unknown'),
                    timestamp=doc.metadata.get('timestamp', '')
                )
                for doc, score in relevant_docs if 0.3 <= score <= 0.7
            ]
            
            # 創建模型上下文
            context = ModelContext(
                primary_context=primary_windows,
                secondary_context=secondary_windows,
                global_context=additional_metadata or {}
            )
            
            # 緩存上下文
            context_id = f"{context_type}_{hash(query)}"
            self.context_cache[context_id] = context
            
            return context
            
        except Exception as e:
            logger.error(f"創建上下文時發生錯誤: {str(e)}")
            raise
    
    async def update_context(self, 
                           context_id: str, 
                           new_information: Dict[str, Any]) -> ModelContext:
        """更新現有上下文"""
        if context_id not in self.context_cache:
            raise ValueError(f"上下文 ID {context_id} 不存在")
            
        context = self.context_cache[context_id]
        
        # 更新全局上下文
        context.global_context.update(new_information)
        
        # 如果有新的相關文檔，添加到次要上下文
        if 'documents' in new_information:
            new_windows = [
                ContextWindow(
                    content=doc.get('content', ''),
                    metadata=doc.get('metadata', {}),
                    relevance_score=doc.get('relevance', 0.5),
                    source=doc.get('source', 'unknown'),
                    timestamp=doc.get('timestamp', '')
                )
                for doc in new_information['documents']
            ]
            context.secondary_context.extend(new_windows)
        
        # 確保上下文長度不超過限制
        self._trim_context(context)
        
        return context
    
    def _trim_context(self, context: ModelContext) -> None:
        """裁剪上下文以符合長度限制"""
        total_length = sum(len(w.content) for w in context.primary_context)
        total_length += sum(len(w.content) for w in context.secondary_context)
        
        while total_length > context.max_context_length and context.secondary_context:
            # 移除最不相關的次要上下文
            context.secondary_context.sort(key=lambda x: x.relevance_score)
            removed = context.secondary_context.pop(0)
            total_length -= len(removed.content)
    
    async def get_context_summary(self, context_id: str) -> Dict[str, Any]:
        """獲取上下文摘要"""
        if context_id not in self.context_cache:
            raise ValueError(f"上下文 ID {context_id} 不存在")
            
        context = self.context_cache[context_id]
        
        return {
            "primary_sources": len(context.primary_context),
            "secondary_sources": len(context.secondary_context),
            "total_tokens": sum(len(w.content.split()) for w in context.primary_context + context.secondary_context),
            "global_context_keys": list(context.global_context.keys())
        }
    
    def clear_context(self, context_id: str) -> None:
        """清除特定上下文"""
        if context_id in self.context_cache:
            del self.context_cache[context_id]
            
    def clear_all_contexts(self) -> None:
        """清除所有上下文"""
        self.context_cache.clear()
        self.active_contexts.clear() 