#!/usr/bin/env python3
"""
硬體需求分析工具
分析不同LLM模型的硬體需求和成本
"""

import json
from typing import Dict, List

class HardwareAnalyzer:
    """硬體需求分析器"""
    
    def __init__(self):
        self.models = {
            "Llama2-7B": {
                "parameters": "7B",
                "model_size_gb": 13,
                "min_ram_gb": 16,
                "recommended_ram_gb": 32,
                "min_vram_gb": 8,
                "recommended_vram_gb": 16,
                "cpu_cores": 8,
                "storage_gb": 50,
                "inference_speed": "medium",
                "tokens_per_second": 15
            },
            "Llama2-13B": {
                "parameters": "13B", 
                "model_size_gb": 26,
                "min_ram_gb": 32,
                "recommended_ram_gb": 64,
                "min_vram_gb": 16,
                "recommended_vram_gb": 24,
                "cpu_cores": 16,
                "storage_gb": 100,
                "inference_speed": "medium-slow",
                "tokens_per_second": 10
            },
            "Mistral-7B": {
                "parameters": "7B",
                "model_size_gb": 14,
                "min_ram_gb": 16,
                "recommended_ram_gb": 32,
                "min_vram_gb": 8,
                "recommended_vram_gb": 16,
                "cpu_cores": 8,
                "storage_gb": 50,
                "inference_speed": "fast",
                "tokens_per_second": 20
            },
            "Qwen-14B": {
                "parameters": "14B",
                "model_size_gb": 28,
                "min_ram_gb": 32,
                "recommended_ram_gb": 64,
                "min_vram_gb": 16,
                "recommended_vram_gb": 32,
                "cpu_cores": 16,
                "storage_gb": 100,
                "inference_speed": "medium-slow", 
                "tokens_per_second": 8
            }
        }
        
        self.hardware_costs = {
            "cpu_server": {
                "name": "高階CPU伺服器",
                "specs": "32核心CPU, 64GB RAM, 1TB SSD",
                "cost_usd": 3000,
                "monthly_power": 150,
                "suitable_models": ["Llama2-7B", "Mistral-7B"]
            },
            "gpu_server_mid": {
                "name": "中階GPU伺服器", 
                "specs": "16核心CPU, 64GB RAM, RTX 4090 24GB",
                "cost_usd": 5000,
                "monthly_power": 400,
                "suitable_models": ["Llama2-13B", "Mistral-7B", "Llama2-7B"]
            },
            "gpu_server_high": {
                "name": "高階GPU伺服器",
                "specs": "32核心CPU, 128GB RAM, A100 80GB",
                "cost_usd": 15000,
                "monthly_power": 600,
                "suitable_models": ["Qwen-14B", "Llama2-13B", "All Models"]
            },
            "cloud_gpu": {
                "name": "雲端GPU實例",
                "specs": "A100 40GB (按時計費)",
                "cost_per_hour": 2.5,
                "monthly_cost_24x7": 1800,
                "suitable_models": ["All Models"]
            }
        }
    
    def analyze_model_requirements(self, model_name: str) -> Dict:
        """分析特定模型的硬體需求"""
        if model_name not in self.models:
            return {"error": f"Model {model_name} not found"}
        
        model = self.models[model_name]
        
        # 找出適合的硬體配置
        suitable_hardware = []
        for hw_name, hw_spec in self.hardware_costs.items():
            if model_name in hw_spec["suitable_models"] or "All Models" in hw_spec["suitable_models"]:
                suitable_hardware.append({
                    "name": hw_spec["name"],
                    "specs": hw_spec["specs"],
                    "initial_cost": hw_spec.get("cost_usd", 0),
                    "monthly_cost": hw_spec.get("monthly_power", hw_spec.get("monthly_cost_24x7", 0))
                })
        
        return {
            "model": model_name,
            "requirements": model,
            "suitable_hardware": suitable_hardware,
            "performance_estimate": self.estimate_performance(model)
        }
    
    def estimate_performance(self, model_spec: Dict) -> Dict:
        """估算性能表現"""
        return {
            "concurrent_users": max(1, model_spec["tokens_per_second"] // 5),
            "daily_analyses": model_spec["tokens_per_second"] * 60 * 60 * 8 // 100,  # 8小時工作時間
            "response_time_seconds": 100 / model_spec["tokens_per_second"],
            "scalability": "High" if model_spec["tokens_per_second"] > 15 else "Medium"
        }
    
    def compare_total_cost_of_ownership(self, years: int = 3) -> Dict:
        """比較總體擁有成本"""
        tco_analysis = {}
        
        for model_name in self.models.keys():
            model_analysis = self.analyze_model_requirements(model_name)
            
            if "error" in model_analysis:
                continue
            
            # 選擇最經濟的硬體配置
            best_hardware = min(
                model_analysis["suitable_hardware"], 
                key=lambda x: x["initial_cost"] + x["monthly_cost"] * 12 * years
            )
            
            # 計算TCO
            initial_cost = best_hardware["initial_cost"]
            operational_cost = best_hardware["monthly_cost"] * 12 * years
            maintenance_cost = initial_cost * 0.1 * years  # 10% annual maintenance
            
            total_cost = initial_cost + operational_cost + maintenance_cost
            
            tco_analysis[model_name] = {
                "hardware": best_hardware["name"],
                "initial_cost": initial_cost,
                "operational_cost": operational_cost, 
                "maintenance_cost": maintenance_cost,
                "total_cost": total_cost,
                "cost_per_analysis": total_cost / (model_analysis["performance_estimate"]["daily_analyses"] * 365 * years),
                "performance": model_analysis["performance_estimate"]
            }
        
        return tco_analysis
    
    def generate_recommendation(self) -> Dict:
        """生成硬體推薦"""
        tco = self.compare_total_cost_of_ownership()
        
        # 按不同標準排序
        by_cost = sorted(tco.items(), key=lambda x: x[1]["total_cost"])
        by_performance = sorted(tco.items(), key=lambda x: x[1]["performance"]["tokens_per_second"], reverse=True)
        by_efficiency = sorted(tco.items(), key=lambda x: x[1]["cost_per_analysis"])
        
        return {
            "most_cost_effective": by_cost[0],
            "best_performance": by_performance[0] if by_performance else None,
            "best_efficiency": by_efficiency[0],
            "detailed_comparison": tco
        }

def main():
    analyzer = HardwareAnalyzer()
    
    print("🔧 硬體需求分析報告")
    print("=" * 50)
    
    # 分析各模型需求
    for model in ["Llama2-7B", "Llama2-13B", "Mistral-7B", "Qwen-14B"]:
        print(f"\n📊 {model} 分析:")
        analysis = analyzer.analyze_model_requirements(model)
        
        if "error" not in analysis:
            req = analysis["requirements"]
            perf = analysis["performance_estimate"]
            
            print(f"  模型大小: {req['model_size_gb']}GB")
            print(f"  最小RAM: {req['min_ram_gb']}GB")
            print(f"  推薦RAM: {req['recommended_ram_gb']}GB")
            print(f"  推理速度: {req['tokens_per_second']} tokens/秒")
            print(f"  並發用戶: {perf['concurrent_users']} 人")
            print(f"  日分析量: {perf['daily_analyses']} 次")
    
    # TCO分析
    print(f"\n💰 3年總體擁有成本分析:")
    print("=" * 50)
    
    tco = analyzer.compare_total_cost_of_ownership(3)
    for model, cost_data in tco.items():
        print(f"\n{model}:")
        print(f"  硬體: {cost_data['hardware']}")
        print(f"  初始成本: ${cost_data['initial_cost']:,}")
        print(f"  營運成本: ${cost_data['operational_cost']:,}")
        print(f"  總成本: ${cost_data['total_cost']:,}")
        print(f"  每次分析成本: ${cost_data['cost_per_analysis']:.4f}")
    
    # 推薦方案
    print(f"\n🎯 推薦方案:")
    print("=" * 50)
    
    recommendation = analyzer.generate_recommendation()
    
    print(f"最具成本效益: {recommendation['most_cost_effective'][0]}")
    print(f"  總成本: ${recommendation['most_cost_effective'][1]['total_cost']:,}")
    
    if recommendation['best_performance']:
        print(f"最佳性能: {recommendation['best_performance'][0]}")
        print(f"  推理速度: {recommendation['best_performance'][1]['performance']['tokens_per_second']} tokens/秒")
    
    print(f"最高效率: {recommendation['best_efficiency'][0]}")
    print(f"  每次分析成本: ${recommendation['best_efficiency'][1]['cost_per_analysis']:.4f}")

if __name__ == "__main__":
    main()