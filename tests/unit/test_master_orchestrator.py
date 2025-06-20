"""
Unit Tests for Master Orchestrator
Master Orchestrator 單元測試
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agents.master_orchestrator import MasterOrchestrator, AnalysisContext, IntegratedStrategy


@pytest.mark.unit
@pytest.mark.agent
class TestMasterOrchestrator:
    """Master Orchestrator測試類"""
    
    @pytest.fixture
    def orchestrator(self, mock_llm_client, mock_vector_store, mock_graph_store, mock_cache_store):
        """創建測試用的Master Orchestrator"""
        orchestrator = MasterOrchestrator()
        orchestrator.llm_client = mock_llm_client
        orchestrator.vector_store = mock_vector_store
        orchestrator.graph_store = mock_graph_store
        orchestrator.cache = mock_cache_store
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_analyze_comprehensive_success(self, orchestrator, sample_analysis_context):
        """測試綜合分析成功情況"""
        # 準備測試數據
        context = AnalysisContext(**sample_analysis_context)
        
        # 模擬子代理分析結果
        mock_insights = {
            'brain_analysis': {'cognitive_load': 0.7, 'learning_capacity': 0.8},
            'talent_analysis': {'performance_prediction': 0.85, 'career_fit': 0.9},
            'culture_analysis': {'team_harmony': 0.8, 'conflict_risk': 0.2},
            'future_analysis': {'skill_trends': ['AI', 'Cloud'], 'market_demand': 0.9},
            'process_analysis': {'efficiency_score': 0.75, 'optimization_potential': 0.6}
        }
        
        # 模擬並行分析執行
        with patch.object(orchestrator, '_execute_parallel_analysis', return_value=mock_insights):
            with patch.object(orchestrator, '_check_emergency_conditions', return_value=None):
                with patch.object(orchestrator, '_synthesize_insights', return_value={
                    'integrated_score': 0.82,
                    'priority_actions': ['skill_development', 'team_collaboration']
                }):
                    with patch.object(orchestrator, '_generate_strategic_plan', return_value={
                        'short_term': ['training_program'],
                        'long_term': ['career_progression']
                    }):
                        
                        result = await orchestrator.analyze_comprehensive(context)
                        
                        # 驗證結果
                        assert isinstance(result, IntegratedStrategy)
                        assert result.integrated_score > 0
                        assert len(result.priority_actions) > 0
                        assert result.strategic_plan is not None
    
    @pytest.mark.asyncio
    async def test_execute_parallel_analysis(self, orchestrator, sample_analysis_context):
        """測試並行分析執行"""
        context = AnalysisContext(**sample_analysis_context)
        
        # 模擬各個代理的分析方法
        orchestrator.brain_agent = Mock()
        orchestrator.brain_agent.analyze_cognitive_state = AsyncMock(return_value={
            'cognitive_load': 0.7, 'learning_capacity': 0.8
        })
        
        orchestrator.talent_agent = Mock()
        orchestrator.talent_agent.analyze_talent_ecosystem = AsyncMock(return_value={
            'performance_prediction': 0.85, 'career_fit': 0.9
        })
        
        orchestrator.culture_agent = Mock()
        orchestrator.culture_agent.analyze_cultural_dynamics = AsyncMock(return_value={
            'team_harmony': 0.8, 'conflict_risk': 0.2
        })
        
        orchestrator.future_agent = Mock()
        orchestrator.future_agent.predict_future_trends = AsyncMock(return_value={
            'skill_trends': ['AI', 'Cloud'], 'market_demand': 0.9
        })
        
        orchestrator.process_agent = Mock()
        orchestrator.process_agent.optimize_workflows = AsyncMock(return_value={
            'efficiency_score': 0.75, 'optimization_potential': 0.6
        })
        
        # 執行並行分析
        insights = await orchestrator._execute_parallel_analysis(context)
        
        # 驗證結果
        assert 'brain_analysis' in insights
        assert 'talent_analysis' in insights
        assert 'culture_analysis' in insights
        assert 'future_analysis' in insights
        assert 'process_analysis' in insights
        
        # 驗證所有代理都被調用
        orchestrator.brain_agent.analyze_cognitive_state.assert_called_once()
        orchestrator.talent_agent.analyze_talent_ecosystem.assert_called_once()
        orchestrator.culture_agent.analyze_cultural_dynamics.assert_called_once()
        orchestrator.future_agent.predict_future_trends.assert_called_once()
        orchestrator.process_agent.optimize_workflows.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_emergency_conditions(self, orchestrator, sample_analysis_context):
        """測試緊急情況檢查"""
        context = AnalysisContext(**sample_analysis_context)
        
        # 測試正常情況（無緊急情況）
        normal_insights = {
            'brain_analysis': {'cognitive_load': 0.7, 'stress_level': 0.3},
            'culture_analysis': {'conflict_risk': 0.2, 'team_harmony': 0.8}
        }
        
        emergency_response = await orchestrator._check_emergency_conditions(normal_insights, context)
        assert emergency_response is None
        
        # 測試緊急情況
        emergency_insights = {
            'brain_analysis': {'cognitive_load': 0.95, 'stress_level': 0.9},
            'culture_analysis': {'conflict_risk': 0.85, 'team_harmony': 0.2}
        }
        
        emergency_response = await orchestrator._check_emergency_conditions(emergency_insights, context)
        assert emergency_response is not None
        assert emergency_response['urgency_level'] == 'high'
        assert len(emergency_response['immediate_actions']) > 0
    
    def test_synthesize_insights(self, orchestrator):
        """測試洞察合成"""
        insights = {
            'brain_analysis': {'cognitive_load': 0.7, 'learning_capacity': 0.8},
            'talent_analysis': {'performance_prediction': 0.85, 'career_fit': 0.9},
            'culture_analysis': {'team_harmony': 0.8, 'conflict_risk': 0.2},
            'future_analysis': {'skill_trends': ['AI', 'Cloud'], 'market_demand': 0.9},
            'process_analysis': {'efficiency_score': 0.75, 'optimization_potential': 0.6}
        }
        
        synthesized = orchestrator._synthesize_insights(insights)
        
        # 驗證合成結果
        assert 'integrated_score' in synthesized
        assert 'priority_actions' in synthesized
        assert 'risk_factors' in synthesized
        assert 'opportunity_areas' in synthesized
        
        # 驗證分數計算
        assert 0 <= synthesized['integrated_score'] <= 1
        assert len(synthesized['priority_actions']) > 0
    
    def test_generate_strategic_plan(self, orchestrator, sample_analysis_context):
        """測試戰略計劃生成"""
        context = AnalysisContext(**sample_analysis_context)
        
        synthesized_insights = {
            'integrated_score': 0.82,
            'priority_actions': ['skill_development', 'team_collaboration'],
            'risk_factors': ['cognitive_overload'],
            'opportunity_areas': ['leadership_development']
        }
        
        strategic_plan = orchestrator._generate_strategic_plan(synthesized_insights, context)
        
        # 驗證戰略計劃
        assert 'short_term' in strategic_plan
        assert 'medium_term' in strategic_plan
        assert 'long_term' in strategic_plan
        
        # 驗證時間範圍
        assert len(strategic_plan['short_term']) > 0
        assert len(strategic_plan['medium_term']) > 0
        assert len(strategic_plan['long_term']) > 0
        
        # 驗證行動項目結構
        for action in strategic_plan['short_term']:
            assert 'action' in action
            assert 'timeline' in action
            assert 'priority' in action
    
    def test_calculate_confidence_level(self, orchestrator):
        """測試信心水平計算"""
        insights = {
            'brain_analysis': {'confidence': 0.9},
            'talent_analysis': {'confidence': 0.8},
            'culture_analysis': {'confidence': 0.7},
            'future_analysis': {'confidence': 0.6},
            'process_analysis': {'confidence': 0.8}
        }
        
        confidence = orchestrator._calculate_confidence_level(insights)
        
        # 驗證信心水平
        assert 0 <= confidence <= 1
        assert confidence == pytest.approx(0.76, rel=1e-2)  # 平均值
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator, sample_analysis_context):
        """測試錯誤處理"""
        context = AnalysisContext(**sample_analysis_context)
        
        # 模擬代理分析失敗
        orchestrator.brain_agent = Mock()
        orchestrator.brain_agent.analyze_cognitive_state = AsyncMock(side_effect=Exception("分析失敗"))
        
        with patch.object(orchestrator, '_handle_analysis_error') as mock_error_handler:
            mock_error_handler.return_value = {'error': 'handled'}
            
            # 應該優雅地處理錯誤
            with patch.object(orchestrator, '_execute_parallel_analysis', side_effect=Exception("測試錯誤")):
                with pytest.raises(Exception):
                    await orchestrator.analyze_comprehensive(context)
    
    def test_priority_scoring(self, orchestrator):
        """測試優先級評分"""
        actions = [
            {'action': 'skill_development', 'impact': 0.8, 'urgency': 0.6},
            {'action': 'team_building', 'impact': 0.7, 'urgency': 0.9},
            {'action': 'process_improvement', 'impact': 0.9, 'urgency': 0.4}
        ]
        
        scored_actions = orchestrator._calculate_action_priorities(actions)
        
        # 驗證優先級排序
        assert len(scored_actions) == 3
        assert all('priority_score' in action for action in scored_actions)
        
        # 驗證排序（高優先級在前）
        priorities = [action['priority_score'] for action in scored_actions]
        assert priorities == sorted(priorities, reverse=True)
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, orchestrator, sample_analysis_context):
        """測試緩存行為"""
        context = AnalysisContext(**sample_analysis_context)
        
        # 第一次調用 - 應該執行分析並緩存結果
        with patch.object(orchestrator, '_should_use_cache', return_value=False):
            with patch.object(orchestrator, '_execute_parallel_analysis', return_value={}) as mock_analysis:
                with patch.object(orchestrator, '_cache_analysis_result') as mock_cache:
                    
                    await orchestrator.analyze_comprehensive(context)
                    
                    mock_analysis.assert_called_once()
                    mock_cache.assert_called_once()
        
        # 第二次調用 - 應該使用緩存
        with patch.object(orchestrator, '_should_use_cache', return_value=True):
            with patch.object(orchestrator, '_get_cached_analysis', return_value={'cached': True}) as mock_get_cache:
                
                result = await orchestrator.analyze_comprehensive(context)
                
                mock_get_cache.assert_called_once()
                # 應該返回緩存的結果（轉換為IntegratedStrategy）
                assert result is not None