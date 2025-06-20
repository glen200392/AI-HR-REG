"""
Environment Configuration Management
環境配置管理
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from functools import lru_cache


class EnvironmentType(Enum):
    """環境類型枚舉"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Environment:
    """環境配置管理器"""
    
    def __init__(self):
        self.env_type = self._detect_environment()
        self.config = self._load_environment_config()
    
    def _detect_environment(self) -> EnvironmentType:
        """檢測當前環境"""
        env_name = os.getenv('ENVIRONMENT', 'development').lower()
        
        try:
            return EnvironmentType(env_name)
        except ValueError:
            # 默認為開發環境
            return EnvironmentType.DEVELOPMENT
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """加載環境特定配置"""
        
        base_config = {
            'debug': False,
            'testing': False,
            'log_level': 'INFO',
            'cors_enabled': True,
            'rate_limiting_enabled': True,
            'metrics_enabled': True,
            'cache_enabled': True
        }
        
        env_configs = {
            EnvironmentType.DEVELOPMENT: {
                'debug': True,
                'log_level': 'DEBUG',
                'cors_enabled': True,
                'rate_limiting_enabled': False,
                'auto_reload': True,
                'db_echo': True
            },
            
            EnvironmentType.TESTING: {
                'testing': True,
                'log_level': 'WARNING',
                'cors_enabled': False,
                'rate_limiting_enabled': False,
                'metrics_enabled': False,
                'cache_enabled': False,
                'db_echo': False
            },
            
            EnvironmentType.STAGING: {
                'debug': False,
                'log_level': 'INFO',
                'cors_enabled': True,
                'rate_limiting_enabled': True,
                'metrics_enabled': True,
                'db_echo': False
            },
            
            EnvironmentType.PRODUCTION: {
                'debug': False,
                'log_level': 'WARNING',
                'cors_enabled': False,
                'rate_limiting_enabled': True,
                'metrics_enabled': True,
                'security_headers': True,
                'ssl_required': True,
                'db_echo': False
            }
        }
        
        config = base_config.copy()
        config.update(env_configs.get(self.env_type, {}))
        
        return config
    
    def is_development(self) -> bool:
        """是否為開發環境"""
        return self.env_type == EnvironmentType.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """是否為測試環境"""
        return self.env_type == EnvironmentType.TESTING
    
    def is_staging(self) -> bool:
        """是否為預發布環境"""
        return self.env_type == EnvironmentType.STAGING
    
    def is_production(self) -> bool:
        """是否為生產環境"""
        return self.env_type == EnvironmentType.PRODUCTION
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self.config.get(key, default)
    
    def get_database_config(self) -> Dict[str, Any]:
        """獲取數據庫環境配置"""
        if self.is_testing():
            return {
                'use_memory_db': True,
                'connection_pool_size': 1,
                'max_connections': 5,
                'echo': False
            }
        elif self.is_development():
            return {
                'use_memory_db': False,
                'connection_pool_size': 5,
                'max_connections': 20,
                'echo': True
            }
        elif self.is_staging():
            return {
                'use_memory_db': False,
                'connection_pool_size': 10,
                'max_connections': 50,
                'echo': False,
                'ssl_mode': 'require'
            }
        else:  # production
            return {
                'use_memory_db': False,
                'connection_pool_size': 20,
                'max_connections': 100,
                'echo': False,
                'ssl_mode': 'require',
                'connection_timeout': 30
            }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """獲取緩存環境配置"""
        if self.is_testing():
            return {
                'enabled': False,
                'backend': 'memory',
                'ttl': 60
            }
        elif self.is_development():
            return {
                'enabled': True,
                'backend': 'memory',
                'ttl': 300
            }
        else:  # staging, production
            return {
                'enabled': True,
                'backend': 'redis',
                'ttl': 3600,
                'max_connections': 20
            }
    
    def get_security_config(self) -> Dict[str, Any]:
        """獲取安全環境配置"""
        base_security = {
            'jwt_expiration': 3600,  # 1 hour
            'max_login_attempts': 5,
            'password_min_length': 8
        }
        
        if self.is_production():
            base_security.update({
                'jwt_expiration': 1800,  # 30 minutes
                'require_https': True,
                'secure_cookies': True,
                'max_login_attempts': 3,
                'password_min_length': 12
            })
        elif self.is_staging():
            base_security.update({
                'jwt_expiration': 3600,  # 1 hour
                'require_https': True,
                'secure_cookies': True
            })
        
        return base_security
    
    def get_agent_config(self) -> Dict[str, Any]:
        """獲取代理環境配置"""
        if self.is_testing():
            return {
                'timeout': 10,
                'max_retries': 1,
                'parallel_limit': 2,
                'use_mock_llm': True
            }
        elif self.is_development():
            return {
                'timeout': 60,
                'max_retries': 2,
                'parallel_limit': 3,
                'use_mock_llm': False,
                'verbose_logging': True
            }
        else:  # staging, production
            return {
                'timeout': 120,
                'max_retries': 3,
                'parallel_limit': 5,
                'use_mock_llm': False,
                'circuit_breaker_enabled': True
            }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """獲取監控環境配置"""
        if self.is_testing():
            return {
                'metrics_enabled': False,
                'tracing_enabled': False,
                'health_checks_enabled': False
            }
        elif self.is_development():
            return {
                'metrics_enabled': True,
                'tracing_enabled': True,
                'health_checks_enabled': True,
                'metrics_interval': 10
            }
        else:  # staging, production
            return {
                'metrics_enabled': True,
                'tracing_enabled': True,
                'health_checks_enabled': True,
                'metrics_interval': 60,
                'alerting_enabled': True
            }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """獲取功能開關"""
        flags = {
            'new_ui': False,
            'experimental_agents': False,
            'beta_features': False,
            'advanced_analytics': False
        }
        
        if self.is_development():
            flags.update({
                'experimental_agents': True,
                'beta_features': True,
                'advanced_analytics': True
            })
        elif self.is_staging():
            flags.update({
                'beta_features': True,
                'advanced_analytics': True
            })
        
        # 從環境變量中覆蓋
        for flag_name in flags:
            env_var = f"FEATURE_{flag_name.upper()}"
            if os.getenv(env_var):
                flags[flag_name] = os.getenv(env_var).lower() == 'true'
        
        return flags
    
    def __str__(self) -> str:
        return f"Environment({self.env_type.value})"
    
    def __repr__(self) -> str:
        return f"Environment(type={self.env_type.value}, config_keys={list(self.config.keys())})"


@lru_cache()
def get_environment() -> Environment:
    """獲取環境配置單例"""
    return Environment()


def current_environment() -> str:
    """獲取當前環境名稱"""
    return get_environment().env_type.value


def is_debug_mode() -> bool:
    """是否為調試模式"""
    return get_environment().get_config('debug', False)


def get_feature_flag(flag_name: str, default: bool = False) -> bool:
    """獲取功能開關狀態"""
    flags = get_environment().get_feature_flags()
    return flags.get(flag_name, default)