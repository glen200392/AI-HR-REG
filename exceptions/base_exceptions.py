"""
Base Exception Classes for AI Talent Ecosystem
AI人才生態系統基礎異常類
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class TalentEcosystemException(Exception):
    """
    AI人才生態系統基礎異常類
    所有自定義異常的父類
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now()
        self.exception_id = str(uuid.uuid4())
        
    def _generate_error_code(self) -> str:
        """生成錯誤代碼"""
        class_name = self.__class__.__name__
        return f"TE_{class_name.upper()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'exception_id': self.exception_id,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': self.__class__.__name__,
            'cause': str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', error_code='{self.error_code}')"


class ValidationError(TalentEcosystemException):
    """數據驗證錯誤"""
    
    def __init__(
        self,
        message: str = "數據驗證失敗",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['invalid_value'] = str(value)
        
        super().__init__(message, details=details, **kwargs)
        self.field = field
        self.value = value


class ConfigurationError(TalentEcosystemException):
    """配置錯誤"""
    
    def __init__(
        self,
        message: str = "系統配置錯誤",
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(message, details=details, **kwargs)
        self.config_key = config_key


class ServiceUnavailableError(TalentEcosystemException):
    """服務不可用錯誤"""
    
    def __init__(
        self,
        message: str = "服務暫時不可用",
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(message, details=details, **kwargs)
        self.service_name = service_name
        self.retry_after = retry_after


class ResourceNotFoundError(TalentEcosystemException):
    """資源未找到錯誤"""
    
    def __init__(
        self,
        message: str = "請求的資源未找到",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        
        super().__init__(message, details=details, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class PermissionDeniedError(TalentEcosystemException):
    """權限拒絕錯誤"""
    
    def __init__(
        self,
        message: str = "權限不足，無法執行此操作",
        required_permission: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if required_permission:
            details['required_permission'] = required_permission
        if user_id:
            details['user_id'] = user_id
        
        super().__init__(message, details=details, **kwargs)
        self.required_permission = required_permission
        self.user_id = user_id


class TimeoutError(TalentEcosystemException):
    """超時錯誤"""
    
    def __init__(
        self,
        message: str = "操作超時",
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation
        
        super().__init__(message, details=details, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class ConcurrencyError(TalentEcosystemException):
    """併發錯誤"""
    
    def __init__(
        self,
        message: str = "併發操作衝突",
        resource_id: Optional[str] = None,
        conflict_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_id:
            details['resource_id'] = resource_id
        if conflict_type:
            details['conflict_type'] = conflict_type
        
        super().__init__(message, details=details, **kwargs)
        self.resource_id = resource_id
        self.conflict_type = conflict_type


class BusinessLogicError(TalentEcosystemException):
    """業務邏輯錯誤"""
    
    def __init__(
        self,
        message: str = "業務邏輯錯誤",
        business_rule: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if business_rule:
            details['business_rule'] = business_rule
        if context:
            details['context'] = context
        
        super().__init__(message, details=details, **kwargs)
        self.business_rule = business_rule
        self.context = context