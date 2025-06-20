from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from utils.visualization import PerformanceVisualizer
from core.model_manager import MultiModelManager
from core.model_router import ModelRouter
from typing import Dict, Any
from datetime import datetime
import os

router = APIRouter(prefix="/visualization", tags=["visualization"])
visualizer = PerformanceVisualizer()

@router.get("/performance-dashboard")
async def get_performance_dashboard(
    time_range: str = "24h",
    model_manager: MultiModelManager = None,
    save: bool = True
) -> Dict[str, Any]:
    """獲取性能儀表板"""
    try:
        if not model_manager:
            raise HTTPException(status_code=400, detail="Model manager not initialized")
            
        # 獲取性能數據
        performance_data = model_manager.get_model_performance_stats()
        
        # 生成儀表板
        svg_content = visualizer.create_model_performance_dashboard(
            performance_data,
            time_range
        )
        
        if save:
            # 保存 SVG 文件
            filename = f"performance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = visualizer.save_svg(svg_content, filename)
            
            return {
                "status": "success",
                "filepath": filepath,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "success",
                "svg_content": svg_content,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing-analysis")
async def get_routing_analysis(
    model_router: ModelRouter = None,
    save: bool = True
) -> Dict[str, Any]:
    """獲取路由分析可視化"""
    try:
        if not model_router:
            raise HTTPException(status_code=400, detail="Model router not initialized")
            
        # 獲取路由統計
        routing_stats = model_router.get_routing_statistics()
        
        # 生成可視化
        svg_content = visualizer.create_routing_visualization(routing_stats)
        
        if save:
            # 保存 SVG 文件
            filename = f"routing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = visualizer.save_svg(svg_content, filename)
            
            return {
                "status": "success",
                "filepath": filepath,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "success",
                "svg_content": svg_content,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/{filename}")
async def get_chart(filename: str):
    """獲取已保存的圖表"""
    filepath = f"static/charts/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Chart not found")
        
    return FileResponse(filepath) 