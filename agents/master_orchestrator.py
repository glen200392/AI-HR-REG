"""
Master Orchestrator - RAG Knowledge Management System
專門管理RAG智能知識助手，提供統一的知識查詢服務
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from datetime import datetime, timedelta
import logging
from .base_agent import BaseAgent
from .rag_knowledge_agent import RAGKnowledgeAgent, QueryResult, DocumentInfo


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AnalysisContext:
    """分析上下文數據結構"""
    employee_data: Dict[str, Any]
    organizational_data: Dict[str, Any] 
    priority_goals: List[str]
    time_horizon: str  # short_term, medium_term, long_term
    urgency_level: Priority
    business_context: Dict[str, Any]


@dataclass
class AgentInsight:
    """智能體洞察結果"""
    agent_name: str
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    risk_factors: List[str]
    opportunities: List[str]
    data_quality_score: float
    processing_time: float


@dataclass
class IntegratedStrategy:
    """整合策略輸出"""
    individual_recommendations: List[Dict[str, Any]]
    team_recommendations: List[Dict[str, Any]]
    organizational_recommendations: List[Dict[str, Any]]
    priority_score: float
    implementation_timeline: Dict[str, str]
    success_metrics: List[str]
    risk_mitigation: List[str]


class StrategicDecisionEngine:
    """戰略決策引擎 - 整合多智能體洞察"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.decision_history = []
        
    def integrate_recommendations(
        self, 
        insights: Dict[str, AgentInsight], 
        context: AnalysisContext
    ) -> IntegratedStrategy:
        """整合各智能體建議並生成統一策略"""
        
        # Step 1: 信心度加權整合
        weighted_recommendations = self._weight_by_confidence(insights)
        
        # Step 2: 優先級評分
        priority_scores = self._calculate_priority_scores(weighted_recommendations, context)
        
        # Step 3: 風險評估整合
        integrated_risks = self._integrate_risk_assessment(insights)
        
        # Step 4: 機會整合
        integrated_opportunities = self._integrate_opportunities(insights)
        
        # Step 5: 生成實施時間線
        timeline = self._generate_implementation_timeline(
            weighted_recommendations, context
        )
        
        # Step 6: 定義成功指標
        success_metrics = self._define_success_metrics(
            weighted_recommendations, context
        )
        
        return IntegratedStrategy(
            individual_recommendations=self._extract_individual_recommendations(weighted_recommendations),
            team_recommendations=self._extract_team_recommendations(weighted_recommendations),
            organizational_recommendations=self._extract_org_recommendations(weighted_recommendations),
            priority_score=max(priority_scores.values()) if priority_scores else 0.5,
            implementation_timeline=timeline,
            success_metrics=success_metrics,
            risk_mitigation=integrated_risks
        )
    
    def _weight_by_confidence(self, insights: Dict[str, AgentInsight]) -> List[Dict[str, Any]]:
        """基於信心度對建議進行加權"""
        weighted_recommendations = []
        
        for agent_name, insight in insights.items():
            weight = insight.confidence_score * insight.data_quality_score
            
            for recommendation in insight.recommendations:
                weighted_recommendation = {
                    **recommendation,
                    'source_agent': agent_name,
                    'weight': weight,
                    'original_confidence': insight.confidence_score
                }
                weighted_recommendations.append(weighted_recommendation)
        
        # 按權重排序
        weighted_recommendations.sort(key=lambda x: x['weight'], reverse=True)
        return weighted_recommendations
    
    def _calculate_priority_scores(
        self, 
        recommendations: List[Dict[str, Any]], 
        context: AnalysisContext
    ) -> Dict[str, float]:
        """計算優先級評分"""
        priority_scores = {}
        
        for rec in recommendations:
            score = rec.get('weight', 0.5)
            
            # 根據業務目標調整優先級
            if any(goal in rec.get('description', '') for goal in context.priority_goals):
                score *= 1.3
            
            # 根據緊急程度調整
            if context.urgency_level == Priority.CRITICAL:
                score *= 1.5
            elif context.urgency_level == Priority.HIGH:
                score *= 1.2
            
            priority_scores[rec.get('id', 'unknown')] = min(score, 1.0)
        
        return priority_scores
    
    def _integrate_risk_assessment(self, insights: Dict[str, AgentInsight]) -> List[str]:
        """整合風險評估"""
        all_risks = []
        risk_frequency = {}
        
        for insight in insights.values():
            for risk in insight.risk_factors:
                all_risks.append(risk)
                risk_frequency[risk] = risk_frequency.get(risk, 0) + 1
        
        # 只返回被多個智能體識別的高風險項目
        critical_risks = [
            risk for risk, freq in risk_frequency.items() 
            if freq >= 2 or any(keyword in risk.lower() for keyword in ['critical', 'severe', 'immediate'])
        ]
        
        return critical_risks
    
    def _integrate_opportunities(self, insights: Dict[str, AgentInsight]) -> List[str]:
        """整合機會分析"""
        all_opportunities = []
        opportunity_scores = {}
        
        for agent_name, insight in insights.values():
            for opportunity in insight.opportunities:
                if opportunity not in opportunity_scores:
                    opportunity_scores[opportunity] = []
                
                opportunity_scores[opportunity].append(insight.confidence_score)
        
        # 按平均信心度排序機會
        sorted_opportunities = sorted(
            opportunity_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True
        )
        
        return [opp[0] for opp in sorted_opportunities[:10]]  # 返回前10個機會
    
    def _generate_implementation_timeline(
        self,
        recommendations: List[Dict[str, Any]],
        context: AnalysisContext
    ) -> Dict[str, str]:
        """生成實施時間線"""
        timeline = {
            'immediate': [],  # 0-2 weeks
            'short_term': [],  # 2-8 weeks  
            'medium_term': [],  # 2-6 months
            'long_term': []  # 6+ months
        }
        
        for rec in recommendations[:15]:  # 只處理前15個高優先級建議
            urgency = rec.get('urgency', 'medium')
            complexity = rec.get('complexity', 'medium')
            
            if urgency == 'critical' or complexity == 'low':
                timeline['immediate'].append(rec.get('title', 'Unknown task'))
            elif urgency == 'high' and complexity == 'medium':
                timeline['short_term'].append(rec.get('title', 'Unknown task'))
            elif complexity == 'high' or rec.get('strategic_importance') == 'high':
                timeline['long_term'].append(rec.get('title', 'Unknown task'))
            else:
                timeline['medium_term'].append(rec.get('title', 'Unknown task'))
        
        return timeline
    
    def _define_success_metrics(
        self,
        recommendations: List[Dict[str, Any]],
        context: AnalysisContext
    ) -> List[str]:
        """定義成功指標"""
        metrics = set()
        
        # 基於業務目標的指標
        for goal in context.priority_goals:
            if 'retention' in goal.lower():
                metrics.add('Employee retention rate increase >15%')
            elif 'satisfaction' in goal.lower():
                metrics.add('Employee satisfaction score >4.2/5.0')
            elif 'performance' in goal.lower():
                metrics.add('Team performance metrics improvement >20%')
            elif 'efficiency' in goal.lower():
                metrics.add('HR process efficiency improvement >40%')
        
        # 基於建議類型的指標
        for rec in recommendations[:10]:
            rec_type = rec.get('type', '')
            if 'learning' in rec_type:
                metrics.add('Learning completion rate >85%')
            elif 'culture' in rec_type:
                metrics.add('Culture health index improvement >25%')
            elif 'talent' in rec_type:
                metrics.add('Internal promotion rate >30%')
        
        return list(metrics)[:8]  # 限制指標數量
    
    def _extract_individual_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取個人層面建議"""
        return [rec for rec in recommendations if rec.get('scope') == 'individual'][:5]
    
    def _extract_team_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取團隊層面建議"""
        return [rec for rec in recommendations if rec.get('scope') == 'team'][:5]
    
    def _extract_org_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取組織層面建議"""
        return [rec for rec in recommendations if rec.get('scope') == 'organization'][:5]


class MasterOrchestrator(BaseAgent):
    """Master Orchestrator - 策略協調中心"""
    
    def __init__(self):
        super().__init__(temperature=0.7)
        self.agents = {
            'brain': BrainAgent(),
            'talent': TalentAgent(),
            'culture': CultureAgent(),
            'future': FutureAgent(),
            'process': ProcessAgent()
        }
        self.decision_engine = StrategicDecisionEngine()
        self.logger = logging.getLogger(__name__)
        
    async def analyze_comprehensive(self, context: AnalysisContext) -> IntegratedStrategy:
        """進行全面分析和策略整合"""
        start_time = datetime.now()
        
        try:
            # Step 1: 並行執行各智能體分析
            insights = await self._execute_parallel_analysis(context)
            
            # Step 2: 檢查緊急情況
            emergency_response = await self._check_emergency_conditions(insights, context)
            if emergency_response:
                return emergency_response
            
            # Step 3: 整合策略建議
            integrated_strategy = self.decision_engine.integrate_recommendations(insights, context)
            
            # Step 4: 策略驗證和優化
            validated_strategy = await self._validate_and_optimize_strategy(
                integrated_strategy, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Complete analysis finished in {processing_time:.2f} seconds")
            
            return validated_strategy
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {str(e)}")
            return await self._generate_fallback_strategy(context)
    
    async def _execute_parallel_analysis(self, context: AnalysisContext) -> Dict[str, AgentInsight]:
        """並行執行各智能體分析"""
        tasks = []
        
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(
                self._run_agent_analysis(agent_name, agent, context)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        insights = {}
        for i, result in enumerate(results):
            agent_name = list(self.agents.keys())[i]
            
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent_name} failed: {str(result)}")
                # 創建默認洞察
                insights[agent_name] = AgentInsight(
                    agent_name=agent_name,
                    recommendations=[],
                    confidence_score=0.3,
                    risk_factors=[f"Agent {agent_name} analysis failed"],
                    opportunities=[],
                    data_quality_score=0.3,
                    processing_time=0.0
                )
            else:
                insights[agent_name] = result
        
        return insights
    
    async def _run_agent_analysis(
        self, 
        agent_name: str, 
        agent: BaseAgent, 
        context: AnalysisContext
    ) -> AgentInsight:
        """運行單個智能體分析"""
        start_time = datetime.now()
        
        try:
            analysis_result = await agent.analyze_context(context)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AgentInsight(
                agent_name=agent_name,
                recommendations=analysis_result.get('recommendations', []),
                confidence_score=analysis_result.get('confidence', 0.7),
                risk_factors=analysis_result.get('risks', []),
                opportunities=analysis_result.get('opportunities', []),
                data_quality_score=analysis_result.get('data_quality', 0.8),
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Agent {agent_name} analysis failed: {str(e)}")
            raise
    
    async def _check_emergency_conditions(
        self, 
        insights: Dict[str, AgentInsight], 
        context: AnalysisContext
    ) -> Optional[IntegratedStrategy]:
        """檢查是否存在需要緊急處理的情況"""
        
        critical_risks = []
        high_urgency_count = 0
        
        for insight in insights.values():
            for risk in insight.risk_factors:
                if any(keyword in risk.lower() for keyword in 
                      ['critical', 'immediate', 'urgent', 'crisis', 'severe']):
                    critical_risks.append(risk)
            
            if insight.confidence_score > 0.8 and len(insight.risk_factors) > 3:
                high_urgency_count += 1
        
        # 如果檢測到緊急情況，生成緊急響應策略
        if len(critical_risks) >= 2 or high_urgency_count >= 3:
            return await self._generate_emergency_strategy(critical_risks, context)
        
        return None
    
    async def _generate_emergency_strategy(
        self, 
        critical_risks: List[str], 
        context: AnalysisContext
    ) -> IntegratedStrategy:
        """生成緊急響應策略"""
        
        emergency_recommendations = []
        
        for i, risk in enumerate(critical_risks[:5]):
            recommendation = {
                'id': f'emergency_{i}',
                'title': f'Emergency Response: {risk}',
                'description': f'Immediate action required to address: {risk}',
                'scope': 'organization',
                'urgency': 'critical',
                'weight': 1.0,
                'type': 'emergency_response'
            }
            emergency_recommendations.append(recommendation)
        
        return IntegratedStrategy(
            individual_recommendations=[],
            team_recommendations=[],
            organizational_recommendations=emergency_recommendations,
            priority_score=1.0,
            implementation_timeline={'immediate': [rec['title'] for rec in emergency_recommendations]},
            success_metrics=['Crisis resolution within 48 hours', 'Risk mitigation effectiveness >90%'],
            risk_mitigation=critical_risks
        )
    
    async def _validate_and_optimize_strategy(
        self, 
        strategy: IntegratedStrategy, 
        context: AnalysisContext
    ) -> IntegratedStrategy:
        """驗證和優化策略"""
        
        # 檢查資源約束
        if len(strategy.individual_recommendations + 
               strategy.team_recommendations + 
               strategy.organizational_recommendations) > 20:
            
            # 重新優化，保留最高優先級的建議
            all_recommendations = (
                strategy.individual_recommendations + 
                strategy.team_recommendations + 
                strategy.organizational_recommendations
            )
            
            # 按權重排序並限制數量
            sorted_recommendations = sorted(
                all_recommendations, 
                key=lambda x: x.get('weight', 0.5), 
                reverse=True
            )
            
            strategy.individual_recommendations = [
                rec for rec in sorted_recommendations[:7] if rec.get('scope') == 'individual'
            ]
            strategy.team_recommendations = [
                rec for rec in sorted_recommendations[:7] if rec.get('scope') == 'team'
            ]
            strategy.organizational_recommendations = [
                rec for rec in sorted_recommendations[:6] if rec.get('scope') == 'organization'
            ]
        
        return strategy
    
    async def _generate_fallback_strategy(self, context: AnalysisContext) -> IntegratedStrategy:
        """生成後備策略（當主要分析失敗時）"""
        
        fallback_recommendations = [
            {
                'id': 'fallback_1',
                'title': 'Comprehensive HR Assessment',
                'description': 'Conduct thorough assessment of current HR processes',
                'scope': 'organization',
                'urgency': 'medium',
                'weight': 0.7,
                'type': 'assessment'
            },
            {
                'id': 'fallback_2', 
                'title': 'Employee Feedback Collection',
                'description': 'Gather comprehensive employee feedback',
                'scope': 'organization',
                'urgency': 'high',
                'weight': 0.8,
                'type': 'feedback'
            }
        ]
        
        return IntegratedStrategy(
            individual_recommendations=[],
            team_recommendations=[],
            organizational_recommendations=fallback_recommendations,
            priority_score=0.6,
            implementation_timeline={
                'short_term': ['Comprehensive HR Assessment'],
                'medium_term': ['Employee Feedback Collection']
            },
            success_metrics=['Assessment completion rate 100%', 'Feedback response rate >70%'],
            risk_mitigation=['System analysis failure addressed']
        )