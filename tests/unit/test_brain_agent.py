"""
Unit Tests for Brain Agent
Brain Agent 單元測試
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agents.brain_agent import (
    BrainAgent, CognitiveProfile, LearningPathway, 
    CognitiveLoadTracker, NeuroplasticityPredictor, PersonalizedLearningPathway
)


@pytest.mark.unit
@pytest.mark.agent
class TestBrainAgent:
    """Brain Agent測試類"""
    
    @pytest.fixture
    def brain_agent(self, mock_llm_client, mock_vector_store, mock_cache_store):
        """創建測試用的Brain Agent"""
        agent = BrainAgent()
        agent.llm_client = mock_llm_client
        agent.vector_store = mock_vector_store
        agent.cache = mock_cache_store
        return agent
    
    @pytest.mark.asyncio
    async def test_analyze_cognitive_state_success(self, brain_agent, sample_employee_data):
        """測試認知狀態分析成功情況"""
        # 模擬認知負載追踪器
        mock_tracker = Mock(spec=CognitiveLoadTracker)
        mock_tracker.calculate_current_load = Mock(return_value=0.7)
        mock_tracker.analyze_load_factors = Mock(return_value={
            'task_complexity': 0.8,
            'time_pressure': 0.6,
            'information_overload': 0.7
        })
        
        brain_agent.cognitive_tracker = mock_tracker
        
        # 模擬學習能力預測
        with patch.object(brain_agent, '_predict_learning_capacity', return_value=0.85):
            with patch.object(brain_agent, '_analyze_cognitive_patterns', return_value={
                'focus_periods': [9, 14, 16],  # 最佳專注時間
                'learning_style': 'visual',
                'retention_rate': 0.8
            }):
                
                result = await brain_agent.analyze_cognitive_state(sample_employee_data)
                
                # 驗證結果結構
                assert 'cognitive_load' in result
                assert 'learning_capacity' in result
                assert 'cognitive_patterns' in result
                assert 'recommendations' in result
                
                # 驗證數值範圍
                assert 0 <= result['cognitive_load'] <= 1
                assert 0 <= result['learning_capacity'] <= 1
    
    @pytest.mark.asyncio
    async def test_generate_learning_pathway(self, brain_agent, sample_employee_data):
        """測試學習路徑生成"""
        # 準備認知檔案
        cognitive_profile = CognitiveProfile(
            employee_id=sample_employee_data['id'],
            learning_style='visual',
            cognitive_load=0.7,
            focus_periods=[9, 14, 16],
            retention_rate=0.8,
            preferred_pace='moderate'
        )
        
        target_skills = ['Machine Learning', 'Deep Learning', 'Data Science']
        
        # 模擬個人化學習路徑生成器
        mock_pathway_generator = Mock(spec=PersonalizedLearningPathway)
        mock_pathway_generator.design_pathway = Mock(return_value=LearningPathway(
            pathway_id='pathway_001',
            employee_id=sample_employee_data['id'],
            target_skills=target_skills,
            milestones=[
                {'skill': 'Machine Learning', 'timeline': '2 months', 'difficulty': 'intermediate'},
                {'skill': 'Deep Learning', 'timeline': '3 months', 'difficulty': 'advanced'}
            ],
            estimated_duration_weeks=12,
            success_probability=0.85
        ))
        
        brain_agent.pathway_generator = mock_pathway_generator
        
        # 執行學習路徑生成
        result = await brain_agent.generate_learning_pathway(cognitive_profile, target_skills)
        
        # 驗證結果
        assert isinstance(result, LearningPathway)
        assert result.employee_id == sample_employee_data['id']
        assert len(result.target_skills) == 3
        assert len(result.milestones) > 0
        assert result.success_probability > 0
    
    def test_cognitive_load_tracker(self):
        """測試認知負載追踪器"""
        tracker = CognitiveLoadTracker()
        
        # 測試當前負載計算
        work_context = {
            'active_projects': 3,
            'meeting_hours_per_day': 4,
            'deadline_pressure': 0.8,
            'task_complexity_avg': 0.7,
            'interruption_frequency': 15  # 每小時中斷次數
        }
        
        current_load = tracker.calculate_current_load(work_context)
        
        # 驗證負載值
        assert 0 <= current_load <= 1
        assert isinstance(current_load, float)
        
        # 測試負載因子分析
        load_factors = tracker.analyze_load_factors(work_context)
        
        assert 'task_complexity' in load_factors
        assert 'time_pressure' in load_factors
        assert 'information_overload' in load_factors
        assert 'interruption_impact' in load_factors
    
    def test_neuroplasticity_predictor(self, sample_employee_data):
        """測試神經可塑性預測器"""
        predictor = NeuroplasticityPredictor()
        
        # 準備預測因子
        factors = {
            'age': 30,
            'experience_years': sample_employee_data['experience_years'],
            'recent_learning_activity': 0.8,
            'cognitive_flexibility': 0.7,
            'stress_level': 0.4,
            'sleep_quality': 0.8
        }
        
        # 預測學習能力
        learning_capacity = predictor.predict_learning_capacity(factors)
        
        # 驗證預測結果
        assert 0 <= learning_capacity <= 1
        assert isinstance(learning_capacity, float)
        
        # 測試年齡對學習能力的影響
        young_factors = factors.copy()
        young_factors['age'] = 25
        young_capacity = predictor.predict_learning_capacity(young_factors)
        
        older_factors = factors.copy()
        older_factors['age'] = 50
        older_capacity = predictor.predict_learning_capacity(older_factors)
        
        # 年輕人通常有更高的學習能力（在其他條件相同的情況下）
        assert young_capacity >= older_capacity
    
    def test_personalized_learning_pathway(self, sample_employee_data):
        """測試個人化學習路徑"""
        pathway_generator = PersonalizedLearningPathway()
        
        # 準備認知檔案
        cognitive_profile = CognitiveProfile(
            employee_id=sample_employee_data['id'],
            learning_style='kinesthetic',
            cognitive_load=0.6,
            focus_periods=[9, 14],
            retention_rate=0.75,
            preferred_pace='fast'
        )
        
        target_skills = ['Python', 'Machine Learning']
        
        # 設計學習路徑
        pathway = pathway_generator.design_pathway(cognitive_profile, target_skills)
        
        # 驗證路徑設計
        assert isinstance(pathway, LearningPathway)
        assert pathway.employee_id == sample_employee_data['id']
        assert set(pathway.target_skills) == set(target_skills)
        assert len(pathway.milestones) > 0
        
        # 驗證里程碑順序和依賴關係
        milestones = pathway.milestones
        for i, milestone in enumerate(milestones):
            assert 'skill' in milestone
            assert 'timeline' in milestone
            assert 'difficulty' in milestone
            
            # 檢查難度遞進
            if i > 0:
                current_difficulty = milestone['difficulty']
                previous_difficulty = milestones[i-1]['difficulty']
                
                difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert']
                current_idx = difficulty_levels.index(current_difficulty)
                previous_idx = difficulty_levels.index(previous_difficulty)
                
                # 難度不應該大幅度跳躍
                assert current_idx - previous_idx <= 2
    
    @pytest.mark.asyncio
    async def test_cognitive_pattern_analysis(self, brain_agent, sample_employee_data):
        """測試認知模式分析"""
        # 準備歷史數據
        historical_data = {
            'work_sessions': [
                {'start_time': 9, 'duration': 2, 'productivity': 0.9},
                {'start_time': 14, 'duration': 1.5, 'productivity': 0.8},
                {'start_time': 16, 'duration': 1, 'productivity': 0.6}
            ],
            'learning_sessions': [
                {'topic': 'Python', 'success_rate': 0.85, 'time_of_day': 10},
                {'topic': 'Machine Learning', 'success_rate': 0.7, 'time_of_day': 15}
            ],
            'stress_indicators': [0.3, 0.4, 0.6, 0.5, 0.2]  # 過去5天
        }
        
        patterns = await brain_agent._analyze_cognitive_patterns(sample_employee_data, historical_data)
        
        # 驗證模式分析結果
        assert 'focus_periods' in patterns
        assert 'learning_style' in patterns
        assert 'productivity_patterns' in patterns
        assert 'stress_patterns' in patterns
        
        # 驗證最佳專注時間段
        focus_periods = patterns['focus_periods']
        assert isinstance(focus_periods, list)
        assert all(0 <= period <= 23 for period in focus_periods)  # 24小時制
    
    @pytest.mark.asyncio
    async def test_learning_recommendation_engine(self, brain_agent, sample_employee_data):
        """測試學習推薦引擎"""
        cognitive_state = {
            'cognitive_load': 0.7,
            'learning_capacity': 0.8,
            'focus_periods': [9, 14, 16],
            'learning_style': 'visual',
            'current_skills': sample_employee_data['skills']
        }
        
        recommendations = await brain_agent._generate_learning_recommendations(
            sample_employee_data, cognitive_state
        )
        
        # 驗證推薦結果
        assert 'immediate_actions' in recommendations
        assert 'skill_development' in recommendations
        assert 'learning_schedule' in recommendations
        assert 'resource_suggestions' in recommendations
        
        # 驗證即時行動建議
        immediate_actions = recommendations['immediate_actions']
        assert isinstance(immediate_actions, list)
        assert len(immediate_actions) > 0
        
        for action in immediate_actions:
            assert 'action' in action
            assert 'reason' in action
            assert 'priority' in action
    
    def test_cognitive_profile_validation(self):
        """測試認知檔案驗證"""
        # 測試有效的認知檔案
        valid_profile = CognitiveProfile(
            employee_id='emp_001',
            learning_style='visual',
            cognitive_load=0.7,
            focus_periods=[9, 14, 16],
            retention_rate=0.8,
            preferred_pace='moderate'
        )
        
        assert valid_profile.employee_id == 'emp_001'
        assert valid_profile.learning_style == 'visual'
        assert 0 <= valid_profile.cognitive_load <= 1
        
        # 測試無效的認知負載值
        with pytest.raises(ValueError):
            CognitiveProfile(
                employee_id='emp_001',
                learning_style='visual',
                cognitive_load=1.5,  # 超出範圍
                focus_periods=[9, 14, 16],
                retention_rate=0.8,
                preferred_pace='moderate'
            )
        
        # 測試無效的專注時間
        with pytest.raises(ValueError):
            CognitiveProfile(
                employee_id='emp_001',
                learning_style='visual',
                cognitive_load=0.7,
                focus_periods=[25],  # 超出24小時制
                retention_rate=0.8,
                preferred_pace='moderate'
            )
    
    @pytest.mark.asyncio
    async def test_error_handling(self, brain_agent, sample_employee_data):
        """測試錯誤處理"""
        # 測試空數據處理
        empty_data = {}
        
        with patch.object(brain_agent, '_handle_missing_data') as mock_handler:
            mock_handler.return_value = {'cognitive_load': 0.5, 'learning_capacity': 0.6}
            
            result = await brain_agent.analyze_cognitive_state(empty_data)
            
            mock_handler.assert_called_once()
            assert result is not None
        
        # 測試異常情況處理
        with patch.object(brain_agent.cognitive_tracker, 'calculate_current_load', side_effect=Exception("計算錯誤")):
            with pytest.raises(Exception):
                await brain_agent.analyze_cognitive_state(sample_employee_data)
    
    @pytest.mark.asyncio
    async def test_caching_integration(self, brain_agent, sample_employee_data):
        """測試緩存集成"""
        # 第一次分析 - 應該緩存結果
        with patch.object(brain_agent.cache, 'get_cached_analysis', return_value=None):
            with patch.object(brain_agent.cache, 'cache_analysis_result', return_value=True) as mock_cache:
                
                result = await brain_agent.analyze_cognitive_state(sample_employee_data)
                
                mock_cache.assert_called_once()
                assert result is not None
        
        # 第二次分析 - 應該使用緩存
        cached_result = {'cognitive_load': 0.7, 'learning_capacity': 0.8}
        with patch.object(brain_agent.cache, 'get_cached_analysis', return_value=cached_result):
            
            result = await brain_agent.analyze_cognitive_state(sample_employee_data)
            
            assert result == cached_result