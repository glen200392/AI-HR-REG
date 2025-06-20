"""
Main Settings Configuration
主要設置配置
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field, validator
from functools import lru_cache
import logging


class Settings(BaseSettings):
    """主要配置設置"""
    
    # 應用基本設置
    app_name: str = Field(default="AI Talent Ecosystem", description="應用名稱")
    app_version: str = Field(default="1.0.0", description="應用版本")
    environment: str = Field(default="development", description="運行環境")
    debug: bool = Field(default=False, description="調試模式")
    
    # API設置
    api_host: str = Field(default="0.0.0.0", description="API主機地址")
    api_port: int = Field(default=8000, description="API端口")
    api_prefix: str = Field(default="/api/v1", description="API前綴")
    cors_origins: List[str] = Field(default=["*"], description="CORS允許源")
    
    # LLM設置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密鑰")
    openai_model: str = Field(default="gpt-4", description="OpenAI模型")
    openai_max_tokens: int = Field(default=4000, description="最大令牌數")
    openai_temperature: float = Field(default=0.7, description="創造性溫度")
    
    # 數據庫設置
    redis_url: str = Field(default="redis://localhost:6379", description="Redis連接URL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j連接URI")
    neo4j_username: str = Field(default="neo4j", description="Neo4j用戶名")
    neo4j_password: str = Field(default="password", description="Neo4j密碼")
    chroma_persist_directory: str = Field(default="./chroma_db", description="ChromaDB持久化目錄")
    
    # 安全設置
    secret_key: str = Field(default="your-secret-key-here", description="密鑰")
    jwt_algorithm: str = Field(default="HS256", description="JWT算法")
    jwt_expiration_hours: int = Field(default=24, description="JWT過期時間（小時）")
    encryption_key: Optional[str] = Field(default=None, description="加密密鑰")
    
    # 限流設置
    rate_limit_requests: int = Field(default=100, description="限流請求數")
    rate_limit_window: int = Field(default=3600, description="限流時間窗口（秒）")
    
    # 日誌設置
    log_level: str = Field(default="INFO", description="日誌級別")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日誌格式"
    )
    log_file: Optional[str] = Field(default=None, description="日誌文件路徑")
    
    # 代理設置
    agent_timeout_seconds: int = Field(default=120, description="代理超時時間（秒）")
    max_parallel_agents: int = Field(default=5, description="最大並行代理數")
    agent_retry_attempts: int = Field(default=3, description="代理重試次數")
    
    # 緩存設置
    cache_ttl_seconds: int = Field(default=3600, description="緩存生存時間（秒）")
    cache_max_entries: int = Field(default=10000, description="緩存最大條目數")
    
    # 監控設置
    metrics_enabled: bool = Field(default=True, description="啟用指標收集")
    health_check_interval: int = Field(default=30, description="健康檢查間隔（秒）")
    
    @validator('environment')
    def validate_environment(cls, v):
        """驗證環境設置"""
        allowed = ['development', 'testing', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'Environment must be one of {allowed}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """驗證日誌級別"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of {allowed}')
        return v.upper()
    
    @validator('openai_temperature')
    def validate_temperature(cls, v):
        """驗證溫度參數"""
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v
    
    def is_development(self) -> bool:
        """是否為開發環境"""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """是否為生產環境"""
        return self.environment == 'production'
    
    def is_testing(self) -> bool:
        """是否為測試環境"""
        return self.environment == 'testing'
    
    def get_database_config(self) -> Dict[str, Any]:
        """獲取數據庫配置"""
        return {
            'redis_url': self.redis_url,
            'neo4j_uri': self.neo4j_uri,
            'neo4j_username': self.neo4j_username,
            'neo4j_password': self.neo4j_password,
            'chroma_persist_directory': self.chroma_persist_directory
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """獲取LLM配置"""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model,
            'max_tokens': self.openai_max_tokens,
            'temperature': self.openai_temperature
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """獲取安全配置"""
        return {
            'secret_key': self.secret_key,
            'jwt_algorithm': self.jwt_algorithm,
            'jwt_expiration_hours': self.jwt_expiration_hours,
            'encryption_key': self.encryption_key
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """獲取API配置"""
        return {
            'host': self.api_host,
            'port': self.api_port,
            'prefix': self.api_prefix,
            'cors_origins': self.cors_origins
        }
    
    def setup_logging(self):
        """設置日誌配置"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=self.log_format,
            filename=self.log_file
        )
        
        # 設置第三方庫日誌級別
        if not self.is_development():
            logging.getLogger('httpx').setLevel(logging.WARNING)
            logging.getLogger('chromadb').setLevel(logging.WARNING)
            logging.getLogger('neo4j').setLevel(logging.WARNING)
    
    def validate_required_settings(self):
        """驗證必需的設置"""
        errors = []
        
        if self.is_production():
            # 生產環境必需的設置
            if not self.openai_api_key:
                errors.append("OpenAI API key is required in production")
            
            if self.secret_key == "your-secret-key-here":
                errors.append("Secret key must be changed in production")
            
            if self.debug:
                errors.append("Debug mode should be disabled in production")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """獲取設置單例"""
    settings = Settings()
    
    # 驗證設置
    try:
        settings.validate_required_settings()
    except ValueError as e:
        logging.warning(f"Configuration validation warning: {e}")
    
    # 設置日誌
    settings.setup_logging()
    
    return settings


# 便捷函數
def get_database_url(db_type: str) -> str:
    """獲取數據庫URL"""
    settings = get_settings()
    
    if db_type == 'redis':
        return settings.redis_url
    elif db_type == 'neo4j':
        return settings.neo4j_uri
    elif db_type == 'chroma':
        return settings.chroma_persist_directory
    else:
        raise ValueError(f"Unknown database type: {db_type}")


def is_feature_enabled(feature_name: str) -> bool:
    """檢查功能是否啟用"""
    settings = get_settings()
    
    feature_flags = {
        'metrics': settings.metrics_enabled,
        'debug': settings.debug,
        'cors': len(settings.cors_origins) > 0
    }
    
    return feature_flags.get(feature_name, False)


def get_timeout_config() -> Dict[str, int]:
    """獲取超時配置"""
    settings = get_settings()
    
    return {
        'agent_timeout': settings.agent_timeout_seconds,
        'health_check_interval': settings.health_check_interval,
        'cache_ttl': settings.cache_ttl_seconds
    }