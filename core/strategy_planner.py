from typing import List, Dict, Any, Optional
from app.models.knowledge_graph_models import (
    EmploymentStrategy, 
    KnowledgeGraph, 
    EntityType,
    RelationType,
    EmploymentModel
)
from core.comparison_engine import ComparisonEngine
from loguru import logger
import asyncio
from datetime import datetime
import json
import uuid
from core.model_manager import MultiModelManager, ModelType

class StrategyPlanner:
    """聘用策略規劃器 - 用於生成跨國聘用策略"""
    
    def __init__(self, 
                 knowledge_graph: KnowledgeGraph,
                 comparison_engine: ComparisonEngine,
                 model_manager: MultiModelManager):
        self.knowledge_graph = knowledge_graph
        self.comparison_engine = comparison_engine
        self.model_manager = model_manager
        self.strategy_cache = {}
    
    async def generate_strategy(self,
                              company_name: str,
                              target_countries: List[str],
                              requirements: Dict[str, Any],
                              focus_areas: Optional[Dict[str, float]] = None) -> EmploymentStrategy:
        """生成聘用策略"""
        try:
            # 檢查緩存
            cache_key = self._generate_cache_key(company_name, target_countries, requirements)
            if cache_key in self.strategy_cache:
                cached_result = self.strategy_cache[cache_key]
                # 檢查緩存是否過期 (7天)
                if (datetime.now() - cached_result['timestamp']).total_seconds() < 604800:
                    return cached_result['data']
            
            # 設置默認值
            if focus_areas is None:
                focus_areas = {
                    'legal': 1.0,
                    'tax': 1.0,
                    'insurance': 1.0,
                    'cost': 1.0,
                    'risk': 1.0
                }
            
            # 1. 獲取國家比較
            comparison = await self.comparison_engine.compare_countries(
                country_ids=target_countries,
                focus_areas=focus_areas
            )
            
            # 2. 獲取可用的聘用模式
            employment_models = await self._get_employment_models(target_countries)
            
            # 3. 為每個國家選擇最佳聘用模式
            recommended_models = await self._select_best_models(
                target_countries, 
                employment_models,
                comparison,
                requirements
            )
            
            # 4. 估算成本
            cost_estimates = await self._estimate_costs(
                target_countries,
                recommended_models,
                requirements
            )
            
            # 5. 評估風險
            risk_assessments = await self._assess_risks(
                target_countries,
                recommended_models,
                comparison
            )
            
            # 6. 生成實施步驟
            implementation_steps = await self._generate_implementation_steps(
                target_countries,
                recommended_models,
                requirements
            )
            
            # 創建策略
            strategy = EmploymentStrategy(
                company_name=company_name,
                target_countries=target_countries,
                requirements=requirements,
                recommended_models=recommended_models,
                cost_estimates=cost_estimates,
                risk_assessments=risk_assessments,
                implementation_steps=implementation_steps
            )
            
            # 更新緩存
            self.strategy_cache[cache_key] = {
                'data': strategy,
                'timestamp': datetime.now()
            }
            
            return strategy
            
        except Exception as e:
            logger.error(f"生成聘用策略時發生錯誤: {str(e)}")
            raise
    
    async def _get_employment_models(self, country_ids: List[str]) -> Dict[str, List[EmploymentModel]]:
        """獲取可用的聘用模式"""
        try:
            # 獲取所有聘用模式
            all_models = await self.knowledge_graph.query_entities(
                entity_type=EntityType.EMPLOYMENT_MODEL,
                filters={}
            )
            
            # 按國家分組
            country_models = {}
            for country_id in country_ids:
                # 篩選適用於該國家的模式
                models = [
                    model for model in all_models
                    if country_id in model.applicable_countries
                ]
                country_models[country_id] = models
            
            return country_models
            
        except Exception as e:
            logger.error(f"獲取聘用模式時發生錯誤: {str(e)}")
            return {country_id: [] for country_id in country_ids}
    
    async def _select_best_models(self,
                                country_ids: List[str],
                                employment_models: Dict[str, List[EmploymentModel]],
                                comparison,
                                requirements: Dict[str, Any]) -> Dict[str, str]:
        """為每個國家選擇最佳聘用模式"""
        try:
            # 使用LLM選擇最佳模式
            llm = self.model_manager.get_model(ModelType.GPT4)
            
            # 構建提示
            prompt = f"""基於以下信息，為每個國家選擇最佳聘用模式:
            
            公司需求:
            {json.dumps(requirements, ensure_ascii=False, indent=2)}
            
            國家比較:
            {json.dumps({
                'legal_comparison': comparison.legal_comparison,
                'tax_comparison': comparison.tax_comparison,
                'insurance_comparison': comparison.insurance_comparison,
                'cost_comparison': comparison.cost_comparison,
                'risk_comparison': comparison.risk_comparison
            }, ensure_ascii=False, indent=2)}
            
            可用聘用模式:
            {json.dumps({
                country_id: [
                    {
                        'name': model.name,
                        'description': model.description,
                        'requirements': model.requirements
                    }
                    for model in models
                ]
                for country_id, models in employment_models.items()
            }, ensure_ascii=False, indent=2)}
            
            請為每個國家選擇最佳聘用模式，並提供選擇理由。返回以下格式的JSON:
            {{
                "country_id1": {{
                    "model": "模式名稱",
                    "reason": "選擇理由"
                }},
                "country_id2": {{
                    "model": "模式名稱",
                    "reason": "選擇理由"
                }}
            }}
            """
            
            response = await llm.apredict(prompt)
            
            try:
                # 解析JSON回答
                result = json.loads(response)
                
                # 提取模式名稱
                recommended_models = {
                    country_id: data['model']
                    for country_id, data in result.items()
                }
                
                return recommended_models
                
            except:
                logger.warning(f"無法解析模式選擇結果: {response}")
                
                # 回退方案：為每個國家選擇第一個可用模式
                recommended_models = {}
                for country_id, models in employment_models.items():
                    if models:
                        recommended_models[country_id] = models[0].name
                    else:
                        recommended_models[country_id] = "直接聘用"  # 默認模式
                
                return recommended_models
            
        except Exception as e:
            logger.error(f"選擇最佳模式時發生錯誤: {str(e)}")
            return {country_id: "直接聘用" for country_id in country_ids}
    
    async def _estimate_costs(self,
                            country_ids: List[str],
                            recommended_models: Dict[str, str],
                            requirements: Dict[str, Any]) -> Dict[str, float]:
        """估算成本"""
        try:
            # 使用LLM估算成本
            llm = self.model_manager.get_model(ModelType.GPT4)
            
            # 構建提示
            prompt = f"""基於以下信息，估算每個國家的聘用成本:
            
            公司需求:
            {json.dumps(requirements, ensure_ascii=False, indent=2)}
            
            推薦聘用模式:
            {json.dumps(recommended_models, ensure_ascii=False, indent=2)}
            
            請估算每個國家的年度聘用成本（美元），考慮以下因素:
            1. 薪資成本
            2. 稅務成本
            3. 保險成本
            4. 合規成本
            5. 其他相關成本
            
            返回以下格式的JSON:
            {{
                "country_id1": 估算成本1,
                "country_id2": 估算成本2
            }}
            """
            
            response = await llm.apredict(prompt)
            
            try:
                # 解析JSON回答
                result = json.loads(response)
                return result
                
            except:
                logger.warning(f"無法解析成本估算結果: {response}")
                
                # 回退方案：為每個國家設置默認成本
                return {country_id: 50000.0 for country_id in country_ids}
            
        except Exception as e:
            logger.error(f"估算成本時發生錯誤: {str(e)}")
            return {country_id: 50000.0 for country_id in country_ids}
    
    async def _assess_risks(self,
                          country_ids: List[str],
                          recommended_models: Dict[str, str],
                          comparison) -> Dict[str, List[Dict[str, Any]]]:
        """評估風險"""
        try:
            # 使用LLM評估風險
            llm = self.model_manager.get_model(ModelType.GPT4)
            
            # 構建提示
            prompt = f"""基於以下信息，評估每個國家的聘用風險:
            
            推薦聘用模式:
            {json.dumps(recommended_models, ensure_ascii=False, indent=2)}
            
            國家比較:
            {json.dumps({
                'legal_comparison': comparison.legal_comparison,
                'tax_comparison': comparison.tax_comparison,
                'risk_comparison': comparison.risk_comparison
            }, ensure_ascii=False, indent=2)}
            
            請評估每個國家的主要風險，包括:
            1. 法規風險
            2. 稅務風險
            3. 勞資關係風險
            4. 政治風險
            5. 其他相關風險
            
            對每個風險，提供:
            - 風險描述
            - 嚴重程度 (1-5)
            - 可能性 (1-5)
            - 緩解策略
            
            返回以下格式的JSON:
            {{
                "country_id1": [
                    {{
                        "type": "風險類型1",
                        "description": "風險描述1",
                        "severity": 嚴重程度1,
                        "likelihood": 可能性1,
                        "mitigation": "緩解策略1"
                    }},
                    {{
                        "type": "風險類型2",
                        "description": "風險描述2",
                        "severity": 嚴重程度2,
                        "likelihood": 可能性2,
                        "mitigation": "緩解策略2"
                    }}
                ],
                "country_id2": [
                    ...
                ]
            }}
            """
            
            response = await llm.apredict(prompt)
            
            try:
                # 解析JSON回答
                result = json.loads(response)
                return result
                
            except:
                logger.warning(f"無法解析風險評估結果: {response}")
                
                # 回退方案：為每個國家設置默認風險
                default_risks = [
                    {
                        "type": "法規風險",
                        "description": "可能存在法規合規問題",
                        "severity": 3,
                        "likelihood": 3,
                        "mitigation": "諮詢當地法律專家"
                    },
                    {
                        "type": "稅務風險",
                        "description": "可能存在稅務合規問題",
                        "severity": 3,
                        "likelihood": 3,
                        "mitigation": "諮詢當地稅務專家"
                    }
                ]
                
                return {country_id: default_risks for country_id in country_ids}
            
        except Exception as e:
            logger.error(f"評估風險時發生錯誤: {str(e)}")
            
            default_risks = [
                {
                    "type": "法規風險",
                    "description": "可能存在法規合規問題",
                    "severity": 3,
                    "likelihood": 3,
                    "mitigation": "諮詢當地法律專家"
                },
                {
                    "type": "稅務風險",
                    "description": "可能存在稅務合規問題",
                    "severity": 3,
                    "likelihood": 3,
                    "mitigation": "諮詢當地稅務專家"
                }
            ]
            
            return {country_id: default_risks for country_id in country_ids}
    
    async def _generate_implementation_steps(self,
                                          country_ids: List[str],
                                          recommended_models: Dict[str, str],
                                          requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成實施步驟"""
        try:
            # 使用LLM生成實施步驟
            llm = self.model_manager.get_model(ModelType.GPT4)
            
            # 構建提示
            prompt = f"""基於以下信息，生成跨國聘用策略的實施步驟:
            
            公司需求:
            {json.dumps(requirements, ensure_ascii=False, indent=2)}
            
            目標國家:
            {json.dumps(country_ids, ensure_ascii=False, indent=2)}
            
            推薦聘用模式:
            {json.dumps(recommended_models, ensure_ascii=False, indent=2)}
            
            請生成詳細的實施步驟，包括:
            1. 準備階段
            2. 實施階段
            3. 監控階段
            
            對每個步驟，提供:
            - 步驟名稱
            - 步驟描述
            - 預計時間
            - 所需資源
            - 關鍵考量
            
            返回以下格式的JSON:
            [
                {{
                    "name": "步驟1",
                    "description": "步驟1描述",
                    "phase": "準備/實施/監控",
                    "timeline": "預計時間",
                    "resources": ["資源1", "資源2"],
                    "considerations": ["考量1", "考量2"]
                }},
                {{
                    "name": "步驟2",
                    "description": "步驟2描述",
                    "phase": "準備/實施/監控",
                    "timeline": "預計時間",
                    "resources": ["資源1", "資源2"],
                    "considerations": ["考量1", "考量2"]
                }}
            ]
            """
            
            response = await llm.apredict(prompt)
            
            try:
                # 解析JSON回答
                result = json.loads(response)
                return result
                
            except:
                logger.warning(f"無法解析實施步驟結果: {response}")
                
                # 回退方案：設置默認實施步驟
                default_steps = [
                    {
                        "name": "法律諮詢",
                        "description": "諮詢各目標國家的法律專家",
                        "phase": "準備",
                        "timeline": "1-2週",
                        "resources": ["法律顧問", "HR團隊"],
                        "considerations": ["確保了解所有法規要求"]
                    },
                    {
                        "name": "制定聘用合同",
                        "description": "根據各國法規制定聘用合同",
                        "phase": "準備",
                        "timeline": "2-3週",
                        "resources": ["法律顧問", "HR團隊"],
                        "considerations": ["確保合同符合當地法規"]
                    },
                    {
                        "name": "實施聘用",
                        "description": "開始聘用流程",
                        "phase": "實施",
                        "timeline": "1-3個月",
                        "resources": ["HR團隊", "招聘團隊"],
                        "considerations": ["遵循當地勞動法規"]
                    },
                    {
                        "name": "合規監控",
                        "description": "持續監控合規情況",
                        "phase": "監控",
                        "timeline": "持續",
                        "resources": ["HR團隊", "法律顧問"],
                        "considerations": ["定期審查法規變更"]
                    }
                ]
                
                return default_steps
            
        except Exception as e:
            logger.error(f"生成實施步驟時發生錯誤: {str(e)}")
            
            default_steps = [
                {
                    "name": "法律諮詢",
                    "description": "諮詢各目標國家的法律專家",
                    "phase": "準備",
                    "timeline": "1-2週",
                    "resources": ["法律顧問", "HR團隊"],
                    "considerations": ["確保了解所有法規要求"]
                },
                {
                    "name": "制定聘用合同",
                    "description": "根據各國法規制定聘用合同",
                    "phase": "準備",
                    "timeline": "2-3週",
                    "resources": ["法律顧問", "HR團隊"],
                    "considerations": ["確保合同符合當地法規"]
                },
                {
                    "name": "實施聘用",
                    "description": "開始聘用流程",
                    "phase": "實施",
                    "timeline": "1-3個月",
                    "resources": ["HR團隊", "招聘團隊"],
                    "considerations": ["遵循當地勞動法規"]
                },
                {
                    "name": "合規監控",
                    "description": "持續監控合規情況",
                    "phase": "監控",
                    "timeline": "持續",
                    "resources": ["HR團隊", "法律顧問"],
                    "considerations": ["定期審查法規變更"]
                }
            ]
            
            return default_steps
    
    def _generate_cache_key(self, company_name: str, country_ids: List[str], requirements: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        key_parts = [
            company_name,
            ','.join(sorted(country_ids)),
            json.dumps(requirements, sort_keys=True)
        ]
        return '|'.join(key_parts)
    
    def clear_cache(self):
        """清除緩存"""
        self.strategy_cache.clear()
        logger.info("策略規劃器緩存已清除")
