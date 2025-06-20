"""
Future Agent - 未來趨勢預測師
預測未來人才需求和組織發展方向
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


class TrendType(Enum):
    TECHNOLOGY = "technology"
    SKILLS = "skills"
    WORK_PATTERNS = "work_patterns"
    MARKET = "market"
    REGULATORY = "regulatory"
    SOCIAL = "social"
    ECONOMIC = "economic"


class TimeHorizon(Enum):
    SHORT_TERM = "3_months"
    MEDIUM_TERM = "1_year"
    LONG_TERM = "3_years"
    STRATEGIC = "5_years"


class ImpactLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    TRANSFORMATIONAL = "transformational"


@dataclass
class SkillDemandForecast:
    """技能需求預測"""
    skill_name: str
    current_demand: float  # 0.0 - 1.0
    predicted_demand: Dict[TimeHorizon, float]
    growth_rate: float  # annual growth rate
    demand_drivers: List[str]
    replacement_risk: float  # risk of being replaced by AI/automation
    investment_priority: str  # high, medium, low
    learning_difficulty: float  # 0.0 - 1.0
    market_availability: float  # talent pool availability


@dataclass
class OrganizationalReadinessAssessment:
    """組織準備度評估"""
    overall_readiness: float  # 0.0 - 1.0
    capability_gaps: List[Dict[str, Any]]
    adaptation_speed: float  # 0.0 - 1.0
    change_capacity: float  # 0.0 - 1.0
    resource_adequacy: float  # 0.0 - 1.0
    cultural_alignment: float  # 0.0 - 1.0
    leadership_preparedness: float  # 0.0 - 1.0
    risk_factors: List[str]
    improvement_recommendations: List[str]


@dataclass
class ScenarioAnalysis:
    """情境分析"""
    scenario_id: str
    scenario_name: str
    probability: float  # 0.0 - 1.0
    impact_level: ImpactLevel
    key_assumptions: List[str]
    implications: Dict[str, Any]
    required_responses: List[str]
    timeline: Dict[str, str]
    success_factors: List[str]
    failure_risks: List[str]


@dataclass
class TrendAnalysis:
    """趨勢分析"""
    trend_id: str
    trend_name: str
    trend_type: TrendType
    confidence_level: float  # 0.0 - 1.0
    impact_timeline: Dict[TimeHorizon, float]
    affected_areas: List[str]
    driving_forces: List[str]
    potential_barriers: List[str]
    organizational_implications: List[str]
    strategic_responses: List[str]


class TrendAnalysisEngine:
    """趨勢分析引擎"""
    
    def __init__(self):
        self.trend_indicators = {
            TrendType.TECHNOLOGY: {
                'ai_adoption_rate': 0.25,
                'automation_penetration': 0.20,
                'digital_transformation': 0.20,
                'cloud_migration': 0.15,
                'data_analytics_usage': 0.20
            },
            TrendType.SKILLS: {
                'digital_literacy_demand': 0.30,
                'soft_skills_importance': 0.25,
                'specialized_expertise': 0.20,
                'adaptability_requirements': 0.25
            },
            TrendType.WORK_PATTERNS: {
                'remote_work_adoption': 0.30,
                'flexible_schedules': 0.25,
                'gig_economy_growth': 0.20,
                'cross_functional_teams': 0.25
            },
            TrendType.MARKET: {
                'industry_disruption': 0.30,
                'customer_behavior_change': 0.25,
                'competitive_landscape': 0.25,
                'globalization_impact': 0.20
            },
            TrendType.SOCIAL: {
                'generational_shifts': 0.25,
                'diversity_expectations': 0.25,
                'sustainability_focus': 0.25,
                'work_life_balance': 0.25
            }
        }
        
        self.external_data_sources = [
            'industry_reports', 'labor_statistics', 'technology_trends',
            'economic_indicators', 'demographic_data'
        ]
    
    def analyze_emerging_trends(self, industry_data: Dict[str, Any], 
                              organizational_context: Dict[str, Any]) -> List[TrendAnalysis]:
        """分析新興趨勢"""
        
        trends = []
        
        for trend_type, indicators in self.trend_indicators.items():
            trend = self._analyze_trend_type(
                trend_type, indicators, industry_data, organizational_context
            )
            if trend:
                trends.append(trend)
        
        # 按信心度和影響力排序
        trends.sort(key=lambda x: x.confidence_level * max(x.impact_timeline.values()), reverse=True)
        
        return trends
    
    def _analyze_trend_type(self, trend_type: TrendType, indicators: Dict[str, float],
                           industry_data: Dict[str, Any], 
                           organizational_context: Dict[str, Any]) -> Optional[TrendAnalysis]:
        """分析特定類型趨勢"""
        
        # 計算趨勢強度
        trend_strength = self._calculate_trend_strength(trend_type, indicators, industry_data)
        
        if trend_strength < 0.3:  # 低於閾值不納入分析
            return None
        
        # 計算信心度
        confidence = self._calculate_trend_confidence(trend_type, industry_data)
        
        # 預測影響時間線
        impact_timeline = self._predict_impact_timeline(trend_type, trend_strength)
        
        # 識別影響領域
        affected_areas = self._identify_affected_areas(trend_type, organizational_context)
        
        # 分析驅動力
        driving_forces = self._analyze_driving_forces(trend_type, industry_data)
        
        # 識別潛在障礙
        barriers = self._identify_barriers(trend_type, organizational_context)
        
        # 組織影響分析
        org_implications = self._analyze_organizational_implications(
            trend_type, trend_strength, organizational_context
        )
        
        # 戰略響應建議
        strategic_responses = self._generate_strategic_responses(
            trend_type, trend_strength, organizational_context
        )
        
        return TrendAnalysis(
            trend_id=f"{trend_type.value}_{datetime.now().strftime('%Y%m%d')}",
            trend_name=self._generate_trend_name(trend_type, trend_strength),
            trend_type=trend_type,
            confidence_level=confidence,
            impact_timeline=impact_timeline,
            affected_areas=affected_areas,
            driving_forces=driving_forces,
            potential_barriers=barriers,
            organizational_implications=org_implications,
            strategic_responses=strategic_responses
        )
    
    def _calculate_trend_strength(self, trend_type: TrendType, indicators: Dict[str, float],
                                industry_data: Dict[str, Any]) -> float:
        """計算趨勢強度"""
        
        # 從行業數據中提取指標值
        indicator_values = []
        trend_data = industry_data.get('trend_data', {}).get(trend_type.value, {})
        
        for indicator, weight in indicators.items():
            value = trend_data.get(indicator, 0.5)  # 默認中性值
            weighted_value = value * weight
            indicator_values.append(weighted_value)
        
        # 計算加權平均
        trend_strength = sum(indicator_values)
        
        # 考慮外部驅動因素
        external_factors = industry_data.get('external_factors', {})
        if external_factors:
            adjustment = np.mean(list(external_factors.values())) * 0.2
            trend_strength += adjustment
        
        return min(trend_strength, 1.0)
    
    def _calculate_trend_confidence(self, trend_type: TrendType, 
                                  industry_data: Dict[str, Any]) -> float:
        """計算趨勢信心度"""
        
        # 基於數據質量和來源多樣性
        data_quality = industry_data.get('data_quality', {}).get(trend_type.value, 0.7)
        source_diversity = len(industry_data.get('data_sources', [])) / len(self.external_data_sources)
        
        # 基於歷史預測準確性
        historical_accuracy = industry_data.get('prediction_accuracy', {}).get(trend_type.value, 0.7)
        
        # 基於專家共識度
        expert_consensus = industry_data.get('expert_consensus', {}).get(trend_type.value, 0.6)
        
        confidence = (
            data_quality * 0.3 +
            source_diversity * 0.2 +
            historical_accuracy * 0.3 +
            expert_consensus * 0.2
        )
        
        return min(confidence, 1.0)
    
    def _predict_impact_timeline(self, trend_type: TrendType, trend_strength: float) -> Dict[TimeHorizon, float]:
        """預測影響時間線"""
        
        # 不同趨勢類型的影響模式
        impact_patterns = {
            TrendType.TECHNOLOGY: {
                TimeHorizon.SHORT_TERM: 0.2,
                TimeHorizon.MEDIUM_TERM: 0.6,
                TimeHorizon.LONG_TERM: 0.9,
                TimeHorizon.STRATEGIC: 1.0
            },
            TrendType.SKILLS: {
                TimeHorizon.SHORT_TERM: 0.3,
                TimeHorizon.MEDIUM_TERM: 0.7,
                TimeHorizon.LONG_TERM: 0.8,
                TimeHorizon.STRATEGIC: 0.9
            },
            TrendType.WORK_PATTERNS: {
                TimeHorizon.SHORT_TERM: 0.5,
                TimeHorizon.MEDIUM_TERM: 0.8,
                TimeHorizon.LONG_TERM: 0.9,
                TimeHorizon.STRATEGIC: 0.8
            },
            TrendType.SOCIAL: {
                TimeHorizon.SHORT_TERM: 0.1,
                TimeHorizon.MEDIUM_TERM: 0.4,
                TimeHorizon.LONG_TERM: 0.8,
                TimeHorizon.STRATEGIC: 1.0
            }
        }
        
        base_pattern = impact_patterns.get(trend_type, {
            TimeHorizon.SHORT_TERM: 0.3,
            TimeHorizon.MEDIUM_TERM: 0.6,
            TimeHorizon.LONG_TERM: 0.8,
            TimeHorizon.STRATEGIC: 0.9
        })
        
        # 基於趨勢強度調整影響
        adjusted_timeline = {}
        for horizon, base_impact in base_pattern.items():
            adjusted_impact = base_impact * trend_strength
            adjusted_timeline[horizon] = min(adjusted_impact, 1.0)
        
        return adjusted_timeline
    
    def _identify_affected_areas(self, trend_type: TrendType, 
                               organizational_context: Dict[str, Any]) -> List[str]:
        """識別影響領域"""
        
        area_mapping = {
            TrendType.TECHNOLOGY: ['IT', 'Operations', 'Customer Service', 'Data Analytics'],
            TrendType.SKILLS: ['Learning & Development', 'Recruitment', 'Performance Management'],
            TrendType.WORK_PATTERNS: ['HR Policies', 'Workplace Design', 'Management Practices'],
            TrendType.MARKET: ['Strategy', 'Sales', 'Marketing', 'Product Development'],
            TrendType.SOCIAL: ['Culture', 'Diversity & Inclusion', 'Employee Engagement']
        }
        
        base_areas = area_mapping.get(trend_type, ['General Operations'])
        
        # 根據組織特點調整
        org_functions = organizational_context.get('key_functions', [])
        relevant_areas = [area for area in base_areas if any(func in area for func in org_functions)]
        
        return relevant_areas or base_areas
    
    def _analyze_driving_forces(self, trend_type: TrendType, 
                              industry_data: Dict[str, Any]) -> List[str]:
        """分析驅動力"""
        
        driving_force_mapping = {
            TrendType.TECHNOLOGY: [
                'Digital transformation acceleration',
                'AI and machine learning advancement',
                'Cloud computing adoption',
                'Data proliferation'
            ],
            TrendType.SKILLS: [
                'Technology skill requirements',
                'Changing job roles',
                'Competitive market pressures',
                'Innovation demands'
            ],
            TrendType.WORK_PATTERNS: [
                'Employee expectations evolution',
                'Technology enabling flexibility',
                'Productivity optimization',
                'Cost management needs'
            ],
            TrendType.MARKET: [
                'Industry disruption',
                'Consumer behavior changes',
                'Global competition',
                'Economic pressures'
            ],
            TrendType.SOCIAL: [
                'Generational workforce changes',
                'Social consciousness growth',
                'Work-life balance priorities',
                'Diversity and inclusion focus'
            ]
        }
        
        return driving_force_mapping.get(trend_type, ['General market forces'])
    
    def _identify_barriers(self, trend_type: TrendType, 
                         organizational_context: Dict[str, Any]) -> List[str]:
        """識別潛在障礙"""
        
        common_barriers = {
            TrendType.TECHNOLOGY: [
                'Legacy system constraints',
                'Technical skill gaps',
                'Change resistance',
                'Budget limitations'
            ],
            TrendType.SKILLS: [
                'Training capacity limitations',
                'Talent acquisition challenges',
                'Learning curve difficulties',
                'Resource allocation conflicts'
            ],
            TrendType.WORK_PATTERNS: [
                'Management mindset resistance',
                'Operational complexity',
                'Performance measurement challenges',
                'Cultural inertia'
            ]
        }
        
        base_barriers = common_barriers.get(trend_type, ['General resistance to change'])
        
        # 基於組織特定因素添加障礙
        org_constraints = organizational_context.get('constraints', [])
        if org_constraints:
            base_barriers.extend(org_constraints[:2])  # 添加最多2個組織特定障礙
        
        return base_barriers
    
    def _analyze_organizational_implications(self, trend_type: TrendType, trend_strength: float,
                                           organizational_context: Dict[str, Any]) -> List[str]:
        """分析組織影響"""
        implications = []
        
        if trend_strength > 0.7:  # 高強度趨勢
            implications.append(f'Significant {trend_type.value} transformation required')
            implications.append('Strategic planning adjustment needed')
            implications.append('Resource reallocation may be necessary')
        elif trend_strength > 0.5:  # 中等強度趨勢
            implications.append(f'Moderate {trend_type.value} adaptation needed')
            implications.append('Gradual capability building required')
        else:  # 低強度趨勢
            implications.append(f'Monitor {trend_type.value} developments')
            implications.append('Prepare for potential future impact')
        
        # 基於組織成熟度添加特定影響
        org_maturity = organizational_context.get('digital_maturity', 'medium')
        if org_maturity == 'low' and trend_type in [TrendType.TECHNOLOGY, TrendType.SKILLS]:
            implications.append('Accelerated capability building urgently needed')
        
        return implications
    
    def _generate_strategic_responses(self, trend_type: TrendType, trend_strength: float,
                                    organizational_context: Dict[str, Any]) -> List[str]:
        """生成戰略響應建議"""
        responses = []
        
        response_templates = {
            TrendType.TECHNOLOGY: [
                'Invest in technology infrastructure upgrade',
                'Develop digital capabilities across workforce',
                'Partner with technology providers',
                'Create innovation labs or centers'
            ],
            TrendType.SKILLS: [
                'Launch comprehensive upskilling programs',
                'Revise recruitment strategies for new skills',
                'Establish learning partnerships with institutions',
                'Create internal skill development pathways'
            ],
            TrendType.WORK_PATTERNS: [
                'Redesign work policies and practices',
                'Implement flexible work arrangements',
                'Upgrade collaboration tools and processes',
                'Train managers for new work models'
            ]
        }
        
        base_responses = response_templates.get(trend_type, [
            'Monitor trend developments closely',
            'Assess organizational readiness',
            'Develop adaptation strategies'
        ])
        
        # 基於趨勢強度選擇響應數量和緊急程度
        if trend_strength > 0.7:
            responses = base_responses  # 全部響應
        elif trend_strength > 0.5:
            responses = base_responses[:3]  # 前3個響應
        else:
            responses = base_responses[:2]  # 前2個響應
        
        return responses
    
    def _generate_trend_name(self, trend_type: TrendType, trend_strength: float) -> str:
        """生成趨勢名稱"""
        intensity_map = {
            0.8: 'Transformational',
            0.6: 'Significant',
            0.4: 'Moderate',
            0.2: 'Emerging'
        }
        
        intensity = 'Emerging'
        for threshold, label in sorted(intensity_map.items(), reverse=True):
            if trend_strength >= threshold:
                intensity = label
                break
        
        return f'{intensity} {trend_type.value.replace("_", " ").title()} Trend'


class SkillDemandPredictor:
    """技能需求預測器"""
    
    def __init__(self):
        self.skill_categories = {
            'technical': ['programming', 'data_analysis', 'cybersecurity', 'cloud_computing', 'ai_ml'],
            'digital': ['digital_literacy', 'social_media', 'e_commerce', 'digital_marketing'],
            'soft': ['leadership', 'communication', 'problem_solving', 'creativity', 'emotional_intelligence'],
            'analytical': ['critical_thinking', 'statistical_analysis', 'research', 'strategic_planning'],
            'collaborative': ['teamwork', 'cross_cultural', 'project_management', 'negotiation']
        }
        
        self.automation_risk_factors = {
            'routine_tasks': 0.8,
            'predictable_physical': 0.7,
            'data_processing': 0.6,
            'basic_analysis': 0.5,
            'creative_work': 0.2,
            'complex_problem_solving': 0.2,
            'interpersonal': 0.1
        }
    
    def predict_skill_demand(self, industry_trends: Dict[str, Any], 
                           organizational_strategy: Dict[str, Any]) -> List[SkillDemandForecast]:
        """預測技能需求"""
        
        forecasts = []
        
        # 分析每個技能類別
        for category, skills in self.skill_categories.items():
            for skill in skills:
                forecast = self._create_skill_forecast(
                    skill, category, industry_trends, organizational_strategy
                )
                forecasts.append(forecast)
        
        # 按投資優先級排序
        forecasts.sort(key=lambda x: (
            x.investment_priority == 'high',
            x.predicted_demand[TimeHorizon.MEDIUM_TERM],
            -x.replacement_risk
        ), reverse=True)
        
        return forecasts
    
    def _create_skill_forecast(self, skill: str, category: str,
                             industry_trends: Dict[str, Any],
                             organizational_strategy: Dict[str, Any]) -> SkillDemandForecast:
        """創建技能預測"""
        
        # 計算當前需求
        current_demand = self._calculate_current_demand(skill, industry_trends)
        
        # 預測未來需求
        predicted_demand = self._predict_future_demand(skill, category, industry_trends)
        
        # 計算增長率
        growth_rate = self._calculate_growth_rate(current_demand, predicted_demand)
        
        # 識別需求驅動因素
        demand_drivers = self._identify_demand_drivers(skill, category, industry_trends)
        
        # 評估替代風險
        replacement_risk = self._assess_replacement_risk(skill, category)
        
        # 確定投資優先級
        investment_priority = self._determine_investment_priority(
            predicted_demand, growth_rate, replacement_risk, organizational_strategy
        )
        
        # 評估學習難度
        learning_difficulty = self._assess_learning_difficulty(skill, category)
        
        # 評估市場可用性
        market_availability = self._assess_market_availability(skill, industry_trends)
        
        return SkillDemandForecast(
            skill_name=skill,
            current_demand=current_demand,
            predicted_demand=predicted_demand,
            growth_rate=growth_rate,
            demand_drivers=demand_drivers,
            replacement_risk=replacement_risk,
            investment_priority=investment_priority,
            learning_difficulty=learning_difficulty,
            market_availability=market_availability
        )
    
    def _calculate_current_demand(self, skill: str, industry_trends: Dict[str, Any]) -> float:
        """計算當前需求"""
        
        # 從行業數據獲取當前需求指標
        skill_data = industry_trends.get('current_skill_demand', {})
        base_demand = skill_data.get(skill, 0.5)
        
        # 根據職位發布、薪資趨勢等調整
        job_posting_frequency = skill_data.get(f'{skill}_job_postings', 0.5)
        salary_trend = skill_data.get(f'{skill}_salary_trend', 0.5)
        
        adjusted_demand = (base_demand * 0.6 + job_posting_frequency * 0.2 + salary_trend * 0.2)
        
        return min(adjusted_demand, 1.0)
    
    def _predict_future_demand(self, skill: str, category: str,
                             industry_trends: Dict[str, Any]) -> Dict[TimeHorizon, float]:
        """預測未來需求"""
        
        current_demand = self._calculate_current_demand(skill, industry_trends)
        
        # 基於類別的增長模式
        growth_patterns = {
            'technical': {
                TimeHorizon.SHORT_TERM: 1.2,
                TimeHorizon.MEDIUM_TERM: 1.5,
                TimeHorizon.LONG_TERM: 1.8,
                TimeHorizon.STRATEGIC: 2.0
            },
            'digital': {
                TimeHorizon.SHORT_TERM: 1.1,
                TimeHorizon.MEDIUM_TERM: 1.3,
                TimeHorizon.LONG_TERM: 1.5,
                TimeHorizon.STRATEGIC: 1.6
            },
            'soft': {
                TimeHorizon.SHORT_TERM: 1.0,
                TimeHorizon.MEDIUM_TERM: 1.1,
                TimeHorizon.LONG_TERM: 1.2,
                TimeHorizon.STRATEGIC: 1.3
            },
            'analytical': {
                TimeHorizon.SHORT_TERM: 1.1,
                TimeHorizon.MEDIUM_TERM: 1.4,
                TimeHorizon.LONG_TERM: 1.7,
                TimeHorizon.STRATEGIC: 1.9
            },
            'collaborative': {
                TimeHorizon.SHORT_TERM: 1.0,
                TimeHorizon.MEDIUM_TERM: 1.2,
                TimeHorizon.LONG_TERM: 1.4,
                TimeHorizon.STRATEGIC: 1.5
            }
        }
        
        pattern = growth_patterns.get(category, growth_patterns['soft'])
        
        predicted_demand = {}
        for horizon, multiplier in pattern.items():
            predicted_value = current_demand * multiplier
            # 考慮市場飽和效應
            predicted_value = min(predicted_value, 1.0)
            predicted_demand[horizon] = predicted_value
        
        return predicted_demand
    
    def _calculate_growth_rate(self, current_demand: float, 
                             predicted_demand: Dict[TimeHorizon, float]) -> float:
        """計算年增長率"""
        
        # 基於中期預測計算年增長率
        medium_term_demand = predicted_demand.get(TimeHorizon.MEDIUM_TERM, current_demand)
        
        if current_demand > 0:
            growth_rate = (medium_term_demand / current_demand) - 1
        else:
            growth_rate = 0.5  # 默認增長率
        
        return growth_rate
    
    def _identify_demand_drivers(self, skill: str, category: str,
                               industry_trends: Dict[str, Any]) -> List[str]:
        """識別需求驅動因素"""
        
        driver_mapping = {
            'technical': [
                'Digital transformation acceleration',
                'Automation and AI adoption',
                'Cybersecurity concerns',
                'Cloud migration trends'
            ],
            'digital': [
                'Digital customer expectations',
                'E-commerce growth',
                'Remote work normalization',
                'Digital marketing evolution'
            ],
            'soft': [
                'Complex problem solving needs',
                'Leadership development focus',
                'Cross-functional collaboration',
                'Change management requirements'
            ],
            'analytical': [
                'Data-driven decision making',
                'Business intelligence growth',
                'Strategic planning importance',
                'Performance optimization needs'
            ],
            'collaborative': [
                'Team-based work models',
                'Global collaboration needs',
                'Project-based organizations',
                'Stakeholder management complexity'
            ]
        }
        
        base_drivers = driver_mapping.get(category, ['General market demand'])
        
        # 基於行業特定趨勢調整
        industry_specific = industry_trends.get('industry_drivers', {}).get(skill, [])
        
        return base_drivers[:3] + industry_specific[:2]  # 限制驅動因素數量
    
    def _assess_replacement_risk(self, skill: str, category: str) -> float:
        """評估替代風險"""
        
        # 基於技能類型的基礎風險
        category_risk = {
            'technical': 0.4,  # 中等風險，部分可自動化
            'digital': 0.3,   # 較低風險，需要人類判斷
            'soft': 0.1,      # 低風險，難以自動化
            'analytical': 0.5, # 中高風險，部分可被AI替代
            'collaborative': 0.2 # 低風險，需要人際互動
        }.get(category, 0.3)
        
        # 基於特定技能調整
        skill_adjustments = {
            'programming': 0.2,  # 創造性編程難以替代
            'data_analysis': 0.6, # 基礎分析可自動化
            'leadership': 0.05,   # 極低替代風險
            'communication': 0.1, # 低替代風險
            'creative': 0.05     # 創造性工作低風險
        }
        
        adjustment = skill_adjustments.get(skill, 0.0)
        final_risk = category_risk + adjustment
        
        return min(max(final_risk, 0.0), 1.0)
    
    def _determine_investment_priority(self, predicted_demand: Dict[TimeHorizon, float],
                                     growth_rate: float, replacement_risk: float,
                                     organizational_strategy: Dict[str, Any]) -> str:
        """確定投資優先級"""
        
        # 計算優先級分數
        demand_score = predicted_demand.get(TimeHorizon.MEDIUM_TERM, 0.5)
        growth_score = min(growth_rate, 1.0) if growth_rate > 0 else 0
        risk_score = 1 - replacement_risk  # 低替代風險 = 高投資價值
        
        # 加權計算
        priority_score = (demand_score * 0.4 + growth_score * 0.3 + risk_score * 0.3)
        
        # 考慮組織戰略重點
        strategic_priorities = organizational_strategy.get('strategic_skills', [])
        if any(skill in str(strategic_priorities) for skill in [predicted_demand]):
            priority_score += 0.2
        
        # 分類優先級
        if priority_score > 0.7:
            return 'high'
        elif priority_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _assess_learning_difficulty(self, skill: str, category: str) -> float:
        """評估學習難度"""
        
        # 基於類別的基礎難度
        category_difficulty = {
            'technical': 0.7,
            'digital': 0.4,
            'soft': 0.5,
            'analytical': 0.6,
            'collaborative': 0.3
        }.get(category, 0.5)
        
        # 特定技能調整
        skill_difficulty = {
            'programming': 0.8,
            'ai_ml': 0.9,
            'leadership': 0.6,
            'communication': 0.3,
            'emotional_intelligence': 0.5
        }
        
        specific_difficulty = skill_difficulty.get(skill, category_difficulty)
        
        return specific_difficulty
    
    def _assess_market_availability(self, skill: str, industry_trends: Dict[str, Any]) -> float:
        """評估市場可用性"""
        
        talent_market = industry_trends.get('talent_market', {})
        
        # 基於供需比例
        supply = talent_market.get(f'{skill}_supply', 0.5)
        demand = talent_market.get(f'{skill}_demand', 0.5)
        
        # 計算可用性（供給相對於需求）
        if demand > 0:
            availability = supply / demand
        else:
            availability = supply
        
        return min(availability, 1.0)


class ScenarioSimulator:
    """情境模擬器"""
    
    def __init__(self):
        self.scenario_templates = {
            'technology_disruption': {
                'name': 'Technology Disruption Scenario',
                'probability_base': 0.6,
                'impact_level': ImpactLevel.HIGH,
                'key_variables': ['ai_adoption_rate', 'automation_speed', 'digital_transformation']
            },
            'workforce_evolution': {
                'name': 'Workforce Evolution Scenario',
                'probability_base': 0.7,
                'impact_level': ImpactLevel.MEDIUM,
                'key_variables': ['remote_work_adoption', 'gig_economy_growth', 'skill_requirements']
            },
            'economic_shift': {
                'name': 'Economic Environment Shift',
                'probability_base': 0.5,
                'impact_level': ImpactLevel.HIGH,
                'key_variables': ['market_conditions', 'industry_consolidation', 'investment_patterns']
            },
            'regulatory_change': {
                'name': 'Regulatory Environment Change',
                'probability_base': 0.4,
                'impact_level': ImpactLevel.MEDIUM,
                'key_variables': ['compliance_requirements', 'data_privacy', 'labor_regulations']
            }
        }
    
    def generate_scenarios(self, trend_analysis: List[TrendAnalysis],
                          organizational_context: Dict[str, Any]) -> List[ScenarioAnalysis]:
        """生成情境分析"""
        
        scenarios = []
        
        for scenario_type, template in self.scenario_templates.items():
            scenario = self._create_scenario(
                scenario_type, template, trend_analysis, organizational_context
            )
            scenarios.append(scenario)
        
        # 按概率和影響力排序
        scenarios.sort(key=lambda x: x.probability * self._impact_weight(x.impact_level), reverse=True)
        
        return scenarios
    
    def _create_scenario(self, scenario_type: str, template: Dict[str, Any],
                        trend_analysis: List[TrendAnalysis],
                        organizational_context: Dict[str, Any]) -> ScenarioAnalysis:
        """創建情境分析"""
        
        # 計算情境概率
        probability = self._calculate_scenario_probability(
            template, trend_analysis, organizational_context
        )
        
        # 生成關鍵假設
        key_assumptions = self._generate_key_assumptions(
            scenario_type, template, trend_analysis
        )
        
        # 分析影響
        implications = self._analyze_scenario_implications(
            scenario_type, template, organizational_context
        )
        
        # 生成響應要求
        required_responses = self._generate_required_responses(
            scenario_type, template, implications
        )
        
        # 創建時間線
        timeline = self._create_scenario_timeline(scenario_type, template)
        
        # 識別成功因素
        success_factors = self._identify_success_factors(scenario_type, organizational_context)
        
        # 識別失敗風險
        failure_risks = self._identify_failure_risks(scenario_type, organizational_context)
        
        return ScenarioAnalysis(
            scenario_id=f"{scenario_type}_{datetime.now().strftime('%Y%m%d')}",
            scenario_name=template['name'],
            probability=probability,
            impact_level=template['impact_level'],
            key_assumptions=key_assumptions,
            implications=implications,
            required_responses=required_responses,
            timeline=timeline,
            success_factors=success_factors,
            failure_risks=failure_risks
        )
    
    def _calculate_scenario_probability(self, template: Dict[str, Any],
                                      trend_analysis: List[TrendAnalysis],
                                      organizational_context: Dict[str, Any]) -> float:
        """計算情境概率"""
        
        base_probability = template['probability_base']
        
        # 基於相關趨勢調整概率
        relevant_trends = [
            trend for trend in trend_analysis
            if any(var in str(trend.driving_forces) for var in template['key_variables'])
        ]
        
        if relevant_trends:
            trend_strength_avg = np.mean([
                max(trend.impact_timeline.values()) for trend in relevant_trends
            ])
            probability_adjustment = (trend_strength_avg - 0.5) * 0.3
        else:
            probability_adjustment = 0
        
        # 基於組織準備度調整
        org_readiness = organizational_context.get('change_readiness', 0.5)
        readiness_adjustment = (org_readiness - 0.5) * 0.2
        
        final_probability = base_probability + probability_adjustment + readiness_adjustment
        
        return min(max(final_probability, 0.1), 0.9)
    
    def _generate_key_assumptions(self, scenario_type: str, template: Dict[str, Any],
                                trend_analysis: List[TrendAnalysis]) -> List[str]:
        """生成關鍵假設"""
        
        assumption_templates = {
            'technology_disruption': [
                'AI adoption accelerates beyond current projections',
                'Automation replaces 30-40% of routine tasks within 3 years',
                'Digital transformation becomes business-critical',
                'Technology costs continue to decrease'
            ],
            'workforce_evolution': [
                'Remote work becomes permanent for 60%+ of knowledge workers',
                'Gig economy expands to 40% of workforce',
                'Skill half-life decreases to 2-3 years',
                'Generational preferences drive work model changes'
            ],
            'economic_shift': [
                'Market volatility increases significantly',
                'Industry consolidation accelerates',
                'Investment priorities shift toward sustainability',
                'Global supply chains undergo restructuring'
            ],
            'regulatory_change': [
                'Data privacy regulations expand globally',
                'Labor law reforms favor employee flexibility',
                'Environmental compliance becomes mandatory',
                'Cross-border talent mobility increases'
            ]
        }
        
        base_assumptions = assumption_templates.get(scenario_type, [
            'Current trends continue',
            'External factors remain stable',
            'Organizational adaptation proceeds as planned'
        ])
        
        # 基於趨勢分析調整假設
        relevant_trends = [
            trend for trend in trend_analysis
            if any(var in str(trend.driving_forces) for var in template['key_variables'])
        ]
        
        if relevant_trends:
            trend_assumptions = [
                f"{trend.trend_name} continues with {trend.confidence_level:.0%} confidence"
                for trend in relevant_trends[:2]
            ]
            base_assumptions.extend(trend_assumptions)
        
        return base_assumptions[:5]  # 限制假設數量
    
    def _analyze_scenario_implications(self, scenario_type: str, template: Dict[str, Any],
                                     organizational_context: Dict[str, Any]) -> Dict[str, Any]:
        """分析情境影響"""
        
        implications = {
            'workforce_impact': [],
            'operational_impact': [],
            'strategic_impact': [],
            'financial_impact': []
        }
        
        implication_mapping = {
            'technology_disruption': {
                'workforce_impact': ['Massive reskilling needs', 'Role redefinition', 'New talent requirements'],
                'operational_impact': ['Process automation', 'System integration challenges', 'Workflow redesign'],
                'strategic_impact': ['Business model evolution', 'Competitive advantage shifts', 'Innovation priorities'],
                'financial_impact': ['Technology investment surge', 'Training cost increases', 'Efficiency gains']
            },
            'workforce_evolution': {
                'workforce_impact': ['Flexible work arrangements', 'Performance management changes', 'Culture adaptation'],
                'operational_impact': ['Remote work infrastructure', 'Collaboration tool needs', 'Management practice changes'],
                'strategic_impact': ['Talent acquisition strategy shift', 'Geographic expansion opportunities', 'Culture redefinition'],
                'financial_impact': ['Real estate cost reduction', 'Technology cost increase', 'Productivity variations']
            }
        }
        
        base_implications = implication_mapping.get(scenario_type, {
            'workforce_impact': ['General workforce changes'],
            'operational_impact': ['Operational adjustments needed'],
            'strategic_impact': ['Strategic review required'],
            'financial_impact': ['Financial planning adjustment']
        })
        
        # 基於組織特點調整影響
        org_size = organizational_context.get('organization_size', 'medium')
        if org_size == 'large':
            for category in implications:
                base_implications[category].append('Large-scale change management required')
        
        return base_implications
    
    def _generate_required_responses(self, scenario_type: str, template: Dict[str, Any],
                                   implications: Dict[str, Any]) -> List[str]:
        """生成所需響應"""
        
        responses = []
        
        # 基於影響生成響應
        for category, impacts in implications.items():
            if category == 'workforce_impact':
                responses.append('Develop comprehensive workforce transformation plan')
            elif category == 'operational_impact':
                responses.append('Redesign operational processes and systems')
            elif category == 'strategic_impact':
                responses.append('Revise strategic plan and priorities')
            elif category == 'financial_impact':
                responses.append('Adjust financial planning and resource allocation')
        
        # 基於情境類型添加特定響應
        scenario_responses = {
            'technology_disruption': [
                'Accelerate digital transformation initiatives',
                'Implement AI and automation strategy'
            ],
            'workforce_evolution': [
                'Design hybrid work policies',
                'Develop virtual collaboration capabilities'
            ],
            'economic_shift': [
                'Enhance business agility and resilience',
                'Diversify revenue streams'
            ],
            'regulatory_change': [
                'Strengthen compliance capabilities',
                'Engage with regulatory developments'
            ]
        }
        
        specific_responses = scenario_responses.get(scenario_type, [])
        responses.extend(specific_responses)
        
        return responses[:6]  # 限制響應數量
    
    def _create_scenario_timeline(self, scenario_type: str, template: Dict[str, Any]) -> Dict[str, str]:
        """創建情境時間線"""
        
        timeline_templates = {
            'technology_disruption': {
                'Initial signals': '3-6 months',
                'Acceleration phase': '6-18 months',
                'Full impact': '18-36 months',
                'Stabilization': '36+ months'
            },
            'workforce_evolution': {
                'Early adoption': '0-6 months',
                'Mainstream adoption': '6-24 months',
                'Maturation': '24-48 months',
                'New equilibrium': '48+ months'
            },
            'economic_shift': {
                'Market signals': '0-3 months',
                'Industry impact': '3-12 months',
                'Organizational response': '12-24 months',
                'Adaptation complete': '24+ months'
            },
            'regulatory_change': {
                'Regulatory announcement': '0-6 months',
                'Implementation period': '6-18 months',
                'Compliance deadline': '18-30 months',
                'Full compliance': '30+ months'
            }
        }
        
        return timeline_templates.get(scenario_type, {
            'Phase 1': '0-12 months',
            'Phase 2': '12-24 months',
            'Phase 3': '24+ months'
        })
    
    def _identify_success_factors(self, scenario_type: str, 
                                organizational_context: Dict[str, Any]) -> List[str]:
        """識別成功因素"""
        
        success_factor_mapping = {
            'technology_disruption': [
                'Strong digital leadership',
                'Agile technology infrastructure',
                'Continuous learning culture',
                'Innovation mindset'
            ],
            'workforce_evolution': [
                'Flexible management practices',
                'Strong communication systems',
                'Trust-based culture',
                'Performance measurement adaptation'
            ],
            'economic_shift': [
                'Financial resilience',
                'Market diversification',
                'Agile decision-making',
                'Stakeholder relationships'
            ],
            'regulatory_change': [
                'Compliance expertise',
                'Regulatory monitoring systems',
                'Risk management capabilities',
                'Legal advisory support'
            ]
        }
        
        base_factors = success_factor_mapping.get(scenario_type, [
            'Strong leadership',
            'Organizational agility',
            'Employee engagement',
            'Strategic clarity'
        ])
        
        # 基於組織能力調整
        org_strengths = organizational_context.get('organizational_strengths', [])
        relevant_strengths = [strength for strength in org_strengths if strength in str(base_factors)]
        
        if relevant_strengths:
            base_factors.append(f'Leverage existing {relevant_strengths[0]}')
        
        return base_factors[:5]
    
    def _identify_failure_risks(self, scenario_type: str,
                              organizational_context: Dict[str, Any]) -> List[str]:
        """識別失敗風險"""
        
        risk_mapping = {
            'technology_disruption': [
                'Technology investment delays',
                'Skill development bottlenecks',
                'Change resistance',
                'Integration complexities'
            ],
            'workforce_evolution': [
                'Management resistance to flexibility',
                'Performance measurement difficulties',
                'Communication breakdowns',
                'Culture fragmentation'
            ],
            'economic_shift': [
                'Insufficient financial reserves',
                'Market position weakening',
                'Strategic misalignment',
                'Stakeholder confidence loss'
            ],
            'regulatory_change': [
                'Compliance gaps',
                'Regulatory misinterpretation',
                'Implementation delays',
                'Cost overruns'
            ]
        }
        
        base_risks = risk_mapping.get(scenario_type, [
            'Inadequate preparation',
            'Resource constraints',
            'Execution failures',
            'External pressures'
        ])
        
        # 基於組織弱點調整
        org_weaknesses = organizational_context.get('organizational_weaknesses', [])
        if org_weaknesses:
            base_risks.append(f'Existing weakness in {org_weaknesses[0]}')
        
        return base_risks[:5]
    
    def _impact_weight(self, impact_level: ImpactLevel) -> float:
        """影響權重"""
        weights = {
            ImpactLevel.LOW: 0.2,
            ImpactLevel.MEDIUM: 0.5,
            ImpactLevel.HIGH: 0.8,
            ImpactLevel.TRANSFORMATIONAL: 1.0
        }
        return weights.get(impact_level, 0.5)


class AdaptabilityEvaluator:
    """適應性評估器"""
    
    def __init__(self):
        self.readiness_dimensions = {
            'technological_readiness': 0.25,
            'cultural_adaptability': 0.20,
            'leadership_capability': 0.20,
            'resource_availability': 0.15,
            'learning_agility': 0.20
        }
    
    def assess_organizational_readiness(self, organizational_data: Dict[str, Any],
                                     future_requirements: Dict[str, Any]) -> OrganizationalReadinessAssessment:
        """評估組織準備度"""
        
        # 計算各維度準備度
        dimension_scores = {}
        for dimension, weight in self.readiness_dimensions.items():
            score = self._assess_dimension_readiness(organizational_data, dimension)
            dimension_scores[dimension] = score
        
        # 計算總體準備度
        overall_readiness = sum(
            score * weight for (dimension, score), weight in 
            zip(dimension_scores.items(), self.readiness_dimensions.values())
        )
        
        # 識別能力差距
        capability_gaps = self._identify_capability_gaps(
            organizational_data, future_requirements
        )
        
        # 評估其他關鍵指標
        adaptation_speed = self._assess_adaptation_speed(organizational_data)
        change_capacity = self._assess_change_capacity(organizational_data)
        resource_adequacy = self._assess_resource_adequacy(organizational_data, future_requirements)
        cultural_alignment = self._assess_cultural_alignment(organizational_data)
        leadership_preparedness = self._assess_leadership_preparedness(organizational_data)
        
        # 識別風險因素
        risk_factors = self._identify_readiness_risks(
            dimension_scores, organizational_data
        )
        
        # 生成改進建議
        improvement_recommendations = self._generate_improvement_recommendations(
            dimension_scores, capability_gaps, risk_factors
        )
        
        return OrganizationalReadinessAssessment(
            overall_readiness=overall_readiness,
            capability_gaps=capability_gaps,
            adaptation_speed=adaptation_speed,
            change_capacity=change_capacity,
            resource_adequacy=resource_adequacy,
            cultural_alignment=cultural_alignment,
            leadership_preparedness=leadership_preparedness,
            risk_factors=risk_factors,
            improvement_recommendations=improvement_recommendations
        )
    
    def _assess_dimension_readiness(self, organizational_data: Dict[str, Any], 
                                  dimension: str) -> float:
        """評估維度準備度"""
        
        dimension_data = organizational_data.get('readiness_metrics', {}).get(dimension, {})
        
        if dimension == 'technological_readiness':
            return self._assess_tech_readiness(dimension_data)
        elif dimension == 'cultural_adaptability':
            return self._assess_cultural_adaptability(dimension_data)
        elif dimension == 'leadership_capability':
            return self._assess_leadership_capability(dimension_data)
        elif dimension == 'resource_availability':
            return self._assess_resource_availability(dimension_data)
        elif dimension == 'learning_agility':
            return self._assess_learning_agility(dimension_data)
        else:
            return 0.6  # 默認分數
    
    def _assess_tech_readiness(self, data: Dict[str, Any]) -> float:
        """評估技術準備度"""
        indicators = [
            data.get('infrastructure_maturity', 0.6),
            data.get('digital_skills_level', 0.5),
            data.get('technology_adoption_rate', 0.6),
            data.get('innovation_capacity', 0.5)
        ]
        return np.mean(indicators)
    
    def _assess_cultural_adaptability(self, data: Dict[str, Any]) -> float:
        """評估文化適應性"""
        indicators = [
            data.get('change_acceptance', 0.6),
            data.get('learning_orientation', 0.7),
            data.get('innovation_mindset', 0.5),
            data.get('risk_tolerance', 0.5)
        ]
        return np.mean(indicators)
    
    def _assess_leadership_capability(self, data: Dict[str, Any]) -> float:
        """評估領導能力"""
        indicators = [
            data.get('vision_clarity', 0.6),
            data.get('change_leadership', 0.6),
            data.get('decision_agility', 0.5),
            data.get('stakeholder_management', 0.6)
        ]
        return np.mean(indicators)
    
    def _assess_resource_availability(self, data: Dict[str, Any]) -> float:
        """評估資源可用性"""
        indicators = [
            data.get('financial_capacity', 0.6),
            data.get('human_resources', 0.7),
            data.get('time_availability', 0.5),
            data.get('technology_resources', 0.6)
        ]
        return np.mean(indicators)
    
    def _assess_learning_agility(self, data: Dict[str, Any]) -> float:
        """評估學習敏捷性"""
        indicators = [
            data.get('learning_speed', 0.6),
            data.get('knowledge_retention', 0.7),
            data.get('skill_transfer', 0.6),
            data.get('continuous_improvement', 0.6)
        ]
        return np.mean(indicators)
    
    def _identify_capability_gaps(self, organizational_data: Dict[str, Any],
                                future_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """識別能力差距"""
        gaps = []
        
        current_capabilities = organizational_data.get('current_capabilities', {})
        required_capabilities = future_requirements.get('required_capabilities', {})
        
        for capability, required_level in required_capabilities.items():
            current_level = current_capabilities.get(capability, 0.3)
            
            if current_level < required_level:
                gap = {
                    'capability': capability,
                    'current_level': current_level,
                    'required_level': required_level,
                    'gap_size': required_level - current_level,
                    'priority': 'high' if required_level - current_level > 0.4 else 'medium',
                    'development_time': self._estimate_development_time(
                        capability, required_level - current_level
                    )
                }
                gaps.append(gap)
        
        # 按差距大小排序
        gaps.sort(key=lambda x: x['gap_size'], reverse=True)
        
        return gaps
    
    def _estimate_development_time(self, capability: str, gap_size: float) -> str:
        """估算發展時間"""
        base_months = 6
        
        # 基於能力類型調整
        capability_multipliers = {
            'technical': 1.5,
            'leadership': 2.0,
            'cultural': 2.5,
            'process': 1.0
        }
        
        capability_type = 'process'  # 默認
        for cap_type in capability_multipliers:
            if cap_type in capability.lower():
                capability_type = cap_type
                break
        
        estimated_months = int(base_months * capability_multipliers[capability_type] * (gap_size + 0.5))
        
        if estimated_months <= 6:
            return '3-6 months'
        elif estimated_months <= 12:
            return '6-12 months'
        elif estimated_months <= 24:
            return '1-2 years'
        else:
            return '2+ years'
    
    def _assess_adaptation_speed(self, organizational_data: Dict[str, Any]) -> float:
        """評估適應速度"""
        speed_indicators = organizational_data.get('adaptation_metrics', {})
        
        indicators = [
            speed_indicators.get('decision_speed', 0.6),
            speed_indicators.get('implementation_speed', 0.5),
            speed_indicators.get('learning_speed', 0.6),
            speed_indicators.get('change_adoption_rate', 0.5)
        ]
        
        return np.mean(indicators)
    
    def _assess_change_capacity(self, organizational_data: Dict[str, Any]) -> float:
        """評估變革能力"""
        change_metrics = organizational_data.get('change_capacity_metrics', {})
        
        indicators = [
            change_metrics.get('change_bandwidth', 0.6),
            change_metrics.get('change_management_maturity', 0.5),
            change_metrics.get('employee_change_readiness', 0.6),
            change_metrics.get('change_success_rate', 0.5)
        ]
        
        return np.mean(indicators)
    
    def _assess_resource_adequacy(self, organizational_data: Dict[str, Any],
                                future_requirements: Dict[str, Any]) -> float:
        """評估資源充足性"""
        
        available_resources = organizational_data.get('available_resources', {})
        required_resources = future_requirements.get('resource_requirements', {})
        
        adequacy_scores = []
        for resource_type, required_amount in required_resources.items():
            available_amount = available_resources.get(resource_type, 0.5)
            adequacy = min(available_amount / required_amount, 1.0) if required_amount > 0 else 1.0
            adequacy_scores.append(adequacy)
        
        return np.mean(adequacy_scores) if adequacy_scores else 0.6
    
    def _assess_cultural_alignment(self, organizational_data: Dict[str, Any]) -> float:
        """評估文化匹配度"""
        cultural_metrics = organizational_data.get('cultural_alignment_metrics', {})
        
        indicators = [
            cultural_metrics.get('value_alignment', 0.7),
            cultural_metrics.get('behavior_consistency', 0.6),
            cultural_metrics.get('culture_change_readiness', 0.5),
            cultural_metrics.get('leadership_culture_fit', 0.6)
        ]
        
        return np.mean(indicators)
    
    def _assess_leadership_preparedness(self, organizational_data: Dict[str, Any]) -> float:
        """評估領導準備度"""
        leadership_metrics = organizational_data.get('leadership_preparedness_metrics', {})
        
        indicators = [
            leadership_metrics.get('future_vision_clarity', 0.6),
            leadership_metrics.get('transformation_experience', 0.5),
            leadership_metrics.get('stakeholder_buy_in', 0.6),
            leadership_metrics.get('resource_commitment', 0.6)
        ]
        
        return np.mean(indicators)
    
    def _identify_readiness_risks(self, dimension_scores: Dict[str, float],
                                organizational_data: Dict[str, Any]) -> List[str]:
        """識別準備度風險"""
        risks = []
        
        # 基於低分維度識別風險
        for dimension, score in dimension_scores.items():
            if score < 0.5:
                risk_mapping = {
                    'technological_readiness': 'Technology infrastructure may not support future requirements',
                    'cultural_adaptability': 'Organizational culture may resist necessary changes',
                    'leadership_capability': 'Leadership may lack skills for transformation management',
                    'resource_availability': 'Insufficient resources for required changes',
                    'learning_agility': 'Organization may struggle to acquire new capabilities quickly'
                }
                
                risk = risk_mapping.get(dimension)
                if risk:
                    risks.append(risk)
        
        # 基於組織特定因素添加風險
        org_risks = organizational_data.get('specific_risks', [])
        risks.extend(org_risks[:3])  # 添加最多3個特定風險
        
        return risks
    
    def _generate_improvement_recommendations(self, dimension_scores: Dict[str, float],
                                            capability_gaps: List[Dict[str, Any]],
                                            risk_factors: List[str]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 基於低分維度生成建議
        for dimension, score in dimension_scores.items():
            if score < 0.6:
                improvement_mapping = {
                    'technological_readiness': 'Invest in technology infrastructure and digital skills development',
                    'cultural_adaptability': 'Implement culture change initiatives and change management training',
                    'leadership_capability': 'Develop leadership capabilities for transformation management',
                    'resource_availability': 'Secure additional resources or optimize resource allocation',
                    'learning_agility': 'Establish learning and development programs for capability building'
                }
                
                recommendation = improvement_mapping.get(dimension)
                if recommendation:
                    recommendations.append(recommendation)
        
        # 基於能力差距生成建議
        high_priority_gaps = [gap for gap in capability_gaps if gap['priority'] == 'high']
        if high_priority_gaps:
            recommendations.append(f'Priority focus on {len(high_priority_gaps)} critical capability gaps')
        
        # 基於風險因素生成建議
        if len(risk_factors) > 3:
            recommendations.append('Comprehensive risk mitigation strategy required')
        
        return recommendations[:6]  # 限制建議數量


class FutureAgent(BaseAgent):
    """Future Agent - 未來趨勢預測師"""
    
    def __init__(self):
        super().__init__(temperature=0.6)
        self.trend_analyzer = TrendAnalysisEngine()
        self.skill_predictor = SkillDemandPredictor()
        self.scenario_simulator = ScenarioSimulator()
        self.adaptability_evaluator = AdaptabilityEvaluator()
        self.logger = logging.getLogger(__name__)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位專業的未來趨勢預測師和戰略前瞻專家。你的核心職責包括：

1. 趨勢分析：識別和分析影響人才管理的新興趨勢
2. 技能需求預測：預測未來3-5年的關鍵技能需求變化
3. 情境規劃：設計多種未來情境並分析應對策略
4. 組織適應力評估：評估組織面對未來變化的準備度
5. 戰略前瞻建議：提供前瞻性的人才戰略建議

你的分析基於以下方法論：
- 趨勢分析方法 (Trend Analysis Methodology)
- 情境規劃技術 (Scenario Planning Techniques)
- 德爾菲預測法 (Delphi Forecasting Method)
- 技術採用生命週期 (Technology Adoption Lifecycle)
- 組織變革理論 (Organizational Change Theory)
- 戰略前瞻框架 (Strategic Foresight Framework)

請提供基於數據和證據的預測，並考慮多種可能性和不確定性。你的建議應該幫助組織為未來做好準備並建立適應能力。""")
    
    async def analyze_context(self, context) -> Dict[str, Any]:
        """分析未來趨勢上下文"""
        try:
            organizational_data = context.organizational_data
            business_context = context.business_context
            
            analysis_results = {
                'recommendations': [],
                'risks': [],
                'opportunities': [],
                'confidence': 0.0,
                'data_quality': 0.0
            }
            
            # Step 1: 趨勢分析
            trend_analysis = await self._analyze_emerging_trends(business_context, organizational_data)
            
            # Step 2: 技能需求預測
            skill_forecasts = await self._predict_skill_demands(business_context, organizational_data)
            
            # Step 3: 情境模擬
            scenario_analysis = await self._simulate_future_scenarios(trend_analysis, organizational_data)
            
            # Step 4: 組織適應力評估
            readiness_assessment = await self._assess_organizational_readiness(
                organizational_data, business_context
            )
            
            # Step 5: 整合建議生成
            integrated_recommendations = await self._generate_future_recommendations(
                trend_analysis, skill_forecasts, scenario_analysis, readiness_assessment
            )
            
            # Step 6: 風險和機會識別
            future_risks = await self._identify_future_risks(trend_analysis, scenario_analysis)
            future_opportunities = await self._identify_future_opportunities(
                skill_forecasts, scenario_analysis
            )
            
            analysis_results.update({
                'recommendations': integrated_recommendations,
                'risks': future_risks,
                'opportunities': future_opportunities,
                'confidence': self._calculate_analysis_confidence(business_context),
                'data_quality': self._assess_data_quality(business_context),
                'trend_analysis': trend_analysis,
                'skill_forecasts': skill_forecasts,
                'scenario_analysis': scenario_analysis,
                'readiness_assessment': readiness_assessment
            })
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Future Agent analysis failed: {str(e)}")
            return {
                'recommendations': [],
                'risks': ['Future analysis system error'],
                'opportunities': [],
                'confidence': 0.3,
                'data_quality': 0.3
            }
    
    async def _analyze_emerging_trends(self, business_context: Dict[str, Any],
                                     organizational_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析新興趨勢"""
        
        # 構建行業數據
        industry_data = self._construct_industry_data(business_context)
        
        # 執行趨勢分析
        trends = self.trend_analyzer.analyze_emerging_trends(industry_data, organizational_data)
        
        # 轉換為字典格式便於後續處理
        trend_dicts = [trend.__dict__ for trend in trends]
        
        return trend_dicts
    
    async def _predict_skill_demands(self, business_context: Dict[str, Any],
                                   organizational_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """預測技能需求"""
        
        # 構建行業趨勢數據
        industry_trends = self._construct_industry_trends(business_context)
        
        # 提取組織戰略
        organizational_strategy = organizational_data.get('strategic_priorities', {})
        
        # 執行技能需求預測
        forecasts = self.skill_predictor.predict_skill_demand(industry_trends, organizational_strategy)
        
        # 轉換為字典格式
        forecast_dicts = [forecast.__dict__ for forecast in forecasts]
        
        return forecast_dicts
    
    async def _simulate_future_scenarios(self, trend_analysis: List[Dict[str, Any]],
                                       organizational_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """模擬未來情境"""
        
        # 重建TrendAnalysis對象（簡化處理）
        trend_objects = []
        for trend_dict in trend_analysis:
            # 創建簡化的趨勢對象用於模擬
            trend_obj = type('TrendAnalysis', (), trend_dict)
            trend_objects.append(trend_obj)
        
        # 執行情境模擬
        scenarios = self.scenario_simulator.generate_scenarios(trend_objects, organizational_data)
        
        # 轉換為字典格式
        scenario_dicts = [scenario.__dict__ for scenario in scenarios]
        
        return scenario_dicts
    
    async def _assess_organizational_readiness(self, organizational_data: Dict[str, Any],
                                             business_context: Dict[str, Any]) -> Dict[str, Any]:
        """評估組織準備度"""
        
        # 構建未來需求數據
        future_requirements = self._construct_future_requirements(business_context)
        
        # 執行準備度評估
        assessment = self.adaptability_evaluator.assess_organizational_readiness(
            organizational_data, future_requirements
        )
        
        # 轉換為字典格式
        return assessment.__dict__
    
    async def _generate_future_recommendations(self, trend_analysis: List[Dict[str, Any]],
                                             skill_forecasts: List[Dict[str, Any]],
                                             scenario_analysis: List[Dict[str, Any]],
                                             readiness_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成未來建議"""
        recommendations = []
        
        # 基於趨勢分析的建議
        high_impact_trends = [
            trend for trend in trend_analysis 
            if trend.get('confidence_level', 0.5) > 0.7 and 
               max(trend.get('impact_timeline', {}).values()) > 0.7
        ]
        
        if high_impact_trends:
            recommendations.append({
                'id': 'high_impact_trend_preparation',
                'title': 'Prepare for High-Impact Trends',
                'description': f'Proactive preparation for {len(high_impact_trends)} high-impact trends',
                'scope': 'organization',
                'type': 'trend_adaptation',
                'urgency': 'high',
                'weight': 0.9,
                'affected_trends': [trend.get('trend_name') for trend in high_impact_trends]
            })
        
        # 基於技能預測的建議
        high_priority_skills = [
            forecast for forecast in skill_forecasts 
            if forecast.get('investment_priority') == 'high'
        ]
        
        if high_priority_skills:
            recommendations.append({
                'id': 'strategic_skill_development',
                'title': 'Strategic Skill Development Program',
                'description': f'Invest in {len(high_priority_skills)} high-priority skills for future readiness',
                'scope': 'organization',
                'type': 'skill_development',
                'urgency': 'high',
                'weight': 0.9,
                'priority_skills': [skill.get('skill_name') for skill in high_priority_skills]
            })
        
        # 基於情境分析的建議
        high_probability_scenarios = [
            scenario for scenario in scenario_analysis 
            if scenario.get('probability', 0.5) > 0.6
        ]
        
        if high_probability_scenarios:
            recommendations.append({
                'id': 'scenario_contingency_planning',
                'title': 'Scenario-Based Contingency Planning',
                'description': f'Develop contingency plans for {len(high_probability_scenarios)} likely scenarios',
                'scope': 'organization',
                'type': 'strategic_planning',
                'urgency': 'medium',
                'weight': 0.8,
                'target_scenarios': [scenario.get('scenario_name') for scenario in high_probability_scenarios]
            })
        
        # 基於準備度評估的建議
        overall_readiness = readiness_assessment.get('overall_readiness', 0.5)
        if overall_readiness < 0.6:
            recommendations.append({
                'id': 'organizational_readiness_enhancement',
                'title': 'Organizational Readiness Enhancement',
                'description': 'Comprehensive program to improve future readiness capabilities',
                'scope': 'organization',
                'type': 'capability_building',
                'urgency': 'high',
                'weight': 0.9,
                'focus_areas': readiness_assessment.get('improvement_recommendations', [])
            })
        
        # 基於能力差距的建議
        capability_gaps = readiness_assessment.get('capability_gaps', [])
        critical_gaps = [gap for gap in capability_gaps if gap.get('priority') == 'high']
        
        if critical_gaps:
            recommendations.append({
                'id': 'critical_capability_gap_closure',
                'title': 'Critical Capability Gap Closure',
                'description': f'Address {len(critical_gaps)} critical capability gaps',
                'scope': 'organization',
                'type': 'capability_development',
                'urgency': 'critical',
                'weight': 1.0,
                'capability_gaps': [gap.get('capability') for gap in critical_gaps]
            })
        
        return recommendations[:8]  # 限制建議數量
    
    def _construct_industry_data(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建行業數據"""
        
        # 基於業務上下文構建行業趨勢數據
        industry_data = {
            'trend_data': {},
            'external_factors': {},
            'data_quality': {},
            'data_sources': ['industry_reports', 'market_research'],
            'prediction_accuracy': {},
            'expert_consensus': {}
        }
        
        # 填充趨勢數據
        for trend_type in TrendType:
            industry_data['trend_data'][trend_type.value] = self._generate_trend_indicators(
                trend_type, business_context
            )
            industry_data['data_quality'][trend_type.value] = 0.7
            industry_data['prediction_accuracy'][trend_type.value] = 0.7
            industry_data['expert_consensus'][trend_type.value] = 0.6
        
        # 外部因素
        industry_data['external_factors'] = business_context.get('external_factors', {
            'economic_conditions': 0.6,
            'regulatory_environment': 0.5,
            'competitive_pressure': 0.7
        })
        
        return industry_data
    
    def _generate_trend_indicators(self, trend_type: TrendType, 
                                 business_context: Dict[str, Any]) -> Dict[str, float]:
        """生成趨勢指標"""
        
        # 基於業務上下文和趨勢類型生成指標
        base_indicators = {
            'indicator_1': 0.6,
            'indicator_2': 0.5,
            'indicator_3': 0.7,
            'indicator_4': 0.4
        }
        
        # 根據行業特點調整
        industry = business_context.get('industry', 'general')
        if industry in ['technology', 'software']:
            if trend_type in [TrendType.TECHNOLOGY, TrendType.SKILLS]:
                # 技術行業的技術和技能趨勢更強
                base_indicators = {k: min(v + 0.2, 1.0) for k, v in base_indicators.items()}
        
        return base_indicators
    
    def _construct_industry_trends(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建行業趨勢數據"""
        
        return {
            'current_skill_demand': self._generate_current_skill_demand(business_context),
            'talent_market': self._generate_talent_market_data(business_context),
            'industry_drivers': self._generate_industry_drivers(business_context)
        }
    
    def _generate_current_skill_demand(self, business_context: Dict[str, Any]) -> Dict[str, float]:
        """生成當前技能需求數據"""
        
        base_demand = {
            'programming': 0.8,
            'data_analysis': 0.7,
            'leadership': 0.6,
            'communication': 0.7,
            'digital_literacy': 0.6,
            'ai_ml': 0.5,
            'project_management': 0.6,
            'cybersecurity': 0.7
        }
        
        # 根據行業調整
        industry = business_context.get('industry', 'general')
        if industry in ['technology', 'software']:
            technical_skills = ['programming', 'data_analysis', 'ai_ml', 'cybersecurity']
            for skill in technical_skills:
                if skill in base_demand:
                    base_demand[skill] = min(base_demand[skill] + 0.2, 1.0)
        
        return base_demand
    
    def _generate_talent_market_data(self, business_context: Dict[str, Any]) -> Dict[str, float]:
        """生成人才市場數據"""
        
        return {
            'programming_supply': 0.4,
            'programming_demand': 0.8,
            'leadership_supply': 0.6,
            'leadership_demand': 0.7,
            'data_analysis_supply': 0.5,
            'data_analysis_demand': 0.8
        }
    
    def _generate_industry_drivers(self, business_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """生成行業驅動因素"""
        
        return {
            'programming': ['Digital transformation', 'Automation needs'],
            'data_analysis': ['Data-driven decisions', 'Business intelligence'],
            'leadership': ['Organizational change', 'Team management']
        }
    
    def _construct_future_requirements(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """構建未來需求數據"""
        
        return {
            'required_capabilities': {
                'digital_transformation': 0.8,
                'agile_leadership': 0.7,
                'data_analytics': 0.6,
                'innovation_management': 0.5,
                'change_management': 0.7
            },
            'resource_requirements': {
                'technology_investment': 0.8,
                'training_budget': 0.7,
                'talent_acquisition': 0.6,
                'change_capacity': 0.5
            }
        }
    
    def _calculate_analysis_confidence(self, business_context: Dict[str, Any]) -> float:
        """計算分析信心度"""
        
        # 基於數據完整性和質量
        data_completeness = len(business_context) / 10  # 假設完整數據有10個字段
        data_quality = business_context.get('data_quality_score', 0.7)
        
        confidence = (data_completeness * 0.5 + data_quality * 0.5)
        return min(confidence, 1.0)
    
    def _assess_data_quality(self, business_context: Dict[str, Any]) -> float:
        """評估數據質量"""
        
        quality_indicators = [
            'industry_trends' in business_context,
            'market_data' in business_context,
            'competitive_intelligence' in business_context,
            'external_factors' in business_context
        ]
        
        quality_score = sum(quality_indicators) / len(quality_indicators)
        return quality_score
    
    async def _identify_future_risks(self, trend_analysis: List[Dict[str, Any]],
                                   scenario_analysis: List[Dict[str, Any]]) -> List[str]:
        """識別未來風險"""
        risks = []
        
        # 基於趨勢分析的風險
        high_uncertainty_trends = [
            trend for trend in trend_analysis 
            if trend.get('confidence_level', 0.5) < 0.6 and 
               max(trend.get('impact_timeline', {}).values()) > 0.6
        ]
        
        if high_uncertainty_trends:
            risks.append(f'{len(high_uncertainty_trends)} high-impact trends with uncertain timing')
        
        # 基於情境分析的風險
        high_impact_scenarios = [
            scenario for scenario in scenario_analysis 
            if scenario.get('impact_level') in ['high', 'transformational']
        ]
        
        if high_impact_scenarios:
            risks.append(f'{len(high_impact_scenarios)} high-impact scenarios require preparation')
        
        # 通用未來風險
        risks.extend([
            'Skill obsolescence due to automation',
            'Talent acquisition challenges in emerging skills',
            'Organizational inertia limiting adaptation speed'
        ])
        
        return risks[:6]  # 限制風險數量
    
    async def _identify_future_opportunities(self, skill_forecasts: List[Dict[str, Any]],
                                           scenario_analysis: List[Dict[str, Any]]) -> List[str]:
        """識別未來機會"""
        opportunities = []
        
        # 基於技能預測的機會
        high_growth_skills = [
            forecast for forecast in skill_forecasts 
            if forecast.get('growth_rate', 0) > 0.3
        ]
        
        if high_growth_skills:
            opportunities.append(f'{len(high_growth_skills)} skills with high growth potential identified')
        
        # 基於低替代風險技能的機會
        secure_skills = [
            forecast for forecast in skill_forecasts 
            if forecast.get('replacement_risk', 0.5) < 0.3
        ]
        
        if secure_skills:
            opportunities.append(f'{len(secure_skills)} skills with low automation risk provide stable investment')
        
        # 基於情境分析的機會
        positive_scenarios = [
            scenario for scenario in scenario_analysis 
            if 'opportunity' in str(scenario.get('implications', {})).lower()
        ]
        
        if positive_scenarios:
            opportunities.append(f'{len(positive_scenarios)} scenarios present strategic opportunities')
        
        # 通用未來機會
        opportunities.extend([
            'Early adoption advantage in emerging technologies',
            'Talent development differentiation in competitive market',
            'Organizational agility as competitive advantage'
        ])
        
        return opportunities[:6]  # 限制機會數量