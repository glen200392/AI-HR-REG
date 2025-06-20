"""
Integration Tests for Agent Coordination
代理協調集成測試
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agents.master_orchestrator import MasterOrchestrator, AnalysisContext
from agents.brain_agent import BrainAgent
from agents.talent_agent import TalentAgent


@pytest.mark.integration
@pytest.mark.agent
class TestAgentCoordination:
    """代理協調集成測試"""
    
    @pytest.mark.asyncio
    async def test_full_system_analysis(self, master_orchestrator, sample_analysis_context):
        """測試完整系統分析"""
        context = AnalysisContext(**sample_analysis_context)
        
        # 模擬代理分析結果
        with patch.object(master_orchestrator, '_execute_parallel_analysis', return_value={
            'brain_analysis': {'cognitive_load': 0.7},
            'talent_analysis': {'performance_prediction': 0.85},
            'culture_analysis': {'team_harmony': 0.8},
            'future_analysis': {'skill_trends': ['AI']},
            'process_analysis': {'efficiency_score': 0.75}
        }):
            result = await master_orchestrator.analyze_comprehensive(context)
            
            assert result is not None
            assert hasattr(result, 'integrated_score')
            assert 0 <= result.integrated_score <= 1