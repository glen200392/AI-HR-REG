"""
Data Layer Exception Classes
數據層異常類
"""

from typing import Dict, Any, Optional, List
from .base_exceptions import TalentEcosystemException


class DataAccessError(TalentEcosystemException):
    """數據訪問錯誤基類"""
    
    def __init__(
        self,
        message: str = "數據訪問失敗",
        data_source: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if data_source:
            details['data_source'] = data_source
        if operation:
            details['operation'] = operation
        
        super().__init__(message, details=details, **kwargs)
        self.data_source = data_source
        self.operation = operation


class DataValidationError(TalentEcosystemException):
    """數據驗證錯誤"""
    
    def __init__(
        self,
        message: str = "數據驗證失敗",
        validation_rules: Optional[List[str]] = None,
        invalid_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if validation_rules:
            details['validation_rules'] = validation_rules
        if invalid_data:
            details['invalid_fields'] = list(invalid_data.keys())
        
        super().__init__(message, details=details, **kwargs)
        self.validation_rules = validation_rules or []
        self.invalid_data = invalid_data


class DatabaseConnectionError(DataAccessError):
    """數據庫連接錯誤"""
    
    def __init__(
        self,
        message: str = "數據庫連接失敗",
        database_type: Optional[str] = None,
        connection_string: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if database_type:
            details['database_type'] = database_type
        if connection_string:
            # 隱藏敏感信息
            details['connection_host'] = connection_string.split('@')[-1] if '@' in connection_string else 'unknown'
        
        super().__init__(
            message=message,
            data_source=database_type,
            operation="connect",
            details=details,
            **kwargs
        )
        self.database_type = database_type
        self.connection_string = connection_string


class CacheError(DataAccessError):
    """緩存操作錯誤"""
    
    def __init__(
        self,
        message: str = "緩存操作失敗",
        cache_type: Optional[str] = None,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if cache_type:
            details['cache_type'] = cache_type
        if cache_key:
            details['cache_key'] = cache_key
        
        super().__init__(
            message=message,
            data_source=f"{cache_type}_cache",
            operation=operation,
            details=details,
            **kwargs
        )
        self.cache_type = cache_type
        self.cache_key = cache_key


class VectorStoreError(DataAccessError):
    """向量數據庫錯誤"""
    
    def __init__(
        self,
        message: str = "向量數據庫操作失敗",
        collection_name: Optional[str] = None,
        vector_dimension: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if collection_name:
            details['collection_name'] = collection_name
        if vector_dimension:
            details['vector_dimension'] = vector_dimension
        
        super().__init__(
            message=message,
            data_source="vector_store",
            operation=operation,
            details=details,
            **kwargs
        )
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension


class GraphStoreError(DataAccessError):
    """圖數據庫錯誤"""
    
    def __init__(
        self,
        message: str = "圖數據庫操作失敗",
        node_type: Optional[str] = None,
        relationship_type: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if node_type:
            details['node_type'] = node_type
        if relationship_type:
            details['relationship_type'] = relationship_type
        if query:
            # 只記錄查詢的前100個字符
            details['query_preview'] = query[:100] + "..." if len(query) > 100 else query
        
        super().__init__(
            message=message,
            data_source="graph_store",
            details=details,
            **kwargs
        )
        self.node_type = node_type
        self.relationship_type = relationship_type
        self.query = query


class DataIntegrityError(TalentEcosystemException):
    """數據完整性錯誤"""
    
    def __init__(
        self,
        message: str = "數據完整性檢查失敗",
        integrity_type: Optional[str] = None,
        affected_records: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if integrity_type:
            details['integrity_type'] = integrity_type
        if affected_records:
            details['affected_records'] = affected_records
        
        super().__init__(message, details=details, **kwargs)
        self.integrity_type = integrity_type
        self.affected_records = affected_records


class DataMigrationError(TalentEcosystemException):
    """數據遷移錯誤"""
    
    def __init__(
        self,
        message: str = "數據遷移失敗",
        migration_step: Optional[str] = None,
        source_version: Optional[str] = None,
        target_version: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if migration_step:
            details['migration_step'] = migration_step
        if source_version:
            details['source_version'] = source_version
        if target_version:
            details['target_version'] = target_version
        
        super().__init__(message, details=details, **kwargs)
        self.migration_step = migration_step
        self.source_version = source_version
        self.target_version = target_version


class DataConsistencyError(TalentEcosystemException):
    """數據一致性錯誤"""
    
    def __init__(
        self,
        message: str = "數據一致性檢查失敗",
        inconsistent_fields: Optional[List[str]] = None,
        data_sources: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if inconsistent_fields:
            details['inconsistent_fields'] = inconsistent_fields
        if data_sources:
            details['data_sources'] = data_sources
        
        super().__init__(message, details=details, **kwargs)
        self.inconsistent_fields = inconsistent_fields or []
        self.data_sources = data_sources or []


class QueryExecutionError(DataAccessError):
    """查詢執行錯誤"""
    
    def __init__(
        self,
        message: str = "查詢執行失敗",
        query_type: Optional[str] = None,
        execution_time: Optional[float] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if query_type:
            details['query_type'] = query_type
        if execution_time:
            details['execution_time'] = execution_time
        
        super().__init__(
            message=message,
            operation="query",
            details=details,
            **kwargs
        )
        self.query_type = query_type
        self.execution_time = execution_time


class DataSerializationError(TalentEcosystemException):
    """數據序列化錯誤"""
    
    def __init__(
        self,
        message: str = "數據序列化失敗",
        serialization_format: Optional[str] = None,
        data_type: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if serialization_format:
            details['serialization_format'] = serialization_format
        if data_type:
            details['data_type'] = data_type
        
        super().__init__(message, details=details, **kwargs)
        self.serialization_format = serialization_format
        self.data_type = data_type


class DataSchemaError(TalentEcosystemException):
    """數據架構錯誤"""
    
    def __init__(
        self,
        message: str = "數據架構不匹配",
        expected_schema: Optional[Dict[str, Any]] = None,
        actual_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if expected_schema:
            details['expected_fields'] = list(expected_schema.keys())
        if actual_schema:
            details['actual_fields'] = list(actual_schema.keys())
        
        super().__init__(message, details=details, **kwargs)
        self.expected_schema = expected_schema
        self.actual_schema = actual_schema