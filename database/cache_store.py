"""
Cache Store Implementation for AI Talent Ecosystem
緩存存儲實現 - 用於提升系統性能
"""

import redis
import json
import pickle
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib


class RedisCache:
    """Redis緩存實現"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # 測試連接
            self.redis_client.ping()
            self.logger.info("Redis connection established successfully")
            self.connected = True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {str(e)}")
            self.connected = False
            # 使用內存緩存作為後備方案
            self.memory_cache = {}
            self.cache_expiry = {}
            self.logger.info("Using in-memory cache as fallback")
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """生成緩存鍵"""
        return f"talent_ai:{namespace}:{identifier}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """序列化數據"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)):
                return json.dumps(data, ensure_ascii=False).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            self.logger.error(f"Error serializing data: {str(e)}")
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """反序列化數據"""
        try:
            # 先嘗試JSON反序列化
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # 如果JSON失敗，嘗試pickle
                return pickle.loads(data)
            except Exception as e:
                self.logger.error(f"Error deserializing data: {str(e)}")
                return None
    
    async def set(self, namespace: str, key: str, value: Any, 
                  expiry_seconds: int = 3600) -> bool:
        """設置緩存值"""
        try:
            cache_key = self._generate_key(namespace, key)
            serialized_data = self._serialize_data(value)
            
            if self.connected:
                result = self.redis_client.setex(cache_key, expiry_seconds, serialized_data)
                return result
            else:
                # 使用內存緩存
                self.memory_cache[cache_key] = value
                self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=expiry_seconds)
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting cache {namespace}:{key}: {str(e)}")
            return False
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """獲取緩存值"""
        try:
            cache_key = self._generate_key(namespace, key)
            
            if self.connected:
                data = self.redis_client.get(cache_key)
                if data:
                    return self._deserialize_data(data)
                return None
            else:
                # 使用內存緩存
                if cache_key in self.memory_cache:
                    # 檢查過期時間
                    if cache_key in self.cache_expiry:
                        if datetime.now() > self.cache_expiry[cache_key]:
                            del self.memory_cache[cache_key]
                            del self.cache_expiry[cache_key]
                            return None
                    return self.memory_cache[cache_key]
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting cache {namespace}:{key}: {str(e)}")
            return None
    
    async def delete(self, namespace: str, key: str) -> bool:
        """刪除緩存值"""
        try:
            cache_key = self._generate_key(namespace, key)
            
            if self.connected:
                result = self.redis_client.delete(cache_key)
                return result > 0
            else:
                # 使用內存緩存
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    if cache_key in self.cache_expiry:
                        del self.cache_expiry[cache_key]
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting cache {namespace}:{key}: {str(e)}")
            return False
    
    async def exists(self, namespace: str, key: str) -> bool:
        """檢查緩存是否存在"""
        try:
            cache_key = self._generate_key(namespace, key)
            
            if self.connected:
                return self.redis_client.exists(cache_key) > 0
            else:
                return cache_key in self.memory_cache
                
        except Exception as e:
            self.logger.error(f"Error checking cache existence {namespace}:{key}: {str(e)}")
            return False
    
    async def set_hash(self, namespace: str, hash_key: str, 
                      field_values: Dict[str, Any], expiry_seconds: int = 3600) -> bool:
        """設置哈希緩存"""
        try:
            cache_key = self._generate_key(namespace, hash_key)
            
            if self.connected:
                # 序列化所有值
                serialized_values = {}
                for field, value in field_values.items():
                    serialized_values[field] = self._serialize_data(value)
                
                pipe = self.redis_client.pipeline()
                pipe.hset(cache_key, mapping=serialized_values)
                pipe.expire(cache_key, expiry_seconds)
                result = pipe.execute()
                return all(result)
            else:
                # 使用內存緩存
                if cache_key not in self.memory_cache:
                    self.memory_cache[cache_key] = {}
                self.memory_cache[cache_key].update(field_values)
                self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=expiry_seconds)
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting hash cache {namespace}:{hash_key}: {str(e)}")
            return False
    
    async def get_hash(self, namespace: str, hash_key: str, field: str) -> Optional[Any]:
        """獲取哈希緩存字段值"""
        try:
            cache_key = self._generate_key(namespace, hash_key)
            
            if self.connected:
                data = self.redis_client.hget(cache_key, field)
                if data:
                    return self._deserialize_data(data)
                return None
            else:
                # 使用內存緩存
                if cache_key in self.memory_cache and isinstance(self.memory_cache[cache_key], dict):
                    return self.memory_cache[cache_key].get(field)
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting hash cache {namespace}:{hash_key}:{field}: {str(e)}")
            return None
    
    async def get_all_hash(self, namespace: str, hash_key: str) -> Optional[Dict[str, Any]]:
        """獲取所有哈希緩存字段"""
        try:
            cache_key = self._generate_key(namespace, hash_key)
            
            if self.connected:
                data = self.redis_client.hgetall(cache_key)
                if data:
                    result = {}
                    for field, value in data.items():
                        field_str = field.decode('utf-8') if isinstance(field, bytes) else field
                        result[field_str] = self._deserialize_data(value)
                    return result
                return None
            else:
                # 使用內存緩存
                if cache_key in self.memory_cache and isinstance(self.memory_cache[cache_key], dict):
                    return self.memory_cache[cache_key].copy()
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting all hash cache {namespace}:{hash_key}: {str(e)}")
            return None
    
    async def cache_analysis_result(self, analysis_type: str, input_hash: str, 
                                  result: Dict[str, Any], expiry_hours: int = 24) -> bool:
        """緩存分析結果"""
        namespace = f"analysis:{analysis_type}"
        expiry_seconds = expiry_hours * 3600
        
        cache_data = {
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'input_hash': input_hash
        }
        
        return await self.set(namespace, input_hash, cache_data, expiry_seconds)
    
    async def get_cached_analysis(self, analysis_type: str, input_hash: str) -> Optional[Dict[str, Any]]:
        """獲取緩存的分析結果"""
        namespace = f"analysis:{analysis_type}"
        return await self.get(namespace, input_hash)
    
    def generate_input_hash(self, input_data: Dict[str, Any]) -> str:
        """生成輸入數據的哈希值"""
        # 創建輸入數據的標準化字符串表示
        normalized_data = json.dumps(input_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(normalized_data.encode('utf-8')).hexdigest()
    
    async def cache_employee_profile(self, employee_id: str, profile_data: Dict[str, Any]) -> bool:
        """緩存員工檔案"""
        return await self.set('employee_profiles', employee_id, profile_data, 7200)  # 2小時過期
    
    async def get_cached_employee_profile(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """獲取緩存的員工檔案"""
        return await self.get('employee_profiles', employee_id)
    
    async def cache_skill_recommendations(self, employee_id: str, 
                                        recommendations: List[Dict[str, Any]]) -> bool:
        """緩存技能推薦"""
        return await self.set('skill_recommendations', employee_id, recommendations, 3600)  # 1小時過期
    
    async def get_cached_skill_recommendations(self, employee_id: str) -> Optional[List[Dict[str, Any]]]:
        """獲取緩存的技能推薦"""
        return await self.get('skill_recommendations', employee_id)
    
    async def cache_team_analysis(self, team_id: str, analysis_data: Dict[str, Any]) -> bool:
        """緩存團隊分析"""
        return await self.set('team_analysis', team_id, analysis_data, 1800)  # 30分鐘過期
    
    async def get_cached_team_analysis(self, team_id: str) -> Optional[Dict[str, Any]]:
        """獲取緩存的團隊分析"""
        return await self.get('team_analysis', team_id)
    
    async def invalidate_employee_cache(self, employee_id: str) -> bool:
        """清除員工相關的所有緩存"""
        try:
            # 刪除相關的緩存項
            cache_patterns = [
                ('employee_profiles', employee_id),
                ('skill_recommendations', employee_id),
                ('analysis:brain', f'*{employee_id}*'),
                ('analysis:talent', f'*{employee_id}*')
            ]
            
            success_count = 0
            for namespace, key_pattern in cache_patterns:
                if '*' in key_pattern:
                    # 模式匹配刪除（簡化實現）
                    continue
                else:
                    if await self.delete(namespace, key_pattern):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error invalidating employee cache {employee_id}: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        try:
            if self.connected:
                info = self.redis_client.info()
                return {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'total_keys': self.redis_client.dbsize(),
                    'cache_hits': info.get('keyspace_hits', 0),
                    'cache_misses': info.get('keyspace_misses', 0),
                    'cache_type': 'redis'
                }
            else:
                # 內存緩存統計
                total_keys = len(self.memory_cache)
                expired_keys = sum(1 for key, expiry in self.cache_expiry.items() 
                                 if datetime.now() > expiry)
                
                return {
                    'total_keys': total_keys,
                    'expired_keys': expired_keys,
                    'active_keys': total_keys - expired_keys,
                    'cache_type': 'memory'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}
    
    async def clear_expired_cache(self) -> int:
        """清理過期的內存緩存（僅適用於內存緩存模式）"""
        if self.connected:
            return 0  # Redis自動處理過期
        
        try:
            expired_keys = []
            current_time = datetime.now()
            
            for key, expiry_time in self.cache_expiry.items():
                if current_time > expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                del self.cache_expiry[key]
            
            self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            return len(expired_keys)
            
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {str(e)}")
            return 0
    
    def close(self):
        """關閉緩存連接"""
        if self.connected and self.redis_client:
            self.redis_client.close()
            self.logger.info("Redis connection closed")