from typing import Dict, List, Any, Optional
from langchain.schema import SystemMessage
from .base_agent import BaseAgent
from loguru import logger
import json
import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

class CountryLegalExpertAgent(BaseAgent):
    """國家法規專家Agent - 專注於特定國家的勞動法規分析"""
    
    def __init__(self, country_code: str, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.3)  # 法規分析需要低溫度
        self.country_code = country_code
        self.country_name = self._get_country_name(country_code)
    
    def _get_country_name(self, code: str) -> str:
        """根據國家代碼獲取國家名稱"""
        country_map = {
            'tw': '台灣',
            'jp': '日本',
            'us': '美國',
            'sg': '新加坡',
            'cn': '中國',
            'vn': '越南'
        }
        return country_map.get(code.lower(), code)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content=f"""你是一位專精於{self.country_name}勞動法規的專家。你的職責是：
        1. 提供{self.country_name}勞動法規的準確解釋
        2. 分析法規對聘用決策的影響
        3. 識別法規風險和合規要求
        4. 追蹤法規變更和最新發展
        
        請確保所有建議都基於最新的法規，並明確指出任何不確定性。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 構建專業查詢
            enhanced_task = f"作為{self.country_name}勞動法規專家，{task}"
            
            # 生成回答
            response = await self.llm.apredict(enhanced_task)
            
            return self._format_response(
                content=response,
                confidence=0.85,
                metadata={
                    'country': self.country_name,
                    'country_code': self.country_code,
                    'domain': 'labor_law'
                }
            )
        except Exception as e:
            self._log_error(e, f"處理{self.country_name}法規任務時")
            raise

class TaxExpertAgent(BaseAgent):
    """稅務專家Agent - 專注於跨國稅務分析"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.3)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的跨國稅務專家。你的職責是：
        1. 分析各國稅務制度對僱傭關係的影響
        2. 提供稅務優化建議
        3. 評估稅務風險和合規要求
        4. 比較不同國家的稅務負擔
        
        請確保所有建議都基於最新的稅法，並考慮國際稅務協定的影響。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 構建專業查詢
            enhanced_task = f"作為跨國稅務專家，{task}"
            
            # 生成回答
            response = await self.llm.apredict(enhanced_task)
            
            return self._format_response(
                content=response,
                confidence=0.8,
                metadata={
                    'domain': 'tax'
                }
            )
        except Exception as e:
            self._log_error(e, "處理稅務任務時")
            raise

class InsuranceExpertAgent(BaseAgent):
    """保險專家Agent - 專注於跨國保險和福利分析"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.4)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的跨國保險和員工福利專家。你的職責是：
        1. 分析各國保險制度和福利要求
        2. 提供福利設計和優化建議
        3. 評估保險成本和風險
        4. 比較不同國家的保險負擔
        
        請確保所有建議都基於最新的保險法規，並考慮成本效益和員工需求。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 構建專業查詢
            enhanced_task = f"作為跨國保險和福利專家，{task}"
            
            # 生成回答
            response = await self.llm.apredict(enhanced_task)
            
            return self._format_response(
                content=response,
                confidence=0.8,
                metadata={
                    'domain': 'insurance'
                }
            )
        except Exception as e:
            self._log_error(e, "處理保險任務時")
            raise

class EmploymentStrategyAgent(BaseAgent):
    """聘用策略Agent - 專注於跨國聘用策略規劃"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.5)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的跨國聘用策略專家。你的職責是：
        1. 設計最佳聘用模式和策略
        2. 評估不同聘用模式的成本和風險
        3. 提供合規和優化建議
        4. 制定實施路線圖
        
        請確保所有建議都考慮法規、稅務、保險等多方面因素，並根據公司具體需求提供個性化建議。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 構建專業查詢
            enhanced_task = f"作為跨國聘用策略專家，{task}"
            
            # 生成回答
            response = await self.llm.apredict(enhanced_task)
            
            return self._format_response(
                content=response,
                confidence=0.85,
                metadata={
                    'domain': 'employment_strategy'
                }
            )
        except Exception as e:
            self._log_error(e, "處理聘用策略任務時")
            raise

class ComparisonAnalysisAgent(BaseAgent):
    """比較分析Agent - 專注於跨國數據比較和可視化"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.4)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的跨國數據比較和分析專家。你的職責是：
        1. 比較不同國家的法規、稅務和保險數據
        2. 生成清晰的比較表格和圖表
        3. 識別關鍵差異和相似點
        4. 提供數據驅動的決策建議
        
        請確保所有比較都基於可靠數據，並以清晰、易懂的方式呈現。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 構建專業查詢
            enhanced_task = f"作為跨國數據比較專家，{task}。請提供清晰的比較表格和分析。"
            
            # 生成回答
            response = await self.llm.apredict(enhanced_task)
            
            return self._format_response(
                content=response,
                confidence=0.8,
                metadata={
                    'domain': 'comparison_analysis'
                }
            )
        except Exception as e:
            self._log_error(e, "處理比較分析任務時")
            raise

class HRStrategyCoordinator(BaseAgent):
    """HR策略協調Agent - 協調多個專家Agent並整合結果"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name=model_name, temperature=0.6)
        
        # 初始化專家Agent
        self.country_experts = {
            'tw': CountryLegalExpertAgent('tw'),
            'jp': CountryLegalExpertAgent('jp'),
            'us': CountryLegalExpertAgent('us'),
            'sg': CountryLegalExpertAgent('sg')
        }
        
        self.domain_experts = {
            'tax': TaxExpertAgent(),
            'insurance': InsuranceExpertAgent(),
            'strategy': EmploymentStrategyAgent(),
            'comparison': ComparisonAnalysisAgent()
        }
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是HR策略團隊的總協調者。你的職責是：
        1. 分析用戶需求並分配給適當的專家
        2. 整合各專家的分析結果
        3. 提供全面的跨國HR策略建議
        4. 確保建議的一致性和實用性
        
        請確保回答全面、準確，並考慮法規、稅務、保險等多方面因素。""")
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        try:
            # 分析任務類型和涉及的國家
            task_analysis = await self._analyze_task(task)
            
            # 收集各專家的回答
            expert_responses = await self._collect_expert_responses(task, task_analysis)
            
            # 整合回答
            integrated_response = await self._integrate_responses(task, expert_responses)
            
            return self._format_response(
                content=integrated_response,
                confidence=0.9,
                metadata={
                    'task_type': task_analysis['task_type'],
                    'countries': task_analysis['countries'],
                    'domains': task_analysis['domains']
                }
            )
        except Exception as e:
            self._log_error(e, "協調處理任務時")
            raise
    
    async def _analyze_task(self, task: str) -> Dict[str, Any]:
        """分析任務類型和涉及的國家"""
        analysis_prompt = f"""請分析以下查詢，並以JSON格式返回：
        1. task_type: 任務類型 (comparison, strategy, legal, tax, insurance)
        2. countries: 涉及的國家代碼列表 (tw, jp, us, sg, cn, vn等)
        3. domains: 涉及的領域列表 (legal, tax, insurance, strategy, comparison)
        
        查詢: {task}
        
        JSON格式回答:"""
        
        response = await self.llm.apredict(analysis_prompt)
        
        try:
            # 嘗試解析JSON
            analysis = json.loads(response)
            return analysis
        except:
            # 如果解析失敗，返回默認分析
            logger.warning(f"無法解析任務分析結果: {response}")
            return {
                'task_type': 'general',
                'countries': ['tw'],
                'domains': ['legal', 'strategy']
            }
    
    async def _collect_expert_responses(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """收集各專家的回答"""
        responses = []
        
        # 收集國家專家回答
        for country in analysis['countries']:
            if country in self.country_experts:
                expert = self.country_experts[country]
                response = await expert.process_task(task)
                responses.append(response)
        
        # 收集領域專家回答
        for domain in analysis['domains']:
            if domain in self.domain_experts:
                expert = self.domain_experts[domain]
                response = await expert.process_task(task)
                responses.append(response)
        
        return responses
    
    async def _integrate_responses(self, task: str, responses: List[Dict[str, Any]]) -> str:
        """整合各專家的回答"""
        if not responses:
            return "無法獲取專家回答，請提供更多信息。"
        
        # 提取各專家的內容
        expert_contents = [
            f"專家 {i+1} ({r.get('metadata', {}).get('domain', '未知')}{'/' + r.get('metadata', {}).get('country', '') if 'country' in r.get('metadata', {}) else ''}):\n{r['content']}"
            for i, r in enumerate(responses)
        ]
        
        # 構建整合提示
        integration_prompt = f"""基於以下專家回答，提供一個全面、連貫的回應：
        
        原始問題: {task}
        
        {chr(10).join(expert_contents)}
        
        請整合上述專家意見，提供一個全面的回答，包括：
        1. 跨國法規比較（如適用）
        2. 稅務和保險考量（如適用）
        3. 具體的聘用策略建議
        4. 實施步驟和注意事項
        
        回答:"""
        
        # 生成整合回答
        integrated_response = await self.llm.apredict(integration_prompt)
        
        return integrated_response
