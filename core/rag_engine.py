from typing import List, Dict, Any, Optional
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from .model_context_protocol import MCPManager
import asyncio
from loguru import logger

class RAGEngine:
    """檢索增強生成引擎"""
    
    def __init__(self, mcp_manager: MCPManager):
        self.llm = ChatOpenAI(temperature=0.3)
        self.embeddings = OpenAIEmbeddings()
        self.mcp_manager = mcp_manager
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # 設置上下文壓縮檢索器
        self.compressor = LLMChainExtractor.from_llm(self.llm)
        
    async def process_documents(self, 
                              raw_documents: List[Dict[str, Any]]) -> List[Document]:
        """處理和切分文檔"""
        try:
            documents = []
            for doc in raw_documents:
                # 轉換為 Langchain Document 格式
                text = doc.get('content', '')
                metadata = doc.get('metadata', {})
                metadata.update({
                    'source': doc.get('source', 'unknown'),
                    'timestamp': doc.get('timestamp', ''),
                    'doc_type': doc.get('type', 'general')
                })
                
                # 切分文檔
                splits = self.text_splitter.split_text(text)
                for i, split in enumerate(splits):
                    documents.append(Document(
                        page_content=split,
                        metadata={
                            **metadata,
                            'chunk_id': i,
                            'total_chunks': len(splits)
                        }
                    ))
            
            return documents
            
        except Exception as e:
            logger.error(f"處理文檔時發生錯誤: {str(e)}")
            raise
    
    async def setup_retriever(self, 
                            documents: List[Document],
                            retriever_type: str = "contextual") -> ContextualCompressionRetriever:
        """設置檢索器"""
        try:
            # 創建基礎檢索器
            base_retriever = Chroma.from_documents(
                documents,
                self.embeddings
            ).as_retriever(search_kwargs={"k": 5})
            
            # 根據類型設置檢索器
            if retriever_type == "contextual":
                retriever = ContextualCompressionRetriever(
                    base_compressor=self.compressor,
                    base_retriever=base_retriever
                )
            else:
                retriever = base_retriever
                
            return retriever
            
        except Exception as e:
            logger.error(f"設置檢索器時發生錯誤: {str(e)}")
            raise
    
    async def retrieve_and_generate(self,
                                  query: str,
                                  context_type: str,
                                  additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """檢索相關文檔並生成回答"""
        try:
            # 創建查詢上下文
            context = await self.mcp_manager.create_context(
                query,
                context_type,
                additional_context
            )
            
            # 準備提示
            prompt = self._prepare_generation_prompt(query, context)
            
            # 生成回答
            response = await self.llm.agenerate([prompt])
            
            # 提取相關來源
            sources = [
                {
                    'content': w.content,
                    'source': w.source,
                    'relevance': w.relevance_score
                }
                for w in context.primary_context
            ]
            
            return {
                'answer': response.generations[0][0].text,
                'sources': sources,
                'context_summary': await self.mcp_manager.get_context_summary(
                    f"{context_type}_{hash(query)}"
                )
            }
            
        except Exception as e:
            logger.error(f"檢索和生成過程中發生錯誤: {str(e)}")
            raise
    
    def _prepare_generation_prompt(self, query: str, context: Any) -> str:
        """準備生成提示"""
        # 組合主要上下文
        primary_contexts = "\n".join([
            f"來源 {i+1}:\n{w.content}"
            for i, w in enumerate(context.primary_context)
        ])
        
        # 組合次要上下文
        secondary_contexts = "\n".join([
            f"補充來源 {i+1}:\n{w.content}"
            for i, w in enumerate(context.secondary_context)
        ])
        
        # 返回完整提示
        return f"""基於以下資訊回答問題：

主要參考資料：
{primary_contexts}

補充資料：
{secondary_contexts}

全局上下文：
{context.global_context}

問題：{query}

請提供完整、準確且專業的回答。如果資訊不足，請明確指出。""" 