"""
LLM Manager - 多模型管理器
支援開源和商業LLM的統一接口
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import os
from datetime import datetime

# LangChain imports
from langchain.schema import BaseLanguageModel

# Ollama imports
try:
    from langchain_community.llms import Ollama
    from langchain_community.embeddings import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    Ollama = None
    OllamaEmbeddings = None

# OpenAI imports
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None
    OpenAIEmbeddings = None

# HuggingFace imports
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    HuggingFaceEmbeddings = None


class LLMProvider(Enum):
    """LLM提供商類型"""
    OLLAMA = "ollama"          # 開源本地部署
    OPENAI = "openai"          # OpenAI API
    ANTHROPIC = "anthropic"    # Claude API


class EmbeddingProvider(Enum):
    """Embedding提供商類型"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.1
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60


@dataclass
class EmbeddingConfig:
    """Embedding配置"""
    provider: EmbeddingProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class LLMManager:
    """
    LLM管理器 - 統一管理多種語言模型
    
    支援的開源模型:
    - Qwen2.5:7B/14B/32B (推薦)
    - Llama3.1:8B/70B
    - Mistral:7B/22B
    
    支援的商業模型:
    - OpenAI GPT-4/GPT-3.5
    - Anthropic Claude-3
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_instances: Dict[str, BaseLanguageModel] = {}
        self.embedding_instances: Dict[str, Any] = {}
        self.current_llm: Optional[BaseLanguageModel] = None
        self.current_embedding: Optional[Any] = None
        
        # 預設配置
        self.default_configs = self._get_default_configs()
        
    def _get_default_configs(self) -> Dict[str, Any]:
        """獲取預設配置"""
        return {
            "llm_configs": [
                # 開源模型配置 (主力)
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2.5:14b",  # 推薦模型
                    temperature=0.1,
                    max_tokens=2000,
                    base_url="http://localhost:11434"
                ),
                LLMConfig(
                    provider=LLMProvider.OLLAMA,
                    model_name="qwen2.5:7b",   # 備用輕量模型
                    temperature=0.1,
                    max_tokens=1500,
                    base_url="http://localhost:11434"
                ),
                # 商業模型配置 (備用)
                LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model_name="gpt-4o-mini",
                    temperature=0.1,
                    max_tokens=1000,
                    api_key=os.getenv("OPENAI_API_KEY")
                ),
            ],
            "embedding_configs": [
                # 開源Embedding (主力)
                EmbeddingConfig(
                    provider=EmbeddingProvider.OLLAMA,
                    model_name="nomic-embed-text",
                    base_url="http://localhost:11434"
                ),
                # HuggingFace本地Embedding (備用)
                EmbeddingConfig(
                    provider=EmbeddingProvider.HUGGINGFACE,
                    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                ),
                # 商業Embedding (可選)
                EmbeddingConfig(
                    provider=EmbeddingProvider.OPENAI,
                    model_name="text-embedding-3-small",
                    api_key=os.getenv("OPENAI_API_KEY")
                ),
            ]
        }
    
    async def initialize(self, 
                        preferred_llm: str = "qwen2.5:14b",
                        preferred_embedding: str = "nomic-embed-text") -> bool:
        """
        初始化LLM管理器
        
        Args:
            preferred_llm: 首選LLM模型
            preferred_embedding: 首選Embedding模型
            
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 初始化LLM模型
            llm_success = await self._initialize_llms(preferred_llm)
            
            # 初始化Embedding模型
            embedding_success = await self._initialize_embeddings(preferred_embedding)
            
            if llm_success and embedding_success:
                self.logger.info("LLM Manager initialized successfully")
                return True
            else:
                self.logger.warning("LLM Manager partially initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM Manager: {e}")
            return False
    
    async def _initialize_llms(self, preferred_model: str) -> bool:
        """初始化LLM模型"""
        llm_configs = self.default_configs["llm_configs"]
        
        # 嘗試初始化首選模型
        for config in llm_configs:
            if config.model_name == preferred_model:
                llm = await self._create_llm(config)
                if llm:
                    self.llm_instances[config.model_name] = llm
                    self.current_llm = llm
                    self.logger.info(f"✅ Primary LLM loaded: {config.model_name}")
                    break
        
        # 初始化備用模型
        for config in llm_configs:
            if config.model_name != preferred_model:
                llm = await self._create_llm(config)
                if llm:
                    self.llm_instances[config.model_name] = llm
                    if not self.current_llm:  # 如果首選模型失敗，使用第一個可用的
                        self.current_llm = llm
                    self.logger.info(f"✅ Backup LLM loaded: {config.model_name}")
        
        return len(self.llm_instances) > 0
    
    async def _initialize_embeddings(self, preferred_model: str) -> bool:
        """初始化Embedding模型"""
        embedding_configs = self.default_configs["embedding_configs"]
        
        # 嘗試初始化首選模型
        for config in embedding_configs:
            if config.model_name == preferred_model:
                embedding = await self._create_embedding(config)
                if embedding:
                    self.embedding_instances[config.model_name] = embedding
                    self.current_embedding = embedding
                    self.logger.info(f"✅ Primary Embedding loaded: {config.model_name}")
                    break
        
        # 初始化備用模型
        for config in embedding_configs:
            if config.model_name != preferred_model:
                embedding = await self._create_embedding(config)
                if embedding:
                    self.embedding_instances[config.model_name] = embedding
                    if not self.current_embedding:  # 如果首選模型失敗
                        self.current_embedding = embedding
                    self.logger.info(f"✅ Backup Embedding loaded: {config.model_name}")
        
        return len(self.embedding_instances) > 0
    
    async def _create_llm(self, config: LLMConfig) -> Optional[BaseLanguageModel]:
        """創建LLM實例"""
        try:
            if config.provider == LLMProvider.OLLAMA:
                # 檢查Ollama服務是否可用
                if not await self._check_ollama_health(config.base_url):
                    self.logger.warning(f"Ollama service not available at {config.base_url}")
                    return None
                
                llm = Ollama(
                    model=config.model_name,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    timeout=config.timeout,
                    num_predict=config.max_tokens
                )
                
                # 測試模型可用性
                try:
                    response = llm.invoke("測試")
                    if response:
                        return llm
                except Exception as e:
                    self.logger.warning(f"Ollama model {config.model_name} test failed: {e}")
                    return None
                    
            elif config.provider == LLMProvider.OPENAI:
                if not config.api_key:
                    self.logger.warning("OpenAI API key not provided")
                    return None
                
                llm = ChatOpenAI(
                    model=config.model_name,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
                return llm
                
        except Exception as e:
            self.logger.error(f"Failed to create LLM {config.model_name}: {e}")
            return None
    
    async def _create_embedding(self, config: EmbeddingConfig) -> Optional[Any]:
        """創建Embedding實例"""
        try:
            if config.provider == EmbeddingProvider.OLLAMA:
                if not await self._check_ollama_health(config.base_url):
                    return None
                
                embedding = OllamaEmbeddings(
                    model=config.model_name,
                    base_url=config.base_url
                )
                
                # 測試embedding可用性
                try:
                    test_result = embedding.embed_query("測試")
                    if test_result:
                        return embedding
                except Exception as e:
                    self.logger.warning(f"Ollama embedding {config.model_name} test failed: {e}")
                    return None
                    
            elif config.provider == EmbeddingProvider.HUGGINGFACE:
                embedding = HuggingFaceEmbeddings(
                    model_name=config.model_name,
                    cache_folder="./models"  # 本地快取
                )
                return embedding
                
            elif config.provider == EmbeddingProvider.OPENAI:
                if not config.api_key:
                    return None
                
                embedding = OpenAIEmbeddings(
                    model=config.model_name,
                    api_key=config.api_key
                )
                return embedding
                
        except Exception as e:
            self.logger.error(f"Failed to create Embedding {config.model_name}: {e}")
            return None
    
    async def _check_ollama_health(self, base_url: str) -> bool:
        """檢查Ollama服務健康狀態"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/api/tags", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def invoke_with_fallback(self, prompt: str, timeout: int = 30) -> str:
        """
        智能調用LLM，自動容錯降級
        
        Args:
            prompt: 輸入提示
            timeout: 超時時間（秒）
            
        Returns:
            str: LLM回應
        """
        # 按優先級嘗試所有可用的LLM
        llm_priority = [
            "qwen2.5:14b",    # 主力模型
            "qwen2.5:7b",     # 輕量備用
            "gpt-4o-mini",    # 商業後備
            "gpt-3.5-turbo"   # 最後選擇
        ]
        
        for model_name in llm_priority:
            if model_name in self.llm_instances:
                try:
                    start_time = datetime.now()
                    llm = self.llm_instances[model_name]
                    
                    # 嘗試調用
                    if hasattr(llm, 'ainvoke'):
                        response = await asyncio.wait_for(
                            llm.ainvoke(prompt), 
                            timeout=timeout
                        )
                    else:
                        response = await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, llm.invoke, prompt
                            ),
                            timeout=timeout
                        )
                    
                    # 計算響應時間
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    # 記錄成功
                    self.current_llm = llm
                    self.logger.info(
                        f"✅ LLM {model_name} responded in {response_time:.2f}s"
                    )
                    
                    return response.content if hasattr(response, 'content') else str(response)
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"⏰ LLM {model_name} timed out, trying next...")
                    continue
                except Exception as e:
                    self.logger.warning(f"❌ LLM {model_name} failed: {e}, trying next...")
                    continue
        
        # 如果所有模型都失敗
        raise Exception("所有LLM模型都不可用，請檢查配置或網路連接")
    
    async def check_all_models_health(self) -> Dict[str, Any]:
        """檢查所有模型的健康狀態"""
        health_status = {}
        
        for model_name, llm in self.llm_instances.items():
            try:
                start_time = datetime.now()
                test_prompt = "你好，這是一個測試。請回答：OK"
                
                if hasattr(llm, 'ainvoke'):
                    response = await asyncio.wait_for(llm.ainvoke(test_prompt), timeout=10)
                else:
                    response = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, llm.invoke, test_prompt
                        ),
                        timeout=10
                    )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                health_status[model_name] = {
                    "status": "healthy",
                    "response_time": response_time,
                    "last_check": datetime.now().isoformat(),
                    "provider": "ollama" if "qwen" in model_name or "llama" in model_name else "api"
                }
                
            except Exception as e:
                health_status[model_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now().isoformat(),
                    "provider": "ollama" if "qwen" in model_name or "llama" in model_name else "api"
                }
        
        return health_status
    
    def get_available_llms(self) -> List[str]:
        """獲取可用的LLM列表"""
        return list(self.llm_instances.keys())
    
    def get_available_embeddings(self) -> List[str]:
        """獲取可用的Embedding列表"""
        return list(self.embedding_instances.keys())
    
    def switch_llm(self, model_name: str) -> bool:
        """切換LLM模型"""
        if model_name in self.llm_instances:
            self.current_llm = self.llm_instances[model_name]
            self.logger.info(f"Switched to LLM: {model_name}")
            return True
        return False
    
    def switch_embedding(self, model_name: str) -> bool:
        """切換Embedding模型"""
        if model_name in self.embedding_instances:
            self.current_embedding = self.embedding_instances[model_name]
            self.logger.info(f"Switched to Embedding: {model_name}")
            return True
        return False
    
    def get_current_llm(self) -> Optional[BaseLanguageModel]:
        """獲取當前LLM"""
        return self.current_llm
    
    def get_current_embedding(self) -> Optional[Any]:
        """獲取當前Embedding"""
        return self.current_embedding
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            "available_llms": self.get_available_llms(),
            "available_embeddings": self.get_available_embeddings(),
            "current_llm": getattr(self.current_llm, "model", "None") if self.current_llm else "None",
            "current_embedding": getattr(self.current_embedding, "model", "None") if self.current_embedding else "None",
            "total_llm_instances": len(self.llm_instances),
            "total_embedding_instances": len(self.embedding_instances),
            "last_update": datetime.now().isoformat()
        }


# 全域LLM管理器實例
llm_manager = LLMManager()