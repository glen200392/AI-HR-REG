"""
Monitoring and Metrics Middleware
監控和指標中間件
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, Response
import logging
import psutil
import threading
import json
from dataclasses import dataclass, asdict

from config.settings import get_settings


@dataclass
class RequestMetric:
    """請求指標"""
    timestamp: datetime
    method: str
    path: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class SystemMetric:
    """系統指標"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    queue_size: int


@dataclass
class AgentMetric:
    """代理指標"""
    timestamp: datetime
    agent_name: str
    operation: str
    duration: float
    success: bool
    error_message: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class MetricsCollector:
    """指標收集器"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.request_metrics: deque = deque(maxlen=max_metrics)
        self.system_metrics: deque = deque(maxlen=max_metrics)
        self.agent_metrics: deque = deque(maxlen=max_metrics)
        
        # 實時統計
        self.stats = {
            'total_requests': 0,
            'error_count': 0,
            'avg_response_time': 0.0,
            'requests_per_second': 0.0,
            'active_users': set(),
            'endpoint_stats': defaultdict(lambda: {
                'count': 0, 'avg_time': 0.0, 'errors': 0
            })
        }
        
        self.logger = logging.getLogger(__name__)
        self._lock = asyncio.Lock()
        self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """啟動系統監控"""
        def collect_system_metrics():
            while True:
                try:
                    metric = SystemMetric(
                        timestamp=datetime.now(),
                        cpu_usage=psutil.cpu_percent(interval=1),
                        memory_usage=psutil.virtual_memory().percent,
                        disk_usage=psutil.disk_usage('/').percent,
                        active_connections=len(psutil.net_connections()),
                        queue_size=0  # 需要從應用層獲取
                    )
                    
                    asyncio.run(self.add_system_metric(metric))
                    time.sleep(60)  # 每分鐘收集一次
                    
                except Exception as e:
                    self.logger.error(f"Error collecting system metrics: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
    
    async def add_request_metric(self, metric: RequestMetric):
        """添加請求指標"""
        async with self._lock:
            self.request_metrics.append(metric)
            
            # 更新統計
            self.stats['total_requests'] += 1
            
            if metric.status_code >= 400:
                self.stats['error_count'] += 1
            
            if metric.user_id:
                self.stats['active_users'].add(metric.user_id)
            
            # 更新端點統計
            endpoint = f"{metric.method} {metric.path}"
            endpoint_stat = self.stats['endpoint_stats'][endpoint]
            
            # 計算移動平均響應時間
            old_avg = endpoint_stat['avg_time']
            old_count = endpoint_stat['count']
            new_count = old_count + 1
            new_avg = (old_avg * old_count + metric.response_time) / new_count
            
            endpoint_stat.update({
                'count': new_count,
                'avg_time': new_avg,
                'errors': endpoint_stat['errors'] + (1 if metric.status_code >= 400 else 0)
            })
            
            # 計算總體平均響應時間
            if self.request_metrics:
                total_time = sum(m.response_time for m in list(self.request_metrics)[-1000:])
                count = min(1000, len(self.request_metrics))
                self.stats['avg_response_time'] = total_time / count
    
    async def add_system_metric(self, metric: SystemMetric):
        """添加系統指標"""
        async with self._lock:
            self.system_metrics.append(metric)
    
    async def add_agent_metric(self, metric: AgentMetric):
        """添加代理指標"""
        async with self._lock:
            self.agent_metrics.append(metric)
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """獲取統計摘要"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # 計算最近一小時的請求數
        recent_requests = [
            m for m in self.request_metrics 
            if m.timestamp > hour_ago
        ]
        
        requests_per_hour = len(recent_requests)
        requests_per_second = requests_per_hour / 3600 if requests_per_hour > 0 else 0
        
        # 計算錯誤率
        recent_errors = sum(1 for m in recent_requests if m.status_code >= 400)
        error_rate = (recent_errors / len(recent_requests)) * 100 if recent_requests else 0
        
        # 獲取最新系統指標
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        
        return {
            'overview': {
                'total_requests': self.stats['total_requests'],
                'requests_per_second': requests_per_second,
                'avg_response_time': round(self.stats['avg_response_time'], 3),
                'error_rate': round(error_rate, 2),
                'active_users_count': len(self.stats['active_users'])
            },
            'system': {
                'cpu_usage': latest_system.cpu_usage if latest_system else 0,
                'memory_usage': latest_system.memory_usage if latest_system else 0,
                'disk_usage': latest_system.disk_usage if latest_system else 0,
                'active_connections': latest_system.active_connections if latest_system else 0
            },
            'top_endpoints': self._get_top_endpoints(),
            'recent_errors': self._get_recent_errors(),
            'timestamp': now.isoformat()
        }
    
    def _get_top_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取熱門端點"""
        endpoints = []
        for endpoint, stats in self.stats['endpoint_stats'].items():
            endpoints.append({
                'endpoint': endpoint,
                'count': stats['count'],
                'avg_response_time': round(stats['avg_time'], 3),
                'error_rate': round((stats['errors'] / stats['count']) * 100, 2) if stats['count'] > 0 else 0
            })
        
        return sorted(endpoints, key=lambda x: x['count'], reverse=True)[:limit]
    
    def _get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近錯誤"""
        errors = []
        for metric in reversed(list(self.request_metrics)):
            if metric.status_code >= 400:
                errors.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'method': metric.method,
                    'path': metric.path,
                    'status_code': metric.status_code,
                    'response_time': metric.response_time,
                    'user_id': metric.user_id,
                    'ip_address': metric.ip_address
                })
                
                if len(errors) >= limit:
                    break
        
        return errors
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """獲取代理性能統計"""
        agent_stats = defaultdict(lambda: {
            'total_calls': 0,
            'success_count': 0,
            'error_count': 0,
            'avg_duration': 0.0,
            'total_tokens': 0
        })
        
        for metric in self.agent_metrics:
            stats = agent_stats[metric.agent_name]
            stats['total_calls'] += 1
            
            if metric.success:
                stats['success_count'] += 1
            else:
                stats['error_count'] += 1
            
            # 計算平均持續時間
            old_avg = stats['avg_duration']
            old_count = stats['total_calls'] - 1
            new_avg = (old_avg * old_count + metric.duration) / stats['total_calls'] if stats['total_calls'] > 0 else 0
            stats['avg_duration'] = new_avg
            
            # 統計令牌使用
            if metric.input_tokens:
                stats['total_tokens'] += metric.input_tokens
            if metric.output_tokens:
                stats['total_tokens'] += metric.output_tokens
        
        # 計算成功率
        for agent_name, stats in agent_stats.items():
            stats['success_rate'] = (stats['success_count'] / stats['total_calls']) * 100 if stats['total_calls'] > 0 else 0
            stats['avg_duration'] = round(stats['avg_duration'], 3)
        
        return dict(agent_stats)
    
    def export_metrics(self, format: str = 'json') -> str:
        """導出指標數據"""
        if format == 'json':
            data = {
                'request_metrics': [asdict(m) for m in self.request_metrics],
                'system_metrics': [asdict(m) for m in self.system_metrics],
                'agent_metrics': [asdict(m) for m in self.agent_metrics],
                'stats_summary': self.get_stats_summary(),
                'export_timestamp': datetime.now().isoformat()
            }
            return json.dumps(data, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


class HealthChecker:
    """健康檢查器"""
    
    def __init__(self):
        self.checks = {}
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: Callable[[], bool]):
        """註冊健康檢查"""
        self.checks[name] = check_func
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """運行健康檢查"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'checked_at': datetime.now().isoformat()
                }
                
                if not result:
                    overall_healthy = False
                    
            except Exception as e:
                self.logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'checked_at': datetime.now().isoformat()
                }
                overall_healthy = False
        
        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alert_rules = []
        self.active_alerts = {}
        self.logger = logging.getLogger(__name__)
    
    def add_alert_rule(self, name: str, condition: Callable[[Dict[str, Any]], bool], message: str):
        """添加告警規則"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'message': message
        })
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """檢查告警條件"""
        for rule in self.alert_rules:
            try:
                if rule['condition'](metrics):
                    await self._trigger_alert(rule['name'], rule['message'], metrics)
                else:
                    await self._resolve_alert(rule['name'])
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule['name']}: {e}")
    
    async def _trigger_alert(self, name: str, message: str, metrics: Dict[str, Any]):
        """觸發告警"""
        if name not in self.active_alerts:
            self.active_alerts[name] = {
                'triggered_at': datetime.now(),
                'message': message,
                'metrics': metrics
            }
            
            self.logger.warning(f"ALERT TRIGGERED: {name} - {message}")
            # 這裡可以集成郵件、Slack等通知系統
    
    async def _resolve_alert(self, name: str):
        """解決告警"""
        if name in self.active_alerts:
            resolved_at = datetime.now()
            duration = resolved_at - self.active_alerts[name]['triggered_at']
            
            self.logger.info(f"ALERT RESOLVED: {name} - Duration: {duration}")
            del self.active_alerts[name]


class MonitoringMiddleware:
    """監控中間件"""
    
    def __init__(self):
        self.settings = get_settings()
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self.alert_manager = AlertManager()
        self.logger = logging.getLogger(__name__)
        
        self._setup_default_checks()
        self._setup_default_alerts()
    
    def _setup_default_checks(self):
        """設置默認健康檢查"""
        
        def check_disk_space():
            """檢查磁盤空間"""
            return psutil.disk_usage('/').percent < 90
        
        def check_memory():
            """檢查內存使用"""
            return psutil.virtual_memory().percent < 85
        
        def check_cpu():
            """檢查CPU使用"""
            return psutil.cpu_percent(interval=1) < 80
        
        self.health_checker.register_check('disk_space', check_disk_space)
        self.health_checker.register_check('memory', check_memory)
        self.health_checker.register_check('cpu', check_cpu)
    
    def _setup_default_alerts(self):
        """設置默認告警規則"""
        
        # 錯誤率告警
        self.alert_manager.add_alert_rule(
            'high_error_rate',
            lambda m: m['overview']['error_rate'] > 10,
            'Error rate is above 10%'
        )
        
        # 響應時間告警
        self.alert_manager.add_alert_rule(
            'slow_response',
            lambda m: m['overview']['avg_response_time'] > 5.0,
            'Average response time is above 5 seconds'
        )
        
        # 系統資源告警
        self.alert_manager.add_alert_rule(
            'high_cpu_usage',
            lambda m: m['system']['cpu_usage'] > 80,
            'CPU usage is above 80%'
        )
        
        self.alert_manager.add_alert_rule(
            'high_memory_usage',
            lambda m: m['system']['memory_usage'] > 85,
            'Memory usage is above 85%'
        )
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """中間件調用"""
        start_time = time.time()
        
        # 獲取請求信息
        request_size = int(request.headers.get('content-length', 0))
        user = getattr(request.state, 'user', None)
        user_id = user.get('user_id') if user else None
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', '')
        
        try:
            # 處理請求
            response = await call_next(request)
            
            # 計算響應時間
            response_time = time.time() - start_time
            
            # 獲取響應大小
            response_size = 0
            if hasattr(response, 'body'):
                response_size = len(response.body) if response.body else 0
            
            # 記錄請求指標
            metric = RequestMetric(
                timestamp=datetime.now(),
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            await self.metrics_collector.add_request_metric(metric)
            
            # 添加監控頭部
            response.headers['X-Response-Time'] = f"{response_time:.3f}"
            response.headers['X-Request-ID'] = getattr(request.state, 'request_id', 'unknown')
            
            return response
            
        except Exception as e:
            # 記錄錯誤請求
            response_time = time.time() - start_time
            
            metric = RequestMetric(
                timestamp=datetime.now(),
                method=request.method,
                path=request.url.path,
                status_code=500,
                response_time=response_time,
                request_size=request_size,
                response_size=0,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            await self.metrics_collector.add_request_metric(metric)
            
            # 重新拋出異常
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """獲取客戶端IP"""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'
    
    async def get_metrics(self) -> Dict[str, Any]:
        """獲取指標數據"""
        stats = self.metrics_collector.get_stats_summary()
        
        # 檢查告警
        await self.alert_manager.check_alerts(stats)
        
        return {
            **stats,
            'agent_performance': self.metrics_collector.get_agent_performance(),
            'active_alerts': self.alert_manager.active_alerts
        }
    
    async def get_health(self) -> Dict[str, Any]:
        """獲取健康狀態"""
        return await self.health_checker.run_health_checks()


# 全局監控中間件實例
_monitoring_middleware = None


def get_monitoring_middleware() -> MonitoringMiddleware:
    """獲取監控中間件實例"""
    global _monitoring_middleware
    
    if _monitoring_middleware is None:
        _monitoring_middleware = MonitoringMiddleware()
    
    return _monitoring_middleware


async def record_agent_metric(
    agent_name: str,
    operation: str,
    duration: float,
    success: bool,
    error_message: Optional[str] = None,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None
):
    """記錄代理指標"""
    middleware = get_monitoring_middleware()
    
    metric = AgentMetric(
        timestamp=datetime.now(),
        agent_name=agent_name,
        operation=operation,
        duration=duration,
        success=success,
        error_message=error_message,
        input_tokens=input_tokens,
        output_tokens=output_tokens
    )
    
    await middleware.metrics_collector.add_agent_metric(metric)