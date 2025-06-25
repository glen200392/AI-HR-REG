from typing import Dict, Any, Optional, List
from enum import Enum
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseLanguageModel
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    DEEPSEEK_R1 = "deepseek-r1"
    CUSTOM = "custom"

class ModelConfig:
    """模型配置類"""
    def __init__(self,
                 model_type: ModelType,
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 model_kwargs: Optional[Dict[str, Any]] = None):
        self.model_type = model_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_kwargs = model_kwargs or {}

class MultiModelManager:
    """多模型管理器"""
    
    def __init__(self):
        self.models: Dict[ModelType, BaseLanguageModel] = {}
        self.default_model_type = ModelType.GPT4
        self.model_configs: Dict[ModelType, ModelConfig] = {}
        self._initialize_default_configs()
        
    def _initialize_default_configs(self):
        """初始化默認配置"""
        self.model_configs = {
            ModelType.GPT4: ModelConfig(
                model_type=ModelType.GPT4,
                temperature=0.7,
                max_tokens=2000
            ),
            ModelType.GPT35: ModelConfig(
                model_type=ModelType.GPT35,
                temperature=0.8,
                max_tokens=2000
            ),
            ModelType.DEEPSEEK_R1: ModelConfig(
                model_type=ModelType.DEEPSEEK_R1,
                temperature=0.6,
                max_tokens=4000,
                model_kwargs={
                    "model_endpoint": os.getenv("DEEPSEEK_ENDPOINT"),
                    "api_key": os.getenv("DEEPSEEK_API_KEY")
                }
            )
        }
    
    async def initialize_models(self):
        """初始化所有模型"""
        try:
            # 初始化 GPT 模型
            self.models[ModelType.GPT4] = ChatOpenAI(
                model_name="gpt-4",
                temperature=self.model_configs[ModelType.GPT4].temperature,
                max_tokens=self.model_configs[ModelType.GPT4].max_tokens
            )
            
            self.models[ModelType.GPT35] = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=self.model_configs[ModelType.GPT35].temperature,
                max_tokens=self.model_configs[ModelType.GPT35].max_tokens
            )
            
            # 初始化 DeepSeek-R1
            self.models[ModelType.DEEPSEEK_R1] = await self._initialize_deepseek()
            
            logger.info("所有模型初始化完成")
        except Exception as e:
            logger.error(f"模型初始化失敗: {str(e)}")
            raise
    
    async def _initialize_deepseek(self) -> BaseLanguageModel:
        """初始化 DeepSeek-R1 模型"""
        try:
            from langchain.llms import DeepSeek
            
            config = self.model_configs[ModelType.DEEPSEEK_R1]
            return DeepSeek(
                model_name="deepseek-r1",
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                **config.model_kwargs
            )
        except Exception as e:
            logger.error(f"DeepSeek-R1 初始化失敗: {str(e)}")
            raise
    
    def get_model(self, model_type: Optional[ModelType] = None) -> BaseLanguageModel:
        """獲取指定類型的模型"""
        model_type = model_type or self.default_model_type
        if model_type not in self.models:
            raise ValueError(f"模型類型 {model_type} 未初始化")
        return self.models[model_type]
    
    def update_model_config(self,
                          model_type: ModelType,
                          config: ModelConfig) -> None:
        """更新模型配置"""
        self.model_configs[model_type] = config
        if model_type in self.models:
            # 重新初始化模型
            self._reinitialize_model(model_type)
    
    async def _reinitialize_model(self, model_type: ModelType):
        """重新初始化特定模型"""
        try:
            if model_type == ModelType.DEEPSEEK_R1:
                self.models[model_type] = await self._initialize_deepseek()
            else:
                config = self.model_configs[model_type]
                self.models[model_type] = ChatOpenAI(
                    model_name=model_type.value,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    **config.model_kwargs
                )
        except Exception as e:
            logger.error(f"重新初始化模型 {model_type} 失敗: {str(e)}")
            raise
    
    def get_model_performance_stats(self) -> Dict[ModelType, Dict[str, Any]]:
        """獲取模型性能統計"""
        return {
            model_type: {
                "total_requests": 0,  # TODO: 實現請求計數
                "average_latency": 0.0,  # TODO: 實現延遲統計
                "error_rate": 0.0,  # TODO: 實現錯誤率統計
                "token_usage": 0  # TODO: 實現 token 使用統計
            }
            for model_type in self.models.keys()
        }
    
    async def select_best_model(self,
                              task_type: str,
                              context_length: int) -> ModelType:
        """根據任務類型和上下文長度選擇最佳模型"""
        if task_type == "legal" and context_length > 3000:
            return ModelType.DEEPSEEK_R1
        elif task_type == "creative":
            return ModelType.GPT4
        else:
            return ModelType.GPT35 