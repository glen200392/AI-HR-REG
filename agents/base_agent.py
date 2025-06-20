from abc import ABC, abstractmethod
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from typing import List, Dict, Any, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.system_message = self._get_system_message()
    
    @abstractmethod
    def _get_system_message(self) -> SystemMessage:
        """返回 Agent 的系統提示訊息"""
        pass
    
    @abstractmethod
    async def process_task(self, task: str) -> Dict[str, Any]:
        """處理任務的主要方法"""
        pass
    
    async def analyze_context(self, context) -> Dict[str, Any]:
        """分析上下文 - 默認實現，可被子類覆蓋"""
        # 默認實現，將上下文轉換為任務字符串
        task_description = f"Analyze context: {str(context)}"
        return await self.process_task(task_description)
    
    def _format_response(self, 
                        content: str, 
                        sources: Optional[List[str]] = None, 
                        confidence: float = 0.0,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化 Agent 的回應"""
        return {
            "content": content,
            "sources": sources or [],
            "confidence": confidence,
            "metadata": metadata or {},
            "agent_type": self.__class__.__name__
        }
    
    def _log_error(self, error: Exception, context: str = "") -> None:
        """記錄錯誤信息"""
        logger.error(f"{self.__class__.__name__} - {context}: {str(error)}")
        
    def clear_memory(self) -> None:
        """清除對話歷史"""
        self.memory.clear() 