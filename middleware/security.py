"""
Security Middleware
安全中間件
"""

import secrets
import hashlib
import hmac
from typing import Dict, Optional, List, Callable, Any
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging
import re
from urllib.parse import urlparse

from config.settings import get_settings
from exceptions.api_exceptions import SecurityPolicyViolation


class SecurityHeaders:
    """安全頭部管理"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """獲取安全頭部"""
        return {
            # 防止點擊劫持
            'X-Frame-Options': 'DENY',
            
            # 防止MIME類型嗅探
            'X-Content-Type-Options': 'nosniff',
            
            # XSS保護
            'X-XSS-Protection': '1; mode=block',
            
            # 引用者政策
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # 內容安全政策
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            ),
            
            # 權限政策
            'Permissions-Policy': (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "accelerometer=(), "
                "gyroscope=()"
            ),
            
            # HSTS (在生產環境中啟用)
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            
            # 快取控制
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    
    @staticmethod
    def apply_headers(response: Response, environment: str = 'production'):
        """應用安全頭部"""
        headers = SecurityHeaders.get_security_headers()
        
        # 開發環境調整
        if environment == 'development':
            # 放寬CSP政策以便開發
            headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
            # 移除HSTS
            headers.pop('Strict-Transport-Security', None)
        
        for header, value in headers.items():
            response.headers[header] = value


class InputValidator:
    """輸入驗證器"""
    
    def __init__(self):
        # 惡意模式檢測
        self.malicious_patterns = [
            # SQL注入
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bDROP\b|\bUPDATE\b)',
            # XSS
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            # 命令注入
            r'[;&|`$()]',
            # 路徑遍歷
            r'\.\./|\.\.\\',
            # LDAP注入
            r'[()&|!]',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
        self.logger = logging.getLogger(__name__)
    
    def validate_input(self, data: Any, field_name: str = '') -> bool:
        """驗證輸入數據"""
        if isinstance(data, str):
            return self._validate_string(data, field_name)
        elif isinstance(data, dict):
            return self._validate_dict(data, field_name)
        elif isinstance(data, list):
            return self._validate_list(data, field_name)
        return True
    
    def _validate_string(self, text: str, field_name: str) -> bool:
        """驗證字符串"""
        # 檢查長度
        if len(text) > 10000:  # 10KB限制
            self.logger.warning(f"Input too long in field {field_name}: {len(text)} characters")
            return False
        
        # 檢查惡意模式
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                self.logger.warning(f"Malicious pattern detected in field {field_name}: {text[:100]}...")
                return False
        
        return True
    
    def _validate_dict(self, data: dict, field_name: str) -> bool:
        """驗證字典"""
        for key, value in data.items():
            if not self.validate_input(key, f"{field_name}.key"):
                return False
            if not self.validate_input(value, f"{field_name}.{key}"):
                return False
        return True
    
    def _validate_list(self, data: list, field_name: str) -> bool:
        """驗證列表"""
        for i, item in enumerate(data):
            if not self.validate_input(item, f"{field_name}[{i}]"):
                return False
        return True
    
    def sanitize_input(self, data: str) -> str:
        """清理輸入數據"""
        # 移除危險字符
        sanitized = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', data)
        
        # 限制長度
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()


class RequestSignatureValidator:
    """請求簽名驗證器"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
    
    def generate_signature(self, payload: str, timestamp: str) -> str:
        """生成請求簽名"""
        message = f"{timestamp}:{payload}"
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def validate_signature(
        self, 
        payload: str, 
        timestamp: str, 
        received_signature: str,
        tolerance_seconds: int = 300
    ) -> bool:
        """驗證請求簽名"""
        
        # 檢查時間戳有效性
        try:
            request_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            if abs((now - request_time).total_seconds()) > tolerance_seconds:
                return False
        except (ValueError, TypeError):
            return False
        
        # 驗證簽名
        expected_signature = self.generate_signature(payload, timestamp)
        return hmac.compare_digest(expected_signature, received_signature)


class SecurityMiddleware:
    """安全中間件"""
    
    def __init__(self):
        self.settings = get_settings()
        self.validator = InputValidator()
        self.signature_validator = RequestSignatureValidator(self.settings.secret_key)
        self.logger = logging.getLogger(__name__)
        
        # 受信任的IP地址
        self.trusted_ips = set([
            '127.0.0.1',
            '::1',
            'localhost'
        ])
        
        # 被封禁的IP地址（可以從數據庫或配置文件讀取）
        self.blocked_ips = set()
        
        # 請求頻率監控
        self.suspicious_activity = {}
        
        # 允許的User-Agent模式
        self.allowed_user_agents = [
            r'Mozilla/.*',
            r'Chrome/.*',
            r'Safari/.*',
            r'curl/.*',
            r'Python-requests/.*',
            r'axios/.*'
        ]
        self.user_agent_patterns = [re.compile(pattern) for pattern in self.allowed_user_agents]
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """中間件調用"""
        
        # 安全檢查
        security_result = await self._perform_security_checks(request)
        if security_result:
            return security_result
        
        # 處理請求
        response = await call_next(request)
        
        # 應用安全頭部
        SecurityHeaders.apply_headers(response, self.settings.environment)
        
        # 添加請求ID
        request_id = self._generate_request_id()
        response.headers['X-Request-ID'] = request_id
        
        return response
    
    async def _perform_security_checks(self, request: Request) -> Optional[JSONResponse]:
        """執行安全檢查"""
        
        # 1. IP黑名單檢查
        client_ip = self._get_client_ip(request)
        if self._is_blocked_ip(client_ip):
            self.logger.warning(f"Blocked IP access attempt: {client_ip}")
            return self._create_security_error_response(
                "ACCESS_DENIED",
                "訪問被拒絕"
            )
        
        # 2. User-Agent檢查
        if not self._validate_user_agent(request):
            self.logger.warning(f"Suspicious User-Agent: {request.headers.get('user-agent', 'None')}")
            return self._create_security_error_response(
                "INVALID_USER_AGENT",
                "無效的User-Agent"
            )
        
        # 3. 請求大小檢查
        if not await self._validate_request_size(request):
            self.logger.warning(f"Request too large from {client_ip}")
            return self._create_security_error_response(
                "REQUEST_TOO_LARGE",
                "請求過大"
            )
        
        # 4. 輸入驗證
        if not await self._validate_request_data(request):
            self.logger.warning(f"Malicious input detected from {client_ip}")
            return self._create_security_error_response(
                "MALICIOUS_INPUT",
                "檢測到惡意輸入"
            )
        
        # 5. 請求簽名驗證（對於API調用）
        if request.url.path.startswith('/api/') and not await self._validate_request_signature(request):
            self.logger.warning(f"Invalid request signature from {client_ip}")
            # 簽名驗證失敗只記錄警告，不阻止請求（可配置）
            pass
        
        # 6. 可疑活動檢測
        if self._detect_suspicious_activity(request):
            self.logger.warning(f"Suspicious activity detected from {client_ip}")
            # 可以選擇阻止或僅記錄
            pass
        
        return None  # 通過所有檢查
    
    def _get_client_ip(self, request: Request) -> str:
        """獲取客戶端IP"""
        # 檢查代理頭部
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'
    
    def _is_blocked_ip(self, ip: str) -> bool:
        """檢查IP是否被封禁"""
        return ip in self.blocked_ips
    
    def _validate_user_agent(self, request: Request) -> bool:
        """驗證User-Agent"""
        user_agent = request.headers.get('user-agent', '')
        
        # 允許空User-Agent（某些合法的API客戶端）
        if not user_agent:
            return True
        
        # 檢查是否匹配允許的模式
        for pattern in self.user_agent_patterns:
            if pattern.match(user_agent):
                return True
        
        return False
    
    async def _validate_request_size(self, request: Request) -> bool:
        """驗證請求大小"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                # 限制請求大小為10MB
                return size <= 10 * 1024 * 1024
            except ValueError:
                return False
        return True
    
    async def _validate_request_data(self, request: Request) -> bool:
        """驗證請求數據"""
        try:
            # 驗證查詢參數
            for key, value in request.query_params.items():
                if not self.validator.validate_input(key, f"query.{key}"):
                    return False
                if not self.validator.validate_input(value, f"query.{key}"):
                    return False
            
            # 驗證路徑參數
            for key, value in request.path_params.items():
                if not self.validator.validate_input(value, f"path.{key}"):
                    return False
            
            # 如果有請求體，驗證內容
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('content-type', '')
                if 'application/json' in content_type:
                    # 注意：這裡不讀取body，因為可能影響後續處理
                    # 實際實現中可以通過自定義的body解析來驗證
                    pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating request data: {e}")
            return False
    
    async def _validate_request_signature(self, request: Request) -> bool:
        """驗證請求簽名"""
        try:
            signature = request.headers.get('X-Signature')
            timestamp = request.headers.get('X-Timestamp')
            
            if not signature or not timestamp:
                return True  # 如果沒有簽名頭部，跳過驗證
            
            # 獲取請求體用於簽名驗證
            # 注意：這需要特殊處理以避免消耗請求體
            # 實際實現中可能需要自定義中間件來處理
            
            return True  # 簡化實現，實際中需要完整的簽名驗證
            
        except Exception as e:
            self.logger.error(f"Error validating request signature: {e}")
            return False
    
    def _detect_suspicious_activity(self, request: Request) -> bool:
        """檢測可疑活動"""
        client_ip = self._get_client_ip(request)
        now = datetime.now()
        
        # 初始化IP記錄
        if client_ip not in self.suspicious_activity:
            self.suspicious_activity[client_ip] = {
                'requests': [],
                'failed_auth': 0,
                'last_request': now
            }
        
        activity = self.suspicious_activity[client_ip]
        activity['requests'].append(now)
        activity['last_request'] = now
        
        # 清理舊記錄（保留最近1小時）
        cutoff = now - timedelta(hours=1)
        activity['requests'] = [req_time for req_time in activity['requests'] if req_time > cutoff]
        
        # 檢查請求頻率
        if len(activity['requests']) > 1000:  # 1小時內超過1000次請求
            return True
        
        # 檢查短時間內的高頻請求
        recent_cutoff = now - timedelta(minutes=1)
        recent_requests = [req_time for req_time in activity['requests'] if req_time > recent_cutoff]
        if len(recent_requests) > 60:  # 1分鐘內超過60次請求
            return True
        
        return False
    
    def _generate_request_id(self) -> str:
        """生成請求ID"""
        return secrets.token_urlsafe(16)
    
    def _create_security_error_response(self, error_code: str, message: str) -> JSONResponse:
        """創建安全錯誤響應"""
        content = {
            'error_code': error_code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        return JSONResponse(
            status_code=403,
            content=content,
            headers={'X-Security-Error': error_code}
        )
    
    def add_blocked_ip(self, ip: str):
        """添加被封禁IP"""
        self.blocked_ips.add(ip)
        self.logger.info(f"Added IP to blocklist: {ip}")
    
    def remove_blocked_ip(self, ip: str):
        """移除被封禁IP"""
        self.blocked_ips.discard(ip)
        self.logger.info(f"Removed IP from blocklist: {ip}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """獲取安全統計"""
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'monitored_ips_count': len(self.suspicious_activity),
            'total_blocked_ips': list(self.blocked_ips),
            'suspicious_activity_summary': {
                ip: {
                    'request_count': len(activity['requests']),
                    'last_request': activity['last_request'].isoformat()
                }
                for ip, activity in self.suspicious_activity.items()
            }
        }


class CSRFProtection:
    """CSRF保護"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_csrf_token(self, session_id: str) -> str:
        """生成CSRF令牌"""
        message = f"{session_id}:{secrets.token_urlsafe(32)}"
        token = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return token
    
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        """驗證CSRF令牌"""
        try:
            # 簡化的CSRF驗證邏輯
            # 實際實現需要更完整的驗證機制
            return len(token) == 64 and all(c in '0123456789abcdef' for c in token)
        except Exception:
            return False


# 全局安全中間件實例
_security_middleware = None


def get_security_middleware() -> SecurityMiddleware:
    """獲取安全中間件實例"""
    global _security_middleware
    
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    
    return _security_middleware