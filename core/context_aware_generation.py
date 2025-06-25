from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from .model_context_protocol import MCPManager, ModelContext
from .rag_engine import RAGEngine
import asyncio
from loguru import logger

class ContextAwareGenerator:
    """上下文感知生成器"""
    
    def __init__(self, mcp_manager: MCPManager, rag_engine: RAGEngine):
        self.llm = ChatOpenAI(temperature=0.7)
        self.mcp_manager = mcp_manager
        self.rag_engine = rag_engine
        self.context_history = {}
        
    async def generate_response(self,
                              query: str,
                              context_type: str,
                              task_specific_context: Optional[Dict] = None) -> Dict[str, Any]:
        """生成上下文感知的回應"""
        try:
            # 獲取檢索增強的上下文
            rag_result = await self.rag_engine.retrieve_and_generate(
                query,
                context_type,
                task_specific_context
            )
            
            # 獲取歷史上下文
            history_context = self.context_history.get(context_type, [])
            
            # 準備生成提示
            prompt = self._create_context_aware_prompt(
                query,
                rag_result,
                history_context,
                task_specific_context
            )
            
            # 生成回應
            response = await self.llm.agenerate([prompt])
            
            # 更新上下文歷史
            self._update_context_history(
                context_type,
                query,
                response.generations[0][0].text,
                rag_result
            )
            
            return {
                'response': response.generations[0][0].text,
                'context_used': {
                    'rag_context': rag_result['context_summary'],
                    'history_length': len(history_context),
                    'task_context': bool(task_specific_context)
                },
                'sources': rag_result['sources']
            }
            
        except Exception as e:
            logger.error(f"生成上下文感知回應時發生錯誤: {str(e)}")
            raise
    
    def _create_context_aware_prompt(self,
                                   query: str,
                                   rag_result: Dict[str, Any],
                                   history_context: List[Dict[str, Any]],
                                   task_context: Optional[Dict] = None) -> str:
        """創建上下文感知提示"""
        # 組合檢索結果
        rag_context = rag_result['answer']
        
        # 組合歷史上下文
        history_summary = "\n".join([
            f"之前的問題：{h['query']}\n回答：{h['response']}"
            for h in history_context[-3:]  # 只使用最近的3條歷史記錄
        ])
        
        # 組合任務特定上下文
        task_specific_info = ""
        if task_context:
            task_specific_info = "\n".join([
                f"{k}: {v}" for k, v in task_context.items()
            ])
        
        # 返回完整提示
        return f"""請基於以下完整上下文生成回應：

檢索到的相關信息：
{rag_context}

歷史對話記錄：
{history_summary}

任務特定信息：
{task_specific_info}

當前問題：{query}

請生成一個專業、連貫且符合上下文的回答。確保：
1. 回答準確反映檢索到的信息
2. 考慮歷史對話的連續性
3. 整合任務特定要求
4. 保持專業的語氣和格式"""
    
    def _update_context_history(self,
                              context_type: str,
                              query: str,
                              response: str,
                              rag_result: Dict[str, Any]) -> None:
        """更新上下文歷史"""
        if context_type not in self.context_history:
            self.context_history[context_type] = []
            
        # 添加新的對話記錄
        self.context_history[context_type].append({
            'query': query,
            'response': response,
            'timestamp': asyncio.get_event_loop().time(),
            'rag_summary': rag_result['context_summary']
        })
        
        # 保持歷史記錄在合理範圍內
        if len(self.context_history[context_type]) > 10:
            self.context_history[context_type] = self.context_history[context_type][-10:]
    
    def clear_context_history(self, context_type: Optional[str] = None) -> None:
        """清除上下文歷史"""
        if context_type:
            if context_type in self.context_history:
                del self.context_history[context_type]
        else:
            self.context_history.clear() 