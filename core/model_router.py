from typing import Dict, Any, Optional, List
from .model_manager import MultiModelManager, ModelType
from loguru import logger
import asyncio
from datetime import datetime

class ModelRouter:
    """模型路由器"""
    
    def __init__(self, model_manager: MultiModelManager):
        self.model_manager = model_manager
        self.route_history: List[Dict[str, Any]] = []
        self.performance_cache: Dict[ModelType, Dict[str, float]] = {}
    
    async def route_query(self,
                         query: str,
                         task_type: str,
                         context: Optional[Dict[str, Any]] = None) -> ModelType:
        """根據查詢內容和上下文選擇合適的模型"""
        try:
            # 計算上下文長度
            context_length = self._calculate_context_length(context)
            
            # 獲取任務特徵
            task_features = await self._analyze_task(query, task_type)
            
            # 檢查性能緩存
            if self._should_use_cached_route(task_features):
                return self._get_cached_route(task_features)
            
            # 選擇最佳模型
            selected_model = await self.model_manager.select_best_model(
                task_type=task_type,
                context_length=context_length
            )
            
            # 記錄路由決策
            self._record_routing_decision(
                query=query,
                task_type=task_type,
                selected_model=selected_model,
                features=task_features
            )
            
            return selected_model
            
        except Exception as e:
            logger.error(f"模型路由失敗: {str(e)}")
            return ModelType.GPT35  # 默認回退到 GPT-3.5
    
    async def _analyze_task(self, query: str, task_type: str) -> Dict[str, Any]:
        """分析任務特徵"""
        return {
            "query_length": len(query),
            "task_type": task_type,
            "complexity": self._estimate_task_complexity(query),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_context_length(self, context: Optional[Dict[str, Any]]) -> int:
        """計算上下文長度"""
        if not context:
            return 0
            
        total_length = 0
        if "primary_context" in context:
            total_length += sum(len(str(item)) for item in context["primary_context"])
        if "secondary_context" in context:
            total_length += sum(len(str(item)) for item in context["secondary_context"])
            
        return total_length
    
    def _estimate_task_complexity(self, query: str) -> str:
        """估計任務複雜度"""
        # 基於關鍵詞和查詢長度評估複雜度
        complexity_keywords = {
            "high": ["比較", "分析", "評估", "建議", "優化", "設計"],
            "medium": ["說明", "描述", "列舉", "總結"],
            "low": ["是否", "什麼", "如何", "哪些"]
        }
        
        query_lower = query.lower()
        
        # 檢查複雜度關鍵詞
        for complexity, keywords in complexity_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return complexity
                
        # 基於查詢長度的後備評估
        if len(query) > 100:
            return "high"
        elif len(query) > 50:
            return "medium"
        return "low"
    
    def _should_use_cached_route(self, task_features: Dict[str, Any]) -> bool:
        """判斷是否使用緩存的路由決策"""
        # 檢查是否有相似的歷史任務
        for history in self.route_history[-10:]:  # 只檢查最近的10條記錄
            if (history["task_type"] == task_features["task_type"] and
                abs(history["features"]["complexity"] - task_features["complexity"]) < 0.2):
                return True
        return False
    
    def _get_cached_route(self, task_features: Dict[str, Any]) -> ModelType:
        """獲取緩存的路由決策"""
        # 從相似任務中選擇性能最好的模型
        similar_tasks = [
            h for h in self.route_history[-10:]
            if h["task_type"] == task_features["task_type"]
        ]
        
        if not similar_tasks:
            return ModelType.GPT35
            
        # 根據歷史性能選擇最佳模型
        best_model = max(
            similar_tasks,
            key=lambda x: x.get("performance_score", 0)
        )["selected_model"]
        
        return best_model
    
    def _record_routing_decision(self,
                               query: str,
                               task_type: str,
                               selected_model: ModelType,
                               features: Dict[str, Any]) -> None:
        """記錄路由決策"""
        self.route_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "task_type": task_type,
            "selected_model": selected_model,
            "features": features
        })
        
        # 保持歷史記錄在合理範圍內
        if len(self.route_history) > 1000:
            self.route_history = self.route_history[-1000:]
    
    async def update_performance_metrics(self,
                                      model_type: ModelType,
                                      metrics: Dict[str, float]) -> None:
        """更新模型性能指標"""
        self.performance_cache[model_type] = {
            **self.performance_cache.get(model_type, {}),
            **metrics,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """獲取路由統計信息"""
        stats = {
            "total_routes": len(self.route_history),
            "model_distribution": {},
            "task_type_distribution": {},
            "average_response_time": {}
        }
        
        for record in self.route_history:
            model = record["selected_model"]
            task_type = record["task_type"]
            
            # 更新模型分佈
            stats["model_distribution"][model] = stats["model_distribution"].get(model, 0) + 1
            
            # 更新任務類型分佈
            stats["task_type_distribution"][task_type] = stats["task_type_distribution"].get(task_type, 0) + 1
        
        return stats 