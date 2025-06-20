"""
API Layer Exception Classes
API層異常類
"""

from typing import Dict, Any, Optional, List
from .base_exceptions import TalentEcosystemException


class APIError(TalentEcosystemException):
    """API錯誤基類"""
    
    def __init__(
        self,
        message: str = "API請求處理失敗",
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if status_code:
            details['status_code'] = status_code
        if endpoint:
            details['endpoint'] = endpoint
        if method:
            details['method'] = method
        
        super().__init__(message, details=details, **kwargs)
        self.status_code = status_code
        self.endpoint = endpoint
        self.method = method


class AuthenticationError(APIError):
    """認證錯誤"""
    
    def __init__(
        self,
        message: str = "認證失敗",
        auth_method: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if auth_method:
            details['auth_method'] = auth_method
        if user_id:
            details['user_id'] = user_id
        
        super().__init__(
            message=message,
            status_code=401,
            details=details,
            **kwargs
        )
        self.auth_method = auth_method
        self.user_id = user_id


class AuthorizationError(APIError):
    """授權錯誤"""
    
    def __init__(
        self,
        message: str = "權限不足",
        required_role: Optional[str] = None,
        user_role: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if required_role:
            details['required_role'] = required_role
        if user_role:
            details['user_role'] = user_role
        if resource:
            details['resource'] = resource
        
        super().__init__(
            message=message,
            status_code=403,
            details=details,
            **kwargs
        )
        self.required_role = required_role
        self.user_role = user_role
        self.resource = resource


class RateLimitExceededError(APIError):
    """請求頻率限制錯誤"""
    
    def __init__(
        self,
        message: str = "請求頻率超過限制",
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if limit:
            details['limit'] = limit
        if window_seconds:
            details['window_seconds'] = window_seconds
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(
            message=message,
            status_code=429,
            details=details,
            **kwargs
        )
        self.limit = limit
        self.window_seconds = window_seconds
        self.retry_after = retry_after


class InvalidRequestError(APIError):
    """無效請求錯誤"""
    
    def __init__(
        self,
        message: str = "請求格式無效",
        validation_errors: Optional[List[str]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if validation_errors:
            details['validation_errors'] = validation_errors
        if request_data:
            details['request_fields'] = list(request_data.keys())
        
        super().__init__(
            message=message,
            status_code=400,
            details=details,
            **kwargs
        )
        self.validation_errors = validation_errors or []
        self.request_data = request_data


class ResponseValidationError(APIError):
    """響應驗證錯誤"""
    
    def __init__(
        self,
        message: str = "響應數據驗證失敗",
        expected_schema: Optional[Dict[str, Any]] = None,
        actual_response: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if expected_schema:
            details['expected_fields'] = list(expected_schema.keys())
        if actual_response:
            details['actual_fields'] = list(actual_response.keys())
        
        super().__init__(
            message=message,
            status_code=500,
            details=details,
            **kwargs
        )
        self.expected_schema = expected_schema
        self.actual_response = actual_response


class RequestTimeoutError(APIError):
    """請求超時錯誤"""
    
    def __init__(
        self,
        message: str = "請求處理超時",
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {}}
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            status_code=408,
            details=details,
            **kwargs
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class ContentTypeError(APIError):
    """內容類型錯誤"""
    
    def __init__(
        self,
        message: str = "不支持的內容類型",
        provided_type: Optional[str] = None,
        supported_types: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if provided_type:
            details['provided_type'] = provided_type
        if supported_types:
            details['supported_types'] = supported_types
        
        super().__init__(
            message=message,
            status_code=415,
            details=details,
            **kwargs
        )
        self.provided_type = provided_type
        self.supported_types = supported_types or []


class PayloadTooLargeError(APIError):
    """請求載荷過大錯誤"""
    
    def __init__(
        self,
        message: str = "請求載荷過大",
        payload_size: Optional[int] = None,
        max_size: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if payload_size:
            details['payload_size'] = payload_size
        if max_size:
            details['max_size'] = max_size
        
        super().__init__(
            message=message,
            status_code=413,
            details=details,
            **kwargs
        )
        self.payload_size = payload_size
        self.max_size = max_size


class MethodNotAllowedError(APIError):
    """請求方法不允許錯誤"""
    
    def __init__(
        self,
        message: str = "請求方法不允許",
        method: Optional[str] = None,
        allowed_methods: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if method:
            details['method'] = method
        if allowed_methods:
            details['allowed_methods'] = allowed_methods
        
        super().__init__(
            message=message,
            status_code=405,
            details=details,
            **kwargs
        )
        self.method = method
        self.allowed_methods = allowed_methods or []


class ConflictError(APIError):
    """資源衝突錯誤"""
    
    def __init__(
        self,
        message: str = "資源狀態衝突",
        resource_id: Optional[str] = None,
        conflict_reason: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_id:
            details['resource_id'] = resource_id
        if conflict_reason:
            details['conflict_reason'] = conflict_reason
        
        super().__init__(
            message=message,
            status_code=409,
            details=details,
            **kwargs
        )
        self.resource_id = resource_id
        self.conflict_reason = conflict_reason


class InternalServerError(APIError):
    """內部服務器錯誤"""
    
    def __init__(
        self,
        message: str = "內部服務器錯誤",
        component: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if component:
            details['component'] = component
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            status_code=500,
            details=details,
            **kwargs
        )
        self.component = component
        self.operation = operation


class ServiceDependencyError(APIError):
    """服務依賴錯誤"""
    
    def __init__(
        self,
        message: str = "依賴服務不可用",
        service_name: Optional[str] = None,
        service_status: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if service_name:
            details['service_name'] = service_name
        if service_status:
            details['service_status'] = service_status
        
        super().__init__(
            message=message,
            status_code=503,
            details=details,
            **kwargs
        )
        self.service_name = service_name
        self.service_status = service_status