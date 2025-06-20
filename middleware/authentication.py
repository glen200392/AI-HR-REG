"""
Authentication Middleware
認證中間件
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import hashlib
import secrets
import bcrypt

from config.settings import get_settings
from exceptions.api_exceptions import AuthenticationError


class JWTAuth:
    """JWT認證管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration_hours: int = 24):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
        self.logger = logging.getLogger(__name__)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """創建訪問令牌"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(hours=self.expiration_hours)
        
        payload = {
            'user_id': user_data['user_id'],
            'email': user_data.get('email'),
            'role': user_data.get('role', 'standard'),
            'permissions': user_data.get('permissions', []),
            'iat': now,
            'exp': expire,
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created access token for user {user_data['user_id']}")
            return token
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise AuthenticationError("無法創建訪問令牌")
    
    def create_refresh_token(self, user_id: str) -> str:
        """創建刷新令牌"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=30)  # 30天有效期
        
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': expire,
            'jti': secrets.token_urlsafe(16)
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created refresh token for user {user_id}")
            return token
        except Exception as e:
            self.logger.error(f"Error creating refresh token: {e}")
            raise AuthenticationError("無法創建刷新令牌")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """驗證令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # 檢查令牌是否被撤銷（需要實現撤銷列表）
            if self._is_token_revoked(payload.get('jti')):
                raise AuthenticationError("令牌已被撤銷")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已過期")
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            raise AuthenticationError("無效的令牌")
        except Exception as e:
            self.logger.error(f"Token verification error: {e}")
            raise AuthenticationError("令牌驗證失敗")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """刷新訪問令牌"""
        try:
            payload = self.verify_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise AuthenticationError("無效的刷新令牌")
            
            # 創建新的訪問令牌
            user_data = {
                'user_id': payload['user_id'],
                'role': 'standard'  # 需要從數據庫獲取最新用戶信息
            }
            
            return self.create_access_token(user_data)
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Token refresh error: {e}")
            raise AuthenticationError("令牌刷新失敗")
    
    def _is_token_revoked(self, jti: str) -> bool:
        """檢查令牌是否被撤銷"""
        # 簡化實現，實際中需要查詢數據庫或Redis
        # 這裡可以實現JWT黑名單機制
        return False
    
    def revoke_token(self, jti: str):
        """撤銷令牌"""
        # 實際實現中需要將JTI添加到撤銷列表
        self.logger.info(f"Token revoked: {jti}")


class PasswordManager:
    """密碼管理器"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密碼"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """驗證密碼"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """生成隨機密碼"""
        import string
        import random
        
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """驗證密碼強度"""
        import re
        
        score = 0
        feedback = []
        
        # 長度檢查
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("密碼至少需要8個字符")
        
        if len(password) >= 12:
            score += 1
        
        # 複雜度檢查
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("需要包含小寫字母")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("需要包含大寫字母")
        
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("需要包含數字")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("需要包含特殊字符")
        
        # 常見密碼檢查
        common_passwords = ['password', '123456', 'admin', 'qwerty']
        if password.lower() in common_passwords:
            score = 0
            feedback.append("不能使用常見密碼")
        
        strength_levels = {
            0: 'very_weak',
            1: 'weak', 
            2: 'weak',
            3: 'medium',
            4: 'strong',
            5: 'strong',
            6: 'very_strong'
        }
        
        return {
            'score': score,
            'strength': strength_levels[min(score, 6)],
            'feedback': feedback,
            'is_valid': score >= 4
        }


class SessionManager:
    """會話管理器"""
    
    def __init__(self):
        self.active_sessions = {}  # 實際中應使用Redis
        self.session_timeout = timedelta(hours=24)
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """創建會話"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'user_id': user_id,
            'user_data': user_data,
            'created_at': datetime.now(timezone.utc),
            'last_activity': datetime.now(timezone.utc),
            'ip_address': None,  # 需要從請求中獲取
            'user_agent': None   # 需要從請求中獲取
        }
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """獲取會話"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return None
        
        # 檢查會話是否過期
        if datetime.now(timezone.utc) - session['last_activity'] > self.session_timeout:
            self.revoke_session(session_id)
            return None
        
        # 更新最後活動時間
        session['last_activity'] = datetime.now(timezone.utc)
        return session
    
    def revoke_session(self, session_id: str):
        """撤銷會話"""
        self.active_sessions.pop(session_id, None)
    
    def revoke_user_sessions(self, user_id: str):
        """撤銷用戶的所有會話"""
        sessions_to_remove = [
            sid for sid, session in self.active_sessions.items()
            if session['user_id'] == user_id
        ]
        
        for session_id in sessions_to_remove:
            self.revoke_session(session_id)


class AuthenticationMiddleware:
    """認證中間件"""
    
    def __init__(self):
        self.settings = get_settings()
        self.jwt_auth = JWTAuth(
            secret_key=self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm,
            expiration_hours=self.settings.jwt_expiration_hours
        )
        self.session_manager = SessionManager()
        self.security = HTTPBearer(auto_error=False)
        self.logger = logging.getLogger(__name__)
        
        # 不需要認證的路徑
        self.public_paths = {
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/forgot-password',
            '/favicon.ico'
        }
        
        # 需要特殊權限的路徑
        self.protected_paths = {
            '/api/v1/admin/': 'admin',
            '/api/v1/analyze/comprehensive': 'premium',
            '/api/v1/predict/trends': 'premium'
        }
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """中間件調用"""
        
        # 檢查是否為公開路徑
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # 執行認證
        auth_result = await self._authenticate_request(request)
        if isinstance(auth_result, Response):
            return auth_result
        
        # 設置用戶上下文
        request.state.user = auth_result
        
        # 檢查路徑權限
        if not self._check_path_permission(request.url.path, auth_result):
            return self._create_auth_error_response(
                "INSUFFICIENT_PERMISSIONS",
                "權限不足"
            )
        
        # 記錄用戶活動
        self._log_user_activity(request, auth_result)
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """檢查是否為公開路徑"""
        return path in self.public_paths or path.startswith('/static/')
    
    async def _authenticate_request(self, request: Request) -> Any:
        """認證請求"""
        
        # 嘗試從Authorization頭部獲取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = self.jwt_auth.verify_token(token)
                return {
                    'user_id': payload['user_id'],
                    'email': payload.get('email'),
                    'role': payload.get('role', 'standard'),
                    'permissions': payload.get('permissions', []),
                    'auth_method': 'jwt'
                }
            except AuthenticationError as e:
                return self._create_auth_error_response("INVALID_TOKEN", str(e))
        
        # 嘗試從Cookie獲取會話ID
        session_id = request.cookies.get('session_id')
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session:
                user_data = session['user_data'].copy()
                user_data['auth_method'] = 'session'
                return user_data
        
        # 檢查API密鑰認證
        api_key = request.headers.get('X-API-Key')
        if api_key:
            # 簡化的API密鑰驗證
            # 實際中需要從數據庫驗證
            if self._validate_api_key(api_key):
                return {
                    'user_id': 'api_user',
                    'role': 'api',
                    'permissions': ['api_access'],
                    'auth_method': 'api_key'
                }
        
        return self._create_auth_error_response(
            "AUTHENTICATION_REQUIRED",
            "需要認證"
        )
    
    def _validate_api_key(self, api_key: str) -> bool:
        """驗證API密鑰"""
        # 簡化實現，實際中需要查詢數據庫
        valid_keys = ['demo_api_key_123', 'test_api_key_456']
        return api_key in valid_keys
    
    def _check_path_permission(self, path: str, user: Dict[str, Any]) -> bool:
        """檢查路徑權限"""
        user_role = user.get('role', 'standard')
        user_permissions = user.get('permissions', [])
        
        # 檢查特殊路徑權限
        for protected_path, required_role in self.protected_paths.items():
            if path.startswith(protected_path):
                if user_role != required_role and required_role not in user_permissions:
                    return False
        
        return True
    
    def _log_user_activity(self, request: Request, user: Dict[str, Any]):
        """記錄用戶活動"""
        self.logger.info(
            f"User activity - User: {user['user_id']}, "
            f"Path: {request.url.path}, "
            f"Method: {request.method}, "
            f"IP: {request.client.host if request.client else 'unknown'}"
        )
    
    def _create_auth_error_response(self, error_code: str, message: str) -> Response:
        """創建認證錯誤響應"""
        content = {
            'error_code': error_code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=401,
            content=content,
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    async def login(self, email: str, password: str, request: Request) -> Dict[str, Any]:
        """用戶登錄"""
        try:
            # 這裡需要實際的用戶驗證邏輯
            # 從數據庫獲取用戶信息並驗證密碼
            
            # 簡化的用戶驗證
            if email == "admin@example.com" and password == "admin123":
                user_data = {
                    'user_id': 'admin_001',
                    'email': email,
                    'role': 'admin',
                    'permissions': ['all']
                }
                
                # 創建令牌
                access_token = self.jwt_auth.create_access_token(user_data)
                refresh_token = self.jwt_auth.create_refresh_token(user_data['user_id'])
                
                # 創建會話
                session_id = self.session_manager.create_session(
                    user_data['user_id'], 
                    user_data
                )
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'session_id': session_id,
                    'user': user_data,
                    'expires_in': self.settings.jwt_expiration_hours * 3600
                }
            else:
                raise AuthenticationError("無效的電子郵件或密碼")
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            raise AuthenticationError("登錄失敗")
    
    async def logout(self, request: Request):
        """用戶登出"""
        user = getattr(request.state, 'user', None)
        if user:
            # 撤銷會話
            session_id = request.cookies.get('session_id')
            if session_id:
                self.session_manager.revoke_session(session_id)
            
            self.logger.info(f"User logged out: {user['user_id']}")


# 全局認證中間件實例
_auth_middleware = None


def get_auth_middleware() -> AuthenticationMiddleware:
    """獲取認證中間件實例"""
    global _auth_middleware
    
    if _auth_middleware is None:
        _auth_middleware = AuthenticationMiddleware()
    
    return _auth_middleware


def get_current_user(request: Request) -> Dict[str, Any]:
    """獲取當前用戶"""
    user = getattr(request.state, 'user', None)
    if not user:
        raise AuthenticationError("未認證的用戶")
    return user


def require_role(required_role: str):
    """角色要求裝飾器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            if user.get('role') != required_role:
                raise AuthenticationError("權限不足")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(required_permission: str):
    """權限要求裝飾器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            permissions = user.get('permissions', [])
            if required_permission not in permissions and user.get('role') != 'admin':
                raise AuthenticationError("權限不足")
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator