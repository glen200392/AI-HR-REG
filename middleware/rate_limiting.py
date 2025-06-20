"""
Rate Limiting Middleware
限流中間件
"""

import time
import asyncio
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import hashlib

from exceptions.api_exceptions import RateLimitExceededError
from config.settings import get_settings


class TokenBucket:
    """令牌桶算法實現"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """消費令牌"""
        async with self._lock:
            now = time.time()
            # 計算需要添加的令牌數
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            # 更新令牌數量，但不超過容量
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # 檢查是否有足夠的令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class SlidingWindowCounter:
    """滑動窗口計數器"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size  # 窗口大小（秒）
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> tuple[bool, Optional[int]]:
        """檢查是否允許請求"""
        async with self._lock:
            now = time.time()
            
            # 移除過期的請求記錄
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            
            # 檢查當前請求數
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True, None
            else:
                # 計算需要等待的時間
                oldest_request = self.requests[0]
                retry_after = int(oldest_request + self.window_size - now) + 1
                return False, retry_after


class DistributedRateLimiter:
    """分佈式限流器（使用Redis）"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.local_limiters: Dict[str, SlidingWindowCounter] = {}
        self.logger = logging.getLogger(__name__)
    
    async def is_allowed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, Optional[int]]:
        """檢查是否允許請求"""
        
        if self.redis:
            return await self._redis_rate_limit(key, max_requests, window_seconds)
        else:
            return await self._local_rate_limit(key, max_requests, window_seconds)
    
    async def _redis_rate_limit(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, Optional[int]]:
        """使用Redis的分佈式限流"""
        try:
            now = time.time()
            pipeline = self.redis.pipeline()
            
            # 使用Lua腳本保證原子性
            lua_script = """
            local key = KEYS[1]
            local window = tonumber(ARGV[1])
            local limit = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            
            -- 移除過期的記錄
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
            
            -- 計算當前請求數
            local current = redis.call('ZCARD', key)
            
            if current < limit then
                -- 添加當前請求
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window)
                return {1, 0}
            else
                -- 計算重試時間
                local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
                local retry_after = 0
                if #oldest > 0 then
                    retry_after = math.ceil(oldest[2] + window - now)
                end
                return {0, retry_after}
            end
            """
            
            result = await self.redis.eval(
                lua_script, 
                1, 
                f"rate_limit:{key}", 
                window_seconds, 
                max_requests, 
                now
            )
            
            allowed = bool(result[0])
            retry_after = result[1] if result[1] > 0 else None
            
            return allowed, retry_after
            
        except Exception as e:
            self.logger.error(f"Redis rate limiting error: {e}")
            # 降級到本地限流
            return await self._local_rate_limit(key, max_requests, window_seconds)
    
    async def _local_rate_limit(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, Optional[int]]:
        """本地內存限流"""
        if key not in self.local_limiters:
            self.local_limiters[key] = SlidingWindowCounter(window_seconds, max_requests)
        
        return await self.local_limiters[key].is_allowed()


class RateLimitMiddleware:
    """限流中間件"""
    
    def __init__(
        self,
        default_rate_limit: int = 100,
        default_window: int = 3600,
        redis_client: Optional[redis.Redis] = None
    ):
        self.default_rate_limit = default_rate_limit
        self.default_window = default_window
        self.limiter = DistributedRateLimiter(redis_client)
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # 端點特定的限流配置
        self.endpoint_limits = {
            '/api/v1/analyze/comprehensive': {'limit': 10, 'window': 3600},  # 1小時10次
            '/api/v1/analyze/cognitive': {'limit': 20, 'window': 3600},      # 1小時20次
            '/api/v1/analyze/talent': {'limit': 20, 'window': 3600},         # 1小時20次
            '/api/v1/analyze/culture': {'limit': 30, 'window': 3600},        # 1小時30次
            '/api/v1/predict/trends': {'limit': 5, 'window': 3600},          # 1小時5次
            '/api/v1/optimize/processes': {'limit': 15, 'window': 3600},     # 1小時15次
            '/api/v1/auth/login': {'limit': 5, 'window': 900},               # 15分鐘5次
            '/api/v1/auth/refresh': {'limit': 10, 'window': 3600},           # 1小時10次
        }
        
        # 用戶角色限流配置
        self.role_limits = {
            'admin': {'multiplier': 5.0},      # 管理員5倍限制
            'premium': {'multiplier': 3.0},    # 高級用戶3倍限制
            'standard': {'multiplier': 1.0},   # 標準用戶1倍限制
            'trial': {'multiplier': 0.5},      # 試用用戶0.5倍限制
        }
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """中間件調用"""
        
        # 獲取限流配置
        endpoint = request.url.path
        rate_config = self._get_rate_config(request, endpoint)
        
        # 生成限流鍵
        rate_key = self._generate_rate_key(request)
        
        # 檢查限流
        allowed, retry_after = await self.limiter.is_allowed(
            rate_key,
            rate_config['limit'],
            rate_config['window']
        )
        
        if not allowed:
            # 記錄限流事件
            self.logger.warning(
                f"Rate limit exceeded for {rate_key} on {endpoint}. "
                f"Retry after: {retry_after} seconds"
            )
            
            # 返回限流錯誤
            return self._create_rate_limit_response(retry_after, rate_config)
        
        # 添加限流頭部信息
        response = await call_next(request)
        self._add_rate_limit_headers(response, rate_config, rate_key)
        
        return response
    
    def _get_rate_config(self, request: Request, endpoint: str) -> Dict[str, int]:
        """獲取限流配置"""
        # 獲取端點特定配置
        config = self.endpoint_limits.get(endpoint, {
            'limit': self.default_rate_limit,
            'window': self.default_window
        })
        
        # 根據用戶角色調整限制
        user = getattr(request.state, 'user', None)
        if user and 'role' in user:
            role = user['role']
            multiplier = self.role_limits.get(role, {}).get('multiplier', 1.0)
            config['limit'] = int(config['limit'] * multiplier)
        
        return config
    
    def _generate_rate_key(self, request: Request) -> str:
        """生成限流鍵"""
        # 優先使用用戶ID
        user = getattr(request.state, 'user', None)
        if user and 'user_id' in user:
            return f"user:{user['user_id']}"
        
        # 降級到IP地址
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """獲取客戶端IP"""
        # 檢查代理頭部
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # 降級到直連IP
        return request.client.host if request.client else 'unknown'
    
    def _create_rate_limit_response(
        self, 
        retry_after: Optional[int], 
        rate_config: Dict[str, int]
    ) -> JSONResponse:
        """創建限流響應"""
        
        content = {
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'message': '請求頻率超過限制',
            'limit': rate_config['limit'],
            'window': rate_config['window'],
            'retry_after': retry_after
        }
        
        headers = {
            'X-RateLimit-Limit': str(rate_config['limit']),
            'X-RateLimit-Window': str(rate_config['window']),
        }
        
        if retry_after:
            headers['Retry-After'] = str(retry_after)
        
        return JSONResponse(
            status_code=429,
            content=content,
            headers=headers
        )
    
    async def _add_rate_limit_headers(
        self, 
        response: Response, 
        rate_config: Dict[str, int],
        rate_key: str
    ):
        """添加限流頭部信息"""
        
        # 計算剩餘請求數（簡化實現）
        # 在實際應用中，需要查詢當前使用量
        response.headers['X-RateLimit-Limit'] = str(rate_config['limit'])
        response.headers['X-RateLimit-Window'] = str(rate_config['window'])
        response.headers['X-RateLimit-Reset'] = str(int(time.time()) + rate_config['window'])


class AdaptiveRateLimiter:
    """自適應限流器"""
    
    def __init__(self):
        self.base_limits = {}
        self.adjustment_factors = defaultdict(lambda: 1.0)
        self.error_rates = defaultdict(lambda: deque(maxlen=100))
        self.response_times = defaultdict(lambda: deque(maxlen=100))
    
    async def adjust_limits(self, endpoint: str, response_time: float, is_error: bool):
        """動態調整限流"""
        
        # 記錄響應時間和錯誤率
        self.response_times[endpoint].append(response_time)
        self.error_rates[endpoint].append(1 if is_error else 0)
        
        # 計算平均響應時間和錯誤率
        avg_response_time = sum(self.response_times[endpoint]) / len(self.response_times[endpoint])
        error_rate = sum(self.error_rates[endpoint]) / len(self.error_rates[endpoint])
        
        # 根據性能指標調整限流因子
        if avg_response_time > 5.0 or error_rate > 0.1:  # 響應慢或錯誤率高
            self.adjustment_factors[endpoint] *= 0.9  # 降低限制
        elif avg_response_time < 1.0 and error_rate < 0.01:  # 響應快且錯誤率低
            self.adjustment_factors[endpoint] = min(2.0, self.adjustment_factors[endpoint] * 1.1)
        
        # 確保調整因子在合理範圍內
        self.adjustment_factors[endpoint] = max(0.1, min(5.0, self.adjustment_factors[endpoint]))


# 全局限流器實例
_rate_limiter = None


async def get_rate_limiter() -> RateLimitMiddleware:
    """獲取限流器實例"""
    global _rate_limiter
    
    if _rate_limiter is None:
        settings = get_settings()
        
        # 嘗試連接Redis
        redis_client = None
        try:
            redis_client = redis.from_url(settings.redis_url)
            await redis_client.ping()
        except Exception:
            logging.getLogger(__name__).warning("Redis not available, using local rate limiting")
            redis_client = None
        
        _rate_limiter = RateLimitMiddleware(
            default_rate_limit=settings.rate_limit_requests,
            default_window=settings.rate_limit_window,
            redis_client=redis_client
        )
    
    return _rate_limiter


def create_rate_limit_key(prefix: str, identifier: str) -> str:
    """創建限流鍵"""
    # 使用哈希確保鍵的一致性和安全性
    key_hash = hashlib.md5(f"{prefix}:{identifier}".encode()).hexdigest()
    return f"rate_limit:{prefix}:{key_hash}"


async def check_rate_limit(
    key: str, 
    max_requests: int, 
    window_seconds: int
) -> tuple[bool, Optional[int]]:
    """檢查限流狀態"""
    limiter = await get_rate_limiter()
    return await limiter.limiter.is_allowed(key, max_requests, window_seconds)