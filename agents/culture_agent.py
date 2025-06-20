"""
Culture Agent - 組織文化感知器
監測和優化組織文化健康度
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


class CultureDimension(Enum):
    PSYCHOLOGICAL_SAFETY = "psychological_safety"
    INNOVATION = "innovation"
    COLLABORATION = "collaboration"
    ACCOUNTABILITY = "accountability"
    TRANSPARENCY = "transparency"
    DIVERSITY_INCLUSION = "diversity_inclusion"
    LEARNING_ORIENTATION = "learning_orientation"
    CUSTOMER_FOCUS = "customer_focus"
    RESULTS_ORIENTATION = "results_orientation"
    ADAPTABILITY = "adaptability"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CultureHealthProfile:
    """文化健康檔案"""
    overall_score: float  # 0.0 - 1.0
    dimension_scores: Dict[CultureDimension, float]
    trend_direction: str  # improving, stable, declining
    risk_areas: List[str]
    strength_areas: List[str]
    cultural_alignment: float  # 實際vs期望文化的匹配度
    engagement_indicators: Dict[str, float]
    burnout_risk_score: float


@dataclass
class ConflictPrediction:
    """衝突預測"""
    conflict_probability: float  # 0.0 - 1.0
    potential_sources: List[str]
    affected_teams: List[str]
    severity_estimate: RiskLevel
    early_warning_signals: List[str]
    intervention_window: int  # days
    recommended_actions: List[str]


@dataclass
class TeamDynamics:
    """團隊動態分析"""
    team_id: str
    cohesion_score: float
    communication_effectiveness: float
    trust_level: float
    conflict_frequency: float
    collaboration_patterns: Dict[str, Any]
    leadership_effectiveness: float
    morale_indicators: Dict[str, float]


@dataclass
class CulturalFitAssessment:
    """文化適配評估"""
    person_id: str
    overall_fit_score: float
    dimension_fit_scores: Dict[CultureDimension, float]
    adaptation_probability: float
    integration_challenges: List[str]
    support_recommendations: List[str]
    success_indicators: List[str]


class EmotionalIntelligenceMonitor:
    """情緒智能監測器"""
    
    def __init__(self):
        self.sentiment_indicators = {
            'communication_tone': 0.3,
            'meeting_participation': 0.2,
            'feedback_receptivity': 0.2,
            'stress_signals': -0.15,
            'enthusiasm_markers': 0.15
        }
        
    def analyze_team_emotional_state(self, team_data: Dict[str, Any]) -> Dict[str, float]:
        """分析團隊情緒狀態"""
        
        emotional_metrics = {
            'overall_sentiment': 0.0,
            'stress_level': 0.0,
            'engagement_level': 0.0,
            'satisfaction_level': 0.0,
            'motivation_level': 0.0
        }
        
        # 從通信數據分析情緒指標
        communication_data = team_data.get('communication_data', {})
        emotional_metrics['overall_sentiment'] = self._calculate_sentiment_score(communication_data)
        
        # 從行為數據分析壓力水平
        behavioral_data = team_data.get('behavioral_indicators', {})
        emotional_metrics['stress_level'] = self._calculate_stress_level(behavioral_data)
        
        # 從參與數據分析參與度
        participation_data = team_data.get('participation_metrics', {})
        emotional_metrics['engagement_level'] = self._calculate_engagement_level(participation_data)
        
        # 從績效數據分析滿意度
        performance_data = team_data.get('performance_metrics', {})
        emotional_metrics['satisfaction_level'] = self._calculate_satisfaction_level(performance_data)
        
        # 綜合計算動機水平
        emotional_metrics['motivation_level'] = self._calculate_motivation_level(emotional_metrics)
        
        return emotional_metrics
    
    def _calculate_sentiment_score(self, communication_data: Dict[str, Any]) -> float:
        """計算情緒分數"""
        if not communication_data:
            return 0.6  # 默認中性
        
        positive_indicators = communication_data.get('positive_language_frequency', 0.5)
        negative_indicators = communication_data.get('negative_language_frequency', 0.3)
        neutral_tone = communication_data.get('neutral_tone_frequency', 0.2)
        
        # 加權計算整體情緒
        sentiment_score = (positive_indicators * 0.6 - negative_indicators * 0.4 + neutral_tone * 0.0)
        return max(0.0, min(1.0, sentiment_score + 0.5))
    
    def _calculate_stress_level(self, behavioral_data: Dict[str, Any]) -> float:
        """計算壓力水平"""
        stress_indicators = [
            behavioral_data.get('overtime_frequency', 0.3),
            behavioral_data.get('deadline_pressure', 0.4),
            behavioral_data.get('workload_complaints', 0.2),
            behavioral_data.get('sick_leave_frequency', 0.1)
        ]
        
        return np.mean(stress_indicators)
    
    def _calculate_engagement_level(self, participation_data: Dict[str, Any]) -> float:
        """計算參與度水平"""
        engagement_factors = [
            participation_data.get('meeting_participation_rate', 0.7),
            participation_data.get('voluntary_contribution_frequency', 0.6),
            participation_data.get('initiative_taking_frequency', 0.5),
            participation_data.get('knowledge_sharing_activity', 0.6)
        ]
        
        return np.mean(engagement_factors)
    
    def _calculate_satisfaction_level(self, performance_data: Dict[str, Any]) -> float:
        """計算滿意度水平"""
        satisfaction_indicators = [
            performance_data.get('goal_achievement_rate', 0.7),
            performance_data.get('feedback_positivity', 0.6),
            performance_data.get('retention_indicators', 0.8),
            performance_data.get('internal_mobility_interest', 0.5)
        ]
        
        return np.mean(satisfaction_indicators)
    
    def _calculate_motivation_level(self, emotional_metrics: Dict[str, float]) -> float:
        """計算動機水平"""
        # 動機水平基於其他情緒指標的綜合
        motivation = (
            emotional_metrics['overall_sentiment'] * 0.3 +
            (1 - emotional_metrics['stress_level']) * 0.2 +
            emotional_metrics['engagement_level'] * 0.3 +
            emotional_metrics['satisfaction_level'] * 0.2
        )
        
        return motivation
    
    def detect_emotional_anomalies(self, emotional_metrics: Dict[str, float], 
                                 historical_baseline: Dict[str, float]) -> List[str]:
        """檢測情緒異常"""
        anomalies = []
        threshold = 0.2  # 異常閾值
        
        for metric, current_value in emotional_metrics.items():
            baseline_value = historical_baseline.get(metric, 0.6)
            
            if abs(current_value - baseline_value) > threshold:
                if current_value < baseline_value:
                    anomalies.append(f"Significant decline in {metric}")
                else:
                    anomalies.append(f"Significant improvement in {metric}")
        
        return anomalies


class ConflictEarlyWarningSystem:
    """衝突早期預警系統"""
    
    def __init__(self):
        self.conflict_indicators = {
            'communication_breakdown': 0.25,
            'resource_competition': 0.20,
            'goal_misalignment': 0.20,
            'personality_clashes': 0.15,
            'workload_imbalance': 0.10,
            'cultural_differences': 0.10
        }
    
    def assess_conflict_risk(self, team_data: Dict[str, Any]) -> ConflictPrediction:
        """評估衝突風險"""
        
        # 計算各類衝突指標
        conflict_scores = {}
        for indicator, weight in self.conflict_indicators.items():
            score = self._calculate_indicator_score(team_data, indicator)
            conflict_scores[indicator] = score
        
        # 計算總體衝突概率
        overall_probability = sum(
            score * weight for indicator, (score, weight) in 
            zip(conflict_scores.keys(), zip(conflict_scores.values(), self.conflict_indicators.values()))
        )
        
        # 識別潛在衝突源
        potential_sources = [
            indicator for indicator, score in conflict_scores.items() 
            if score > 0.6
        ]
        
        # 評估嚴重程度
        severity = self._assess_severity(overall_probability, potential_sources)
        
        # 識別早期預警信號
        warning_signals = self._identify_warning_signals(team_data, conflict_scores)
        
        # 確定干預時間窗口
        intervention_window = self._calculate_intervention_window(overall_probability, severity)
        
        # 生成建議行動
        recommended_actions = self._generate_conflict_prevention_actions(
            potential_sources, severity
        )
        
        return ConflictPrediction(
            conflict_probability=overall_probability,
            potential_sources=potential_sources,
            affected_teams=team_data.get('teams', []),
            severity_estimate=severity,
            early_warning_signals=warning_signals,
            intervention_window=intervention_window,
            recommended_actions=recommended_actions
        )
    
    def _calculate_indicator_score(self, team_data: Dict[str, Any], indicator: str) -> float:
        """計算指標分數"""
        indicator_mapping = {
            'communication_breakdown': ['response_time_delays', 'message_frequency_decline', 'misunderstanding_incidents'],
            'resource_competition': ['resource_allocation_disputes', 'priority_conflicts', 'budget_tension'],
            'goal_misalignment': ['objective_inconsistency', 'priority_disagreement', 'strategy_confusion'],
            'personality_clashes': ['interpersonal_tension', 'style_conflicts', 'value_disagreements'],
            'workload_imbalance': ['task_distribution_inequality', 'overtime_variance', 'capacity_mismatches'],
            'cultural_differences': ['cultural_misunderstanding', 'norm_violations', 'inclusion_issues']
        }
        
        sub_indicators = indicator_mapping.get(indicator, [])
        scores = []
        
        for sub_indicator in sub_indicators:
            score = team_data.get(sub_indicator, 0.3)  # 默認低風險
            scores.append(score)
        
        return np.mean(scores) if scores else 0.3
    
    def _assess_severity(self, probability: float, sources: List[str]) -> RiskLevel:
        """評估嚴重程度"""
        if probability > 0.8 or len(sources) > 3:
            return RiskLevel.CRITICAL
        elif probability > 0.6 or len(sources) > 2:
            return RiskLevel.HIGH
        elif probability > 0.4 or len(sources) > 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_warning_signals(self, team_data: Dict[str, Any], 
                                conflict_scores: Dict[str, float]) -> List[str]:
        """識別早期預警信號"""
        signals = []
        
        # 基於衝突分數識別信號
        for indicator, score in conflict_scores.items():
            if score > 0.5:
                signals.append(f"Elevated {indicator.replace('_', ' ')} detected")
        
        # 基於行為變化識別信號
        behavioral_changes = team_data.get('behavioral_changes', {})
        for change, intensity in behavioral_changes.items():
            if intensity > 0.6:
                signals.append(f"Significant behavioral change: {change}")
        
        return signals
    
    def _calculate_intervention_window(self, probability: float, severity: RiskLevel) -> int:
        """計算干預時間窗口（天）"""
        base_window = 14  # 基礎2週窗口
        
        # 根據概率調整
        probability_adjustment = int((1 - probability) * 10)
        
        # 根據嚴重程度調整
        severity_adjustments = {
            RiskLevel.CRITICAL: -7,
            RiskLevel.HIGH: -3,
            RiskLevel.MEDIUM: 0,
            RiskLevel.LOW: 7
        }
        
        severity_adjustment = severity_adjustments.get(severity, 0)
        
        return max(1, base_window + probability_adjustment + severity_adjustment)
    
    def _generate_conflict_prevention_actions(self, sources: List[str], 
                                            severity: RiskLevel) -> List[str]:
        """生成衝突預防行動"""
        actions = []
        
        # 基於衝突源的行動
        action_mapping = {
            'communication_breakdown': 'Implement structured communication protocols',
            'resource_competition': 'Clarify resource allocation and establish fair distribution process',
            'goal_misalignment': 'Conduct goal alignment workshops and clarify objectives',
            'personality_clashes': 'Facilitate team building and conflict resolution training',
            'workload_imbalance': 'Rebalance workload distribution and capacity planning',
            'cultural_differences': 'Provide cultural sensitivity training and inclusive practices'
        }
        
        for source in sources:
            action = action_mapping.get(source)
            if action:
                actions.append(action)
        
        # 基於嚴重程度的緊急行動
        if severity in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            actions.append('Schedule immediate team intervention session')
            actions.append('Assign dedicated conflict mediator')
        
        return actions


class CultureFitAnalyzer:
    """文化適配分析器"""
    
    def __init__(self):
        self.cultural_dimensions = {
            CultureDimension.PSYCHOLOGICAL_SAFETY: {
                'indicators': ['open_communication', 'error_tolerance', 'feedback_comfort'],
                'weight': 0.15
            },
            CultureDimension.INNOVATION: {
                'indicators': ['creativity_encouragement', 'risk_taking_support', 'idea_implementation'],
                'weight': 0.12
            },
            CultureDimension.COLLABORATION: {
                'indicators': ['teamwork_frequency', 'knowledge_sharing', 'cross_functional_cooperation'],
                'weight': 0.13
            },
            CultureDimension.ACCOUNTABILITY: {
                'indicators': ['responsibility_ownership', 'commitment_follow_through', 'performance_standards'],
                'weight': 0.12
            },
            CultureDimension.TRANSPARENCY: {
                'indicators': ['information_sharing', 'decision_clarity', 'process_openness'],
                'weight': 0.11
            },
            CultureDimension.DIVERSITY_INCLUSION: {
                'indicators': ['inclusive_behavior', 'diversity_appreciation', 'equity_practices'],
                'weight': 0.12
            },
            CultureDimension.LEARNING_ORIENTATION: {
                'indicators': ['continuous_learning', 'skill_development', 'knowledge_seeking'],
                'weight': 0.10
            },
            CultureDimension.ADAPTABILITY: {
                'indicators': ['change_acceptance', 'flexibility', 'resilience'],
                'weight': 0.15
            }
        }
    
    def assess_individual_culture_fit(self, person_data: Dict[str, Any], 
                                    team_culture: Dict[str, Any]) -> CulturalFitAssessment:
        """評估個人文化適配度"""
        
        # 計算各文化維度的適配分數
        dimension_fit_scores = {}
        for dimension, config in self.cultural_dimensions.items():
            person_score = self._calculate_person_dimension_score(person_data, config['indicators'])
            team_score = team_culture.get(dimension.value, 0.5)
            
            # 計算適配度（1 - 差異的絕對值）
            fit_score = 1.0 - abs(person_score - team_score)
            dimension_fit_scores[dimension] = fit_score
        
        # 計算總體適配分數
        overall_fit_score = sum(
            score * self.cultural_dimensions[dimension]['weight']
            for dimension, score in dimension_fit_scores.items()
        )
        
        # 評估適應概率
        adaptation_probability = self._calculate_adaptation_probability(
            overall_fit_score, person_data
        )
        
        # 識別整合挑戰
        integration_challenges = self._identify_integration_challenges(
            dimension_fit_scores, person_data, team_culture
        )
        
        # 生成支持建議
        support_recommendations = self._generate_support_recommendations(
            dimension_fit_scores, integration_challenges
        )
        
        # 定義成功指標
        success_indicators = self._define_success_indicators(
            dimension_fit_scores, overall_fit_score
        )
        
        return CulturalFitAssessment(
            person_id=person_data.get('id', 'unknown'),
            overall_fit_score=overall_fit_score,
            dimension_fit_scores=dimension_fit_scores,
            adaptation_probability=adaptation_probability,
            integration_challenges=integration_challenges,
            support_recommendations=support_recommendations,
            success_indicators=success_indicators
        )
    
    def _calculate_person_dimension_score(self, person_data: Dict[str, Any], 
                                        indicators: List[str]) -> float:
        """計算個人維度分數"""
        scores = []
        
        for indicator in indicators:
            # 從個人數據、評估結果或行為指標中獲取分數
            score = (person_data.get(indicator, 0.5) or
                    person_data.get('cultural_assessments', {}).get(indicator, 0.5) or
                    person_data.get('behavioral_indicators', {}).get(indicator, 0.5))
            scores.append(score)
        
        return np.mean(scores) if scores else 0.5
    
    def _calculate_adaptation_probability(self, overall_fit_score: float, 
                                        person_data: Dict[str, Any]) -> float:
        """計算適應概率"""
        base_probability = overall_fit_score
        
        # 調整因子
        adaptability_score = person_data.get('adaptability_score', 0.7)
        learning_agility = person_data.get('learning_agility', 0.6)
        cultural_intelligence = person_data.get('cultural_intelligence', 0.6)
        
        adaptation_probability = (
            base_probability * 0.6 +
            adaptability_score * 0.2 +
            learning_agility * 0.1 +
            cultural_intelligence * 0.1
        )
        
        return min(adaptation_probability, 1.0)
    
    def _identify_integration_challenges(self, dimension_fit_scores: Dict[CultureDimension, float],
                                       person_data: Dict[str, Any], 
                                       team_culture: Dict[str, Any]) -> List[str]:
        """識別整合挑戰"""
        challenges = []
        
        # 基於低適配分數的維度識別挑戰
        low_fit_dimensions = [
            dimension for dimension, score in dimension_fit_scores.items()
            if score < 0.6
        ]
        
        challenge_mapping = {
            CultureDimension.PSYCHOLOGICAL_SAFETY: 'May struggle with open communication and feedback culture',
            CultureDimension.INNOVATION: 'May need support adapting to innovation-focused environment',
            CultureDimension.COLLABORATION: 'May require assistance with collaborative work styles',
            CultureDimension.ACCOUNTABILITY: 'May need clarity on accountability expectations',
            CultureDimension.TRANSPARENCY: 'May need support adapting to transparent communication',
            CultureDimension.DIVERSITY_INCLUSION: 'May require inclusive behavior training',
            CultureDimension.ADAPTABILITY: 'May struggle with pace of change and flexibility requirements'
        }
        
        for dimension in low_fit_dimensions:
            challenge = challenge_mapping.get(dimension)
            if challenge:
                challenges.append(challenge)
        
        return challenges
    
    def _generate_support_recommendations(self, dimension_fit_scores: Dict[CultureDimension, float],
                                        integration_challenges: List[str]) -> List[str]:
        """生成支持建議"""
        recommendations = []
        
        # 基於挑戰生成建議
        if any('communication' in challenge.lower() for challenge in integration_challenges):
            recommendations.append('Assign communication mentor and provide feedback training')
        
        if any('collaboration' in challenge.lower() for challenge in integration_challenges):
            recommendations.append('Facilitate team integration activities and collaboration workshops')
        
        if any('innovation' in challenge.lower() for challenge in integration_challenges):
            recommendations.append('Provide innovation mindset training and creative thinking workshops')
        
        # 基於低分維度生成建議
        low_scoring_dimensions = [
            dimension for dimension, score in dimension_fit_scores.items()
            if score < 0.5
        ]
        
        if low_scoring_dimensions:
            recommendations.append(f'Targeted development in: {", ".join([d.value for d in low_scoring_dimensions])}')
        
        return recommendations
    
    def _define_success_indicators(self, dimension_fit_scores: Dict[CultureDimension, float],
                                 overall_fit_score: float) -> List[str]:
        """定義成功指標"""
        indicators = []
        
        if overall_fit_score > 0.7:
            indicators.append('Monitor integration progress over first 90 days')
        else:
            indicators.append('Intensive monitoring and support over first 6 months')
        
        indicators.extend([
            'Team feedback scores improvement >20%',
            'Cultural behavior assessment scores >0.7',
            'Retention through first year',
            'Peer integration ratings >4.0/5.0'
        ])
        
        return indicators


class CultureAgent(BaseAgent):
    """Culture Agent - 組織文化感知器"""
    
    def __init__(self):
        super().__init__(temperature=0.5)
        self.emotion_monitor = EmotionalIntelligenceMonitor()
        self.conflict_system = ConflictEarlyWarningSystem()
        self.culture_analyzer = CultureFitAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的組織文化感知器和文化健康專家。你的核心職責包括：

1. 文化健康監測：實時監測組織文化的各個維度和健康指標
2. 情緒智能分析：分析團隊情緒狀態、壓力水平和參與度
3. 衝突預警系統：早期識別潛在衝突並提供預防策略
4. 文化適配評估：評估個人與團隊/組織文化的匹配度
5. 文化優化建議：提供改善組織文化和團隊動態的策略

你的分析基於以下理論框架：
- 組織文化理論 (Organizational Culture Theory)
- 情緒智能理論 (Emotional Intelligence Theory)
- 衝突管理理論 (Conflict Management Theory)
- 團隊動態學 (Team Dynamics)
- 心理安全理論 (Psychological Safety Theory)
- 包容性領導原則 (Inclusive Leadership Principles)

請提供基於行為數據的客觀分析，並考慮文化多樣性和個體差異。你的建議應該促進健康、包容和高效的組織文化。""")
    
    async def analyze_context(self, context) -> Dict[str, Any]:
        """分析組織文化上下文"""
        try:
            employee_data = context.employee_data
            organizational_data = context.organizational_data
            
            analysis_results = {
                'recommendations': [],
                'risks': [],
                'opportunities': [],
                'confidence': 0.0,
                'data_quality': 0.0
            }
            
            # Step 1: 文化健康評估
            culture_health = await self._assess_culture_health(organizational_data)
            
            # Step 2: 情緒智能監測
            emotional_analysis = await self._monitor_emotional_intelligence(employee_data)
            
            # Step 3: 衝突風險預測
            conflict_analysis = await self._predict_conflict_risks(employee_data, organizational_data)
            
            # Step 4: 文化適配分析
            cultural_fit_analysis = await self._analyze_cultural_fit(employee_data, organizational_data)
            
            # Step 5: 團隊動態評估
            team_dynamics = await self._assess_team_dynamics(employee_data, organizational_data)
            
            # Step 6: 整合建議生成
            integrated_recommendations = await self._generate_culture_recommendations(
                culture_health, emotional_analysis, conflict_analysis, cultural_fit_analysis, team_dynamics
            )
            
            # Step 7: 風險和機會識別
            culture_risks = await self._identify_culture_risks(conflict_analysis, culture_health)
            culture_opportunities = await self._identify_culture_opportunities(culture_health, team_dynamics)
            
            analysis_results.update({
                'recommendations': integrated_recommendations,
                'risks': culture_risks,
                'opportunities': culture_opportunities,
                'confidence': self._calculate_analysis_confidence(employee_data),
                'data_quality': self._assess_data_quality(employee_data),
                'culture_health_profile': culture_health,
                'emotional_analysis': emotional_analysis,
                'conflict_predictions': conflict_analysis,
                'cultural_fit_assessments': cultural_fit_analysis,
                'team_dynamics': team_dynamics
            })
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Culture Agent analysis failed: {str(e)}")
            return {
                'recommendations': [],
                'risks': ['Culture analysis system error'],
                'opportunities': [],
                'confidence': 0.3,
                'data_quality': 0.3
            }
    
    async def _assess_culture_health(self, organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """評估文化健康"""
        
        # 計算各文化維度分數
        dimension_scores = {}
        for dimension in CultureDimension:
            score = self._calculate_dimension_health(organizational_data, dimension)
            dimension_scores[dimension] = score
        
        # 計算總體文化健康分數
        overall_score = np.mean(list(dimension_scores.values()))
        
        # 分析趨勢方向
        trend_direction = self._analyze_culture_trend(organizational_data)
        
        # 識別風險和優勢領域
        risk_areas = [dim.value for dim, score in dimension_scores.items() if score < 0.5]
        strength_areas = [dim.value for dim, score in dimension_scores.items() if score > 0.8]
        
        # 計算文化匹配度
        cultural_alignment = self._calculate_cultural_alignment(organizational_data)
        
        # 評估參與度指標
        engagement_indicators = self._assess_engagement_indicators(organizational_data)
        
        # 計算倦怠風險
        burnout_risk_score = self._calculate_burnout_risk(organizational_data)
        
        return {
            'overall_score': overall_score,
            'dimension_scores': {dim.value: score for dim, score in dimension_scores.items()},
            'trend_direction': trend_direction,
            'risk_areas': risk_areas,
            'strength_areas': strength_areas,
            'cultural_alignment': cultural_alignment,
            'engagement_indicators': engagement_indicators,
            'burnout_risk_score': burnout_risk_score,
            'health_status': self._categorize_health_status(overall_score)
        }
    
    async def _monitor_emotional_intelligence(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """監測情緒智能"""
        
        if isinstance(employee_data, dict):
            # 單個團隊分析
            emotional_state = self.emotion_monitor.analyze_team_emotional_state(employee_data)
            
            # 檢測異常
            historical_baseline = employee_data.get('emotional_baseline', {
                'overall_sentiment': 0.6,
                'stress_level': 0.4,
                'engagement_level': 0.7,
                'satisfaction_level': 0.6,
                'motivation_level': 0.6
            })
            
            anomalies = self.emotion_monitor.detect_emotional_anomalies(
                emotional_state, historical_baseline
            )
            
            return {
                'emotional_state': emotional_state,
                'emotional_anomalies': anomalies,
                'baseline_comparison': self._compare_with_baseline(emotional_state, historical_baseline),
                'intervention_needs': self._identify_emotional_interventions(emotional_state)
            }
        else:
            # 多團隊分析
            team_emotional_states = []
            for team_data in employee_data:
                state = self.emotion_monitor.analyze_team_emotional_state(team_data)
                team_emotional_states.append({
                    'team_id': team_data.get('team_id', 'unknown'),
                    'emotional_state': state
                })
            
            return {
                'team_emotional_states': team_emotional_states,
                'organizational_emotional_summary': self._summarize_organizational_emotions(team_emotional_states)
            }
    
    async def _predict_conflict_risks(self, employee_data: Dict[str, Any], 
                                    organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """預測衝突風險"""
        
        conflict_predictions = []
        
        if isinstance(employee_data, dict):
            # 單個團隊分析
            prediction = self.conflict_system.assess_conflict_risk(employee_data)
            conflict_predictions.append(prediction.__dict__)
        else:
            # 多團隊分析
            for team_data in employee_data:
                prediction = self.conflict_system.assess_conflict_risk(team_data)
                conflict_predictions.append(prediction.__dict__)
        
        # 分析組織層面衝突風險
        organizational_risk = self._assess_organizational_conflict_risk(conflict_predictions)
        
        return {
            'team_conflict_predictions': conflict_predictions,
            'organizational_conflict_risk': organizational_risk,
            'priority_interventions': self._prioritize_conflict_interventions(conflict_predictions)
        }
    
    async def _analyze_cultural_fit(self, employee_data: Dict[str, Any], 
                                  organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析文化適配"""
        
        team_culture = organizational_data.get('team_culture', {})
        fit_assessments = []
        
        if isinstance(employee_data, dict):
            # 單個員工分析
            assessment = self.culture_analyzer.assess_individual_culture_fit(
                employee_data, team_culture
            )
            fit_assessments.append(assessment.__dict__)
        else:
            # 多員工分析
            for person_data in employee_data:
                assessment = self.culture_analyzer.assess_individual_culture_fit(
                    person_data, team_culture
                )
                fit_assessments.append(assessment.__dict__)
        
        # 分析團隊文化適配總結
        team_fit_summary = self._summarize_team_cultural_fit(fit_assessments)
        
        return {
            'individual_assessments': fit_assessments,
            'team_fit_summary': team_fit_summary,
            'cultural_development_needs': self._identify_cultural_development_needs(fit_assessments)
        }
    
    async def _assess_team_dynamics(self, employee_data: Dict[str, Any], 
                                  organizational_data: Dict[str, Any]) -> Dict[str, Any]:
        """評估團隊動態"""
        
        team_dynamics_list = []
        
        if isinstance(employee_data, dict):
            # 單個團隊
            dynamics = self._calculate_team_dynamics(employee_data)
            team_dynamics_list.append(dynamics.__dict__)
        else:
            # 多個團隊
            for team_data in employee_data:
                dynamics = self._calculate_team_dynamics(team_data)
                team_dynamics_list.append(dynamics.__dict__)
        
        # 分析跨團隊動態
        cross_team_dynamics = self._analyze_cross_team_dynamics(team_dynamics_list)
        
        return {
            'team_dynamics': team_dynamics_list,
            'cross_team_dynamics': cross_team_dynamics,
            'optimization_opportunities': self._identify_dynamics_optimization(team_dynamics_list)
        }
    
    async def _generate_culture_recommendations(self, culture_health: Dict[str, Any],
                                              emotional_analysis: Dict[str, Any],
                                              conflict_analysis: Dict[str, Any],
                                              cultural_fit_analysis: Dict[str, Any],
                                              team_dynamics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成文化建議"""
        recommendations = []
        
        # 基於文化健康的建議
        if culture_health.get('overall_score', 0.5) < 0.6:
            recommendations.append({
                'id': 'culture_health_improvement',
                'title': 'Culture Health Improvement Initiative',
                'description': 'Implement comprehensive culture improvement program',
                'scope': 'organization',
                'type': 'culture_improvement',
                'urgency': 'high',
                'weight': 0.9,
                'focus_areas': culture_health.get('risk_areas', [])
            })
        
        # 基於情緒分析的建議
        emotional_state = emotional_analysis.get('emotional_state', {})
        if emotional_state.get('stress_level', 0.5) > 0.7:
            recommendations.append({
                'id': 'stress_management_program',
                'title': 'Stress Management and Wellbeing Program',
                'description': 'Implement stress reduction and employee wellbeing initiatives',
                'scope': 'team',
                'type': 'wellbeing',
                'urgency': 'high',
                'weight': 0.8
            })
        
        # 基於衝突預測的建議
        high_risk_conflicts = [
            pred for pred in conflict_analysis.get('team_conflict_predictions', [])
            if pred.get('conflict_probability', 0) > 0.7
        ]
        
        if high_risk_conflicts:
            recommendations.append({
                'id': 'conflict_prevention_program',
                'title': 'Conflict Prevention and Resolution Program',
                'description': f'Address {len(high_risk_conflicts)} high-risk conflict situations',
                'scope': 'team',
                'type': 'conflict_management',
                'urgency': 'critical',
                'weight': 1.0,
                'affected_teams': [pred.get('affected_teams', []) for pred in high_risk_conflicts]
            })
        
        # 基於文化適配的建議
        low_fit_individuals = [
            assessment for assessment in cultural_fit_analysis.get('individual_assessments', [])
            if assessment.get('overall_fit_score', 0.5) < 0.5
        ]
        
        if low_fit_individuals:
            recommendations.append({
                'id': 'cultural_integration_support',
                'title': 'Cultural Integration Support Program',
                'description': f'Provide integration support for {len(low_fit_individuals)} employees',
                'scope': 'individual',
                'type': 'cultural_integration',
                'urgency': 'medium',
                'weight': 0.7,
                'target_individuals': [ind.get('person_id') for ind in low_fit_individuals]
            })
        
        # 基於團隊動態的建議
        low_performing_teams = [
            team for team in team_dynamics.get('team_dynamics', [])
            if team.get('cohesion_score', 0.5) < 0.5
        ]
        
        if low_performing_teams:
            recommendations.append({
                'id': 'team_dynamics_enhancement',
                'title': 'Team Dynamics Enhancement Program',
                'description': f'Improve dynamics for {len(low_performing_teams)} underperforming teams',
                'scope': 'team',
                'type': 'team_development',
                'urgency': 'medium',
                'weight': 0.7,
                'target_teams': [team.get('team_id') for team in low_performing_teams]
            })
        
        return recommendations[:8]  # 限制建議數量
    
    def _calculate_dimension_health(self, organizational_data: Dict[str, Any], 
                                  dimension: CultureDimension) -> float:
        """計算文化維度健康度"""
        
        # 獲取維度相關數據
        dimension_data = organizational_data.get('culture_metrics', {}).get(dimension.value, {})
        
        if not dimension_data:
            return 0.6  # 默認分數
        
        # 根據不同維度計算健康度
        if dimension == CultureDimension.PSYCHOLOGICAL_SAFETY:
            return self._calculate_psychological_safety_score(dimension_data)
        elif dimension == CultureDimension.INNOVATION:
            return self._calculate_innovation_score(dimension_data)
        elif dimension == CultureDimension.COLLABORATION:
            return self._calculate_collaboration_score(dimension_data)
        else:
            # 通用計算方法
            indicators = dimension_data.get('indicators', {})
            return np.mean(list(indicators.values())) if indicators else 0.6
    
    def _calculate_psychological_safety_score(self, data: Dict[str, Any]) -> float:
        """計算心理安全分數"""
        indicators = [
            data.get('speak_up_frequency', 0.6),
            data.get('error_reporting_rate', 0.5),
            data.get('feedback_openness', 0.7),
            data.get('interpersonal_risk_taking', 0.6)
        ]
        return np.mean(indicators)
    
    def _calculate_innovation_score(self, data: Dict[str, Any]) -> float:
        """計算創新分數"""
        indicators = [
            data.get('idea_generation_rate', 0.5),
            data.get('experimentation_frequency', 0.4),
            data.get('failure_tolerance', 0.6),
            data.get('creative_problem_solving', 0.6)
        ]
        return np.mean(indicators)
    
    def _calculate_collaboration_score(self, data: Dict[str, Any]) -> float:
        """計算協作分數"""
        indicators = [
            data.get('cross_team_projects', 0.6),
            data.get('knowledge_sharing_frequency', 0.7),
            data.get('mutual_support_instances', 0.7),
            data.get('collective_decision_making', 0.5)
        ]
        return np.mean(indicators)
    
    def _analyze_culture_trend(self, organizational_data: Dict[str, Any]) -> str:
        """分析文化趨勢"""
        historical_data = organizational_data.get('culture_history', [])
        
        if len(historical_data) < 2:
            return 'stable'
        
        recent_scores = [entry.get('overall_score', 0.6) for entry in historical_data[-3:]]
        
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0] + 0.1:
                return 'improving'
            elif recent_scores[-1] < recent_scores[0] - 0.1:
                return 'declining'
        
        return 'stable'
    
    def _calculate_cultural_alignment(self, organizational_data: Dict[str, Any]) -> float:
        """計算文化匹配度"""
        desired_culture = organizational_data.get('desired_culture', {})
        actual_culture = organizational_data.get('actual_culture', {})
        
        if not desired_culture or not actual_culture:
            return 0.7  # 默認分數
        
        alignment_scores = []
        for dimension, desired_score in desired_culture.items():
            actual_score = actual_culture.get(dimension, 0.5)
            alignment = 1.0 - abs(desired_score - actual_score)
            alignment_scores.append(alignment)
        
        return np.mean(alignment_scores) if alignment_scores else 0.7
    
    def _assess_engagement_indicators(self, organizational_data: Dict[str, Any]) -> Dict[str, float]:
        """評估參與度指標"""
        engagement_data = organizational_data.get('engagement_metrics', {})
        
        return {
            'overall_engagement': engagement_data.get('overall_engagement', 0.7),
            'participation_rate': engagement_data.get('participation_rate', 0.6),
            'initiative_taking': engagement_data.get('initiative_taking', 0.5),
            'feedback_frequency': engagement_data.get('feedback_frequency', 0.6),
            'voluntary_contribution': engagement_data.get('voluntary_contribution', 0.5)
        }
    
    def _calculate_burnout_risk(self, organizational_data: Dict[str, Any]) -> float:
        """計算倦怠風險"""
        burnout_indicators = organizational_data.get('burnout_indicators', {})
        
        risk_factors = [
            burnout_indicators.get('workload_intensity', 0.5),
            burnout_indicators.get('overtime_frequency', 0.4),
            burnout_indicators.get('deadline_pressure', 0.5),
            burnout_indicators.get('work_life_imbalance', 0.4),
            burnout_indicators.get('emotional_exhaustion', 0.3)
        ]
        
        return np.mean(risk_factors)
    
    def _categorize_health_status(self, overall_score: float) -> str:
        """分類健康狀態"""
        if overall_score > 0.8:
            return 'excellent'
        elif overall_score > 0.6:
            return 'good'
        elif overall_score > 0.4:
            return 'concerning'
        else:
            return 'critical'
    
    def _compare_with_baseline(self, current_state: Dict[str, float], 
                             baseline: Dict[str, float]) -> Dict[str, str]:
        """與基線比較"""
        comparison = {}
        
        for metric, current_value in current_state.items():
            baseline_value = baseline.get(metric, 0.5)
            difference = current_value - baseline_value
            
            if abs(difference) < 0.1:
                comparison[metric] = 'stable'
            elif difference > 0.1:
                comparison[metric] = 'improved'
            else:
                comparison[metric] = 'declined'
        
        return comparison
    
    def _identify_emotional_interventions(self, emotional_state: Dict[str, float]) -> List[str]:
        """識別情緒干預需求"""
        interventions = []
        
        if emotional_state.get('stress_level', 0.5) > 0.7:
            interventions.append('Stress reduction program needed')
        
        if emotional_state.get('engagement_level', 0.5) < 0.5:
            interventions.append('Engagement enhancement initiatives required')
        
        if emotional_state.get('overall_sentiment', 0.5) < 0.4:
            interventions.append('Morale boosting activities recommended')
        
        return interventions
    
    def _summarize_organizational_emotions(self, team_states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """總結組織情緒"""
        if not team_states:
            return {}
        
        all_metrics = {}
        for team in team_states:
            emotional_state = team.get('emotional_state', {})
            for metric, value in emotional_state.items():
                if metric not in all_metrics:
                    all_metrics[metric] = []
                all_metrics[metric].append(value)
        
        summary = {}
        for metric, values in all_metrics.items():
            summary[f'avg_{metric}'] = np.mean(values)
            summary[f'variance_{metric}'] = np.var(values)
        
        return summary
    
    def _assess_organizational_conflict_risk(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評估組織衝突風險"""
        if not predictions:
            return {'overall_risk': 'low', 'critical_teams': 0}
        
        high_risk_predictions = [
            pred for pred in predictions 
            if pred.get('conflict_probability', 0) > 0.7
        ]
        
        critical_predictions = [
            pred for pred in predictions 
            if pred.get('severity_estimate', 'low') == 'critical'
        ]
        
        avg_probability = np.mean([pred.get('conflict_probability', 0) for pred in predictions])
        
        return {
            'overall_risk': 'high' if avg_probability > 0.6 else 'medium' if avg_probability > 0.4 else 'low',
            'high_risk_teams': len(high_risk_predictions),
            'critical_teams': len(critical_predictions),
            'average_conflict_probability': avg_probability
        }
    
    def _prioritize_conflict_interventions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """優先化衝突干預"""
        priority_interventions = []
        
        # 按嚴重程度和概率排序
        sorted_predictions = sorted(
            predictions,
            key=lambda x: (x.get('conflict_probability', 0), 
                          1 if x.get('severity_estimate') == 'critical' else 0),
            reverse=True
        )
        
        for pred in sorted_predictions[:5]:  # 前5個最高優先級
            intervention = {
                'team': pred.get('affected_teams', ['Unknown'])[0],
                'priority': pred.get('severity_estimate', 'medium'),
                'intervention_window': pred.get('intervention_window', 14),
                'recommended_actions': pred.get('recommended_actions', [])
            }
            priority_interventions.append(intervention)
        
        return priority_interventions
    
    def _summarize_team_cultural_fit(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """總結團隊文化適配"""
        if not assessments:
            return {}
        
        fit_scores = [assessment.get('overall_fit_score', 0.5) for assessment in assessments]
        
        return {
            'team_average_fit': np.mean(fit_scores),
            'fit_variance': np.var(fit_scores),
            'low_fit_individuals': len([score for score in fit_scores if score < 0.5]),
            'high_fit_individuals': len([score for score in fit_scores if score > 0.8]),
            'adaptation_support_needed': len([
                assessment for assessment in assessments
                if assessment.get('adaptation_probability', 0.5) < 0.6
            ])
        }
    
    def _identify_cultural_development_needs(self, assessments: List[Dict[str, Any]]) -> List[str]:
        """識別文化發展需求"""
        needs = []
        
        # 分析共同的低分維度
        all_dimension_scores = {}
        for assessment in assessments:
            dimension_scores = assessment.get('dimension_fit_scores', {})
            for dimension, score in dimension_scores.items():
                if dimension not in all_dimension_scores:
                    all_dimension_scores[dimension] = []
                all_dimension_scores[dimension].append(score)
        
        # 識別需要改進的維度
        for dimension, scores in all_dimension_scores.items():
            avg_score = np.mean(scores)
            if avg_score < 0.6:
                needs.append(f'Team development needed in {dimension}')
        
        return needs
    
    def _calculate_team_dynamics(self, team_data: Dict[str, Any]) -> TeamDynamics:
        """計算團隊動態"""
        
        return TeamDynamics(
            team_id=team_data.get('team_id', 'unknown'),
            cohesion_score=team_data.get('cohesion_indicators', {}).get('overall_cohesion', 0.6),
            communication_effectiveness=team_data.get('communication_metrics', {}).get('effectiveness', 0.6),
            trust_level=team_data.get('trust_indicators', {}).get('overall_trust', 0.6),
            conflict_frequency=team_data.get('conflict_metrics', {}).get('frequency', 0.3),
            collaboration_patterns=team_data.get('collaboration_data', {}),
            leadership_effectiveness=team_data.get('leadership_metrics', {}).get('effectiveness', 0.6),
            morale_indicators=team_data.get('morale_data', {})
        )
    
    def _analyze_cross_team_dynamics(self, team_dynamics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析跨團隊動態"""
        if not team_dynamics:
            return {}
        
        cohesion_scores = [team.get('cohesion_score', 0.5) for team in team_dynamics]
        communication_scores = [team.get('communication_effectiveness', 0.5) for team in team_dynamics]
        trust_scores = [team.get('trust_level', 0.5) for team in team_dynamics]
        
        return {
            'organizational_cohesion': np.mean(cohesion_scores),
            'communication_effectiveness': np.mean(communication_scores),
            'trust_level': np.mean(trust_scores),
            'team_performance_variance': np.var(cohesion_scores),
            'high_performing_teams': len([score for score in cohesion_scores if score > 0.8]),
            'underperforming_teams': len([score for score in cohesion_scores if score < 0.5])
        }
    
    def _identify_dynamics_optimization(self, team_dynamics: List[Dict[str, Any]]) -> List[str]:
        """識別動態優化機會"""
        opportunities = []
        
        # 分析低分領域
        low_cohesion_teams = [
            team for team in team_dynamics 
            if team.get('cohesion_score', 0.5) < 0.5
        ]
        
        if low_cohesion_teams:
            opportunities.append(f'Cohesion improvement needed for {len(low_cohesion_teams)} teams')
        
        low_communication_teams = [
            team for team in team_dynamics 
            if team.get('communication_effectiveness', 0.5) < 0.5
        ]
        
        if low_communication_teams:
            opportunities.append(f'Communication enhancement for {len(low_communication_teams)} teams')
        
        return opportunities
    
    def _calculate_analysis_confidence(self, employee_data: Dict[str, Any]) -> float:
        """計算分析信心度"""
        key_fields = ['behavioral_indicators', 'communication_data', 'team_metrics', 'culture_assessments']
        available_fields = 0
        
        if isinstance(employee_data, dict):
            available_fields = sum(1 for field in key_fields if field in employee_data)
        else:
            # 對於列表數據，檢查平均可用字段
            total_fields = 0
            for data in employee_data:
                total_fields += sum(1 for field in key_fields if field in data)
            available_fields = total_fields / len(employee_data) if employee_data else 0
        
        return available_fields / len(key_fields)
    
    def _assess_data_quality(self, employee_data: Dict[str, Any]) -> float:
        """評估數據質量"""
        quality_score = 0.7  # 基線分數
        
        # 檢查行為數據的完整性
        if isinstance(employee_data, dict):
            if 'behavioral_indicators' in employee_data and employee_data['behavioral_indicators']:
                quality_score += 0.1
            if 'communication_data' in employee_data and employee_data['communication_data']:
                quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    async def _identify_culture_risks(self, conflict_analysis: Dict[str, Any],
                                    culture_health: Dict[str, Any]) -> List[str]:
        """識別文化風險"""
        risks = []
        
        # 基於衝突預測的風險
        high_conflict_risk = conflict_analysis.get('organizational_conflict_risk', {}).get('high_risk_teams', 0)
        if high_conflict_risk > 0:
            risks.append(f'{high_conflict_risk} teams at high conflict risk')
        
        # 基於文化健康的風險
        if culture_health.get('overall_score', 0.5) < 0.5:
            risks.append('Overall culture health below acceptable threshold')
        
        burnout_risk = culture_health.get('burnout_risk_score', 0.5)
        if burnout_risk > 0.7:
            risks.append('High organizational burnout risk detected')
        
        return risks
    
    async def _identify_culture_opportunities(self, culture_health: Dict[str, Any],
                                            team_dynamics: Dict[str, Any]) -> List[str]:
        """識別文化機會"""
        opportunities = []
        
        # 基於文化優勢的機會
        strength_areas = culture_health.get('strength_areas', [])
        if strength_areas:
            opportunities.append(f'Leverage cultural strengths in: {", ".join(strength_areas)}')
        
        # 基於團隊動態的機會
        high_performing_teams = team_dynamics.get('cross_team_dynamics', {}).get('high_performing_teams', 0)
        if high_performing_teams > 0:
            opportunities.append(f'{high_performing_teams} high-performing teams available as cultural models')
        
        return opportunities