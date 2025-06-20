"""
Agent Configuration Management
代理配置管理
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from functools import lru_cache
from .environment import get_environment


class AgentConfig(BaseModel):
    """代理配置"""
    
    # 通用代理設置
    timeout_seconds: int = Field(default=120, description="代理超時時間")
    max_retries: int = Field(default=3, description="最大重試次數")
    retry_delay: float = Field(default=1.0, description="重試延遲（秒）")
    max_parallel: int = Field(default=5, description="最大並行數")
    
    # LLM設置
    llm_provider: str = Field(default="openai", description="LLM提供商")
    llm_model: str = Field(default="gpt-4", description="LLM模型")
    llm_temperature: float = Field(default=0.7, description="LLM溫度")
    llm_max_tokens: int = Field(default=4000, description="LLM最大令牌數")
    
    # 緩存設置
    cache_enabled: bool = Field(default=True, description="啟用緩存")
    cache_ttl: int = Field(default=3600, description="緩存生存時間")
    
    # 代理特定配置
    brain_agent: Dict[str, Any] = Field(default_factory=dict)
    talent_agent: Dict[str, Any] = Field(default_factory=dict)
    culture_agent: Dict[str, Any] = Field(default_factory=dict)
    future_agent: Dict[str, Any] = Field(default_factory=dict)
    process_agent: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._load_agent_specific_configs()
    
    def _load_agent_specific_configs(self):
        """加載代理特定配置"""
        env = get_environment()
        
        # Brain Agent 配置
        self.brain_agent = {
            'cognitive_analysis_depth': 'medium' if env.is_production() else 'high',
            'neuroplasticity_factors': [
                'age', 'experience', 'recent_learning', 
                'cognitive_flexibility', 'stress_level'
            ],
            'learning_pathway_complexity': 'adaptive',
            'focus_period_analysis': True,
            'stress_monitoring': True,
            'cache_cognitive_profiles': self.cache_enabled
        }
        
        # Talent Agent 配置
        self.talent_agent = {
            'performance_prediction_horizon': '6_months',
            'skill_matching_threshold': 0.7,
            'career_path_depth': 3,
            'motivation_factors': [
                'autonomy', 'mastery', 'purpose', 
                'recognition', 'growth'
            ],
            'talent_pool_analysis': True,
            'succession_planning': True,
            'cache_talent_profiles': self.cache_enabled
        }
        
        # Culture Agent 配置
        self.culture_agent = {
            'culture_dimensions': [
                'collaboration', 'innovation', 'diversity',
                'communication', 'trust', 'adaptability'
            ],
            'conflict_detection_sensitivity': 'medium',
            'team_dynamics_analysis': True,
            'emotional_intelligence_tracking': True,
            'culture_fit_scoring': True,
            'sentiment_analysis': True,
            'cache_culture_metrics': self.cache_enabled
        }
        
        # Future Agent 配置
        self.future_agent = {
            'prediction_horizons': ['3_months', '6_months', '1_year', '3_years'],
            'trend_sources': [
                'industry_reports', 'job_market_data', 
                'skill_demand_trends', 'technology_adoption'
            ],
            'scenario_planning': True,
            'skill_obsolescence_tracking': True,
            'market_demand_analysis': True,
            'emerging_skills_detection': True,
            'cache_predictions': self.cache_enabled
        }
        
        # Process Agent 配置
        self.process_agent = {
            'optimization_targets': [
                'efficiency', 'quality', 'satisfaction',
                'collaboration', 'innovation'
            ],
            'workflow_analysis_depth': 'comprehensive',
            'meeting_optimization': True,
            'decision_process_analysis': True,
            'bottleneck_detection': True,
            'automation_suggestions': True,
            'cache_process_metrics': self.cache_enabled
        }
        
        # 根據環境調整配置
        if env.is_testing():
            self._apply_testing_adjustments()
        elif env.is_development():
            self._apply_development_adjustments()
        elif env.is_production():
            self._apply_production_adjustments()
    
    def _apply_testing_adjustments(self):
        """應用測試環境調整"""
        # 減少複雜度以加快測試速度
        self.brain_agent['cognitive_analysis_depth'] = 'basic'
        self.talent_agent['career_path_depth'] = 1
        self.culture_agent['conflict_detection_sensitivity'] = 'low'
        self.future_agent['prediction_horizons'] = ['3_months']
        self.process_agent['workflow_analysis_depth'] = 'basic'
        
        # 禁用緩存以確保測試隔離
        for agent_config in [self.brain_agent, self.talent_agent, 
                           self.culture_agent, self.future_agent, self.process_agent]:
            for key in agent_config:
                if key.startswith('cache_'):
                    agent_config[key] = False
    
    def _apply_development_adjustments(self):
        """應用開發環境調整"""
        # 啟用詳細日誌和調試功能
        for agent_name in ['brain_agent', 'talent_agent', 'culture_agent', 
                          'future_agent', 'process_agent']:
            agent_config = getattr(self, agent_name)
            agent_config['verbose_logging'] = True
            agent_config['debug_mode'] = True
            agent_config['save_intermediate_results'] = True
    
    def _apply_production_adjustments(self):
        """應用生產環境調整"""
        # 優化性能和資源使用
        self.timeout_seconds = 90  # 較短的超時時間
        self.max_parallel = 3      # 減少並行數以節省資源
        
        # 關閉調試功能
        for agent_name in ['brain_agent', 'talent_agent', 'culture_agent', 
                          'future_agent', 'process_agent']:
            agent_config = getattr(self, agent_name)
            agent_config['verbose_logging'] = False
            agent_config['debug_mode'] = False
            agent_config['save_intermediate_results'] = False
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """獲取特定代理配置"""
        agent_configs = {
            'brain': self.brain_agent,
            'talent': self.talent_agent,
            'culture': self.culture_agent,
            'future': self.future_agent,
            'process': self.process_agent
        }
        
        base_config = {
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'llm_provider': self.llm_provider,
            'llm_model': self.llm_model,
            'llm_temperature': self.llm_temperature,
            'llm_max_tokens': self.llm_max_tokens,
            'cache_enabled': self.cache_enabled,
            'cache_ttl': self.cache_ttl
        }
        
        specific_config = agent_configs.get(agent_name, {})
        
        # 合併基礎配置和特定配置
        return {**base_config, **specific_config}
    
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """獲取協調器配置"""
        return {
            'max_parallel_agents': self.max_parallel,
            'agent_timeout': self.timeout_seconds,
            'emergency_threshold': {
                'cognitive_load': 0.9,
                'stress_level': 0.8,
                'conflict_risk': 0.8,
                'performance_decline': 0.7
            },
            'synthesis_weights': {
                'brain_analysis': 0.25,
                'talent_analysis': 0.25,
                'culture_analysis': 0.2,
                'future_analysis': 0.15,
                'process_analysis': 0.15
            },
            'cache_strategy': 'adaptive',
            'fallback_enabled': True
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """獲取LLM配置"""
        return {
            'provider': self.llm_provider,
            'model': self.llm_model,
            'temperature': self.llm_temperature,
            'max_tokens': self.llm_max_tokens,
            'timeout': self.timeout_seconds,
            'retry_attempts': self.max_retries
        }
    
    def validate_config(self) -> List[str]:
        """驗證配置"""
        errors = []
        
        # 驗證基本參數
        if self.timeout_seconds <= 0:
            errors.append("Timeout must be positive")
        
        if not 0 <= self.llm_temperature <= 2:
            errors.append("LLM temperature must be between 0 and 2")
        
        if self.max_retries < 0:
            errors.append("Max retries cannot be negative")
        
        if self.max_parallel <= 0:
            errors.append("Max parallel agents must be positive")
        
        # 驗證代理特定配置
        required_keys = {
            'brain_agent': ['cognitive_analysis_depth', 'neuroplasticity_factors'],
            'talent_agent': ['performance_prediction_horizon', 'skill_matching_threshold'],
            'culture_agent': ['culture_dimensions', 'conflict_detection_sensitivity'],
            'future_agent': ['prediction_horizons', 'trend_sources'],
            'process_agent': ['optimization_targets', 'workflow_analysis_depth']
        }
        
        for agent_name, keys in required_keys.items():
            agent_config = getattr(self, agent_name)
            for key in keys:
                if key not in agent_config:
                    errors.append(f"Missing required key '{key}' in {agent_name}")
        
        return errors


@lru_cache()
def get_agent_config() -> AgentConfig:
    """獲取代理配置單例"""
    return AgentConfig()


def get_specific_agent_config(agent_name: str) -> Dict[str, Any]:
    """獲取特定代理配置"""
    config = get_agent_config()
    return config.get_agent_config(agent_name)


def get_orchestrator_config() -> Dict[str, Any]:
    """獲取協調器配置"""
    config = get_agent_config()
    return config.get_orchestrator_config()


def validate_agent_configs() -> bool:
    """驗證所有代理配置"""
    config = get_agent_config()
    errors = config.validate_config()
    
    if errors:
        import logging
        logger = logging.getLogger(__name__)
        for error in errors:
            logger.error(f"Agent configuration error: {error}")
        return False
    
    return True