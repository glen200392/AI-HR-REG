#!/usr/bin/env python3
"""
HR智能知識助手 - 一鍵啟動腳本
"""

import subprocess
import sys
import os
import time
import signal
import logging
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HRAssistantLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_process = None
        self.frontend_process = None
        self.ollama_process = None
        
    def check_python_version(self):
        """檢查Python版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error("❌ 需要Python 3.8或更高版本")
            return False
        logger.info(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self):
        """檢查依賴是否安裝"""
        try:
            import fastapi
            import uvicorn
            import langchain
            logger.info("✅ 核心依賴已安裝")
            return True
        except ImportError as e:
            logger.error(f"❌ 缺少依賴: {e}")
            logger.info("請運行: pip install -r requirements.txt")
            return False
    
    def check_ollama(self):
        """檢查Ollama是否可用"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Ollama已安裝")
                return True
            else:
                logger.warning("⚠️ Ollama未安裝或未啟動")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("⚠️ Ollama未安裝")
            return False
    
    def start_ollama(self):
        """啟動Ollama服務"""
        if self.check_ollama():
            try:
                # 檢查Ollama是否已經在運行
                result = subprocess.run(['curl', '-s', 'http://localhost:11434/api/tags'],
                                     capture_output=True, timeout=2)
                if result.returncode == 0:
                    logger.info("✅ Ollama服務已運行")
                    return True
            except:
                pass
        
        try:
            logger.info("🚀 啟動Ollama服務...")
            self.ollama_process = subprocess.Popen(['ollama', 'serve'],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
            time.sleep(3)  # 等待服務啟動
            
            # 驗證服務是否啟動成功
            result = subprocess.run(['curl', '-s', 'http://localhost:11434/api/tags'],
                                 capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Ollama服務啟動成功")
                return True
            else:
                logger.error("❌ Ollama服務啟動失敗")
                return False
        except Exception as e:
            logger.error(f"❌ 無法啟動Ollama: {e}")
            return False
    
    def check_models(self):
        """檢查必要的模型是否已下載"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                 capture_output=True, text=True, timeout=10)
            if 'qwen2.5' in result.stdout:
                logger.info("✅ Qwen2.5模型已就緒")
                return True
            else:
                logger.warning("⚠️ 未找到Qwen2.5模型")
                self.download_models()
                return True
        except Exception as e:
            logger.error(f"❌ 檢查模型失敗: {e}")
            return False
    
    def download_models(self):
        """下載必要的模型"""
        logger.info("📥 正在下載Qwen2.5:7B模型 (這可能需要幾分鐘)...")
        try:
            subprocess.run(['ollama', 'pull', 'qwen2.5:7b'], check=True)
            logger.info("✅ 模型下載完成")
        except subprocess.CalledProcessError:
            logger.error("❌ 模型下載失敗")
            logger.info("您可以稍後手動運行: ollama pull qwen2.5:7b")
    
    def start_backend(self):
        """啟動後端服務"""
        try:
            logger.info("🚀 啟動後端API服務...")
            api_path = self.project_root / "api" / "rag_main.py"
            
            self.backend_process = subprocess.Popen([
                sys.executable, str(api_path)
            ], cwd=str(self.project_root))
            
            # 等待後端啟動
            time.sleep(5)
            
            # 檢查後端是否啟動成功
            try:
                import requests
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 後端服務啟動成功")
                    return True
            except:
                pass
            
            logger.info("⚠️ 後端服務啟動中，請稍候...")
            return True
            
        except Exception as e:
            logger.error(f"❌ 後端啟動失敗: {e}")
            return False
    
    def start_frontend(self):
        """啟動前端服務"""
        try:
            frontend_path = self.project_root / "hr-ai-platform" / "frontend"
            
            # 檢查是否已安裝Node.js依賴
            if not (frontend_path / "node_modules").exists():
                logger.info("📦 安裝前端依賴...")
                subprocess.run(['npm', 'install'], cwd=str(frontend_path), check=True)
            
            logger.info("🚀 啟動前端開發服務器...")
            self.frontend_process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], cwd=str(frontend_path))
            
            time.sleep(3)
            logger.info("✅ 前端服務啟動成功")
            logger.info("🌐 請訪問: http://localhost:5173")
            return True
            
        except Exception as e:
            logger.error(f"❌ 前端啟動失敗: {e}")
            logger.info("請確認已安裝Node.js和npm")
            return False
    
    def cleanup(self):
        """清理進程"""
        logger.info("🛑 正在關閉服務...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
        if self.backend_process:
            self.backend_process.terminate()
        if self.ollama_process:
            self.ollama_process.terminate()
        
        time.sleep(2)
        logger.info("✅ 服務已關閉")
    
    def run(self):
        """主運行函數"""
        logger.info("🚀 HR智能知識助手啟動中...")
        
        # 信號處理
        def signal_handler(sig, frame):
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # 檢查環境
            if not self.check_python_version():
                return False
            
            if not self.check_dependencies():
                return False
            
            # 啟動Ollama
            if not self.start_ollama():
                logger.warning("⚠️ Ollama啟動失敗，將使用降級模式")
            else:
                self.check_models()
            
            # 啟動後端
            if not self.start_backend():
                logger.error("❌ 後端啟動失敗")
                return False
            
            # 啟動前端
            if not self.start_frontend():
                logger.error("❌ 前端啟動失敗")
                return False
            
            logger.info("✅ 所有服務啟動完成！")
            logger.info("📱 應用URL: http://localhost:5173")
            logger.info("🔌 API文檔: http://localhost:8000/docs")
            logger.info("按 Ctrl+C 停止服務")
            
            # 保持運行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            logger.error(f"❌ 啟動失敗: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

if __name__ == "__main__":
    launcher = HRAssistantLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)