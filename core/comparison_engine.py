from typing import List, Dict, Any, Optional
from app.models.knowledge_graph_models import (
    CountryComparison, 
    KnowledgeGraph, 
    EntityType,
    RelationType
)
from loguru import logger
import asyncio
from datetime import datetime
import json
import numpy as np
from core.model_manager import MultiModelManager, ModelType

class ComparisonEngine:
    """跨國比較引擎 - 用於比較不同國家的法規、稅務和保險數據"""
    
    def __init__(self, 
                 knowledge_graph: KnowledgeGraph,
                 model_manager: MultiModelManager):
        self.knowledge_graph = knowledge_graph
        self.model_manager = model_manager
        self.comparison_cache = {}
        
    async def compare_countries(self, 
                              country_ids: List[str], 
                              domains: Optional[List[str]] = None,
                              focus_areas: Optional[Dict[str, float]] = None) -> CountryComparison:
        """比較多個國家"""
        try:
            # 檢查緩存
            cache_key = self._generate_cache_key(country_ids, domains, focus_areas)
            if cache_key in self.comparison_cache:
                cached_result = self.comparison_cache[cache_key]
                # 檢查緩存是否過期 (24小時)
                if (datetime.now() - cached_result['timestamp']).total_seconds() < 86400:
                    return cached_result['data']
            
            # 設置默認值
            if domains is None:
                domains = ['legal', 'tax', 'insurance', 'cost', 'risk']
                
            if focus_areas is None:
                focus_areas = {
                    'legal': 1.0,
                    'tax': 1.0,
                    'insurance': 1.0,
                    'cost': 1.0,
                    'risk': 1.0
                }
            
            # 並行獲取各領域比較結果
            comparison_tasks = []
            
            if 'legal' in domains:
                comparison_tasks.append(self._compare_legal(country_ids))
            
            if 'tax' in domains:
                comparison_tasks.append(self._compare_tax(country_ids))
            
            if 'insurance' in domains:
                comparison_tasks.append(self._compare_insurance(country_ids))
            
            if 'cost' in domains:
                comparison_tasks.append(self._compare_cost(country_ids))
            
            if 'risk' in domains:
                comparison_tasks.append(self._compare_risk(country_ids))
            
            # 等待所有比較完成
            results = await asyncio.gather(*comparison_tasks)
            
            # 整合結果
            comparison_result = CountryComparison(
                countries=country_ids,
                legal_comparison=results[0] if 'legal' in domains else {},
                tax_comparison=results[1] if 'tax' in domains else {},
                insurance_comparison=results[2] if 'insurance' in domains else {},
                cost_comparison=results[3] if 'cost' in domains else {},
                risk_comparison=results[4] if 'risk' in domains else {},
                recommendation=""
            )
            
            # 生成綜合建議
            recommendation = await self._generate_recommendation(comparison_result, focus_areas)
            comparison_result.recommendation = recommendation
            
            # 更新緩存
            self.comparison_cache[cache_key] = {
                'data': comparison_result,
                'timestamp': datetime.now()
            }
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"比較國家時發生錯誤: {str(e)}")
            raise
    
    async def _compare_legal(self, country_ids: List[str]) -> Dict[str, Any]:
        """比較法規"""
        try:
            # 獲取各國法規
            country_laws = {}
            for country_id in country_ids:
                laws = await self.knowledge_graph.query_entities(
                    entity_type=EntityType.LAW,
                    filters={'country_id': country_id}
                )
                country_laws[country_id] = laws
            
            # 提取關鍵法規類別
            all_categories = set()
            for laws in country_laws.values():
                for law in laws:
                    all_categories.update(law.categories)
            
            # 按類別比較
            category_comparisons = {}
            for category in all_categories:
                category_comparisons[category] = await self._compare_category_laws(
                    country_laws, category
                )
            
            # 計算整體合規難度評分
            compliance_scores = {}
            for country_id in country_ids:
                # 計算該國家在各類別的平均分數
                scores = []
                for category, comparison in category_comparisons.items():
                    if country_id in comparison['scores']:
                        scores.append(comparison['scores'][country_id])
                
                if scores:
                    compliance_scores[country_id] = sum(scores) / len(scores)
                else:
                    compliance_scores[country_id] = 0
            
            return {
                'category_comparisons': category_comparisons,
                'compliance_scores': compliance_scores,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比較法規時發生錯誤: {str(e)}")
            return {}
    
    async def _compare_category_laws(self, country_laws: Dict[str, List[Any]], category: str) -> Dict[str, Any]:
        """比較特定類別的法規"""
        # 提取各國該類別的法規
        category_laws = {}
        for country_id, laws in country_laws.items():
            category_laws[country_id] = [
                law for law in laws if category in law.categories
            ]
        
        # 使用LLM分析比較
        llm = self.model_manager.get_model(ModelType.GPT4)
        
        # 構建提示
        prompt = f"""請比較以下國家在 {category} 類別的勞動法規:
        
        {json.dumps(category_laws, ensure_ascii=False, indent=2)}
        
        請提供以下格式的JSON回答:
        {{
            "summary": "整體比較摘要",
            "key_differences": [
                {{
                    "aspect": "方面1",
                    "differences": {{
                        "country1": "描述1",
                        "country2": "描述2"
                    }}
                }}
            ],
            "scores": {{
                "country1": 分數1,  // 1-10分，分數越高表示合規難度越高
                "country2": 分數2
            }}
        }}
        """
        
        response = await llm.apredict(prompt)
        
        try:
            # 解析JSON回答
            result = json.loads(response)
            return result
        except:
            logger.warning(f"無法解析法規比較結果: {response}")
            return {
                'summary': '無法生成比較摘要',
                'key_differences': [],
                'scores': {country_id: 5 for country_id in country_laws.keys()}
            }
    
    async def _compare_tax(self, country_ids: List[str]) -> Dict[str, Any]:
        """比較稅務"""
        try:
            # 獲取各國稅務系統
            tax_systems = {}
            for country_id in country_ids:
                systems = await self.knowledge_graph.query_entities(
                    entity_type=EntityType.TAX,
                    filters={'country_id': country_id}
                )
                if systems:
                    tax_systems[country_id] = systems[0]
            
            # 比較所得稅率
            income_tax_comparison = {}
            for country_id, system in tax_systems.items():
                income_tax_comparison[country_id] = system.income_tax_rates
            
            # 比較社會保障稅率
            social_security_comparison = {}
            for country_id, system in tax_systems.items():
                social_security_comparison[country_id] = system.social_security_rates
            
            # 比較稅務協定
            treaty_comparison = {}
            for country_id, system in tax_systems.items():
                treaty_comparison[country_id] = system.tax_treaties
            
            # 計算總體稅務負擔
            tax_burden = {}
            for country_id, system in tax_systems.items():
                # 簡化計算，使用平均所得稅率和社會保障稅率
                avg_income_tax = sum(system.income_tax_rates.values()) / len(system.income_tax_rates)
                avg_social_security = sum(system.social_security_rates.values()) / len(system.social_security_rates)
                tax_burden[country_id] = avg_income_tax + avg_social_security
            
            return {
                'income_tax_comparison': income_tax_comparison,
                'social_security_comparison': social_security_comparison,
                'treaty_comparison': treaty_comparison,
                'tax_burden': tax_burden,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比較稅務時發生錯誤: {str(e)}")
            return {}
    
    async def _compare_insurance(self, country_ids: List[str]) -> Dict[str, Any]:
        """比較保險"""
        try:
            # 獲取各國保險系統
            insurance_systems = {}
            for country_id in country_ids:
                systems = await self.knowledge_graph.query_entities(
                    entity_type=EntityType.INSURANCE,
                    filters={'country_id': country_id}
                )
                if systems:
                    insurance_systems[country_id] = systems[0]
            
            # 比較強制保險
            mandatory_comparison = {}
            for country_id, system in insurance_systems.items():
                mandatory_comparison[country_id] = system.mandatory_insurances
            
            # 比較雇主繳納比例
            employer_comparison = {}
            for country_id, system in insurance_systems.items():
                employer_comparison[country_id] = system.employer_contributions
            
            # 比較員工繳納比例
            employee_comparison = {}
            for country_id, system in insurance_systems.items():
                employee_comparison[country_id] = system.employee_contributions
            
            # 計算雇主總保險成本
            employer_cost = {}
            for country_id, system in insurance_systems.items():
                employer_cost[country_id] = sum(system.employer_contributions.values())
            
            return {
                'mandatory_comparison': mandatory_comparison,
                'employer_comparison': employer_comparison,
                'employee_comparison': employee_comparison,
                'employer_cost': employer_cost,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比較保險時發生錯誤: {str(e)}")
            return {}
    
    async def _compare_cost(self, country_ids: List[str]) -> Dict[str, Any]:
        """比較成本"""
        try:
            # 獲取各國成本
            country_costs = {}
            for country_id in country_ids:
                costs = await self.knowledge_graph.query_entities(
                    entity_type=EntityType.COST,
                    filters={'country_id': country_id}
                )
                country_costs[country_id] = costs
            
            # 按成本類型分組
            cost_types = {}
            for country_id, costs in country_costs.items():
                for cost in costs:
                    if cost.name not in cost_types:
                        cost_types[cost.name] = {}
                    cost_types[cost.name][country_id] = {
                        'amount': cost.amount,
                        'currency': cost.currency,
                        'frequency': cost.frequency
                    }
            
            # 計算總成本
            total_costs = {}
            for country_id, costs in country_costs.items():
                # 簡化計算，假設所有成本都是年度成本
                total = sum(cost.amount for cost in costs)
                total_costs[country_id] = total
            
            return {
                'cost_types': cost_types,
                'total_costs': total_costs,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比較成本時發生錯誤: {str(e)}")
            return {}
    
    async def _compare_risk(self, country_ids: List[str]) -> Dict[str, Any]:
        """比較風險"""
        try:
            # 獲取各國風險
            country_risks = {}
            for country_id in country_ids:
                risks = await self.knowledge_graph.query_entities(
                    entity_type=EntityType.RISK,
                    filters={'country_id': country_id}
                )
                country_risks[country_id] = risks
            
            # 按風險類型分組
            risk_types = {}
            for country_id, risks in country_risks.items():
                for risk in risks:
                    if risk.name not in risk_types:
                        risk_types[risk.name] = {}
                    risk_types[risk.name][country_id] = {
                        'severity': risk.severity,
                        'likelihood': risk.likelihood,
                        'risk_score': risk.severity * risk.likelihood,
                        'mitigation_strategies': risk.mitigation_strategies
                    }
            
            # 計算總風險分數
            risk_scores = {}
            for country_id, risks in country_risks.items():
                if risks:
                    # 計算風險分數 = 嚴重性 * 可能性
                    scores = [risk.severity * risk.likelihood for risk in risks]
                    risk_scores[country_id] = sum(scores) / len(scores)
                else:
                    risk_scores[country_id] = 0
            
            return {
                'risk_types': risk_types,
                'risk_scores': risk_scores,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比較風險時發生錯誤: {str(e)}")
            return {}
    
    async def _generate_recommendation(self, comparison: CountryComparison, focus_areas: Dict[str, float]) -> str:
        """生成綜合建議"""
        try:
            # 使用LLM生成建議
            llm = self.model_manager.get_model(ModelType.GPT4)
            
            # 構建提示
            prompt = f"""基於以下跨國比較結果，生成聘用策略建議:
            
            比較國家: {', '.join(comparison.countries)}
            
            法規比較:
            {json.dumps(comparison.legal_comparison, ensure_ascii=False, indent=2)}
            
            稅務比較:
            {json.dumps(comparison.tax_comparison, ensure_ascii=False, indent=2)}
            
            保險比較:
            {json.dumps(comparison.insurance_comparison, ensure_ascii=False, indent=2)}
            
            成本比較:
            {json.dumps(comparison.cost_comparison, ensure_ascii=False, indent=2)}
            
            風險比較:
            {json.dumps(comparison.risk_comparison, ensure_ascii=False, indent=2)}
            
            重點領域權重:
            {json.dumps(focus_areas, ensure_ascii=False, indent=2)}
            
            請提供全面的建議，包括:
            1. 各國優缺點分析
            2. 最適合的聘用模式
            3. 成本和風險考量
            4. 具體實施建議
            """
            
            recommendation = await llm.apredict(prompt)
            return recommendation
            
        except Exception as e:
            logger.error(f"生成建議時發生錯誤: {str(e)}")
            return "無法生成建議，請稍後再試。"
    
    def _generate_cache_key(self, country_ids: List[str], domains: Optional[List[str]], focus_areas: Optional[Dict[str, float]]) -> str:
        """生成緩存鍵"""
        key_parts = [
            ','.join(sorted(country_ids)),
            ','.join(sorted(domains)) if domains else 'all',
            json.dumps(focus_areas, sort_keys=True) if focus_areas else 'default'
        ]
        return '|'.join(key_parts)
    
    def clear_cache(self):
        """清除緩存"""
        self.comparison_cache.clear()
        logger.info("比較引擎緩存已清除")
