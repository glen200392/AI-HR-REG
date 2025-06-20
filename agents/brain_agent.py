"""
Brain Agent - 學習與認知分析師
基於神經科學原理優化人才發展
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import json
import logging
from .base_agent import BaseAgent
from langchain.schema import SystemMessage


@dataclass
class CognitiveProfile:
    """認知檔案"""
    learning_style: str  # visual, auditory, kinesthetic, mixed
    cognitive_load_capacity: float  # 0.1 - 1.0
    attention_span: int  # minutes
    memory_retention_rate: float  # 0.1 - 1.0
    processing_speed: str  # slow, medium, fast
    preferred_complexity: str  # simple, moderate, complex
    stress_threshold: float  # 0.1 - 1.0
    neuroplasticity_score: float  # 0.1 - 1.0


@dataclass
class LearningPathway:
    """個人化學習路徑"""
    pathway_id: str
    target_skills: List[str]
    learning_modules: List[Dict[str, Any]]
    estimated_duration: int  # weeks
    difficulty_progression: List[float]
    cognitive_load_distribution: List[float]
    milestone_checkpoints: List[Dict[str, Any]]
    adaptation_triggers: List[str]


@dataclass
class SkillDevelopmentPrediction:
    """技能發展預測"""
    skill_name: str
    current_proficiency: float  # 0.0 - 1.0
    predicted_proficiency: float  # 0.0 - 1.0
    learning_velocity: float  # per week
    plateau_probability: float  # 0.0 - 1.0
    breakthrough_probability: float  # 0.0 - 1.0
    optimal_intervention_time: datetime
    confidence_interval: Tuple[float, float]


class CognitiveLoadTracker:
    """認知負荷追蹤器"""
    
    def __init__(self):
        self.load_history = []
        self.optimal_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'overload': 0.9
        }
    
    def calculate_current_load(self, task_complexity: List[float], time_pressure: float, 
                              mental_resources: float) -> float:
        """計算當前認知負荷"""
        avg_complexity = np.mean(task_complexity) if task_complexity else 0.5
        
        # 認知負荷公式：基於多重任務理論
        cognitive_load = (avg_complexity * 0.4 + 
                         time_pressure * 0.3 + 
                         (1 - mental_resources) * 0.3)
        
        return min(cognitive_load, 1.0)
    
    def predict_load_trend(self, current_load: float, planned_activities: List[Dict]) -> List[float]:
        """預測認知負荷趨勢"""
        trend = [current_load]
        
        for activity in planned_activities:
            complexity = activity.get('complexity', 0.5)
            duration = activity.get('duration_hours', 1)
            
            # 考慮學習疲勞效應
            fatigue_factor = min(1.0, len(trend) * 0.05)
            next_load = current_load + (complexity * 0.3) - (fatigue_factor * 0.1)
            trend.append(max(0.1, min(next_load, 1.0)))
            current_load = trend[-1]
        
        return trend
    
    def recommend_load_management(self, predicted_loads: List[float]) -> List[str]:
        """建議認知負荷管理策略"""
        recommendations = []
        
        overload_periods = [i for i, load in enumerate(predicted_loads) if load > self.optimal_thresholds['overload']]
        
        if overload_periods:
            recommendations.append("Schedule breaks during high cognitive load periods")
            recommendations.append("Consider task complexity reduction or time extension")
        
        if max(predicted_loads) > self.optimal_thresholds['high']:
            recommendations.append("Implement progressive skill building approach")
            recommendations.append("Use cognitive aids and structured templates")
        
        return recommendations


class NeuroplasticityPredictor:
    """神經可塑性預測器"""
    
    def __init__(self):
        self.baseline_factors = {
            'age': {'18-25': 1.0, '26-35': 0.9, '36-45': 0.8, '46-55': 0.7, '55+': 0.6},
            'prior_learning': {'none': 0.7, 'some': 0.85, 'extensive': 1.0},
            'motivation': {'low': 0.6, 'medium': 0.8, 'high': 1.0},
            'stress_level': {'low': 1.0, 'medium': 0.8, 'high': 0.6}
        }
    
    def calculate_neuroplasticity_score(self, individual_data: Dict[str, Any]) -> float:
        """計算神經可塑性評分"""
        age_group = self._determine_age_group(individual_data.get('age', 30))
        prior_learning = individual_data.get('prior_learning_experience', 'some')
        motivation = individual_data.get('motivation_level', 'medium')
        stress = individual_data.get('stress_level', 'medium')
        
        score = (self.baseline_factors['age'].get(age_group, 0.8) * 0.3 +
                self.baseline_factors['prior_learning'].get(prior_learning, 0.85) * 0.25 +
                self.baseline_factors['motivation'].get(motivation, 0.8) * 0.3 +
                self.baseline_factors['stress_level'].get(stress, 0.8) * 0.15)
        
        return min(score, 1.0)
    
    def predict_learning_capacity(self, neuroplasticity_score: float, 
                                 skill_complexity: str) -> Dict[str, Any]:
        """預測學習能力"""
        complexity_multipliers = {'simple': 1.2, 'moderate': 1.0, 'complex': 0.8}
        multiplier = complexity_multipliers.get(skill_complexity, 1.0)
        
        adjusted_capacity = neuroplasticity_score * multiplier
        
        return {
            'learning_velocity': adjusted_capacity * 0.8,
            'retention_probability': adjusted_capacity * 0.9,
            'transfer_ability': adjusted_capacity * 0.7,
            'adaptation_speed': adjusted_capacity * 0.85
        }
    
    def _determine_age_group(self, age: int) -> str:
        """確定年齡組"""
        if age <= 25:
            return '18-25'
        elif age <= 35:
            return '26-35'
        elif age <= 45:
            return '36-45'
        elif age <= 55:
            return '46-55'
        else:
            return '55+'


class PersonalizedLearningPathway:
    """個人化學習路徑設計器"""
    
    def __init__(self):
        self.learning_architectures = {
            'visual': {'video': 0.4, 'diagrams': 0.3, 'reading': 0.2, 'practice': 0.1},
            'auditory': {'lectures': 0.4, 'discussions': 0.3, 'audio': 0.2, 'practice': 0.1},
            'kinesthetic': {'practice': 0.5, 'simulation': 0.3, 'case_study': 0.2},
            'mixed': {'video': 0.2, 'practice': 0.3, 'reading': 0.2, 'discussions': 0.3}
        }
    
    def design_pathway(self, cognitive_profile: CognitiveProfile, 
                      target_skills: List[str], business_priority: str) -> LearningPathway:
        """設計個人化學習路徑"""
        
        # Step 1: 分析技能複雜度
        skill_complexities = self._analyze_skill_complexity(target_skills)
        
        # Step 2: 設計學習模組
        learning_modules = self._design_learning_modules(
            cognitive_profile, skill_complexities
        )
        
        # Step 3: 計算認知負荷分佈
        cognitive_loads = self._calculate_load_distribution(
            learning_modules, cognitive_profile
        )
        
        # Step 4: 設定里程碑
        milestones = self._set_milestones(learning_modules, business_priority)
        
        # Step 5: 定義適應觸發器
        adaptation_triggers = self._define_adaptation_triggers(cognitive_profile)
        
        return LearningPathway(
            pathway_id=f"pathway_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            target_skills=target_skills,
            learning_modules=learning_modules,
            estimated_duration=self._calculate_duration(learning_modules),
            difficulty_progression=[m.get('difficulty', 0.5) for m in learning_modules],
            cognitive_load_distribution=cognitive_loads,
            milestone_checkpoints=milestones,
            adaptation_triggers=adaptation_triggers
        )
    
    def _analyze_skill_complexity(self, skills: List[str]) -> Dict[str, float]:
        """分析技能複雜度"""
        complexity_keywords = {
            'leadership': 0.8, 'management': 0.7, 'strategy': 0.8,
            'communication': 0.5, 'technical': 0.6, 'analytical': 0.7,
            'creative': 0.6, 'problem_solving': 0.7, 'collaboration': 0.5
        }
        
        complexities = {}
        for skill in skills:
            skill_lower = skill.lower()
            complexity = 0.5  # default
            
            for keyword, value in complexity_keywords.items():
                if keyword in skill_lower:
                    complexity = max(complexity, value)
            
            complexities[skill] = complexity
        
        return complexities
    
    def _design_learning_modules(self, profile: CognitiveProfile, 
                               skill_complexities: Dict[str, float]) -> List[Dict[str, Any]]:
        """設計學習模組"""
        modules = []
        learning_style_distribution = self.learning_architectures.get(
            profile.learning_style, self.learning_architectures['mixed']
        )
        
        for skill, complexity in skill_complexities.items():
            # 根據認知檔案調整模組設計
            module = {
                'skill': skill,
                'difficulty': complexity,
                'estimated_hours': int(complexity * 20 * (1/profile.neuroplasticity_score)),
                'learning_methods': self._select_methods(learning_style_distribution, complexity),
                'cognitive_load_target': min(complexity * 0.8, profile.cognitive_load_capacity),
                'adaptation_points': self._identify_adaptation_points(complexity)
            }
            modules.append(module)
        
        return modules
    
    def _select_methods(self, distribution: Dict[str, float], complexity: float) -> List[str]:
        """選擇學習方法"""
        methods = []
        
        # 根據複雜度調整方法選擇
        if complexity > 0.7:
            methods.extend(['case_study', 'mentoring', 'practice'])
        elif complexity > 0.4:
            methods.extend(['workshop', 'simulation', 'peer_learning'])
        else:
            methods.extend(['e_learning', 'reading', 'video'])
        
        # 根據學習風格偏好添加方法
        for method, weight in distribution.items():
            if weight > 0.2:
                methods.append(method)
        
        return list(set(methods))[:4]  # 限制方法數量
    
    def _calculate_load_distribution(self, modules: List[Dict[str, Any]], 
                                   profile: CognitiveProfile) -> List[float]:
        """計算認知負荷分佈"""
        loads = []
        cumulative_fatigue = 0.0
        
        for module in modules:
            base_load = module['difficulty'] * 0.8
            fatigue_effect = min(cumulative_fatigue * 0.1, 0.3)
            adjusted_load = min(base_load + fatigue_effect, profile.cognitive_load_capacity)
            
            loads.append(adjusted_load)
            cumulative_fatigue += adjusted_load
        
        return loads
    
    def _set_milestones(self, modules: List[Dict[str, Any]], 
                       business_priority: str) -> List[Dict[str, Any]]:
        """設定學習里程碑"""
        milestones = []
        cumulative_hours = 0
        
        priority_multiplier = {'high': 0.8, 'medium': 1.0, 'low': 1.2}.get(business_priority, 1.0)
        
        for i, module in enumerate(modules):
            cumulative_hours += module['estimated_hours']
            
            if (i + 1) % 2 == 0 or i == len(modules) - 1:  # 每兩個模組一個里程碑
                milestone = {
                    'milestone_id': f"milestone_{i+1}",
                    'target_week': int(cumulative_hours / 10 * priority_multiplier),
                    'skills_covered': [m['skill'] for m in modules[:i+1]],
                    'assessment_type': 'practical' if sum(m['difficulty'] for m in modules[:i+1]) > 1.0 else 'theoretical',
                    'success_criteria': f"Demonstrate proficiency in {module['skill']}"
                }
                milestones.append(milestone)
        
        return milestones
    
    def _calculate_duration(self, modules: List[Dict[str, Any]]) -> int:
        """計算總學習時長（週）"""
        total_hours = sum(module['estimated_hours'] for module in modules)
        return max(int(total_hours / 8), 4)  # 假設每週8小時學習時間，最少4週
    
    def _identify_adaptation_points(self, complexity: float) -> List[str]:
        """識別適應點"""
        points = ['progress_slower_than_expected', 'cognitive_overload_detected']
        
        if complexity > 0.7:
            points.extend(['skill_transfer_difficulty', 'practical_application_challenges'])
        
        return points
    
    def _define_adaptation_triggers(self, profile: CognitiveProfile) -> List[str]:
        """定義適應觸發器"""
        triggers = [
            'learning_velocity_below_threshold',
            'retention_rate_declining',
            'cognitive_load_exceeding_capacity'
        ]
        
        if profile.stress_threshold < 0.6:
            triggers.append('stress_level_elevated')
        
        if profile.attention_span < 30:
            triggers.append('attention_span_exceeded')
        
        return triggers


class BrainAgent(BaseAgent):
    """Brain Agent - 學習與認知分析師"""
    
    def __init__(self):
        super().__init__(temperature=0.4)  # 較低溫度以確保一致性
        self.cognitive_tracker = CognitiveLoadTracker()
        self.neuroplasticity_engine = NeuroplasticityPredictor()
        self.learning_optimizer = PersonalizedLearningPathway()
        self.logger = logging.getLogger(__name__)
    
    def _get_system_message(self) -> SystemMessage:
        return SystemMessage(content="""你是一位基於神經科學原理的學習與認知分析師。你的專業職責包括：

1. 認知能力評估：分析個人學習模式、認知負荷承受能力和注意力特徵
2. 神經可塑性評估：基於年齡、經驗、動機等因素預測學習潛力
3. 個人化學習路徑設計：根據認知檔案設計最適合的學習進程
4. 技能發展預測：預測學習成果和可能遇到的障礙
5. 認知負荷優化：確保學習過程在最適認知負荷區間

你的分析必須基於認知科學理論，包括：
- 認知負荷理論 (Cognitive Load Theory)
- 神經可塑性原理 (Neuroplasticity Principles)  
- 多元智能理論 (Multiple Intelligence Theory)
- 間隔重複學習 (Spaced Repetition)
- 刻意練習理論 (Deliberate Practice)

請提供具體、可操作的建議，並說明科學依據。""")
    
    async def analyze_context(self, context) -> Dict[str, Any]:
        """分析學習和認知上下文"""
        try:
            employee_data = context.employee_data
            analysis_results = {
                'recommendations': [],
                'risks': [],
                'opportunities': [],
                'confidence': 0.0,
                'data_quality': 0.0
            }
            
            # Step 1: 構建認知檔案
            cognitive_profile = await self._build_cognitive_profile(employee_data)
            
            # Step 2: 分析當前認知負荷狀態
            cognitive_load_analysis = await self._analyze_cognitive_load(employee_data, cognitive_profile)
            
            # Step 3: 預測學習能力和發展潛力
            learning_predictions = await self._predict_learning_outcomes(employee_data, cognitive_profile)
            
            # Step 4: 設計個人化學習建議
            learning_recommendations = await self._generate_learning_recommendations(
                cognitive_profile, learning_predictions, context.priority_goals
            )
            
            # Step 5: 識別認知風險和機會
            cognitive_risks = await self._identify_cognitive_risks(cognitive_profile, cognitive_load_analysis)
            cognitive_opportunities = await self._identify_learning_opportunities(learning_predictions)
            
            analysis_results.update({
                'recommendations': learning_recommendations,
                'risks': cognitive_risks,
                'opportunities': cognitive_opportunities,
                'confidence': self._calculate_analysis_confidence(employee_data),
                'data_quality': self._assess_data_quality(employee_data),
                'cognitive_profile': cognitive_profile.__dict__,
                'learning_predictions': learning_predictions
            })
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Brain Agent analysis failed: {str(e)}")
            return {
                'recommendations': [],
                'risks': ['Cognitive analysis system error'],
                'opportunities': [],
                'confidence': 0.3,
                'data_quality': 0.3
            }
    
    async def _build_cognitive_profile(self, employee_data: Dict[str, Any]) -> CognitiveProfile:
        """構建個人認知檔案"""
        
        # 從數據中提取或推斷認知特徵
        learning_style = employee_data.get('learning_style', 'mixed')
        age = employee_data.get('age', 30)
        experience_years = employee_data.get('experience_years', 5)
        stress_indicators = employee_data.get('stress_indicators', {})
        
        # 計算神經可塑性評分
        neuroplasticity_score = self.neuroplasticity_engine.calculate_neuroplasticity_score(employee_data)
        
        # 推斷認知負荷容量（基於經驗和壓力水平）
        base_capacity = 0.7 + (min(experience_years, 10) * 0.02)
        stress_adjustment = -stress_indicators.get('overall_stress', 0.3) * 0.2
        cognitive_load_capacity = max(0.3, base_capacity + stress_adjustment)
        
        # 推斷注意力持續時間
        attention_span = max(15, 45 - age * 0.5 + experience_years * 2)
        
        return CognitiveProfile(
            learning_style=learning_style,
            cognitive_load_capacity=cognitive_load_capacity,
            attention_span=int(attention_span),
            memory_retention_rate=neuroplasticity_score * 0.9,
            processing_speed=self._infer_processing_speed(employee_data),
            preferred_complexity=self._infer_complexity_preference(employee_data),
            stress_threshold=1.0 - stress_indicators.get('overall_stress', 0.3),
            neuroplasticity_score=neuroplasticity_score
        )
    
    async def _analyze_cognitive_load(self, employee_data: Dict[str, Any], 
                                    profile: CognitiveProfile) -> Dict[str, Any]:
        """分析當前認知負荷狀態"""
        
        current_tasks = employee_data.get('current_tasks', [])
        work_pressure = employee_data.get('work_pressure', 0.5)
        mental_fatigue = employee_data.get('mental_fatigue', 0.3)
        
        task_complexities = [task.get('complexity', 0.5) for task in current_tasks]
        
        current_load = self.cognitive_tracker.calculate_current_load(
            task_complexities, work_pressure, 1.0 - mental_fatigue
        )
        
        # 預測未來負荷趨勢
        planned_activities = employee_data.get('planned_learning_activities', [])
        load_trend = self.cognitive_tracker.predict_load_trend(current_load, planned_activities)
        
        # 生成負荷管理建議
        load_management_tips = self.cognitive_tracker.recommend_load_management(load_trend)
        
        return {
            'current_cognitive_load': current_load,
            'load_trend_prediction': load_trend,
            'load_status': self._categorize_load_level(current_load),
            'management_recommendations': load_management_tips,
            'optimal_learning_windows': self._identify_optimal_learning_times(load_trend)
        }
    
    async def _predict_learning_outcomes(self, employee_data: Dict[str, Any], 
                                       profile: CognitiveProfile) -> Dict[str, Any]:
        """預測學習成果"""
        
        target_skills = employee_data.get('target_skills', [])
        predictions = {}
        
        for skill in target_skills:
            current_level = employee_data.get('skill_levels', {}).get(skill, 0.3)
            
            # 基於神經可塑性預測學習能力
            learning_capacity = self.neuroplasticity_engine.predict_learning_capacity(
                profile.neuroplasticity_score, 
                self._categorize_skill_complexity(skill)
            )
            
            # 計算學習速度和預期成果
            learning_velocity = learning_capacity['learning_velocity'] * profile.cognitive_load_capacity
            predicted_improvement = learning_velocity * 12  # 12週預測
            
            prediction = SkillDevelopmentPrediction(
                skill_name=skill,
                current_proficiency=current_level,
                predicted_proficiency=min(current_level + predicted_improvement, 1.0),
                learning_velocity=learning_velocity,
                plateau_probability=max(0.0, current_level - 0.3) * 0.5,
                breakthrough_probability=learning_capacity['adaptation_speed'],
                optimal_intervention_time=datetime.now() + timedelta(weeks=2),
                confidence_interval=(
                    max(0.0, predicted_improvement * 0.7),
                    min(1.0, predicted_improvement * 1.3)
                )
            )
            
            predictions[skill] = prediction.__dict__
        
        return predictions
    
    async def _generate_learning_recommendations(self, profile: CognitiveProfile, 
                                               predictions: Dict[str, Any], 
                                               priority_goals: List[str]) -> List[Dict[str, Any]]:
        """生成學習建議"""
        recommendations = []
        
        # 基於認知檔案的通用建議
        recommendations.extend(self._generate_cognitive_optimization_recommendations(profile))
        
        # 基於學習預測的特定建議
        for skill, prediction in predictions.items():
            if prediction['plateau_probability'] > 0.6:
                recommendations.append({
                    'id': f'plateau_prevention_{skill}',
                    'title': f'Prevent Learning Plateau in {skill}',
                    'description': f'Implement advanced learning techniques to overcome potential plateau in {skill}',
                    'scope': 'individual',
                    'type': 'learning_optimization',
                    'urgency': 'medium',
                    'weight': 0.8,
                    'implementation_methods': ['varied_practice', 'challenge_progression', 'peer_teaching']
                })
            
            if prediction['breakthrough_probability'] > 0.7:
                recommendations.append({
                    'id': f'accelerated_learning_{skill}',
                    'title': f'Accelerated Learning Program for {skill}',
                    'description': f'High potential for breakthrough in {skill} - implement intensive development program',
                    'scope': 'individual', 
                    'type': 'skill_acceleration',
                    'urgency': 'high',
                    'weight': 0.9,
                    'implementation_methods': ['intensive_practice', 'expert_mentoring', 'real_project_application']
                })
        
        # 設計個人化學習路徑
        if predictions:
            target_skills = list(predictions.keys())
            business_priority = 'high' if any(goal in str(priority_goals) for goal in ['performance', 'skill']) else 'medium'
            
            learning_pathway = self.learning_optimizer.design_pathway(
                profile, target_skills, business_priority
            )
            
            recommendations.append({
                'id': 'personalized_learning_pathway',
                'title': 'Personalized Learning Pathway',
                'description': f'Customized {learning_pathway.estimated_duration}-week learning program',
                'scope': 'individual',
                'type': 'learning_pathway',
                'urgency': 'high',
                'weight': 1.0,
                'pathway_details': learning_pathway.__dict__
            })
        
        return recommendations[:8]  # 限制建議數量
    
    def _generate_cognitive_optimization_recommendations(self, profile: CognitiveProfile) -> List[Dict[str, Any]]:
        """生成認知優化建議"""
        recommendations = []
        
        # 基於認知負荷容量的建議
        if profile.cognitive_load_capacity < 0.5:
            recommendations.append({
                'id': 'cognitive_load_management',
                'title': 'Cognitive Load Management Training',
                'description': 'Implement strategies to optimize cognitive resource allocation',
                'scope': 'individual',
                'type': 'cognitive_optimization',
                'urgency': 'high',
                'weight': 0.9
            })
        
        # 基於注意力持續時間的建議
        if profile.attention_span < 25:
            recommendations.append({
                'id': 'attention_enhancement',
                'title': 'Attention Span Enhancement Program',
                'description': 'Implement focused attention training techniques',
                'scope': 'individual',
                'type': 'attention_training',
                'urgency': 'medium',
                'weight': 0.7
            })
        
        # 基於神經可塑性評分的建議
        if profile.neuroplasticity_score > 0.8:
            recommendations.append({
                'id': 'advanced_skill_development',
                'title': 'Advanced Skill Development Opportunity',
                'description': 'High neuroplasticity detected - suitable for complex skill acquisition',
                'scope': 'individual',
                'type': 'advanced_learning',
                'urgency': 'medium',
                'weight': 0.8
            })
        
        return recommendations
    
    def _identify_cognitive_risks(self, profile: CognitiveProfile, 
                                load_analysis: Dict[str, Any]) -> List[str]:
        """識別認知風險"""
        risks = []
        
        if load_analysis['current_cognitive_load'] > 0.8:
            risks.append('High cognitive overload risk - may impair learning effectiveness')
        
        if profile.stress_threshold < 0.4:
            risks.append('Low stress tolerance - vulnerable to performance degradation under pressure')
        
        if profile.memory_retention_rate < 0.6:
            risks.append('Below-average retention rate - may require enhanced reinforcement strategies')
        
        if profile.neuroplasticity_score < 0.5:
            risks.append('Limited neuroplasticity - may require extended learning timeframes')
        
        return risks
    
    def _identify_learning_opportunities(self, predictions: Dict[str, Any]) -> List[str]:
        """識別學習機會"""
        opportunities = []
        
        high_potential_skills = [
            skill for skill, pred in predictions.items() 
            if pred['breakthrough_probability'] > 0.7
        ]
        
        if high_potential_skills:
            opportunities.append(f'High learning potential in: {", ".join(high_potential_skills)}')
        
        rapid_learning_skills = [
            skill for skill, pred in predictions.items()
            if pred['learning_velocity'] > 0.1
        ]
        
        if rapid_learning_skills:
            opportunities.append(f'Rapid skill acquisition possible in: {", ".join(rapid_learning_skills)}')
        
        return opportunities
    
    def _infer_processing_speed(self, employee_data: Dict[str, Any]) -> str:
        """推斷處理速度"""
        task_completion_rates = employee_data.get('task_completion_rates', {})
        avg_rate = np.mean(list(task_completion_rates.values())) if task_completion_rates else 0.7
        
        if avg_rate > 0.8:
            return 'fast'
        elif avg_rate > 0.6:
            return 'medium'
        else:
            return 'slow'
    
    def _infer_complexity_preference(self, employee_data: Dict[str, Any]) -> str:
        """推斷複雜度偏好"""
        role_level = employee_data.get('role_level', 'mid')
        experience = employee_data.get('experience_years', 5)
        
        if role_level == 'senior' or experience > 8:
            return 'complex'
        elif role_level == 'mid' or experience > 3:
            return 'moderate'
        else:
            return 'simple'
    
    def _categorize_load_level(self, load: float) -> str:
        """分類負荷水平"""
        if load > 0.8:
            return 'overload'
        elif load > 0.6:
            return 'high'
        elif load > 0.3:
            return 'optimal'
        else:
            return 'low'
    
    def _categorize_skill_complexity(self, skill: str) -> str:
        """分類技能複雜度"""
        complex_keywords = ['leadership', 'strategy', 'innovation', 'complex', 'advanced']
        simple_keywords = ['basic', 'fundamental', 'introduction', 'simple']
        
        skill_lower = skill.lower()
        
        if any(keyword in skill_lower for keyword in complex_keywords):
            return 'complex'
        elif any(keyword in skill_lower for keyword in simple_keywords):
            return 'simple'
        else:
            return 'moderate'
    
    def _identify_optimal_learning_times(self, load_trend: List[float]) -> List[str]:
        """識別最佳學習時機"""
        optimal_windows = []
        
        for i, load in enumerate(load_trend):
            if 0.3 <= load <= 0.6:  # 最佳認知負荷區間
                optimal_windows.append(f'Window {i+1}: Optimal learning conditions')
        
        return optimal_windows[:3]  # 返回前3個最佳時機
    
    def _calculate_analysis_confidence(self, employee_data: Dict[str, Any]) -> float:
        """計算分析信心度"""
        data_completeness = len(employee_data) / 15  # 假設理想數據有15個字段
        return min(data_completeness, 1.0)
    
    def _assess_data_quality(self, employee_data: Dict[str, Any]) -> float:
        """評估數據質量"""
        key_fields = ['age', 'experience_years', 'current_tasks', 'skill_levels']
        available_fields = sum(1 for field in key_fields if field in employee_data)
        return available_fields / len(key_fields)