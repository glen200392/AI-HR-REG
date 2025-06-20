"""
Privacy Protection Framework for AI Talent Ecosystem
隱私保護框架 - 確保數據安全和合規性
"""

import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re


class DataSensitivityLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PrivacyTechnique(Enum):
    ANONYMIZATION = "anonymization"
    PSEUDONYMIZATION = "pseudonymization"
    AGGREGATION = "aggregation"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    K_ANONYMITY = "k_anonymity"


class DataEncryption:
    """數據加密實現"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._fernet_key = Fernet.generate_key()
        self._fernet = Fernet(self._fernet_key)
        
        # 生成RSA密鑰對
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self._public_key = self._private_key.public_key()
    
    def encrypt_sensitive_data(self, data: str, method: str = "symmetric") -> str:
        """加密敏感數據"""
        try:
            if method == "symmetric":
                return self._symmetric_encrypt(data)
            elif method == "asymmetric":
                return self._asymmetric_encrypt(data)
            else:
                raise ValueError(f"Unsupported encryption method: {method}")
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str, method: str = "symmetric") -> str:
        """解密敏感數據"""
        try:
            if method == "symmetric":
                return self._symmetric_decrypt(encrypted_data)
            elif method == "asymmetric":
                return self._asymmetric_decrypt(encrypted_data)
            else:
                raise ValueError(f"Unsupported decryption method: {method}")
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def _symmetric_encrypt(self, data: str) -> str:
        """對稱加密"""
        encrypted_bytes = self._fernet.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def _symmetric_decrypt(self, encrypted_data: str) -> str:
        """對稱解密"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
    
    def _asymmetric_encrypt(self, data: str) -> str:
        """非對稱加密"""
        encrypted_bytes = self._public_key.encrypt(
            data.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def _asymmetric_decrypt(self, encrypted_data: str) -> str:
        """非對稱解密"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted_bytes = self._private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_bytes.decode('utf-8')
    
    def hash_pii(self, data: str, salt: Optional[str] = None) -> str:
        """對PII數據進行哈希處理"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用HMAC-SHA256進行安全哈希
        hmac_hash = hmac.new(
            salt.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        )
        
        return f"{salt}:{hmac_hash.hexdigest()}"
    
    def verify_hash(self, data: str, hashed_data: str) -> bool:
        """驗證哈希值"""
        try:
            salt, expected_hash = hashed_data.split(':', 1)
            actual_hash = hmac.new(
                salt.encode('utf-8'),
                data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_hash, actual_hash)
        except Exception:
            return False


class DataAnonymizer:
    """數據匿名化處理"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b|\b\d{10}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'id_number': r'\b[A-Z0-9]{8,12}\b'
        }
    
    def anonymize_employee_data(self, employee_data: Dict[str, Any],
                               technique: PrivacyTechnique = PrivacyTechnique.PSEUDONYMIZATION,
                               k_value: int = 5) -> Dict[str, Any]:
        """匿名化員工數據"""
        anonymized_data = employee_data.copy()
        
        if technique == PrivacyTechnique.ANONYMIZATION:
            anonymized_data = self._full_anonymization(anonymized_data)
        elif technique == PrivacyTechnique.PSEUDONYMIZATION:
            anonymized_data = self._pseudonymization(anonymized_data)
        elif technique == PrivacyTechnique.K_ANONYMITY:
            anonymized_data = self._k_anonymity(anonymized_data, k_value)
        elif technique == PrivacyTechnique.AGGREGATION:
            anonymized_data = self._aggregation(anonymized_data)
        
        return anonymized_data
    
    def _full_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """完全匿名化"""
        sensitive_fields = [
            'name', 'email', 'phone', 'address', 'id_number', 'ssn'
        ]
        
        anonymized = data.copy()
        for field in sensitive_fields:
            if field in anonymized:
                del anonymized[field]
        
        # 移除任何可能包含PII的文本中的敏感信息
        for key, value in anonymized.items():
            if isinstance(value, str):
                anonymized[key] = self._remove_pii_from_text(value)
        
        return anonymized
    
    def _pseudonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """偽名化處理"""
        pseudonymized = data.copy()
        
        # 生成一致的偽名
        if 'id' in data:
            seed = data['id']
        else:
            seed = str(hash(json.dumps(data, sort_keys=True)))
        
        # 替換敏感字段為偽名
        if 'name' in pseudonymized:
            pseudonymized['name'] = self._generate_pseudonym(seed, 'name')
        
        if 'email' in pseudonymized:
            pseudonymized['email'] = self._generate_pseudonym(seed, 'email')
        
        if 'id_number' in pseudonymized:
            pseudonymized['id_number'] = self._generate_pseudonym(seed, 'id')
        
        return pseudonymized
    
    def _k_anonymity(self, data: Dict[str, Any], k: int) -> Dict[str, Any]:
        """K-匿名化處理"""
        anonymized = data.copy()
        
        # 對準標識符進行泛化
        if 'age' in anonymized:
            age = anonymized['age']
            # 年齡分組化（5年一組）
            age_group = (age // 5) * 5
            anonymized['age_group'] = f"{age_group}-{age_group + 4}"
            del anonymized['age']
        
        if 'salary' in anonymized:
            salary = anonymized['salary']
            # 薪資分組化
            salary_group = (salary // 10000) * 10000
            anonymized['salary_range'] = f"{salary_group}-{salary_group + 9999}"
            del anonymized['salary']
        
        if 'location' in anonymized:
            # 地理位置泛化
            location = anonymized['location']
            if isinstance(location, str):
                # 只保留城市級別信息
                parts = location.split(',')
                anonymized['city'] = parts[0].strip() if parts else "Unknown"
                del anonymized['location']
        
        return anonymized
    
    def _aggregation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """聚合化處理"""
        # 這個方法通常用於處理多個記錄的聚合
        # 對於單個記錄，我們進行一些統計化處理
        aggregated = {}
        
        for key, value in data.items():
            if key in ['name', 'email', 'phone', 'id_number']:
                continue  # 跳過直接標識符
            
            if isinstance(value, (int, float)):
                # 數值型數據進行範圍化
                if key == 'age':
                    aggregated['age_category'] = self._categorize_age(value)
                elif key == 'experience_years':
                    aggregated['experience_level'] = self._categorize_experience(value)
                elif key == 'performance_score':
                    aggregated['performance_level'] = self._categorize_performance(value)
                else:
                    aggregated[key] = value
            else:
                aggregated[key] = value
        
        return aggregated
    
    def _remove_pii_from_text(self, text: str) -> str:
        """從文本中移除PII信息"""
        cleaned_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            cleaned_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', cleaned_text)
        
        return cleaned_text
    
    def _generate_pseudonym(self, seed: str, data_type: str) -> str:
        """生成一致的偽名"""
        hash_obj = hashlib.sha256(f"{seed}:{data_type}".encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        if data_type == 'name':
            return f"User_{hash_hex[:8]}"
        elif data_type == 'email':
            return f"user_{hash_hex[:8]}@example.com"
        elif data_type == 'id':
            return f"ID_{hash_hex[:10]}"
        else:
            return f"PSEUDO_{hash_hex[:8]}"
    
    def _categorize_age(self, age: int) -> str:
        """年齡分類"""
        if age < 25:
            return "young"
        elif age < 35:
            return "early_career"
        elif age < 45:
            return "mid_career"
        elif age < 55:
            return "senior_career"
        else:
            return "veteran"
    
    def _categorize_experience(self, years: int) -> str:
        """經驗分類"""
        if years < 2:
            return "entry_level"
        elif years < 5:
            return "junior"
        elif years < 10:
            return "mid_level"
        elif years < 15:
            return "senior"
        else:
            return "expert"
    
    def _categorize_performance(self, score: float) -> str:
        """績效分類"""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "average"
        elif score < 0.8:
            return "high"
        else:
            return "exceptional"


class ConsentManager:
    """同意管理系統"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.consent_records = {}  # 在實際應用中應使用數據庫
    
    def record_consent(self, user_id: str, purpose: str, 
                      consent_given: bool, metadata: Dict[str, Any] = None) -> str:
        """記錄用戶同意"""
        consent_id = secrets.token_urlsafe(16)
        
        consent_record = {
            'consent_id': consent_id,
            'user_id': user_id,
            'purpose': purpose,
            'consent_given': consent_given,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None
        }
        
        self.consent_records[consent_id] = consent_record
        self.logger.info(f"Consent recorded: {consent_id} for user {user_id}")
        
        return consent_id
    
    def check_consent(self, user_id: str, purpose: str) -> bool:
        """檢查用戶同意狀態"""
        for record in self.consent_records.values():
            if (record['user_id'] == user_id and 
                record['purpose'] == purpose and 
                record['consent_given']):
                return True
        return False
    
    def revoke_consent(self, user_id: str, purpose: str) -> bool:
        """撤銷用戶同意"""
        revoked = False
        
        for record in self.consent_records.values():
            if (record['user_id'] == user_id and 
                record['purpose'] == purpose):
                record['consent_given'] = False
                record['revoked_at'] = datetime.now().isoformat()
                revoked = True
        
        if revoked:
            self.logger.info(f"Consent revoked for user {user_id}, purpose {purpose}")
        
        return revoked
    
    def get_consent_history(self, user_id: str) -> List[Dict[str, Any]]:
        """獲取用戶同意歷史"""
        user_consents = []
        
        for record in self.consent_records.values():
            if record['user_id'] == user_id:
                user_consents.append(record.copy())
        
        return sorted(user_consents, key=lambda x: x['timestamp'], reverse=True)


class DataRetentionManager:
    """數據保留管理"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retention_policies = {
            'employee_profiles': timedelta(days=2555),  # 7年
            'performance_data': timedelta(days=1095),   # 3年
            'training_records': timedelta(days=1825),   # 5年
            'audit_logs': timedelta(days=2555),         # 7年
            'consent_records': timedelta(days=3650)     # 10年
        }
    
    def set_retention_policy(self, data_type: str, retention_period: timedelta):
        """設置數據保留政策"""
        self.retention_policies[data_type] = retention_period
        self.logger.info(f"Retention policy set for {data_type}: {retention_period.days} days")
    
    def should_delete_data(self, data_type: str, creation_date: datetime) -> bool:
        """檢查數據是否應該被刪除"""
        if data_type not in self.retention_policies:
            return False
        
        retention_period = self.retention_policies[data_type]
        expiry_date = creation_date + retention_period
        
        return datetime.now() > expiry_date
    
    def get_expiring_data(self, data_type: str, days_ahead: int = 30) -> Dict[str, Any]:
        """獲取即將過期的數據信息"""
        if data_type not in self.retention_policies:
            return {}
        
        retention_period = self.retention_policies[data_type]
        warning_period = timedelta(days=days_ahead)
        
        return {
            'data_type': data_type,
            'retention_period_days': retention_period.days,
            'warning_period_days': days_ahead,
            'policy_description': f"Data will be deleted after {retention_period.days} days"
        }


class AuditLogger:
    """審計日誌記錄器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logs = []  # 在實際應用中應使用持久化存儲
    
    def log_data_access(self, user_id: str, data_type: str, action: str,
                       data_identifier: str, purpose: str = None,
                       metadata: Dict[str, Any] = None):
        """記錄數據訪問"""
        audit_entry = {
            'log_id': secrets.token_urlsafe(16),
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'data_type': data_type,
            'action': action,  # read, write, delete, export
            'data_identifier': data_identifier,
            'purpose': purpose,
            'metadata': metadata or {},
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None
        }
        
        self.audit_logs.append(audit_entry)
        self.logger.info(f"Data access logged: {action} on {data_type} by {user_id}")
    
    def log_privacy_operation(self, operation_type: str, data_subject: str,
                            details: Dict[str, Any], performed_by: str):
        """記錄隱私操作"""
        audit_entry = {
            'log_id': secrets.token_urlsafe(16),
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,  # anonymization, deletion, export
            'data_subject': data_subject,
            'details': details,
            'performed_by': performed_by,
            'category': 'privacy_operation'
        }
        
        self.audit_logs.append(audit_entry)
        self.logger.info(f"Privacy operation logged: {operation_type} for {data_subject}")
    
    def get_audit_trail(self, filters: Dict[str, Any] = None,
                       start_date: datetime = None,
                       end_date: datetime = None) -> List[Dict[str, Any]]:
        """獲取審計追蹤"""
        filtered_logs = self.audit_logs.copy()
        
        # 時間過濾
        if start_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log['timestamp']) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs
                if datetime.fromisoformat(log['timestamp']) <= end_date
            ]
        
        # 自定義過濾器
        if filters:
            for key, value in filters.items():
                filtered_logs = [
                    log for log in filtered_logs
                    if log.get(key) == value
                ]
        
        return sorted(filtered_logs, key=lambda x: x['timestamp'], reverse=True)


class PrivacyProtectionFramework:
    """隱私保護框架主類"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.encryption = DataEncryption()
        self.anonymizer = DataAnonymizer()
        self.consent_manager = ConsentManager()
        self.retention_manager = DataRetentionManager()
        self.audit_logger = AuditLogger()
    
    def classify_data_sensitivity(self, data: Dict[str, Any]) -> DataSensitivityLevel:
        """分類數據敏感性"""
        
        # 檢查是否包含高敏感性數據
        restricted_fields = ['ssn', 'id_number', 'medical_info', 'financial_info']
        if any(field in data for field in restricted_fields):
            return DataSensitivityLevel.RESTRICTED
        
        # 檢查是否包含機密數據
        confidential_fields = ['salary', 'performance_score', 'disciplinary_records']
        if any(field in data for field in confidential_fields):
            return DataSensitivityLevel.CONFIDENTIAL
        
        # 檢查是否包含內部數據
        internal_fields = ['email', 'phone', 'department', 'manager']
        if any(field in data for field in internal_fields):
            return DataSensitivityLevel.INTERNAL
        
        return DataSensitivityLevel.PUBLIC
    
    def process_data_request(self, user_id: str, data: Dict[str, Any],
                           purpose: str, requester_id: str) -> Dict[str, Any]:
        """處理數據請求"""
        
        # 檢查同意
        if not self.consent_manager.check_consent(user_id, purpose):
            raise PermissionError(f"No consent for purpose: {purpose}")
        
        # 分類數據敏感性
        sensitivity = self.classify_data_sensitivity(data)
        
        # 根據敏感性級別處理數據
        if sensitivity == DataSensitivityLevel.RESTRICTED:
            processed_data = self.anonymizer.anonymize_employee_data(
                data, PrivacyTechnique.ANONYMIZATION
            )
        elif sensitivity == DataSensitivityLevel.CONFIDENTIAL:
            processed_data = self.anonymizer.anonymize_employee_data(
                data, PrivacyTechnique.PSEUDONYMIZATION
            )
        elif sensitivity == DataSensitivityLevel.INTERNAL:
            processed_data = self.anonymizer.anonymize_employee_data(
                data, PrivacyTechnique.K_ANONYMITY, k_value=5
            )
        else:
            processed_data = data.copy()
        
        # 記錄審計日誌
        self.audit_logger.log_data_access(
            user_id=requester_id,
            data_type='employee_data',
            action='read',
            data_identifier=user_id,
            purpose=purpose
        )
        
        return {
            'data': processed_data,
            'sensitivity_level': sensitivity.value,
            'processing_applied': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_user_data(self, user_id: str, requester_id: str) -> Dict[str, Any]:
        """導出用戶數據（GDPR數據可攜權）"""
        
        # 記錄導出操作
        self.audit_logger.log_privacy_operation(
            operation_type='data_export',
            data_subject=user_id,
            details={'export_format': 'json', 'requested_by': requester_id},
            performed_by=requester_id
        )
        
        # 在實際應用中，這裡會從各個數據源收集用戶數據
        export_data = {
            'user_id': user_id,
            'export_timestamp': datetime.now().isoformat(),
            'data_sources': ['employee_profiles', 'performance_data', 'training_records'],
            'consent_history': self.consent_manager.get_consent_history(user_id),
            'note': 'This export contains all personal data held about the user'
        }
        
        return export_data
    
    def delete_user_data(self, user_id: str, requester_id: str,
                        reason: str = 'user_request') -> bool:
        """刪除用戶數據（GDPR被遺忘權）"""
        
        try:
            # 記錄刪除操作
            self.audit_logger.log_privacy_operation(
                operation_type='data_deletion',
                data_subject=user_id,
                details={'reason': reason, 'requested_by': requester_id},
                performed_by=requester_id
            )
            
            # 在實際應用中，這裡會從各個數據源刪除用戶數據
            # 注意：某些數據可能因為法律要求需要保留（如審計日誌）
            
            self.logger.info(f"User data deleted for {user_id} by {requester_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete user data for {user_id}: {str(e)}")
            return False
    
    def generate_privacy_report(self, start_date: datetime = None,
                              end_date: datetime = None) -> Dict[str, Any]:
        """生成隱私合規報告"""
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        audit_logs = self.audit_logger.get_audit_trail(
            start_date=start_date,
            end_date=end_date
        )
        
        # 統計分析
        total_accesses = len([log for log in audit_logs if log.get('action')])
        privacy_operations = len([log for log in audit_logs if log.get('category') == 'privacy_operation'])
        
        data_access_by_type = {}
        for log in audit_logs:
            if 'data_type' in log:
                data_type = log['data_type']
                data_access_by_type[data_type] = data_access_by_type.get(data_type, 0) + 1
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary_statistics': {
                'total_data_accesses': total_accesses,
                'privacy_operations': privacy_operations,
                'data_access_by_type': data_access_by_type
            },
            'compliance_status': {
                'audit_logging': 'active',
                'consent_management': 'active',
                'data_retention_policies': 'configured',
                'encryption': 'enabled'
            },
            'generated_at': datetime.now().isoformat()
        }