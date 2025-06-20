"""
Unit Tests for Privacy Protection Framework
隱私保護框架單元測試
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from security.privacy_protection import (
    PrivacyProtectionFramework, DataEncryption, DataAnonymizer, 
    ConsentManager, DataRetentionManager, AuditLogger,
    DataSensitivityLevel, PrivacyTechnique
)


@pytest.mark.unit
@pytest.mark.security
class TestDataEncryption:
    """數據加密測試類"""
    
    def test_symmetric_encryption_decryption(self):
        """測試對稱加密解密"""
        encryptor = DataEncryption()
        
        # 測試數據
        original_data = "這是需要加密的敏感數據"
        
        # 加密
        encrypted_data = encryptor.encrypt_sensitive_data(original_data, method="symmetric")
        assert encrypted_data != original_data
        assert len(encrypted_data) > 0
        
        # 解密
        decrypted_data = encryptor.decrypt_sensitive_data(encrypted_data, method="symmetric")
        assert decrypted_data == original_data
    
    def test_asymmetric_encryption_decryption(self):
        """測試非對稱加密解密"""
        encryptor = DataEncryption()
        
        # 測試數據（非對稱加密有長度限制）
        original_data = "敏感數據"
        
        # 加密
        encrypted_data = encryptor.encrypt_sensitive_data(original_data, method="asymmetric")
        assert encrypted_data != original_data
        assert len(encrypted_data) > 0
        
        # 解密
        decrypted_data = encryptor.decrypt_sensitive_data(encrypted_data, method="asymmetric")
        assert decrypted_data == original_data
    
    def test_hash_pii_verification(self):
        """測試PII哈希和驗證"""
        encryptor = DataEncryption()
        
        # 測試數據
        pii_data = "john.doe@company.com"
        
        # 生成哈希
        hashed_data = encryptor.hash_pii(pii_data)
        assert hashed_data != pii_data
        assert ':' in hashed_data  # 鹽值:哈希值格式
        
        # 驗證哈希
        is_valid = encryptor.verify_hash(pii_data, hashed_data)
        assert is_valid == True
        
        # 驗證錯誤數據
        is_invalid = encryptor.verify_hash("wrong.email@company.com", hashed_data)
        assert is_invalid == False
    
    def test_encryption_error_handling(self):
        """測試加密錯誤處理"""
        encryptor = DataEncryption()
        
        # 測試不支持的加密方法
        with pytest.raises(ValueError):
            encryptor.encrypt_sensitive_data("test data", method="unsupported")
        
        # 測試解密錯誤數據
        with pytest.raises(Exception):
            encryptor.decrypt_sensitive_data("invalid_encrypted_data", method="symmetric")


@pytest.mark.unit
@pytest.mark.security
class TestDataAnonymizer:
    """數據匿名化測試類"""
    
    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer()
    
    @pytest.fixture
    def sample_employee_data(self):
        return {
            'id': 'emp_001',
            'name': 'John Doe',
            'email': 'john.doe@company.com',
            'phone': '123-456-7890',
            'address': '123 Main St, City, State',
            'ssn': '123-45-6789',
            'age': 30,
            'salary': 75000,
            'department': 'Engineering',
            'performance_score': 0.85
        }
    
    def test_full_anonymization(self, anonymizer, sample_employee_data):
        """測試完全匿名化"""
        anonymized = anonymizer.anonymize_employee_data(
            sample_employee_data, 
            technique=PrivacyTechnique.ANONYMIZATION
        )
        
        # 驗證敏感字段被移除
        sensitive_fields = ['name', 'email', 'phone', 'address', 'ssn']
        for field in sensitive_fields:
            assert field not in anonymized
        
        # 驗證保留的字段
        assert 'department' in anonymized
        assert 'performance_score' in anonymized
    
    def test_pseudonymization(self, anonymizer, sample_employee_data):
        """測試偽名化"""
        anonymized = anonymizer.anonymize_employee_data(
            sample_employee_data,
            technique=PrivacyTechnique.PSEUDONYMIZATION
        )
        
        # 驗證偽名化處理
        assert 'name' in anonymized
        assert anonymized['name'].startswith('User_')
        assert anonymized['name'] != sample_employee_data['name']
        
        assert 'email' in anonymized
        assert '@example.com' in anonymized['email']
        assert anonymized['email'] != sample_employee_data['email']
        
        # 驗證一致性（相同輸入產生相同偽名）
        anonymized2 = anonymizer.anonymize_employee_data(
            sample_employee_data,
            technique=PrivacyTechnique.PSEUDONYMIZATION
        )
        assert anonymized['name'] == anonymized2['name']
        assert anonymized['email'] == anonymized2['email']
    
    def test_k_anonymity(self, anonymizer, sample_employee_data):
        """測試K-匿名化"""
        anonymized = anonymizer.anonymize_employee_data(
            sample_employee_data,
            technique=PrivacyTechnique.K_ANONYMITY,
            k_value=5
        )
        
        # 驗證年齡分組
        if 'age' in sample_employee_data:
            assert 'age' not in anonymized
            assert 'age_group' in anonymized
            assert '-' in anonymized['age_group']  # 範圍格式
        
        # 驗證薪資分組
        if 'salary' in sample_employee_data:
            assert 'salary' not in anonymized
            assert 'salary_range' in anonymized
            assert '-' in anonymized['salary_range']
    
    def test_aggregation(self, anonymizer, sample_employee_data):
        """測試聚合化處理"""
        anonymized = anonymizer.anonymize_employee_data(
            sample_employee_data,
            technique=PrivacyTechnique.AGGREGATION
        )
        
        # 驗證分類處理
        if 'age' in sample_employee_data:
            assert 'age_category' in anonymized
            assert anonymized['age_category'] in ['young', 'early_career', 'mid_career', 'senior_career', 'veteran']
        
        if 'performance_score' in sample_employee_data:
            assert 'performance_level' in anonymized
            assert anonymized['performance_level'] in ['low', 'average', 'high', 'exceptional']
    
    def test_pii_pattern_detection(self, anonymizer):
        """測試PII模式檢測"""
        text_with_pii = "聯繫 john.doe@company.com 或撥打 123-456-7890"
        
        cleaned_text = anonymizer._remove_pii_from_text(text_with_pii)
        
        # 驗證PII被標記
        assert '[EMAIL_REDACTED]' in cleaned_text
        assert '[PHONE_REDACTED]' in cleaned_text
        assert 'john.doe@company.com' not in cleaned_text
        assert '123-456-7890' not in cleaned_text


@pytest.mark.unit
@pytest.mark.security
class TestConsentManager:
    """同意管理測試類"""
    
    @pytest.fixture
    def consent_manager(self):
        return ConsentManager()
    
    def test_record_consent(self, consent_manager):
        """測試記錄用戶同意"""
        user_id = "user_001"
        purpose = "data_analysis"
        
        consent_id = consent_manager.record_consent(
            user_id=user_id,
            purpose=purpose,
            consent_given=True,
            metadata={'ip_address': '192.168.1.1'}
        )
        
        # 驗證同意記錄
        assert consent_id is not None
        assert len(consent_id) > 0
        
        # 驗證記錄存儲
        assert consent_id in consent_manager.consent_records
        record = consent_manager.consent_records[consent_id]
        assert record['user_id'] == user_id
        assert record['purpose'] == purpose
        assert record['consent_given'] == True
    
    def test_check_consent(self, consent_manager):
        """測試檢查用戶同意"""
        user_id = "user_001"
        purpose = "data_analysis"
        
        # 初始狀態 - 沒有同意
        has_consent = consent_manager.check_consent(user_id, purpose)
        assert has_consent == False
        
        # 記錄同意
        consent_manager.record_consent(user_id, purpose, consent_given=True)
        
        # 檢查同意狀態
        has_consent = consent_manager.check_consent(user_id, purpose)
        assert has_consent == True
        
        # 檢查不同目的
        has_other_consent = consent_manager.check_consent(user_id, "other_purpose")
        assert has_other_consent == False
    
    def test_revoke_consent(self, consent_manager):
        """測試撤銷用戶同意"""
        user_id = "user_001"
        purpose = "data_analysis"
        
        # 記錄同意
        consent_manager.record_consent(user_id, purpose, consent_given=True)
        assert consent_manager.check_consent(user_id, purpose) == True
        
        # 撤銷同意
        revoked = consent_manager.revoke_consent(user_id, purpose)
        assert revoked == True
        
        # 驗證同意被撤銷
        has_consent = consent_manager.check_consent(user_id, purpose)
        assert has_consent == False
    
    def test_consent_history(self, consent_manager):
        """測試同意歷史記錄"""
        user_id = "user_001"
        
        # 記錄多個同意
        purposes = ["data_analysis", "marketing", "research"]
        for purpose in purposes:
            consent_manager.record_consent(user_id, purpose, consent_given=True)
        
        # 獲取歷史記錄
        history = consent_manager.get_consent_history(user_id)
        
        # 驗證歷史記錄
        assert len(history) == 3
        assert all(record['user_id'] == user_id for record in history)
        
        # 驗證按時間排序（最新在前）
        timestamps = [record['timestamp'] for record in history]
        assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.unit
@pytest.mark.security
class TestDataRetentionManager:
    """數據保留管理測試類"""
    
    @pytest.fixture
    def retention_manager(self):
        return DataRetentionManager()
    
    def test_default_retention_policies(self, retention_manager):
        """測試默認保留政策"""
        policies = retention_manager.retention_policies
        
        # 驗證默認政策存在
        assert 'employee_profiles' in policies
        assert 'performance_data' in policies
        assert 'audit_logs' in policies
        
        # 驗證政策為timedelta對象
        assert isinstance(policies['employee_profiles'], timedelta)
        assert policies['employee_profiles'].days > 0
    
    def test_set_retention_policy(self, retention_manager):
        """測試設置保留政策"""
        data_type = "test_data"
        retention_period = timedelta(days=90)
        
        retention_manager.set_retention_policy(data_type, retention_period)
        
        # 驗證政策設置
        assert data_type in retention_manager.retention_policies
        assert retention_manager.retention_policies[data_type] == retention_period
    
    def test_should_delete_data(self, retention_manager):
        """測試數據刪除判斷"""
        data_type = "test_data"
        retention_period = timedelta(days=30)
        
        # 設置保留政策
        retention_manager.set_retention_policy(data_type, retention_period)
        
        # 測試新數據 - 不應該刪除
        recent_date = datetime.now() - timedelta(days=15)
        should_delete = retention_manager.should_delete_data(data_type, recent_date)
        assert should_delete == False
        
        # 測試過期數據 - 應該刪除
        old_date = datetime.now() - timedelta(days=45)
        should_delete = retention_manager.should_delete_data(data_type, old_date)
        assert should_delete == True
        
        # 測試未知數據類型 - 不應該刪除
        should_delete = retention_manager.should_delete_data("unknown_type", old_date)
        assert should_delete == False


@pytest.mark.unit
@pytest.mark.security
class TestAuditLogger:
    """審計日誌測試類"""
    
    @pytest.fixture
    def audit_logger(self):
        return AuditLogger()
    
    def test_log_data_access(self, audit_logger):
        """測試數據訪問日誌"""
        user_id = "user_001"
        data_type = "employee_data"
        action = "read"
        data_identifier = "emp_001"
        purpose = "analysis"
        
        # 記錄數據訪問
        audit_logger.log_data_access(
            user_id=user_id,
            data_type=data_type,
            action=action,
            data_identifier=data_identifier,
            purpose=purpose,
            metadata={'ip_address': '192.168.1.1'}
        )
        
        # 驗證日誌記錄
        assert len(audit_logger.audit_logs) == 1
        log_entry = audit_logger.audit_logs[0]
        
        assert log_entry['user_id'] == user_id
        assert log_entry['data_type'] == data_type
        assert log_entry['action'] == action
        assert log_entry['data_identifier'] == data_identifier
        assert log_entry['purpose'] == purpose
        assert 'timestamp' in log_entry
        assert 'log_id' in log_entry
    
    def test_log_privacy_operation(self, audit_logger):
        """測試隱私操作日誌"""
        operation_type = "data_anonymization"
        data_subject = "emp_001"
        details = {'technique': 'pseudonymization', 'fields': ['name', 'email']}
        performed_by = "system_admin"
        
        # 記錄隱私操作
        audit_logger.log_privacy_operation(
            operation_type=operation_type,
            data_subject=data_subject,
            details=details,
            performed_by=performed_by
        )
        
        # 驗證日誌記錄
        assert len(audit_logger.audit_logs) == 1
        log_entry = audit_logger.audit_logs[0]
        
        assert log_entry['operation_type'] == operation_type
        assert log_entry['data_subject'] == data_subject
        assert log_entry['details'] == details
        assert log_entry['performed_by'] == performed_by
        assert log_entry['category'] == 'privacy_operation'
    
    def test_get_audit_trail(self, audit_logger):
        """測試審計追蹤"""
        # 記錄多個日誌條目
        for i in range(5):
            audit_logger.log_data_access(
                user_id=f"user_{i:03d}",
                data_type="employee_data",
                action="read",
                data_identifier=f"emp_{i:03d}",
                purpose="analysis"
            )
        
        # 獲取所有日誌
        all_logs = audit_logger.get_audit_trail()
        assert len(all_logs) == 5
        
        # 測試過濾器
        filtered_logs = audit_logger.get_audit_trail(
            filters={'user_id': 'user_001'}
        )
        assert len(filtered_logs) == 1
        assert filtered_logs[0]['user_id'] == 'user_001'
        
        # 測試時間過濾
        now = datetime.now()
        recent_logs = audit_logger.get_audit_trail(
            start_date=now - timedelta(minutes=5),
            end_date=now
        )
        assert len(recent_logs) == 5  # 所有日誌都是最近的


@pytest.mark.unit
@pytest.mark.security
class TestPrivacyProtectionFramework:
    """隱私保護框架集成測試類"""
    
    @pytest.fixture
    def privacy_framework(self):
        return PrivacyProtectionFramework()
    
    def test_classify_data_sensitivity(self, privacy_framework):
        """測試數據敏感性分類"""
        # 測試受限數據
        restricted_data = {'ssn': '123-45-6789', 'name': 'John Doe'}
        sensitivity = privacy_framework.classify_data_sensitivity(restricted_data)
        assert sensitivity == DataSensitivityLevel.RESTRICTED
        
        # 測試機密數據
        confidential_data = {'salary': 75000, 'performance_score': 0.85}
        sensitivity = privacy_framework.classify_data_sensitivity(confidential_data)
        assert sensitivity == DataSensitivityLevel.CONFIDENTIAL
        
        # 測試內部數據
        internal_data = {'email': 'john@company.com', 'department': 'Engineering'}
        sensitivity = privacy_framework.classify_data_sensitivity(internal_data)
        assert sensitivity == DataSensitivityLevel.INTERNAL
        
        # 測試公開數據
        public_data = {'company': 'TechCorp', 'industry': 'Technology'}
        sensitivity = privacy_framework.classify_data_sensitivity(public_data)
        assert sensitivity == DataSensitivityLevel.PUBLIC
    
    def test_process_data_request(self, privacy_framework):
        """測試數據請求處理"""
        user_id = "user_001"
        purpose = "analysis"
        requester_id = "analyst_001"
        
        # 先記錄用戶同意
        privacy_framework.consent_manager.record_consent(
            user_id=user_id,
            purpose=purpose,
            consent_given=True
        )
        
        # 測試機密數據請求
        confidential_data = {
            'id': user_id,
            'salary': 75000,
            'performance_score': 0.85,
            'name': 'John Doe'
        }
        
        result = privacy_framework.process_data_request(
            user_id=user_id,
            data=confidential_data,
            purpose=purpose,
            requester_id=requester_id
        )
        
        # 驗證處理結果
        assert 'data' in result
        assert 'sensitivity_level' in result
        assert 'processing_applied' in result
        assert result['processing_applied'] == True
        assert result['sensitivity_level'] == 'confidential'
        
        # 驗證數據被適當處理（偽名化）
        processed_data = result['data']
        assert processed_data['name'].startswith('User_')  # 偽名化處理
    
    def test_process_data_request_no_consent(self, privacy_framework):
        """測試無同意的數據請求"""
        user_id = "user_002"
        purpose = "marketing"
        requester_id = "marketer_001"
        
        data = {'name': 'Jane Doe', 'email': 'jane@company.com'}
        
        # 測試無同意情況
        with pytest.raises(PermissionError):
            privacy_framework.process_data_request(
                user_id=user_id,
                data=data,
                purpose=purpose,
                requester_id=requester_id
            )
    
    def test_export_user_data(self, privacy_framework):
        """測試用戶數據導出（GDPR）"""
        user_id = "user_001"
        requester_id = "user_001"  # 用戶自己請求
        
        # 先記錄一些同意
        privacy_framework.consent_manager.record_consent(
            user_id=user_id,
            purpose="analysis",
            consent_given=True
        )
        
        # 導出數據
        export_data = privacy_framework.export_user_data(user_id, requester_id)
        
        # 驗證導出結果
        assert 'user_id' in export_data
        assert 'export_timestamp' in export_data
        assert 'data_sources' in export_data
        assert 'consent_history' in export_data
        assert export_data['user_id'] == user_id
        
        # 驗證審計日誌
        audit_logs = privacy_framework.audit_logger.get_audit_trail()
        export_logs = [log for log in audit_logs if log.get('operation_type') == 'data_export']
        assert len(export_logs) == 1
    
    def test_delete_user_data(self, privacy_framework):
        """測試用戶數據刪除（被遺忘權）"""
        user_id = "user_001"
        requester_id = "user_001"
        reason = "user_request"
        
        # 刪除用戶數據
        success = privacy_framework.delete_user_data(user_id, requester_id, reason)
        
        # 驗證刪除成功
        assert success == True
        
        # 驗證審計日誌
        audit_logs = privacy_framework.audit_logger.get_audit_trail()
        deletion_logs = [log for log in audit_logs if log.get('operation_type') == 'data_deletion']
        assert len(deletion_logs) == 1
        assert deletion_logs[0]['data_subject'] == user_id
    
    def test_generate_privacy_report(self, privacy_framework):
        """測試隱私合規報告生成"""
        # 生成一些活動
        user_id = "user_001"
        privacy_framework.audit_logger.log_data_access(
            user_id="admin_001",
            data_type="employee_data",
            action="read",
            data_identifier=user_id,
            purpose="analysis"
        )
        
        privacy_framework.audit_logger.log_privacy_operation(
            operation_type="data_anonymization",
            data_subject=user_id,
            details={'technique': 'pseudonymization'},
            performed_by="system"
        )
        
        # 生成報告
        report = privacy_framework.generate_privacy_report()
        
        # 驗證報告結構
        assert 'report_period' in report
        assert 'summary_statistics' in report
        assert 'compliance_status' in report
        assert 'generated_at' in report
        
        # 驗證統計數據
        stats = report['summary_statistics']
        assert 'total_data_accesses' in stats
        assert 'privacy_operations' in stats
        assert stats['total_data_accesses'] >= 1
        assert stats['privacy_operations'] >= 1
        
        # 驗證合規狀態
        compliance = report['compliance_status']
        assert compliance['audit_logging'] == 'active'
        assert compliance['consent_management'] == 'active'
        assert compliance['encryption'] == 'enabled'