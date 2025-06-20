"""
Custom Exception System for AI Talent Ecosystem
AI人才生態系統自定義異常體系
"""

from .base_exceptions import (
    TalentEcosystemException,
    ValidationError,
    ConfigurationError,
    ServiceUnavailableError,
    ResourceNotFoundError,
    PermissionDeniedError
)

from .agent_exceptions import (
    AgentAnalysisError,
    AgentCommunicationError,
    AgentTimeoutError,
    AgentValidationError,
    BrainAgentError,
    TalentAgentError,
    CultureAgentError,
    FutureAgentError,
    ProcessAgentError,
    OrchestratorError
)

from .data_exceptions import (
    DataAccessError,
    DataValidationError,
    DatabaseConnectionError,
    CacheError,
    VectorStoreError,
    GraphStoreError
)

from .privacy_exceptions import (
    DataPrivacyViolation,
    InsufficientConsent,
    EncryptionError,
    AnonymizationError,
    AuditTrailError,
    RetentionPolicyViolation
)

from .api_exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    RateLimitExceededError,
    InvalidRequestError,
    ResponseValidationError
)

__all__ = [
    # Base exceptions
    'TalentEcosystemException',
    'ValidationError',
    'ConfigurationError',
    'ServiceUnavailableError',
    'ResourceNotFoundError',
    'PermissionDeniedError',
    
    # Agent exceptions
    'AgentAnalysisError',
    'AgentCommunicationError',
    'AgentTimeoutError',
    'AgentValidationError',
    'BrainAgentError',
    'TalentAgentError',
    'CultureAgentError',
    'FutureAgentError',
    'ProcessAgentError',
    'OrchestratorError',
    
    # Data exceptions
    'DataAccessError',
    'DataValidationError',
    'DatabaseConnectionError',
    'CacheError',
    'VectorStoreError',
    'GraphStoreError',
    
    # Privacy exceptions
    'DataPrivacyViolation',
    'InsufficientConsent',
    'EncryptionError',
    'AnonymizationError',
    'AuditTrailError',
    'RetentionPolicyViolation',
    
    # API exceptions
    'APIError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitExceededError',
    'InvalidRequestError',
    'ResponseValidationError',
]