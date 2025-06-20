"""
Centralized Error Handler for AI Talent Ecosystem
AI人才生態系統集中錯誤處理器
"""

import logging
import traceback
from typing import Dict, Any, Optional, Type, Callable
from datetime import datetime
from functools import wraps

from .base_exceptions import TalentEcosystemException
from .agent_exceptions import *
from .data_exceptions import *
from .privacy_exceptions import *
from .api_exceptions import *


class ErrorHandler:
    """集中錯誤處理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._recovery_strategies: Dict[Type[Exception], Callable] = {}
        self.error_counts: Dict[str, int] = {}
        
        # 註冊默認錯誤處理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """註冊默認錯誤處理器"""
        
        # 代理錯誤處理
        self.register_handler(AgentTimeoutError, self._handle_agent_timeout)
        self.register_handler(AgentCommunicationError, self._handle_agent_communication_error)
        self.register_handler(LLMIntegrationError, self._handle_llm_error)
        
        # 數據錯誤處理
        self.register_handler(DatabaseConnectionError, self._handle_database_error)
        self.register_handler(CacheError, self._handle_cache_error)
        self.register_handler(VectorStoreError, self._handle_vector_store_error)
        
        # 隱私錯誤處理
        self.register_handler(DataPrivacyViolation, self._handle_privacy_violation)
        self.register_handler(InsufficientConsent, self._handle_insufficient_consent)
        
        # API錯誤處理
        self.register_handler(RateLimitExceededError, self._handle_rate_limit)
        self.register_handler(AuthenticationError, self._handle_auth_error)
    
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """註冊異常處理器"""
        self._error_handlers[exception_type] = handler
        self.logger.info(f"Registered error handler for {exception_type.__name__}")
    
    def register_recovery_strategy(self, exception_type: Type[Exception], strategy: Callable):
        """註冊錯誤恢復策略"""
        self._recovery_strategies[exception_type] = strategy
        self.logger.info(f"Registered recovery strategy for {exception_type.__name__}")
    
    def handle_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """處理異常"""
        
        # 記錄錯誤統計
        exception_name = exception.__class__.__name__
        self.error_counts[exception_name] = self.error_counts.get(exception_name, 0) + 1
        
        # 創建錯誤上下文
        error_context = {
            'exception': exception,
            'context': context or {},
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc()
        }
        
        # 記錄錯誤日誌
        self._log_error(exception, error_context)
        
        # 查找並執行特定處理器
        handler = self._find_handler(type(exception))
        if handler:
            try:
                return handler(exception, error_context)
            except Exception as handler_error:
                self.logger.error(f"Error handler failed: {handler_error}")
        
        # 默認處理
        return self._default_error_response(exception, error_context)
    
    def _find_handler(self, exception_type: Type[Exception]) -> Optional[Callable]:
        """查找異常處理器"""
        # 直接匹配
        if exception_type in self._error_handlers:
            return self._error_handlers[exception_type]
        
        # 查找父類匹配
        for registered_type, handler in self._error_handlers.items():
            if issubclass(exception_type, registered_type):
                return handler
        
        return None
    
    def _log_error(self, exception: Exception, context: Dict[str, Any]):
        """記錄錯誤日誌"""
        if isinstance(exception, TalentEcosystemException):
            # 結構化日誌記錄
            log_data = exception.to_dict()
            log_data.update({
                'context': context.get('context', {}),
                'traceback': context.get('traceback')
            })
            self.logger.error(f"TalentEcosystemException: {exception}", extra=log_data)
        else:
            # 標準錯誤日誌
            self.logger.error(
                f"Unhandled exception: {exception.__class__.__name__}: {str(exception)}",
                exc_info=True,
                extra={'context': context.get('context', {})}
            )
    
    def _default_error_response(self, exception: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """默認錯誤響應"""
        if isinstance(exception, TalentEcosystemException):
            return exception.to_dict()
        
        return {
            'error_code': 'UNKNOWN_ERROR',
            'message': str(exception),
            'exception_type': exception.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'recoverable': False
        }
    
    # 具體錯誤處理器實現
    
    def _handle_agent_timeout(self, exception: AgentTimeoutError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理代理超時錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'retry_with_extended_timeout',
            'fallback_to_cached_result',
            'partial_analysis_mode'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_agent_communication_error(self, exception: AgentCommunicationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理代理通信錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'retry_communication',
            'use_alternative_agent',
            'direct_orchestrator_fallback'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_llm_error(self, exception: LLMIntegrationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理LLM集成錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'retry_with_backoff',
            'switch_to_backup_model',
            'use_rule_based_fallback'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_database_error(self, exception: DatabaseConnectionError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理數據庫錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'retry_connection',
            'switch_to_backup_database',
            'use_memory_fallback'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_cache_error(self, exception: CacheError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理緩存錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'bypass_cache',
            'use_memory_cache',
            'direct_database_query'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_vector_store_error(self, exception: VectorStoreError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理向量存儲錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'retry_operation',
            'use_alternative_collection',
            'fallback_to_keyword_search'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_privacy_violation(self, exception: DataPrivacyViolation, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理隱私違規錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'apply_additional_anonymization',
            'request_explicit_consent',
            'abort_operation'
        ]
        response['recoverable'] = False  # 隱私違規通常不可恢復
        response['security_alert'] = True
        return response
    
    def _handle_insufficient_consent(self, exception: InsufficientConsent, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理同意不足錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'request_user_consent',
            'use_anonymized_data_only',
            'abort_operation'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_rate_limit(self, exception: RateLimitExceededError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理限流錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            f'wait_and_retry:{exception.retry_after}',
            'queue_request',
            'return_cached_result'
        ]
        response['recoverable'] = True
        return response
    
    def _handle_auth_error(self, exception: AuthenticationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """處理認證錯誤"""
        response = exception.to_dict()
        response['recovery_actions'] = [
            'refresh_token',
            'redirect_to_login',
            'use_anonymous_access'
        ]
        response['recoverable'] = True
        return response
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """獲取錯誤統計信息"""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_types': dict(self.error_counts),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1])[0] if self.error_counts else None,
            'registered_handlers': len(self._error_handlers),
            'recovery_strategies': len(self._recovery_strategies)
        }


def exception_handler(fallback_value: Any = None, log_error: bool = True):
    """異常處理裝飾器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logging.getLogger(func.__module__).error(
                        f"Exception in {func.__name__}: {str(e)}", 
                        exc_info=True
                    )
                
                if isinstance(e, TalentEcosystemException):
                    raise
                
                return fallback_value
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logging.getLogger(func.__module__).error(
                        f"Exception in {func.__name__}: {str(e)}", 
                        exc_info=True
                    )
                
                if isinstance(e, TalentEcosystemException):
                    raise
                
                return fallback_value
        
        # 檢查函數是否為異步
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_exception(
    exceptions: tuple = (Exception,),
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    logging.getLogger(func.__module__).warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time:.2f} seconds..."
                    )
                    
                    import asyncio
                    await asyncio.sleep(wait_time)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    logging.getLogger(func.__module__).warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time:.2f} seconds..."
                    )
                    
                    time.sleep(wait_time)
            
            raise last_exception
        
        # 檢查函數是否為異步
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 全局錯誤處理器實例
global_error_handler = ErrorHandler()