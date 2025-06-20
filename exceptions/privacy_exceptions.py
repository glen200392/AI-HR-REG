"""
Privacy and Security Exception Classes
隱私與安全異常類
"""

from typing import Dict, Any, Optional, List
from .base_exceptions import TalentEcosystemException


class DataPrivacyViolation(TalentEcosystemException):
    """數據隱私違規錯誤"""
    
    def __init__(
        self,
        message: str = "數據隱私規則違規",
        violation_type: Optional[str] = None,
        affected_data: Optional[str] = None,
        regulation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if violation_type:
            details['violation_type'] = violation_type
        if affected_data:
            details['affected_data'] = affected_data
        if regulation:
            details['regulation'] = regulation  # GDPR, CCPA, etc.
        
        super().__init__(message, details=details, **kwargs)
        self.violation_type = violation_type
        self.affected_data = affected_data
        self.regulation = regulation


class InsufficientConsent(DataPrivacyViolation):
    """同意不足錯誤"""
    
    def __init__(
        self,
        message: str = "用戶同意不足或已撤銷",
        user_id: Optional[str] = None,
        purpose: Optional[str] = None,
        consent_status: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if purpose:
            details['purpose'] = purpose
        if consent_status:
            details['consent_status'] = consent_status
        
        super().__init__(
            message=message,
            violation_type="insufficient_consent",
            details=details,
            **kwargs
        )
        self.user_id = user_id
        self.purpose = purpose
        self.consent_status = consent_status


class EncryptionError(TalentEcosystemException):
    """加密操作錯誤"""
    
    def __init__(
        self,
        message: str = "數據加密/解密失敗",
        encryption_method: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if encryption_method:
            details['encryption_method'] = encryption_method
        if operation:
            details['operation'] = operation  # encrypt, decrypt, key_generation
        
        super().__init__(message, details=details, **kwargs)
        self.encryption_method = encryption_method
        self.operation = operation


class AnonymizationError(TalentEcosystemException):
    """匿名化處理錯誤"""
    
    def __init__(
        self,
        message: str = "數據匿名化處理失敗",
        anonymization_technique: Optional[str] = None,
        data_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if anonymization_technique:
            details['anonymization_technique'] = anonymization_technique
        if data_type:
            details['data_type'] = data_type
        
        super().__init__(message, details=details, **kwargs)
        self.anonymization_technique = anonymization_technique
        self.data_type = data_type


class AuditTrailError(TalentEcosystemException):
    """審計追蹤錯誤"""
    
    def __init__(
        self,
        message: str = "審計日誌記錄失敗",
        audit_event: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if audit_event:
            details['audit_event'] = audit_event
        if user_id:
            details['user_id'] = user_id
        
        super().__init__(message, details=details, **kwargs)
        self.audit_event = audit_event
        self.user_id = user_id


class RetentionPolicyViolation(DataPrivacyViolation):
    """數據保留政策違規"""
    
    def __init__(
        self,
        message: str = "數據保留政策違規",
        data_type: Optional[str] = None,
        retention_period: Optional[int] = None,
        actual_age: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if data_type:
            details['data_type'] = data_type
        if retention_period:
            details['retention_period_days'] = retention_period
        if actual_age:
            details['actual_age_days'] = actual_age
        
        super().__init__(
            message=message,
            violation_type="retention_policy",
            details=details,
            **kwargs
        )
        self.data_type = data_type
        self.retention_period = retention_period
        self.actual_age = actual_age


class DataExportError(TalentEcosystemException):
    """數據導出錯誤（GDPR數據可攜權）"""
    
    def __init__(
        self,
        message: str = "用戶數據導出失敗",
        user_id: Optional[str] = None,
        export_format: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if export_format:
            details['export_format'] = export_format
        
        super().__init__(message, details=details, **kwargs)
        self.user_id = user_id
        self.export_format = export_format


class DataDeletionError(TalentEcosystemException):
    """數據刪除錯誤（被遺忘權）"""
    
    def __init__(
        self,
        message: str = "用戶數據刪除失敗",
        user_id: Optional[str] = None,
        deletion_scope: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if deletion_scope:
            details['deletion_scope'] = deletion_scope
        
        super().__init__(message, details=details, **kwargs)
        self.user_id = user_id
        self.deletion_scope = deletion_scope or []


class ConsentManagementError(TalentEcosystemException):
    """同意管理錯誤"""
    
    def __init__(
        self,
        message: str = "同意管理操作失敗",
        user_id: Optional[str] = None,
        consent_operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if consent_operation:
            details['consent_operation'] = consent_operation  # grant, revoke, update
        
        super().__init__(message, details=details, **kwargs)
        self.user_id = user_id
        self.consent_operation = consent_operation


class DataClassificationError(TalentEcosystemException):
    """數據分類錯誤"""
    
    def __init__(
        self,
        message: str = "數據敏感性分類失敗",
        data_type: Optional[str] = None,
        classification_algorithm: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if data_type:
            details['data_type'] = data_type
        if classification_algorithm:
            details['classification_algorithm'] = classification_algorithm
        
        super().__init__(message, details=details, **kwargs)
        self.data_type = data_type
        self.classification_algorithm = classification_algorithm


class PIIDetectionError(TalentEcosystemException):
    """個人識別信息檢測錯誤"""
    
    def __init__(
        self,
        message: str = "PII檢測失敗",
        detection_method: Optional[str] = None,
        text_length: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if detection_method:
            details['detection_method'] = detection_method
        if text_length:
            details['text_length'] = text_length
        
        super().__init__(message, details=details, **kwargs)
        self.detection_method = detection_method
        self.text_length = text_length


class AccessControlError(TalentEcosystemException):
    """訪問控制錯誤"""
    
    def __init__(
        self,
        message: str = "訪問控制檢查失敗",
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        if resource:
            details['resource'] = resource
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(message, details=details, **kwargs)
        self.user_id = user_id
        self.resource = resource
        self.required_permission = required_permission


class SecurityPolicyViolation(TalentEcosystemException):
    """安全政策違規"""
    
    def __init__(
        self,
        message: str = "安全政策違規",
        policy_name: Optional[str] = None,
        violation_severity: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if policy_name:
            details['policy_name'] = policy_name
        if violation_severity:
            details['violation_severity'] = violation_severity  # low, medium, high, critical
        
        super().__init__(message, details=details, **kwargs)
        self.policy_name = policy_name
        self.violation_severity = violation_severity