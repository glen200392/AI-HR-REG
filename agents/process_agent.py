"""
Process Agent - 流程優化專家
基於引導科學優化HR流程效能
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import json
import logging
from enum import Enum
from .base_agent import BaseAgent
from langchain.schema import SystemMessage


class ProcessType(Enum):
    MEETING = "meeting"
    DECISION_MAKING = "decision_making"
    WORKFLOW = "workflow"
    COMMUNICATION = "communication"
    PERFORMANCE_REVIEW = "performance_review"
    ONBOARDING = "onboarding"
    TRAINING = "training"
    PROJECT_MANAGEMENT = "project_management"


class EfficiencyLevel(Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class OptimizationOpportunity(Enum):
    ELIMINATE = "eliminate"
    SIMPLIFY = "simplify"
    AUTOMATE = "automate"
    INTEGRATE = "integrate"
    STANDARDIZE = "standardize"


@dataclass
class MeetingAnalysis:
    """會議分析結果"""
    meeting_id: str
    meeting_type: str
    participants_count: int
    duration_minutes: int
    efficiency_score: float  # 0.0 - 1.0
    participation_distribution: Dict[str, float]
    agenda_adherence: float  # 0.0 - 1.0
    decision_quality: float  # 0.0 - 1.0
    action_item_clarity: float  # 0.0 - 1.0
    time_utilization: float  # 0.0 - 1.0
    engagement_level: float  # 0.0 - 1.0
    bottlenecks: List[str]
    improvement_suggestions: List[str]


@dataclass
class WorkflowOptimization:
    """工作流程優化"""
    workflow_id: str
    workflow_name: str
    current_efficiency: float  # 0.0 - 1.0
    bottleneck_points: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]
    estimated_improvement: float  # percentage improvement
    implementation_complexity: str  # low, medium, high
    required_resources: List[str]
    timeline: Dict[str, str]
    success_metrics: List[str]
    risk_factors: List[str]


@dataclass
class DecisionMakingAnalysis:
    """決策制定分析"""
    decision_process_id: str
    decision_type: str
    stakeholders_involved: List[str]
    decision_speed: float  # 0.0 - 1.0 (fast to slow)
    information_quality: float  # 0.0 - 1.0
    consensus_level: float  # 0.0 - 1.0
    implementation_effectiveness: float  # 0.0 - 1.0
    decision_quality_score: float  # 0.0 - 1.0
    cognitive_biases_detected: List[str]
    process_inefficiencies: List[str]
    optimization_recommendations: List[str]


@dataclass
class ProcessBenchmark:
    """流程基準"""
    process_name: str
    industry_benchmark: float
    organizational_performance: float
    performance_gap: float
    best_practice_examples: List[str]
    improvement_potential: float
    competitive_advantage_level: str


class MeetingEfficiencyAnalyzer:
    """會議效能分析器"""
    
    def __init__(self):
        self.efficiency_metrics = {
            'time_utilization': 0.25,
            'participant_engagement': 0.20,
            'agenda_adherence': 0.20,
            'decision_effectiveness': 0.20,
            'action_item_clarity': 0.15
        }
        
        self.meeting_best_practices = {
            'optimal_duration': {
                'status_update': 15,
                'brainstorming': 60,
                'decision_making': 45,
                'planning': 90,
                'review': 30
            },
            'optimal_participants': {
                'status_update': 8,
                'brainstorming': 6,
                'decision_making': 5,
                'planning': 7,
                'review': 4
            }
        }
    
    def analyze_meeting_efficiency(self, meeting_data: Dict[str, Any]) -> MeetingAnalysis:
        """分析會議效能"""
        
        meeting_id = meeting_data.get('meeting_id', 'unknown')
        meeting_type = meeting_data.get('type', 'general')
        participants_count = meeting_data.get('participants_count', 5)
        duration_minutes = meeting_data.get('duration_minutes', 60)
        
        # 計算各項指標
        time_utilization = self._calculate_time_utilization(meeting_data)
        participation_distribution = self._analyze_participation_distribution(meeting_data)
        agenda_adherence = self._calculate_agenda_adherence(meeting_data)
        decision_quality = self._assess_decision_quality(meeting_data)
        action_item_clarity = self._evaluate_action_item_clarity(meeting_data)
        engagement_level = self._measure_engagement_level(meeting_data)
        
        # 計算總體效能分數
        efficiency_score = self._calculate_overall_efficiency(
            time_utilization, engagement_level, agenda_adherence, 
            decision_quality, action_item_clarity
        )
        
        # 識別瓶頸
        bottlenecks = self._identify_meeting_bottlenecks(meeting_data, {
            'time_utilization': time_utilization,
            'engagement_level': engagement_level,
            'agenda_adherence': agenda_adherence,
            'decision_quality': decision_quality
        })
        
        # 生成改進建議
        improvement_suggestions = self._generate_meeting_improvements(
            meeting_type, efficiency_score, bottlenecks, meeting_data
        )
        
        return MeetingAnalysis(
            meeting_id=meeting_id,
            meeting_type=meeting_type,
            participants_count=participants_count,
            duration_minutes=duration_minutes,
            efficiency_score=efficiency_score,
            participation_distribution=participation_distribution,
            agenda_adherence=agenda_adherence,
            decision_quality=decision_quality,
            action_item_clarity=action_item_clarity,
            time_utilization=time_utilization,
            engagement_level=engagement_level,
            bottlenecks=bottlenecks,
            improvement_suggestions=improvement_suggestions
        )
    
    def _calculate_time_utilization(self, meeting_data: Dict[str, Any]) -> float:
        """計算時間利用率"""
        
        # 分析會議時間分配
        time_breakdown = meeting_data.get('time_breakdown', {})
        
        productive_time = (
            time_breakdown.get('discussion', 0) +
            time_breakdown.get('decision_making', 0) +
            time_breakdown.get('planning', 0)
        )
        
        non_productive_time = (
            time_breakdown.get('off_topic', 0) +
            time_breakdown.get('technical_issues', 0) +
            time_breakdown.get('waiting', 0)
        )
        
        total_time = meeting_data.get('duration_minutes', 60)
        
        if total_time > 0:
            utilization = (productive_time / total_time)
            return min(max(utilization, 0.0), 1.0)
        
        return 0.6  # 默認值
    
    def _analyze_participation_distribution(self, meeting_data: Dict[str, Any]) -> Dict[str, float]:
        """分析參與度分佈"""
        
        participation_data = meeting_data.get('participation_data', {})
        
        if not participation_data:
            # 默認均勻分佈
            participants_count = meeting_data.get('participants_count', 5)
            return {f'participant_{i}': 1.0/participants_count for i in range(participants_count)}
        
        # 標準化參與度分數
        total_participation = sum(participation_data.values())
        if total_participation > 0:
            return {
                participant: score / total_participation 
                for participant, score in participation_data.items()
            }
        
        return participation_data
    
    def _calculate_agenda_adherence(self, meeting_data: Dict[str, Any]) -> float:
        """計算議程遵循度"""
        
        agenda_metrics = meeting_data.get('agenda_metrics', {})
        
        agenda_items_covered = agenda_metrics.get('items_covered', 0)
        total_agenda_items = agenda_metrics.get('total_items', 1)
        time_on_agenda = agenda_metrics.get('time_on_agenda_percentage', 0.8)
        
        coverage_score = agenda_items_covered / total_agenda_items if total_agenda_items > 0 else 0.8
        
        # 綜合評分
        adherence_score = (coverage_score * 0.6 + time_on_agenda * 0.4)
        
        return min(max(adherence_score, 0.0), 1.0)
    
    def _assess_decision_quality(self, meeting_data: Dict[str, Any]) -> float:
        """評估決策質量"""
        
        decision_metrics = meeting_data.get('decision_metrics', {})
        
        decisions_made = decision_metrics.get('decisions_made', 0)
        decisions_with_clear_owners = decision_metrics.get('decisions_with_owners', 0)
        decisions_with_timelines = decision_metrics.get('decisions_with_timelines', 0)
        
        if decisions_made == 0:
            return 0.7  # 沒有決策的會議給予中性分數
        
        ownership_ratio = decisions_with_clear_owners / decisions_made
        timeline_ratio = decisions_with_timelines / decisions_made
        
        quality_score = (ownership_ratio * 0.6 + timeline_ratio * 0.4)
        
        return min(max(quality_score, 0.0), 1.0)
    
    def _evaluate_action_item_clarity(self, meeting_data: Dict[str, Any]) -> float:
        """評估行動項目清晰度"""
        
        action_items = meeting_data.get('action_items', [])
        
        if not action_items:
            return 0.5  # 沒有行動項目
        
        clarity_scores = []
        for item in action_items:
            score = 0.0
            
            # 檢查清晰度要素
            if item.get('description'):
                score += 0.3
            if item.get('owner'):
                score += 0.3
            if item.get('deadline'):
                score += 0.2
            if item.get('success_criteria'):
                score += 0.2
            
            clarity_scores.append(score)
        
        return np.mean(clarity_scores)
    
    def _measure_engagement_level(self, meeting_data: Dict[str, Any]) -> float:
        """測量參與度水平"""
        
        engagement_indicators = meeting_data.get('engagement_indicators', {})
        
        active_participation_rate = engagement_indicators.get('active_participation_rate', 0.7)
        questions_asked = engagement_indicators.get('questions_asked', 5)
        interruptions = engagement_indicators.get('interruptions', 2)
        silence_periods = engagement_indicators.get('silence_periods_seconds', 30)
        
        # 標準化指標
        question_score = min(questions_asked / 10, 1.0)  # 理想狀況10個問題
        interruption_penalty = min(interruptions / 20, 0.3)  # 過多打斷扣分
        silence_penalty = min(silence_periods / 300, 0.2)  # 過長靜默扣分
        
        engagement_score = (
            active_participation_rate * 0.5 +
            question_score * 0.3 -
            interruption_penalty * 0.1 -
            silence_penalty * 0.1
        )
        
        return min(max(engagement_score, 0.0), 1.0)
    
    def _calculate_overall_efficiency(self, time_utilization: float, engagement_level: float,
                                    agenda_adherence: float, decision_quality: float,
                                    action_item_clarity: float) -> float:
        """計算總體效能"""
        
        weighted_score = (
            time_utilization * self.efficiency_metrics['time_utilization'] +
            engagement_level * self.efficiency_metrics['participant_engagement'] +
            agenda_adherence * self.efficiency_metrics['agenda_adherence'] +
            decision_quality * self.efficiency_metrics['decision_effectiveness'] +
            action_item_clarity * self.efficiency_metrics['action_item_clarity']
        )
        
        return weighted_score
    
    def _identify_meeting_bottlenecks(self, meeting_data: Dict[str, Any], 
                                    metrics: Dict[str, float]) -> List[str]:
        """識別會議瓶頸"""
        bottlenecks = []
        
        # 基於指標識別瓶頸
        if metrics['time_utilization'] < 0.6:
            bottlenecks.append('Poor time utilization - too much non-productive discussion')
        
        if metrics['engagement_level'] < 0.5:
            bottlenecks.append('Low participant engagement - passive attendance')
        
        if metrics['agenda_adherence'] < 0.6:
            bottlenecks.append('Poor agenda management - frequent off-topic discussions')
        
        if metrics['decision_quality'] < 0.5:
            bottlenecks.append('Ineffective decision-making - unclear outcomes')
        
        # 基於會議數據識別結構性瓶頸
        participants_count = meeting_data.get('participants_count', 5)
        duration_minutes = meeting_data.get('duration_minutes', 60)
        meeting_type = meeting_data.get('type', 'general')
        
        optimal_participants = self.meeting_best_practices['optimal_participants'].get(meeting_type, 6)
        optimal_duration = self.meeting_best_practices['optimal_duration'].get(meeting_type, 60)
        
        if participants_count > optimal_participants * 1.5:
            bottlenecks.append('Too many participants - communication overhead')
        
        if duration_minutes > optimal_duration * 1.5:
            bottlenecks.append('Meeting too long - fatigue and decreased focus')
        
        return bottlenecks
    
    def _generate_meeting_improvements(self, meeting_type: str, efficiency_score: float,
                                     bottlenecks: List[str], meeting_data: Dict[str, Any]) -> List[str]:
        """生成會議改進建議"""
        improvements = []
        
        # 基於瓶頸的具體建議
        if 'Poor time utilization' in ' '.join(bottlenecks):
            improvements.append('Implement strict time-boxing for agenda items')
            improvements.append('Assign a timekeeper role to maintain focus')
        
        if 'Low participant engagement' in ' '.join(bottlenecks):
            improvements.append('Use interactive techniques like round-robin discussions')
            improvements.append('Prepare participants with pre-meeting materials')
        
        if 'Poor agenda management' in ' '.join(bottlenecks):
            improvements.append('Create more specific and actionable agenda items')
            improvements.append('Use a parking lot for off-topic items')
        
        if 'Too many participants' in ' '.join(bottlenecks):
            improvements.append('Reduce attendee list to essential decision-makers only')
            improvements.append('Share information updates asynchronously instead')
        
        # 基於會議類型的特定建議
        type_specific_improvements = {
            'brainstorming': [
                'Use structured brainstorming techniques like brainwriting',
                'Separate idea generation from evaluation phases'
            ],
            'decision_making': [
                'Use decision-making frameworks like RACI or DACI',
                'Prepare decision criteria before the meeting'
            ],
            'status_update': [
                'Consider replacing with asynchronous status reports',
                'Focus only on blockers and cross-team dependencies'
            ]
        }
        
        specific_improvements = type_specific_improvements.get(meeting_type, [])
        improvements.extend(specific_improvements[:2])  # 限制數量
        
        # 基於效能分數的一般建議
        if efficiency_score < 0.5:
            improvements.append('Consider whether this meeting is necessary or could be an email')
            improvements.append('Implement meeting-free time blocks for focused work')
        
        return improvements[:6]  # 限制建議數量


class WorkflowOptimizer:
    """工作流程優化器"""
    
    def __init__(self):
        self.optimization_techniques = {
            OptimizationOpportunity.ELIMINATE: 'Remove non-value-adding steps',
            OptimizationOpportunity.SIMPLIFY: 'Reduce complexity and steps',
            OptimizationOpportunity.AUTOMATE: 'Implement automation solutions',
            OptimizationOpportunity.INTEGRATE: 'Combine related processes',
            OptimizationOpportunity.STANDARDIZE: 'Create consistent procedures'
        }
        
        self.process_patterns = {
            'approval_workflow': {
                'typical_steps': 5,
                'optimal_steps': 3,
                'automation_potential': 0.6
            },
            'onboarding_process': {
                'typical_steps': 12,
                'optimal_steps': 8,
                'automation_potential': 0.4
            },
            'performance_review': {
                'typical_steps': 8,
                'optimal_steps': 5,
                'automation_potential': 0.3
            }
        }
    
    def optimize_workflow(self, workflow_data: Dict[str, Any]) -> WorkflowOptimization:
        """優化工作流程"""
        
        workflow_id = workflow_data.get('workflow_id', 'unknown')
        workflow_name = workflow_data.get('name', 'Unknown Workflow')
        
        # 分析當前效能
        current_efficiency = self._analyze_current_efficiency(workflow_data)
        
        # 識別瓶頸點
        bottleneck_points = self._identify_bottlenecks(workflow_data)
        
        # 識別優化機會
        optimization_opportunities = self._identify_optimization_opportunities(
            workflow_data, bottleneck_points
        )
        
        # 估算改進潛力
        estimated_improvement = self._estimate_improvement_potential(
            workflow_data, optimization_opportunities
        )
        
        # 評估實施複雜度
        implementation_complexity = self._assess_implementation_complexity(
            optimization_opportunities
        )
        
        # 確定所需資源
        required_resources = self._determine_required_resources(
            optimization_opportunities, implementation_complexity
        )
        
        # 創建實施時間線
        timeline = self._create_implementation_timeline(
            optimization_opportunities, implementation_complexity
        )
        
        # 定義成功指標
        success_metrics = self._define_success_metrics(workflow_data, estimated_improvement)
        
        # 識別風險因素
        risk_factors = self._identify_risk_factors(workflow_data, optimization_opportunities)
        
        return WorkflowOptimization(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            current_efficiency=current_efficiency,
            bottleneck_points=bottleneck_points,
            optimization_opportunities=optimization_opportunities,
            estimated_improvement=estimated_improvement,
            implementation_complexity=implementation_complexity,
            required_resources=required_resources,
            timeline=timeline,
            success_metrics=success_metrics,
            risk_factors=risk_factors
        )
    
    def _analyze_current_efficiency(self, workflow_data: Dict[str, Any]) -> float:
        """分析當前效能"""
        
        # 效能指標
        cycle_time = workflow_data.get('average_cycle_time_hours', 24)
        error_rate = workflow_data.get('error_rate', 0.1)
        rework_rate = workflow_data.get('rework_rate', 0.2)
        automation_level = workflow_data.get('automation_percentage', 0.3)
        user_satisfaction = workflow_data.get('user_satisfaction_score', 0.6)
        
        # 標準化指標並計算效能分數
        time_efficiency = max(0, 1 - (cycle_time / 48))  # 48小時為基準
        quality_efficiency = 1 - error_rate - rework_rate
        automation_efficiency = automation_level
        satisfaction_efficiency = user_satisfaction
        
        overall_efficiency = (
            time_efficiency * 0.3 +
            quality_efficiency * 0.3 +
            automation_efficiency * 0.2 +
            satisfaction_efficiency * 0.2
        )
        
        return min(max(overall_efficiency, 0.0), 1.0)
    
    def _identify_bottlenecks(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別瓶頸點"""
        bottlenecks = []
        
        # 分析流程步驟
        process_steps = workflow_data.get('process_steps', [])
        
        for i, step in enumerate(process_steps):
            step_analysis = {
                'step_id': step.get('id', f'step_{i}'),
                'step_name': step.get('name', f'Step {i+1}'),
                'bottleneck_type': [],
                'impact_level': 'medium',
                'improvement_potential': 0.5
            }
            
            # 時間瓶頸
            duration = step.get('average_duration_hours', 2)
            if duration > 8:  # 超過一個工作日
                step_analysis['bottleneck_type'].append('time_consuming')
                step_analysis['impact_level'] = 'high'
            
            # 人工瓶頸
            automation_level = step.get('automation_level', 0.3)
            if automation_level < 0.2:
                step_analysis['bottleneck_type'].append('manual_intensive')
                step_analysis['improvement_potential'] = 0.8
            
            # 錯誤瓶頸
            error_rate = step.get('error_rate', 0.05)
            if error_rate > 0.1:
                step_analysis['bottleneck_type'].append('error_prone')
                step_analysis['impact_level'] = 'high'
            
            # 依賴瓶頸
            dependencies = step.get('external_dependencies', [])
            if len(dependencies) > 3:
                step_analysis['bottleneck_type'].append('dependency_heavy')
            
            # 只保留有瓶頸的步驟
            if step_analysis['bottleneck_type']:
                bottlenecks.append(step_analysis)
        
        return bottlenecks
    
    def _identify_optimization_opportunities(self, workflow_data: Dict[str, Any],
                                           bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """識別優化機會"""
        opportunities = []
        
        # 基於瓶頸分析生成優化機會
        for bottleneck in bottlenecks:
            step_opportunities = []
            
            if 'manual_intensive' in bottleneck['bottleneck_type']:
                step_opportunities.append({
                    'type': OptimizationOpportunity.AUTOMATE,
                    'description': f"Automate {bottleneck['step_name']} to reduce manual effort",
                    'effort_level': 'medium',
                    'impact_level': 'high',
                    'roi_estimate': 3.5
                })
            
            if 'time_consuming' in bottleneck['bottleneck_type']:
                step_opportunities.extend([
                    {
                        'type': OptimizationOpportunity.SIMPLIFY,
                        'description': f"Simplify {bottleneck['step_name']} to reduce cycle time",
                        'effort_level': 'low',
                        'impact_level': 'medium',
                        'roi_estimate': 2.0
                    },
                    {
                        'type': OptimizationOpportunity.ELIMINATE,
                        'description': f"Evaluate if {bottleneck['step_name']} can be eliminated",
                        'effort_level': 'low',
                        'impact_level': 'high',
                        'roi_estimate': 4.0
                    }
                ])
            
            if 'error_prone' in bottleneck['bottleneck_type']:
                step_opportunities.append({
                    'type': OptimizationOpportunity.STANDARDIZE,
                    'description': f"Standardize {bottleneck['step_name']} to reduce errors",
                    'effort_level': 'medium',
                    'impact_level': 'medium',
                    'roi_estimate': 2.5
                })
            
            # 添加步驟信息到機會
            for opp in step_opportunities:
                opp['target_step'] = bottleneck['step_id']
                opportunities.append(opp)
        
        # 添加流程級別的優化機會
        process_opportunities = self._identify_process_level_opportunities(workflow_data)
        opportunities.extend(process_opportunities)
        
        # 按ROI排序
        opportunities.sort(key=lambda x: x.get('roi_estimate', 1.0), reverse=True)
        
        return opportunities[:8]  # 限制機會數量
    
    def _identify_process_level_opportunities(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別流程級別優化機會"""
        opportunities = []
        
        # 流程整合機會
        parallel_processes = workflow_data.get('parallel_processes', [])
        if len(parallel_processes) > 1:
            opportunities.append({
                'type': OptimizationOpportunity.INTEGRATE,
                'description': 'Integrate parallel processes to reduce coordination overhead',
                'effort_level': 'high',
                'impact_level': 'medium',
                'roi_estimate': 2.2,
                'target_step': 'process_level'
            })
        
        # 標準化機會
        process_variants = workflow_data.get('process_variants', 1)
        if process_variants > 2:
            opportunities.append({
                'type': OptimizationOpportunity.STANDARDIZE,
                'description': 'Standardize process variants to reduce complexity',
                'effort_level': 'medium',
                'impact_level': 'medium',
                'roi_estimate': 2.8,
                'target_step': 'process_level'
            })
        
        return opportunities
    
    def _estimate_improvement_potential(self, workflow_data: Dict[str, Any],
                                      opportunities: List[Dict[str, Any]]) -> float:
        """估算改進潛力"""
        
        # 基於優化機會計算總改進潛力
        total_improvement = 0.0
        
        for opportunity in opportunities:
            impact_weights = {'low': 0.1, 'medium': 0.2, 'high': 0.3}
            impact_level = opportunity.get('impact_level', 'medium')
            impact_weight = impact_weights.get(impact_level, 0.2)
            
            roi_factor = min(opportunity.get('roi_estimate', 1.0) / 5.0, 1.0)
            
            opportunity_improvement = impact_weight * roi_factor
            total_improvement += opportunity_improvement
        
        # 考慮實施複雜度和風險調整
        implementation_risk = workflow_data.get('implementation_risk', 0.3)
        adjusted_improvement = total_improvement * (1 - implementation_risk * 0.5)
        
        # 轉換為百分比並限制在合理範圍內
        improvement_percentage = min(adjusted_improvement * 100, 80)  # 最大80%改進
        
        return improvement_percentage
    
    def _assess_implementation_complexity(self, opportunities: List[Dict[str, Any]]) -> str:
        """評估實施複雜度"""
        
        if not opportunities:
            return 'low'
        
        effort_levels = [opp.get('effort_level', 'medium') for opp in opportunities]
        effort_weights = {'low': 1, 'medium': 2, 'high': 3}
        
        average_effort = np.mean([effort_weights[level] for level in effort_levels])
        
        if average_effort <= 1.5:
            return 'low'
        elif average_effort <= 2.5:
            return 'medium'
        else:
            return 'high'
    
    def _determine_required_resources(self, opportunities: List[Dict[str, Any]],
                                    complexity: str) -> List[str]:
        """確定所需資源"""
        resources = []
        
        # 基於優化類型確定資源需求
        automation_opportunities = [
            opp for opp in opportunities 
            if opp.get('type') == OptimizationOpportunity.AUTOMATE
        ]
        
        if automation_opportunities:
            resources.extend(['IT development team', 'Automation tools/software'])
        
        integration_opportunities = [
            opp for opp in opportunities 
            if opp.get('type') == OptimizationOpportunity.INTEGRATE
        ]
        
        if integration_opportunities:
            resources.extend(['Process design expertise', 'Change management support'])
        
        # 基於複雜度添加資源
        complexity_resources = {
            'low': ['Process improvement training'],
            'medium': ['Project management', 'Business analyst'],
            'high': ['Dedicated project team', 'Executive sponsorship', 'External consultants']
        }
        
        resources.extend(complexity_resources.get(complexity, []))
        
        # 去重並限制數量
        return list(set(resources))[:6]
    
    def _create_implementation_timeline(self, opportunities: List[Dict[str, Any]],
                                      complexity: str) -> Dict[str, str]:
        """創建實施時間線"""
        
        # 基於複雜度確定基礎時間線
        base_timelines = {
            'low': {
                'Planning': '2-4 weeks',
                'Implementation': '4-8 weeks',
                'Testing': '2-3 weeks',
                'Rollout': '2-3 weeks'
            },
            'medium': {
                'Planning': '4-6 weeks',
                'Implementation': '8-16 weeks',
                'Testing': '3-4 weeks',
                'Rollout': '4-6 weeks'
            },
            'high': {
                'Planning': '6-10 weeks',
                'Implementation': '16-24 weeks',
                'Testing': '4-6 weeks',
                'Rollout': '6-8 weeks'
            }
        }
        
        timeline = base_timelines.get(complexity, base_timelines['medium'])
        
        # 基於優化機會數量調整
        if len(opportunities) > 5:
            # 增加20%時間
            adjusted_timeline = {}
            for phase, duration in timeline.items():
                # 簡化處理，添加額外時間註記
                adjusted_timeline[phase] = f"{duration} (+20% for scope)"
            timeline = adjusted_timeline
        
        return timeline
    
    def _define_success_metrics(self, workflow_data: Dict[str, Any],
                              estimated_improvement: float) -> List[str]:
        """定義成功指標"""
        metrics = []
        
        # 基於當前痛點定義指標
        current_cycle_time = workflow_data.get('average_cycle_time_hours', 24)
        target_cycle_time = current_cycle_time * (1 - estimated_improvement / 100)
        metrics.append(f'Reduce cycle time to {target_cycle_time:.1f} hours')
        
        current_error_rate = workflow_data.get('error_rate', 0.1)
        target_error_rate = current_error_rate * 0.5  # 50%減少錯誤率
        metrics.append(f'Reduce error rate to {target_error_rate:.2%}')
        
        # 通用成功指標
        metrics.extend([
            f'Achieve {estimated_improvement:.0f}% overall efficiency improvement',
            'User satisfaction score >4.0/5.0',
            'ROI >200% within 12 months'
        ])
        
        return metrics
    
    def _identify_risk_factors(self, workflow_data: Dict[str, Any],
                             opportunities: List[Dict[str, Any]]) -> List[str]:
        """識別風險因素"""
        risks = []
        
        # 基於優化類型的風險
        automation_count = len([
            opp for opp in opportunities 
            if opp.get('type') == OptimizationOpportunity.AUTOMATE
        ])
        
        if automation_count > 2:
            risks.append('Technology implementation risks and dependencies')
        
        # 基於流程特性的風險
        if workflow_data.get('user_count', 10) > 50:
            risks.append('Large user base change management challenges')
        
        if workflow_data.get('compliance_requirements', False):
            risks.append('Regulatory compliance validation required')
        
        # 通用實施風險
        risks.extend([
            'User resistance to process changes',
            'Temporary productivity decline during transition',
            'Resource allocation conflicts with other priorities'
        ])
        
        return risks[:5]  # 限制風險數量


class DecisionMakingAnalyzer:
    """決策制定分析器"""
    
    def __init__(self):
        self.decision_quality_factors = {
            'information_completeness': 0.25,
            'stakeholder_involvement': 0.20,
            'decision_speed': 0.15,
            'consensus_building': 0.15,
            'implementation_clarity': 0.15,
            'bias_mitigation': 0.10
        }
        
        self.cognitive_biases = [
            'confirmation_bias', 'anchoring_bias', 'availability_heuristic',
            'groupthink', 'sunk_cost_fallacy', 'overconfidence_bias'
        ]
    
    def analyze_decision_process(self, decision_data: Dict[str, Any]) -> DecisionMakingAnalysis:
        """分析決策制定過程"""
        
        decision_process_id = decision_data.get('decision_id', 'unknown')
        decision_type = decision_data.get('type', 'operational')
        stakeholders_involved = decision_data.get('stakeholders', [])
        
        # 分析決策速度
        decision_speed = self._analyze_decision_speed(decision_data)
        
        # 評估信息質量
        information_quality = self._assess_information_quality(decision_data)
        
        # 測量共識水平
        consensus_level = self._measure_consensus_level(decision_data)
        
        # 評估實施效果
        implementation_effectiveness = self._evaluate_implementation_effectiveness(decision_data)
        
        # 計算決策質量分數
        decision_quality_score = self._calculate_decision_quality(
            information_quality, consensus_level, decision_speed, implementation_effectiveness
        )
        
        # 檢測認知偏見
        cognitive_biases_detected = self._detect_cognitive_biases(decision_data)
        
        # 識別流程低效
        process_inefficiencies = self._identify_process_inefficiencies(decision_data)
        
        # 生成優化建議
        optimization_recommendations = self._generate_decision_optimization_recommendations(
            decision_type, decision_quality_score, cognitive_biases_detected, process_inefficiencies
        )
        
        return DecisionMakingAnalysis(
            decision_process_id=decision_process_id,
            decision_type=decision_type,
            stakeholders_involved=stakeholders_involved,
            decision_speed=decision_speed,
            information_quality=information_quality,
            consensus_level=consensus_level,
            implementation_effectiveness=implementation_effectiveness,
            decision_quality_score=decision_quality_score,
            cognitive_biases_detected=cognitive_biases_detected,
            process_inefficiencies=process_inefficiencies,
            optimization_recommendations=optimization_recommendations
        )
    
    def _analyze_decision_speed(self, decision_data: Dict[str, Any]) -> float:
        """分析決策速度"""
        
        time_to_decision_days = decision_data.get('time_to_decision_days', 7)
        decision_complexity = decision_data.get('complexity_level', 'medium')
        
        # 基於複雜度的期望時間
        expected_times = {
            'low': 2,      # 2天
            'medium': 7,   # 1週
            'high': 21,    # 3週
            'critical': 1  # 1天（緊急決策）
        }
        
        expected_time = expected_times.get(decision_complexity, 7)
        
        # 計算速度分數（越快越好，但要合理）
        if time_to_decision_days <= expected_time:
            speed_score = 1.0
        elif time_to_decision_days <= expected_time * 2:
            speed_score = 0.7
        elif time_to_decision_days <= expected_time * 3:
            speed_score = 0.4
        else:
            speed_score = 0.2
        
        return speed_score
    
    def _assess_information_quality(self, decision_data: Dict[str, Any]) -> float:
        """評估信息質量"""
        
        info_metrics = decision_data.get('information_metrics', {})
        
        # 信息質量要素
        data_accuracy = info_metrics.get('data_accuracy', 0.7)
        data_completeness = info_metrics.get('data_completeness', 0.6)
        source_credibility = info_metrics.get('source_credibility', 0.7)
        information_recency = info_metrics.get('information_recency', 0.6)
        
        # 加權計算
        quality_score = (
            data_accuracy * 0.3 +
            data_completeness * 0.3 +
            source_credibility * 0.2 +
            information_recency * 0.2
        )
        
        return quality_score
    
    def _measure_consensus_level(self, decision_data: Dict[str, Any]) -> float:
        """測量共識水平"""
        
        consensus_metrics = decision_data.get('consensus_metrics', {})
        
        stakeholder_agreement = consensus_metrics.get('stakeholder_agreement_percentage', 0.7)
        dissenting_opinions = consensus_metrics.get('dissenting_opinions_count', 1)
        total_stakeholders = len(decision_data.get('stakeholders', [5]))
        
        # 計算共識分數
        agreement_score = stakeholder_agreement
        dissent_penalty = min(dissenting_opinions / total_stakeholders, 0.3)
        
        consensus_score = agreement_score - dissent_penalty
        
        return min(max(consensus_score, 0.0), 1.0)
    
    def _evaluate_implementation_effectiveness(self, decision_data: Dict[str, Any]) -> float:
        """評估實施效果"""
        
        implementation_metrics = decision_data.get('implementation_metrics', {})
        
        # 如果決策尚未實施，返回預期分數
        if not implementation_metrics:
            return 0.6  # 默認預期值
        
        implementation_speed = implementation_metrics.get('implementation_speed', 0.6)
        goal_achievement = implementation_metrics.get('goal_achievement', 0.6)
        stakeholder_satisfaction = implementation_metrics.get('stakeholder_satisfaction', 0.6)
        resource_efficiency = implementation_metrics.get('resource_efficiency', 0.6)
        
        effectiveness_score = (
            implementation_speed * 0.2 +
            goal_achievement * 0.4 +
            stakeholder_satisfaction * 0.2 +
            resource_efficiency * 0.2
        )
        
        return effectiveness_score
    
    def _calculate_decision_quality(self, information_quality: float, consensus_level: float,
                                  decision_speed: float, implementation_effectiveness: float) -> float:
        """計算決策質量分數"""
        
        # 假設stakeholder_involvement和bias_mitigation為中等水平
        stakeholder_involvement = 0.7  # 可從數據中獲取
        bias_mitigation = 0.6         # 可通過偏見檢測計算
        
        quality_score = (
            information_quality * self.decision_quality_factors['information_completeness'] +
            stakeholder_involvement * self.decision_quality_factors['stakeholder_involvement'] +
            decision_speed * self.decision_quality_factors['decision_speed'] +
            consensus_level * self.decision_quality_factors['consensus_building'] +
            implementation_effectiveness * self.decision_quality_factors['implementation_clarity'] +
            bias_mitigation * self.decision_quality_factors['bias_mitigation']
        )
        
        return quality_score
    
    def _detect_cognitive_biases(self, decision_data: Dict[str, Any]) -> List[str]:
        """檢測認知偏見"""
        detected_biases = []
        
        bias_indicators = decision_data.get('bias_indicators', {})
        
        # 確認偏見檢測
        if bias_indicators.get('seeking_confirming_evidence', False):
            detected_biases.append('confirmation_bias')
        
        # 錨定偏見檢測
        if bias_indicators.get('over_reliance_on_first_information', False):
            detected_biases.append('anchoring_bias')
        
        # 群體思維檢測
        stakeholder_diversity = len(set(decision_data.get('stakeholder_roles', [])))
        if stakeholder_diversity < 3:
            detected_biases.append('groupthink')
        
        # 過度自信檢測
        confidence_level = bias_indicators.get('confidence_level', 0.7)
        if confidence_level > 0.9:
            detected_biases.append('overconfidence_bias')
        
        # 可得性啟發檢測
        if bias_indicators.get('recent_example_influence', False):
            detected_biases.append('availability_heuristic')
        
        return detected_biases
    
    def _identify_process_inefficiencies(self, decision_data: Dict[str, Any]) -> List[str]:
        """識別流程低效"""
        inefficiencies = []
        
        # 分析決策流程數據
        process_metrics = decision_data.get('process_metrics', {})
        
        # 會議過多
        meetings_count = process_metrics.get('meetings_count', 3)
        if meetings_count > 5:
            inefficiencies.append('Too many meetings slowing decision process')
        
        # 信息收集時間過長
        info_gathering_days = process_metrics.get('information_gathering_days', 3)
        if info_gathering_days > 7:
            inefficiencies.append('Extended information gathering phase')
        
        # 審批層級過多
        approval_levels = process_metrics.get('approval_levels', 2)
        if approval_levels > 3:
            inefficiencies.append('Excessive approval hierarchy')
        
        # 利益相關者過多
        stakeholders_count = len(decision_data.get('stakeholders', []))
        if stakeholders_count > 8:
            inefficiencies.append('Too many stakeholders involved in decision')
        
        # 信息重複收集
        if process_metrics.get('duplicate_information_requests', False):
            inefficiencies.append('Redundant information collection efforts')
        
        return inefficiencies
    
    def _generate_decision_optimization_recommendations(self, decision_type: str,
                                                      quality_score: float,
                                                      biases: List[str],
                                                      inefficiencies: List[str]) -> List[str]:
        """生成決策優化建議"""
        recommendations = []
        
        # 基於決策質量分數的建議
        if quality_score < 0.6:
            recommendations.append('Implement structured decision-making framework (e.g., DECIDE model)')
            recommendations.append('Establish clear decision criteria and weighting before evaluation')
        
        # 基於檢測到的偏見的建議
        if 'confirmation_bias' in biases:
            recommendations.append('Assign devil\'s advocate role to challenge assumptions')
        
        if 'groupthink' in biases:
            recommendations.append('Include diverse perspectives and external viewpoints')
        
        if 'anchoring_bias' in biases:
            recommendations.append('Generate multiple alternatives before anchoring on first option')
        
        # 基於流程低效的建議
        if 'Too many meetings' in ' '.join(inefficiencies):
            recommendations.append('Consolidate decision meetings and use asynchronous input collection')
        
        if 'Extended information gathering' in ' '.join(inefficiencies):
            recommendations.append('Set clear information requirements and deadlines upfront')
        
        if 'Excessive approval hierarchy' in ' '.join(inefficiencies):
            recommendations.append('Streamline approval process and delegate decision authority')
        
        # 基於決策類型的特定建議
        type_specific_recommendations = {
            'strategic': [
                'Use scenario planning for strategic decisions',
                'Implement formal risk assessment process'
            ],
            'operational': [
                'Create decision templates for routine operational choices',
                'Establish clear escalation criteria'
            ],
            'personnel': [
                'Ensure HR policy compliance in personnel decisions',
                'Include relevant stakeholders early in the process'
            ]
        }
        
        specific_recs = type_specific_recommendations.get(decision_type, [])
        recommendations.extend(specific_recs[:2])
        
        return recommendations[:8]  # 限制建議數量


class ProcessAgent(BaseAgent):
    """Process Agent - 流程優化專家"""
    
    def __init__(self):
        super().__init__(temperature=0.5)
        self.meeting_analyzer = MeetingEfficiencyAnalyzer()
        self.workflow_optimizer = WorkflowOptimizer()
        self.decision_analyzer = DecisionMakingAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的流程優化專家和引導科學實踐者。你的核心職責包括：

1. 會議效能分析：分析會議結構、參與度和產出質量，提供優化建議
2. 工作流程優化：識別瓶頸點、消除浪費、提升流程效率
3. 決策制定分析：評估決策過程品質、檢測認知偏見、改進決策機制
4. 流程設計改進：基於引導科學原理設計高效的工作流程
5. 組織效能提升：從系統角度優化整體組織運作效率

你的分析基於以下方法論：
- 精實思維 (Lean Thinking Principles)
- 引導科學 (Facilitation Science)
- 流程挖掘技術 (Process Mining Techniques)
- 決策科學理論 (Decision Science Theory)
- 認知偏見識別 (Cognitive Bias Detection)
- 會議效能框架 (Meeting Effectiveness Frameworks)

請提供基於證據的分析和可執行的改進建議，重點關注消除浪費、提升效率和改善用戶體驗。""")
    
    async def analyze_context(self, context) -> Dict[str, Any]:
        """分析流程優化上下文"""
        try:
            organizational_data = context.organizational_data
            
            analysis_results = {
                'recommendations': [],
                'risks': [],
                'opportunities': [],
                'confidence': 0.0,
                'data_quality': 0.0
            }
            
            # Step 1: 會議效能分析
            meeting_analysis = await self._analyze_meeting_efficiency(organizational_data)
            
            # Step 2: 工作流程優化分析
            workflow_analysis = await self._optimize_workflows(organizational_data)
            
            # Step 3: 決策制定分析
            decision_analysis = await self._analyze_decision_making(organizational_data)
            
            # Step 4: 流程基準對比
            benchmark_analysis = await self._benchmark_processes(organizational_data)
            
            # Step 5: 整合建議生成
            integrated_recommendations = await self._generate_process_recommendations(
                meeting_analysis, workflow_analysis, decision_analysis, benchmark_analysis
            )
            
            # Step 6: 風險和機會識別
            process_risks = await self._identify_process_risks(workflow_analysis, decision_analysis)
            process_opportunities = await self._identify_process_opportunities(
                meeting_analysis, workflow_analysis, benchmark_analysis
            )
            
            analysis_results.update({
                'recommendations': integrated_recommendations,
                'risks': process_risks,
                'opportunities': process_opportunities,
                'confidence': self._calculate_analysis_confidence(organizational_data),
                'data_quality': self._assess_data_quality(organizational_data),
                'meeting_analysis': meeting_analysis,
                'workflow_analysis': workflow_analysis,
                'decision_analysis': decision_analysis,
                'benchmark_analysis': benchmark_analysis
            })
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Process Agent analysis failed: {str(e)}")
            return {
                'recommendations': [],
                'risks': ['Process analysis system error'],
                'opportunities': [],
                'confidence': 0.3,
                'data_quality': 0.3
            }
    
    async def _analyze_meeting_efficiency(self, organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析會議效能"""
        
        meeting_data_list = organizational_data.get('meeting_data', [])
        
        if not meeting_data_list:
            return {
                'total_meetings_analyzed': 0,
                'average_efficiency_score': 0.6,
                'common_bottlenecks': ['No meeting data available'],
                'improvement_recommendations': ['Implement meeting data collection']
            }
        
        # 分析所有會議
        meeting_analyses = []
        for meeting_data in meeting_data_list:
            analysis = self.meeting_analyzer.analyze_meeting_efficiency(meeting_data)
            meeting_analyses.append(analysis.__dict__)
        
        # 計算總體統計
        total_meetings = len(meeting_analyses)
        avg_efficiency = np.mean([m['efficiency_score'] for m in meeting_analyses])
        
        # 識別常見瓶頸
        all_bottlenecks = []
        for analysis in meeting_analyses:
            all_bottlenecks.extend(analysis['bottlenecks'])
        
        bottleneck_counts = {}
        for bottleneck in all_bottlenecks:
            bottleneck_counts[bottleneck] = bottleneck_counts.get(bottleneck, 0) + 1
        
        common_bottlenecks = sorted(bottleneck_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 生成改進建議
        improvement_recommendations = self._generate_meeting_improvement_recommendations(
            avg_efficiency, common_bottlenecks, meeting_analyses
        )
        
        return {
            'total_meetings_analyzed': total_meetings,
            'average_efficiency_score': avg_efficiency,
            'efficiency_distribution': self._calculate_efficiency_distribution(meeting_analyses),
            'common_bottlenecks': [item[0] for item in common_bottlenecks],
            'meeting_type_analysis': self._analyze_by_meeting_type(meeting_analyses),
            'improvement_recommendations': improvement_recommendations,
            'detailed_analyses': meeting_analyses
        }
    
    async def _optimize_workflows(self, organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """優化工作流程"""
        
        workflow_data_list = organizational_data.get('workflow_data', [])
        
        if not workflow_data_list:
            return {
                'total_workflows_analyzed': 0,
                'average_efficiency': 0.6,
                'optimization_opportunities': ['No workflow data available'],
                'total_improvement_potential': 0
            }
        
        # 優化所有工作流程
        workflow_optimizations = []
        for workflow_data in workflow_data_list:
            optimization = self.workflow_optimizer.optimize_workflow(workflow_data)
            workflow_optimizations.append(optimization.__dict__)
        
        # 計算總體統計
        total_workflows = len(workflow_optimizations)
        avg_efficiency = np.mean([w['current_efficiency'] for w in workflow_optimizations])
        total_improvement_potential = sum([w['estimated_improvement'] for w in workflow_optimizations])
        
        # 彙總優化機會
        all_opportunities = []
        for optimization in workflow_optimizations:
            all_opportunities.extend(optimization['optimization_opportunities'])
        
        # 按ROI排序機會
        sorted_opportunities = sorted(
            all_opportunities, 
            key=lambda x: x.get('roi_estimate', 1.0), 
            reverse=True
        )
        
        return {
            'total_workflows_analyzed': total_workflows,
            'average_efficiency': avg_efficiency,
            'total_improvement_potential': total_improvement_potential,
            'top_optimization_opportunities': sorted_opportunities[:10],
            'workflow_efficiency_distribution': self._calculate_workflow_efficiency_distribution(workflow_optimizations),
            'implementation_complexity_analysis': self._analyze_implementation_complexity(workflow_optimizations),
            'detailed_optimizations': workflow_optimizations
        }
    
    async def _analyze_decision_making(self, organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析決策制定"""
        
        decision_data_list = organizational_data.get('decision_data', [])
        
        if not decision_data_list:
            return {
                'total_decisions_analyzed': 0,
                'average_decision_quality': 0.6,
                'common_biases_detected': ['No decision data available'],
                'process_improvement_needs': ['Implement decision tracking']
            }
        
        # 分析所有決策
        decision_analyses = []
        for decision_data in decision_data_list:
            analysis = self.decision_analyzer.analyze_decision_process(decision_data)
            decision_analyses.append(analysis.__dict__)
        
        # 計算統計
        total_decisions = len(decision_analyses)
        avg_quality = np.mean([d['decision_quality_score'] for d in decision_analyses])
        
        # 彙總認知偏見
        all_biases = []
        for analysis in decision_analyses:
            all_biases.extend(analysis['cognitive_biases_detected'])
        
        bias_counts = {}
        for bias in all_biases:
            bias_counts[bias] = bias_counts.get(bias, 0) + 1
        
        common_biases = sorted(bias_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 彙總流程改進需求
        all_inefficiencies = []
        for analysis in decision_analyses:
            all_inefficiencies.extend(analysis['process_inefficiencies'])
        
        inefficiency_counts = {}
        for inefficiency in all_inefficiencies:
            inefficiency_counts[inefficiency] = inefficiency_counts.get(inefficiency, 0) + 1
        
        common_inefficiencies = sorted(inefficiency_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_decisions_analyzed': total_decisions,
            'average_decision_quality': avg_quality,
            'decision_quality_distribution': self._calculate_decision_quality_distribution(decision_analyses),
            'common_biases_detected': [item[0] for item in common_biases],
            'process_improvement_needs': [item[0] for item in common_inefficiencies],
            'decision_speed_analysis': self._analyze_decision_speed(decision_analyses),
            'detailed_analyses': decision_analyses
        }
    
    async def _benchmark_processes(self, organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """流程基準對比"""
        
        # 模擬基準數據（實際應用中應從行業數據庫獲取）
        industry_benchmarks = {
            'meeting_efficiency': 0.7,
            'workflow_automation_level': 0.4,
            'decision_speed_score': 0.65,
            'process_standardization': 0.6
        }
        
        # 計算組織表現
        org_performance = {
            'meeting_efficiency': organizational_data.get('overall_meeting_efficiency', 0.6),
            'workflow_automation_level': organizational_data.get('automation_level', 0.3),
            'decision_speed_score': organizational_data.get('decision_speed', 0.6),
            'process_standardization': organizational_data.get('standardization_level', 0.5)
        }
        
        # 計算差距
        benchmarks = []
        for process_name, industry_score in industry_benchmarks.items():
            org_score = org_performance.get(process_name, 0.5)
            gap = industry_score - org_score
            
            benchmark = ProcessBenchmark(
                process_name=process_name,
                industry_benchmark=industry_score,
                organizational_performance=org_score,
                performance_gap=gap,
                best_practice_examples=self._get_best_practices(process_name),
                improvement_potential=max(gap * 100, 0),
                competitive_advantage_level='below' if gap > 0.1 else 'at' if abs(gap) <= 0.1 else 'above'
            )
            benchmarks.append(benchmark.__dict__)
        
        return {
            'benchmark_results': benchmarks,
            'overall_competitive_position': self._assess_competitive_position(benchmarks),
            'priority_improvement_areas': self._identify_priority_areas(benchmarks)
        }
    
    async def _generate_process_recommendations(self, meeting_analysis: Dict[str, Any],
                                              workflow_analysis: Dict[str, Any],
                                              decision_analysis: Dict[str, Any],
                                              benchmark_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成流程建議"""
        recommendations = []
        
        # 基於會議分析的建議
        meeting_efficiency = meeting_analysis.get('average_efficiency_score', 0.6)
        if meeting_efficiency < 0.6:
            recommendations.append({
                'id': 'meeting_efficiency_improvement',
                'title': 'Meeting Efficiency Enhancement Program',
                'description': 'Implement structured meeting management practices',
                'scope': 'organization',
                'type': 'meeting_optimization',
                'urgency': 'high',
                'weight': 0.8,
                'expected_impact': f'Improve meeting efficiency by {(0.7 - meeting_efficiency) * 100:.0f}%'
            })
        
        # 基於工作流程分析的建議
        workflow_improvement_potential = workflow_analysis.get('total_improvement_potential', 0)
        if workflow_improvement_potential > 20:
            recommendations.append({
                'id': 'workflow_optimization_initiative',
                'title': 'Workflow Optimization Initiative',
                'description': f'Systematic workflow improvements with {workflow_improvement_potential:.0f}% potential gain',
                'scope': 'organization',
                'type': 'workflow_optimization',
                'urgency': 'high',
                'weight': 0.9,
                'improvement_areas': workflow_analysis.get('top_optimization_opportunities', [])[:3]
            })
        
        # 基於決策分析的建議
        decision_quality = decision_analysis.get('average_decision_quality', 0.6)
        if decision_quality < 0.7:
            recommendations.append({
                'id': 'decision_making_enhancement',
                'title': 'Decision-Making Process Enhancement',
                'description': 'Improve decision quality through structured frameworks and bias mitigation',
                'scope': 'organization',
                'type': 'decision_optimization',
                'urgency': 'medium',
                'weight': 0.7,
                'focus_areas': decision_analysis.get('common_biases_detected', [])[:3]
            })
        
        # 基於基準對比的建議
        priority_areas = benchmark_analysis.get('priority_improvement_areas', [])
        if priority_areas:
            recommendations.append({
                'id': 'benchmark_gap_closure',
                'title': 'Industry Benchmark Gap Closure',
                'description': f'Address performance gaps in {len(priority_areas)} key process areas',
                'scope': 'organization',
                'type': 'benchmark_improvement',
                'urgency': 'medium',
                'weight': 0.8,
                'target_processes': priority_areas
            })
        
        # 自動化機會建議
        automation_opportunities = self._identify_automation_opportunities(workflow_analysis)
        if automation_opportunities:
            recommendations.append({
                'id': 'process_automation_program',
                'title': 'Process Automation Program',
                'description': f'Automate {len(automation_opportunities)} high-ROI processes',
                'scope': 'organization',
                'type': 'automation',
                'urgency': 'medium',
                'weight': 0.8,
                'automation_targets': automation_opportunities
            })
        
        return recommendations[:8]  # 限制建議數量
    
    def _generate_meeting_improvement_recommendations(self, avg_efficiency: float,
                                                    common_bottlenecks: List[Tuple[str, int]],
                                                    meeting_analyses: List[Dict[str, Any]]) -> List[str]:
        """生成會議改進建議"""
        recommendations = []
        
        # 基於平均效能的建議
        if avg_efficiency < 0.5:
            recommendations.append('Implement comprehensive meeting management training')
            recommendations.append('Establish meeting-free time blocks for focused work')
        
        # 基於常見瓶頸的建議
        for bottleneck, count in common_bottlenecks[:3]:
            if 'time utilization' in bottleneck.lower():
                recommendations.append('Implement strict agenda time-boxing')
            elif 'engagement' in bottleneck.lower():
                recommendations.append('Use interactive facilitation techniques')
            elif 'participants' in bottleneck.lower():
                recommendations.append('Review and optimize meeting attendance policies')
        
        # 基於會議類型分析的建議
        meeting_types = set([analysis['meeting_type'] for analysis in meeting_analyses])
        if 'status_update' in meeting_types:
            recommendations.append('Replace routine status meetings with asynchronous updates')
        
        return recommendations[:5]
    
    def _calculate_efficiency_distribution(self, meeting_analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """計算效能分佈"""
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for analysis in meeting_analyses:
            score = analysis['efficiency_score']
            if score > 0.8:
                distribution['excellent'] += 1
            elif score > 0.6:
                distribution['good'] += 1
            elif score > 0.4:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _analyze_by_meeting_type(self, meeting_analyses: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """按會議類型分析"""
        type_analysis = {}
        
        for analysis in meeting_analyses:
            meeting_type = analysis['meeting_type']
            if meeting_type not in type_analysis:
                type_analysis[meeting_type] = {
                    'count': 0,
                    'total_efficiency': 0,
                    'total_duration': 0
                }
            
            type_analysis[meeting_type]['count'] += 1
            type_analysis[meeting_type]['total_efficiency'] += analysis['efficiency_score']
            type_analysis[meeting_type]['total_duration'] += analysis['duration_minutes']
        
        # 計算平均值
        for meeting_type, data in type_analysis.items():
            data['average_efficiency'] = data['total_efficiency'] / data['count']
            data['average_duration'] = data['total_duration'] / data['count']
        
        return type_analysis
    
    def _calculate_workflow_efficiency_distribution(self, workflow_optimizations: List[Dict[str, Any]]) -> Dict[str, int]:
        """計算工作流程效能分佈"""
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for optimization in workflow_optimizations:
            score = optimization['current_efficiency']
            if score > 0.8:
                distribution['excellent'] += 1
            elif score > 0.6:
                distribution['good'] += 1
            elif score > 0.4:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _analyze_implementation_complexity(self, workflow_optimizations: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析實施複雜度"""
        complexity_distribution = {'low': 0, 'medium': 0, 'high': 0}
        
        for optimization in workflow_optimizations:
            complexity = optimization['implementation_complexity']
            complexity_distribution[complexity] += 1
        
        return complexity_distribution
    
    def _calculate_decision_quality_distribution(self, decision_analyses: List[Dict[str, Any]]) -> Dict[str, int]:
        """計算決策質量分佈"""
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for analysis in decision_analyses:
            score = analysis['decision_quality_score']
            if score > 0.8:
                distribution['excellent'] += 1
            elif score > 0.6:
                distribution['good'] += 1
            elif score > 0.4:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _analyze_decision_speed(self, decision_analyses: List[Dict[str, Any]]) -> Dict[str, float]:
        """分析決策速度"""
        speeds = [analysis['decision_speed'] for analysis in decision_analyses]
        
        return {
            'average_speed': np.mean(speeds),
            'speed_variance': np.var(speeds),
            'fast_decisions_percentage': len([s for s in speeds if s > 0.7]) / len(speeds) * 100
        }
    
    def _get_best_practices(self, process_name: str) -> List[str]:
        """獲取最佳實踐"""
        best_practices = {
            'meeting_efficiency': [
                'Time-boxed agendas with clear objectives',
                'Standing meetings with defined outcomes',
                'Meeting-free time blocks for focused work'
            ],
            'workflow_automation_level': [
                'Automated approval workflows',
                'Self-service employee portals',
                'Robotic process automation for routine tasks'
            ],
            'decision_speed_score': [
                'RACI decision-making framework',
                'Delegated decision authority',
                'Pre-defined decision criteria'
            ],
            'process_standardization': [
                'Documented standard operating procedures',
                'Process templates and checklists',
                'Regular process review and updates'
            ]
        }
        
        return best_practices.get(process_name, ['Industry standard practices'])
    
    def _assess_competitive_position(self, benchmarks: List[Dict[str, Any]]) -> str:
        """評估競爭地位"""
        below_benchmark = len([b for b in benchmarks if b['performance_gap'] > 0.1])
        total_benchmarks = len(benchmarks)
        
        if below_benchmark / total_benchmarks > 0.6:
            return 'significantly_below_industry'
        elif below_benchmark / total_benchmarks > 0.3:
            return 'below_industry'
        elif below_benchmark / total_benchmarks < 0.2:
            return 'above_industry'
        else:
            return 'at_industry_level'
    
    def _identify_priority_areas(self, benchmarks: List[Dict[str, Any]]) -> List[str]:
        """識別優先改進領域"""
        # 按差距大小排序
        sorted_benchmarks = sorted(benchmarks, key=lambda x: x['performance_gap'], reverse=True)
        
        # 返回差距最大的前3個領域
        priority_areas = [b['process_name'] for b in sorted_benchmarks[:3] if b['performance_gap'] > 0.05]
        
        return priority_areas
    
    def _identify_automation_opportunities(self, workflow_analysis: Dict[str, Any]) -> List[str]:
        """識別自動化機會"""
        opportunities = []
        
        top_opportunities = workflow_analysis.get('top_optimization_opportunities', [])
        
        for opp in top_opportunities:
            if opp.get('type') == 'automate' and opp.get('roi_estimate', 0) > 2.0:
                opportunities.append(opp.get('description', 'Automation opportunity'))
        
        return opportunities[:5]  # 限制數量
    
    def _calculate_analysis_confidence(self, organizational_data: Dict[str, Any]) -> float:
        """計算分析信心度"""
        data_sources = ['meeting_data', 'workflow_data', 'decision_data']
        available_sources = sum(1 for source in data_sources if source in organizational_data)
        
        return available_sources / len(data_sources)
    
    def _assess_data_quality(self, organizational_data: Dict[str, Any]) -> float:
        """評估數據質量"""
        quality_score = 0.7  # 基線分數
        
        # 檢查數據完整性
        if 'meeting_data' in organizational_data and organizational_data['meeting_data']:
            quality_score += 0.1
        
        if 'workflow_data' in organizational_data and organizational_data['workflow_data']:
            quality_score += 0.1
        
        if 'decision_data' in organizational_data and organizational_data['decision_data']:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    async def _identify_process_risks(self, workflow_analysis: Dict[str, Any],
                                    decision_analysis: Dict[str, Any]) -> List[str]:
        """識別流程風險"""
        risks = []
        
        # 基於工作流程分析的風險
        low_efficiency_workflows = [
            w for w in workflow_analysis.get('detailed_optimizations', [])
            if w['current_efficiency'] < 0.5
        ]
        
        if low_efficiency_workflows:
            risks.append(f'{len(low_efficiency_workflows)} workflows operating below acceptable efficiency')
        
        # 基於決策分析的風險
        common_biases = decision_analysis.get('common_biases_detected', [])
        if len(common_biases) > 2:
            risks.append('Multiple cognitive biases affecting decision quality')
        
        # 通用流程風險
        risks.extend([
            'Process optimization changes may face resistance',
            'Automation initiatives require significant technology investment',
            'Workflow changes may temporarily reduce productivity'
        ])
        
        return risks[:5]  # 限制風險數量
    
    async def _identify_process_opportunities(self, meeting_analysis: Dict[str, Any],
                                            workflow_analysis: Dict[str, Any],
                                            benchmark_analysis: Dict[str, Any]) -> List[str]:
        """識別流程機會"""
        opportunities = []
        
        # 基於會議分析的機會
        meeting_efficiency = meeting_analysis.get('average_efficiency_score', 0.6)
        if meeting_efficiency < 0.7:
            improvement_potential = (0.8 - meeting_efficiency) * 100
            opportunities.append(f'Meeting efficiency improvement potential: {improvement_potential:.0f}%')
        
        # 基於工作流程分析的機會
        total_improvement = workflow_analysis.get('total_improvement_potential', 0)
        if total_improvement > 15:
            opportunities.append(f'Workflow optimization potential: {total_improvement:.0f}% efficiency gain')
        
        # 基於基準對比的機會
        competitive_position = benchmark_analysis.get('overall_competitive_position', 'at_industry_level')
        if competitive_position in ['below_industry', 'significantly_below_industry']:
            opportunities.append('Significant competitive advantage achievable through process improvements')
        
        # 通用機會
        opportunities.extend([
            'Process standardization can reduce training costs',
            'Automation can free up human resources for strategic work',
            'Improved processes enhance employee satisfaction and retention'
        ])
        
        return opportunities[:6]  # 限制機會數量