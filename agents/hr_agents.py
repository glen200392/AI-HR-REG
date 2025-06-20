from typing import Dict, Any, List
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from .base_agent import BaseAgent
from database.vector_store import ChromaVectorStore
from utils.text_processor import TextProcessor
import json

class LegalAdvisorAgent(BaseAgent):
    """處理勞動法規諮詢的專門 Agent"""
    
    def __init__(self):
        super().__init__(temperature=0.3)  # 法規諮詢需要更精確的回答
        self.vector_store = ChromaVectorStore()
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的勞動法規顧問。你的職責是：
        1. 解釋勞動法規條文
        2. 提供法規遵循建議
        3. 處理勞資爭議問題
        4. 確保建議符合最新法規
        
        請始終基於現行法規提供建議，如有不確定，請明確說明。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            relevant_laws = await self.vector_store.search_laws(task)
            response = await self.llm.apredict(
                f"基於以下法規資訊回答問題：\n{json.dumps(relevant_laws, ensure_ascii=False)}\n\n問題：{task}"
            )
            return self._format_response(response, sources=relevant_laws, confidence=0.9)
        except Exception as e:
            self._log_error(e, "處理法規諮詢時")
            raise

class PolicyMakerAgent(BaseAgent):
    """處理 HR 政策制定的專門 Agent"""
    
    def __init__(self):
        super().__init__(temperature=0.7)
        self.text_processor = TextProcessor()
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位資深的 HR 政策制定顧問。你的職責是：
        1. 設計人力資源政策
        2. 制定員工手冊內容
        3. 建立績效評估制度
        4. 優化組織架構
        
        請確保建議符合產業最佳實踐和當地法規。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            processed_task = self.text_processor.enhance_policy_query(task)
            response = await self.llm.apredict(processed_task)
            return self._format_response(response, confidence=0.85)
        except Exception as e:
            self._log_error(e, "制定政策時")
            raise

class RecruitmentAgent(BaseAgent):
    """處理招聘相關事務的專門 Agent"""
    
    def __init__(self):
        super().__init__(temperature=0.6)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的招聘顧問。你的職責是：
        1. 編寫和優化職位描述
        2. 設計面試問題
        3. 評估應聘者資格
        4. 提供招聘策略建議
        
        請確保建議符合公平招聘原則和最佳實踐。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            response = await self.llm.apredict(task)
            return self._format_response(response, confidence=0.8)
        except Exception as e:
            self._log_error(e, "處理招聘事務時")
            raise

class EmployeeRelationsAgent(BaseAgent):
    """處理員工關係的專門 Agent"""
    
    def __init__(self):
        super().__init__(temperature=0.6)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位員工關係專家。你的職責是：
        1. 處理員工衝突
        2. 提供溝通建議
        3. 促進團隊合作
        4. 改善工作環境
        
        請以同理心和專業態度處理各種情況。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            response = await self.llm.apredict(task)
            return self._format_response(response, confidence=0.75)
        except Exception as e:
            self._log_error(e, "處理員工關係時")
            raise

class HRCoordinatorAgent(BaseAgent):
    """總協調 Agent，負責任務分配和結果整合"""
    
    def __init__(self):
        super().__init__(temperature=0.7)
        self.agents = {
            'legal': LegalAdvisorAgent(),
            'policy': PolicyMakerAgent(),
            'recruitment': RecruitmentAgent(),
            'relations': EmployeeRelationsAgent()
        }
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是 HR 部門的總協調者。你的職責是：
        1. 分析和分類 HR 相關問題
        2. 將任務分配給適當的專門 Agent
        3. 整合各 Agent 的回答
        4. 提供全面的解決方案
        
        請確保回答完整且符合實際需求。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 分析任務類型
            task_type = await self._analyze_task_type(task)
            
            # 獲取相應的 Agent
            agent = self.agents.get(task_type)
            if not agent:
                return self._format_response(
                    "無法確定適當的處理方式，請提供更多信息。",
                    confidence=0.3
                )
            
            # 處理任務
            result = await agent.process_task(task)
            
            # 整合和優化結果
            enhanced_result = await self._enhance_response(result)
            return enhanced_result
            
        except Exception as e:
            self._log_error(e, "協調處理任務時")
            raise
    
    async def _analyze_task_type(self, task: str) -> str:
        """分析任務類型，返回適當的 Agent 類型"""
        analysis_prompt = f"請分析以下問題屬於哪種類型（legal/policy/recruitment/relations）：\n{task}"
        response = await self.llm.apredict(analysis_prompt)
        return response.lower().strip()
    
    async def _enhance_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """優化和補充 Agent 的回答"""
        enhanced_content = await self.llm.apredict(
            f"請優化並補充以下回答：\n{result['content']}"
        )
        result['content'] = enhanced_content
        result['confidence'] = min(result['confidence'] * 1.1, 1.0)
        return result 