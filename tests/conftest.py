"""
Test Configuration and Fixtures
測試配置和固定設備
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Generator
from datetime import datetime

# 添加項目根目錄到路徑
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.master_orchestrator import MasterOrchestrator
from agents.brain_agent import BrainAgent
from agents.talent_agent import TalentAgent
from agents.culture_agent import CultureAgent
from agents.future_agent import FutureAgent
from agents.process_agent import ProcessAgent
from database.vector_store import ChromaVectorStore
from database.graph_store import Neo4jGraphStore
from database.cache_store import RedisCache
from security.privacy_protection import PrivacyProtectionFramework


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環用於異步測試"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """創建臨時目錄"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_llm_client():
    """模擬LLM客戶端"""
    mock_client = Mock()
    mock_client.chat = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(
            message=Mock(
                content='{"analysis": "test analysis", "recommendations": ["test recommendation"]}'
            )
        )]
    ))
    return mock_client


@pytest.fixture
def sample_employee_data() -> Dict[str, Any]:
    """示例員工數據"""
    return {
        'id': 'emp_001',
        'name': 'John Doe',
        'email': 'john.doe@company.com',
        'department': 'Engineering',
        'role': 'Senior Developer',
        'hire_date': '2020-01-15',
        'experience_years': 8,
        'performance_score': 0.85,
        'skills': {
            'Python': 0.9,
            'JavaScript': 0.8,
            'Machine Learning': 0.7,
            'Leadership': 0.6
        },
        'interests': ['AI', 'Web Development', 'Team Management'],
        'career_goals': ['Tech Lead', 'Solution Architect']
    }


@pytest.fixture
def sample_team_data() -> Dict[str, Any]:
    """示例團隊數據"""
    return {
        'id': 'team_001',
        'name': 'AI Development Team',
        'description': 'Team focused on AI and ML solutions',
        'department': 'Engineering',
        'size': 8,
        'created_date': '2020-03-01',
        'members': ['emp_001', 'emp_002', 'emp_003']
    }


@pytest.fixture
def sample_analysis_context() -> Dict[str, Any]:
    """示例分析上下文"""
    return {
        'employee_id': 'emp_001',
        'analysis_type': 'comprehensive',
        'time_horizon': '3_months',
        'focus_areas': ['performance', 'career_development', 'team_dynamics'],
        'current_context': {
            'recent_projects': ['Project A', 'Project B'],
            'team_changes': False,
            'performance_period': 'Q1_2024'
        }
    }


@pytest.fixture
def mock_vector_store(temp_dir):
    """模擬向量存儲"""
    mock_store = Mock(spec=ChromaVectorStore)
    mock_store.add_employee_profile = AsyncMock(return_value=True)
    mock_store.search_similar_employees = AsyncMock(return_value=[])
    mock_store.add_skill_profile = AsyncMock(return_value=True)
    mock_store.search_related_skills = AsyncMock(return_value=[])
    mock_store.get_collection_stats = AsyncMock(return_value={'employees': 0, 'skills': 0})
    return mock_store


@pytest.fixture
def mock_graph_store():
    """模擬圖存儲"""
    mock_store = Mock(spec=Neo4jGraphStore)
    mock_store.add_employee_node = AsyncMock(return_value=True)
    mock_store.add_team_node = AsyncMock(return_value=True)
    mock_store.create_relationship = AsyncMock(return_value=True)
    mock_store.get_employee_network = AsyncMock(return_value={'nodes': [], 'relationships': []})
    mock_store.analyze_team_dynamics = AsyncMock(return_value={'team_size': 0, 'collaboration_density': 0})
    mock_store.get_graph_statistics = AsyncMock(return_value={'employee_count': 0, 'team_count': 0})
    return mock_store


@pytest.fixture
def mock_cache_store():
    """模擬緩存存儲"""
    mock_store = Mock(spec=RedisCache)
    mock_store.set = AsyncMock(return_value=True)
    mock_store.get = AsyncMock(return_value=None)
    mock_store.delete = AsyncMock(return_value=True)
    mock_store.exists = AsyncMock(return_value=False)
    mock_store.cache_analysis_result = AsyncMock(return_value=True)
    mock_store.get_cached_analysis = AsyncMock(return_value=None)
    return mock_store


@pytest.fixture
def mock_privacy_framework():
    """模擬隱私保護框架"""
    mock_framework = Mock(spec=PrivacyProtectionFramework)
    mock_framework.process_data_request = Mock(return_value={
        'data': {'id': 'emp_001', 'name': 'anonymized'},
        'sensitivity_level': 'internal',
        'processing_applied': True
    })
    mock_framework.export_user_data = Mock(return_value={'user_id': 'emp_001', 'data': {}})
    mock_framework.delete_user_data = Mock(return_value=True)
    return mock_framework


@pytest.fixture
async def master_orchestrator(mock_llm_client, mock_vector_store, mock_graph_store, mock_cache_store):
    """創建Master Orchestrator實例"""
    orchestrator = MasterOrchestrator()
    orchestrator.llm_client = mock_llm_client
    orchestrator.vector_store = mock_vector_store
    orchestrator.graph_store = mock_graph_store
    orchestrator.cache = mock_cache_store
    return orchestrator


@pytest.fixture
async def brain_agent(mock_llm_client, mock_vector_store, mock_cache_store):
    """創建Brain Agent實例"""
    agent = BrainAgent()
    agent.llm_client = mock_llm_client
    agent.vector_store = mock_vector_store
    agent.cache = mock_cache_store
    return agent


@pytest.fixture
async def talent_agent(mock_llm_client, mock_vector_store, mock_graph_store, mock_cache_store):
    """創建Talent Agent實例"""
    agent = TalentAgent()
    agent.llm_client = mock_llm_client
    agent.vector_store = mock_vector_store
    agent.graph_store = mock_graph_store
    agent.cache = mock_cache_store
    return agent


@pytest.fixture
async def culture_agent(mock_llm_client, mock_graph_store, mock_cache_store):
    """創建Culture Agent實例"""
    agent = CultureAgent()
    agent.llm_client = mock_llm_client
    agent.graph_store = mock_graph_store
    agent.cache = mock_cache_store
    return agent


@pytest.fixture
async def future_agent(mock_llm_client, mock_vector_store, mock_cache_store):
    """創建Future Agent實例"""
    agent = FutureAgent()
    agent.llm_client = mock_llm_client
    agent.vector_store = mock_vector_store
    agent.cache = mock_cache_store
    return agent


@pytest.fixture
async def process_agent(mock_llm_client, mock_cache_store):
    """創建Process Agent實例"""
    agent = ProcessAgent()
    agent.llm_client = mock_llm_client
    agent.cache = mock_cache_store
    return agent


@pytest.fixture
def api_client():
    """創建API測試客戶端"""
    from fastapi.testclient import TestClient
    from api.main import app
    return TestClient(app)


class MockDateTime:
    """模擬DateTime類用於測試"""
    
    @classmethod
    def now(cls):
        return datetime(2024, 1, 15, 10, 30, 0)
    
    @classmethod
    def isoformat(cls):
        return "2024-01-15T10:30:00"


@pytest.fixture
def mock_datetime(monkeypatch):
    """模擬datetime.now()"""
    monkeypatch.setattr("datetime.datetime", MockDateTime)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """設置測試環境"""
    # 設置測試環境變數
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # 禁用外部API調用
    monkeypatch.setenv("DISABLE_EXTERNAL_APIS", "true")


@pytest.fixture
def sample_skill_data() -> Dict[str, Any]:
    """示例技能數據"""
    return {
        'id': 'skill_001',
        'name': 'Python Programming',
        'category': 'Programming Languages',
        'description': 'High-level programming language',
        'difficulty': 'medium',
        'market_demand': 0.9,
        'related_skills': ['Data Science', 'Web Development', 'Machine Learning'],
        'learning_resources': ['Online Courses', 'Documentation', 'Practice Projects']
    }


@pytest.fixture
def sample_job_posting() -> Dict[str, Any]:
    """示例職位發布"""
    return {
        'id': 'job_001',
        'title': 'Senior AI Engineer',
        'department': 'Engineering',
        'required_skills': ['Python', 'Machine Learning', 'TensorFlow'],
        'preferred_skills': ['Leadership', 'Communication'],
        'experience_required': 5,
        'description': 'Looking for experienced AI engineer to lead ML projects',
        'posting_date': '2024-01-01'
    }


# 測試標記和配置
pytest_plugins = []

def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試項目收集"""
    for item in items:
        # 添加標記
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # 慢測試標記
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)