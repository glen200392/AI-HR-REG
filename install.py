#!/usr/bin/env python3
"""
HR智能知識助手 - 安裝腳本
"""

import subprocess
import sys
import os
import platform
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HRAssistantInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()
    
    def check_python(self):
        """檢查Python版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error("❌ 需要Python 3.8或更高版本")
            return False
        logger.info(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def install_python_deps(self):
        """安裝Python依賴"""
        try:
            logger.info("📦 安裝Python依賴...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, cwd=self.project_root)
            logger.info("✅ Python依賴安裝完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Python依賴安裝失敗: {e}")
            return False
    
    def check_node(self):
        """檢查Node.js"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Node.js版本: {version}")
                return True
        except FileNotFoundError:
            pass
        
        logger.error("❌ 未找到Node.js")
        logger.info("請安裝Node.js 16或更高版本: https://nodejs.org/")
        return False
    
    def install_frontend_deps(self):
        """安裝前端依賴"""
        try:
            frontend_path = self.project_root / "hr-ai-platform" / "frontend"
            if not frontend_path.exists():
                logger.error("❌ 前端目錄不存在")
                return False
            
            logger.info("📦 安裝前端依賴...")
            subprocess.run(['npm', 'install'], check=True, cwd=frontend_path)
            logger.info("✅ 前端依賴安裝完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 前端依賴安裝失敗: {e}")
            return False
    
    def install_ollama(self):
        """安裝Ollama"""
        try:
            # 檢查是否已安裝
            result = subprocess.run(['ollama', '--version'], capture_output=True)
            if result.returncode == 0:
                logger.info("✅ Ollama已安裝")
                return True
        except FileNotFoundError:
            pass
        
        logger.info("📥 正在安裝Ollama...")
        
        if self.system == "darwin":  # macOS
            try:
                subprocess.run(['brew', 'install', 'ollama'], check=True)
                logger.info("✅ Ollama安裝完成")
                return True
            except:
                logger.info("請手動安裝Ollama: https://ollama.ai/download")
                return False
        
        elif self.system == "linux":
            try:
                subprocess.run([
                    'curl', '-fsSL', 'https://ollama.ai/install.sh'
                ], check=True)
                logger.info("✅ Ollama安裝完成")
                return True
            except:
                logger.info("請手動安裝Ollama: https://ollama.ai/download")
                return False
        
        else:  # Windows
            logger.info("請手動下載並安裝Ollama: https://ollama.ai/download")
            return False
    
    def create_directories(self):
        """創建必要的目錄"""
        dirs = ['vector_store', 'temp_uploads', 'logs']
        for dir_name in dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"✅ 創建目錄: {dir_name}")
    
    def run(self):
        """運行安裝"""
        logger.info("🚀 開始安裝HR智能知識助手...")
        
        # 檢查Python
        if not self.check_python():
            return False
        
        # 創建目錄
        self.create_directories()
        
        # 安裝Python依賴
        if not self.install_python_deps():
            return False
        
        # 檢查Node.js
        if not self.check_node():
            logger.warning("⚠️ 跳過前端安裝")
        else:
            # 安裝前端依賴
            if not self.install_frontend_deps():
                logger.warning("⚠️ 前端安裝失敗")
        
        # 安裝Ollama
        if not self.install_ollama():
            logger.warning("⚠️ Ollama需要手動安裝")
        
        logger.info("✅ 安裝完成！")
        logger.info("🚀 運行 'python start.py' 來啟動應用")
        
        return True

if __name__ == "__main__":
    installer = HRAssistantInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)