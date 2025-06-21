#!/usr/bin/env python3
"""
高質量HR AI助手 - 專注於內容質量和多LLM支持
Quality-First HR AI Assistant with Multi-LLM Support
"""

import json
import os
import sys
import argparse
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class LLMProvider(Enum):
    """LLM提供商"""
    OPENAI = "openai"
    OLLAMA = "ollama" 
    CLAUDE = "claude"
    GROQ = "groq"

@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000

class HighQualityLLMClient:
    """高質量LLM客戶端，支持多個提供商"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """設置LLM客戶端"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self._setup_openai()
            elif self.config.provider == LLMProvider.OLLAMA:
                self._setup_ollama()
            elif self.config.provider == LLMProvider.CLAUDE:
                self._setup_claude()
            elif self.config.provider == LLMProvider.GROQ:
                self._setup_groq()
        except Exception as e:
            self.logger.warning(f"Failed to setup {self.config.provider.value}: {e}")
            self.client = None
    
    def _setup_openai(self):
        """設置OpenAI客戶端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.config.api_key)
            self.logger.info("OpenAI client initialized successfully")
        except ImportError:
            self.logger.error("OpenAI library not installed. Install with: pip install openai")
    
    def _setup_ollama(self):
        """設置Ollama客戶端"""
        try:
            import requests
            base_url = self.config.base_url or "http://localhost:11434"
            # 測試Ollama連接
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.client = "ollama"  # 簡化標記
                self.logger.info("Ollama client initialized successfully")
            else:
                raise Exception("Ollama server not responding")
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
    
    def _setup_claude(self):
        """設置Claude客戶端"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
            self.logger.info("Claude client initialized successfully")
        except ImportError:
            self.logger.error("Anthropic library not installed. Install with: pip install anthropic")
    
    def _setup_groq(self):
        """設置Groq客戶端"""
        try:
            from groq import Groq
            self.client = Groq(api_key=self.config.api_key)
            self.logger.info("Groq client initialized successfully")
        except ImportError:
            self.logger.error("Groq library not installed. Install with: pip install groq")
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """生成回應"""
        if not self.client:
            return self._fallback_response(prompt)
        
        try:
            if self.config.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt, system_prompt)
            elif self.config.provider == LLMProvider.OLLAMA:
                return self._generate_ollama(prompt, system_prompt)
            elif self.config.provider == LLMProvider.CLAUDE:
                return self._generate_claude(prompt, system_prompt)
            elif self.config.provider == LLMProvider.GROQ:
                return self._generate_groq(prompt, system_prompt)
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return self._fallback_response(prompt)
    
    def _generate_openai(self, prompt: str, system_prompt: str) -> str:
        """OpenAI生成"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt: str, system_prompt: str) -> str:
        """Ollama生成"""
        import requests
        
        base_url = self.config.base_url or "http://localhost:11434"
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "model": self.config.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama request failed: {response.status_code}")
    
    def _generate_claude(self, prompt: str, system_prompt: str) -> str:
        """Claude生成"""
        message = self.client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _generate_groq(self, prompt: str, system_prompt: str) -> str:
        """Groq生成"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        return response.choices[0].message.content
    
    def _fallback_response(self, prompt: str) -> str:
        """備用響應"""
        return """基於您提供的信息，我建議進行以下分析：

**專業評估**：
根據現有資料，該員工/團隊展現出良好的基本素質和發展潛力。

**關鍵建議**：
1. 定期進行技能評估和培訓需求分析
2. 建立清晰的職業發展路徑
3. 加強團隊溝通和協作機制
4. 設定可衡量的績效指標

**後續行動**：
建議安排一對一面談，深入了解個人職業目標，並制定具體的發展計劃。

注意：此為系統備用回應，建議配置適當的LLM以獲得更精確的分析。"""

class HRPromptTemplates:
    """HR專業提示模板"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """獲取系統提示"""
        return """你是一位資深的人力資源專家和組織發展顧問，具有以下專業背景：

**專業資格**：
- 15年以上HR管理經驗
- 組織心理學專業背景
- SHRM-SCP認證
- 熟悉台灣和國際HR最佳實務

**分析能力**：
- 人才評估和發展規劃
- 團隊動態和組織文化分析
- 績效管理和職業發展諮詢
- 基於數據的HR決策支持

**回應要求**：
- 提供專業、實用且具體的建議
- 使用繁體中文專業術語
- 結構化呈現分析結果
- 包含可執行的行動方案
- 考慮台灣職場文化和法規環境

請始終保持專業、客觀且富有建設性的分析態度。"""
    
    @staticmethod
    def employee_analysis_prompt(employee_data: Dict[str, Any]) -> str:
        """員工分析提示"""
        return f"""請對以下員工進行全面的人才分析：

**員工基本資料**：
{json.dumps(employee_data, ensure_ascii=False, indent=2)}

**分析要求**：

1. **人才特質評估**
   - 核心優勢和專長分析
   - 性格特質和工作風格評估
   - 學習能力和適應性分析

2. **技能和能力評估**
   - 專業技能水平評估
   - 軟技能能力分析
   - 技能缺口識別

3. **職業發展建議**
   - 短期發展目標（6-12個月）
   - 中期職業規劃（1-3年）
   - 長期職涯發展路徑

4. **具體行動計劃**
   - 技能提升建議
   - 培訓課程推薦
   - 職務輪調機會
   - 導師配對建議

5. **風險評估**
   - 離職風險評估
   - 績效改善建議
   - 激勵因素分析

請提供詳細、專業且可執行的分析報告。"""
    
    @staticmethod
    def team_analysis_prompt(team_data: Dict[str, Any]) -> str:
        """團隊分析提示"""
        return f"""請對以下團隊進行深度的組織動態分析：

**團隊基本資料**：
{json.dumps(team_data, ensure_ascii=False, indent=2)}

**分析要求**：

1. **團隊結構分析**
   - 團隊組成和角色分工
   - 技能分布和互補性
   - 經驗層次和多樣性

2. **協作效能評估**
   - 溝通模式和效率
   - 決策流程和速度
   - 衝突處理機制

3. **文化和氛圍分析**
   - 團隊文化特徵
   - 工作氛圍評估
   - 價值觀一致性

4. **績效和生產力**
   - 團隊績效指標
   - 生產力瓶頸分析
   - 改善機會識別

5. **發展建議**
   - 團隊建設活動
   - 流程優化建議
   - 人才配置調整
   - 培訓發展計劃

6. **風險管控**
   - 團隊風險評估
   - 關鍵人才保留
   - 知識管理策略

請提供專業的團隊診斷報告和改善建議。"""

class QualityAssessment:
    """質量評估模組"""
    
    @staticmethod
    def assess_response_quality(response: str) -> Dict[str, Any]:
        """評估回應質量"""
        quality_score = 0.0
        feedback = []
        
        # 長度檢查
        if len(response) > 500:
            quality_score += 0.2
        else:
            feedback.append("回應內容過短，建議提供更詳細的分析")
        
        # 結構化檢查
        if "**" in response or "##" in response or response.count('\n') > 5:
            quality_score += 0.2
        else:
            feedback.append("建議使用更好的結構化格式")
        
        # 專業術語檢查
        hr_terms = ["績效", "職業發展", "技能", "團隊", "領導", "溝通", "培訓", "人才"]
        term_count = sum(1 for term in hr_terms if term in response)
        if term_count >= 3:
            quality_score += 0.2
        else:
            feedback.append("建議使用更多HR專業術語")
        
        # 可執行性檢查
        action_indicators = ["建議", "應該", "可以", "計劃", "目標", "步驟"]
        action_count = sum(1 for indicator in action_indicators if indicator in response)
        if action_count >= 3:
            quality_score += 0.2
        else:
            feedback.append("建議提供更多可執行的建議")
        
        # 完整性檢查
        if quality_score >= 0.6:
            quality_score += 0.2
        
        return {
            "quality_score": round(quality_score, 2),
            "max_score": 1.0,
            "feedback": feedback,
            "is_acceptable": quality_score >= 0.6
        }

class AdvancedHRAI:
    """高級HR AI助手"""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_client = HighQualityLLMClient(llm_config)
        self.logger = logging.getLogger(__name__)
        self.quality_assessor = QualityAssessment()
    
    def analyze_employee(self, employee_data: Dict[str, Any], 
                        quality_threshold: float = 0.6) -> Dict[str, Any]:
        """高質量員工分析"""
        self.logger.info(f"開始分析員工: {employee_data.get('name', 'Unknown')}")
        
        # 生成分析
        system_prompt = HRPromptTemplates.get_system_prompt()
        user_prompt = HRPromptTemplates.employee_analysis_prompt(employee_data)
        
        analysis = self.llm_client.generate(user_prompt, system_prompt)
        
        # 質量評估
        quality_assessment = self.quality_assessor.assess_response_quality(analysis)
        
        # 如果質量不達標且不是備用回應，嘗試重新生成
        if (quality_assessment["quality_score"] < quality_threshold and 
            "系統備用回應" not in analysis):
            self.logger.warning("初次分析質量不達標，嘗試改進...")
            
            improved_prompt = f"""請改進以下HR分析，使其更加專業和詳細：

原始分析：
{analysis}

改進要求：
- 提供更結構化的分析
- 增加具體的行動建議
- 使用更多專業術語
- 確保內容完整性"""
            
            analysis = self.llm_client.generate(improved_prompt, system_prompt)
            quality_assessment = self.quality_assessor.assess_response_quality(analysis)
        
        return {
            "employee_id": employee_data.get("id", "unknown"),
            "employee_name": employee_data.get("name", "Unknown"),
            "analysis_timestamp": datetime.now().isoformat(),
            "detailed_analysis": analysis,
            "quality_assessment": quality_assessment,
            "llm_provider": self.llm_client.config.provider.value,
            "model_used": self.llm_client.config.model_name,
            "raw_data": employee_data
        }
    
    def analyze_team(self, team_data: Dict[str, Any],
                    quality_threshold: float = 0.6) -> Dict[str, Any]:
        """高質量團隊分析"""
        self.logger.info(f"開始分析團隊: {team_data.get('name', 'Unknown')}")
        
        # 生成分析
        system_prompt = HRPromptTemplates.get_system_prompt()
        user_prompt = HRPromptTemplates.team_analysis_prompt(team_data)
        
        analysis = self.llm_client.generate(user_prompt, system_prompt)
        
        # 質量評估
        quality_assessment = self.quality_assessor.assess_response_quality(analysis)
        
        # 質量改進
        if (quality_assessment["quality_score"] < quality_threshold and 
            "系統備用回應" not in analysis):
            self.logger.warning("初次分析質量不達標，嘗試改進...")
            
            improved_prompt = f"""請改進以下團隊分析，使其更加專業和全面：

原始分析：
{analysis}

改進要求：
- 提供更深入的團隊動態分析
- 增加量化指標和評估
- 提供具體的改善建議
- 考慮組織文化因素"""
            
            analysis = self.llm_client.generate(improved_prompt, system_prompt)
            quality_assessment = self.quality_assessor.assess_response_quality(analysis)
        
        return {
            "team_id": team_data.get("id", "unknown"),
            "team_name": team_data.get("name", "Unknown"),
            "analysis_timestamp": datetime.now().isoformat(),
            "detailed_analysis": analysis,
            "quality_assessment": quality_assessment,
            "llm_provider": self.llm_client.config.provider.value,
            "model_used": self.llm_client.config.model_name,
            "raw_data": team_data
        }

def create_llm_config_from_env() -> LLMConfig:
    """從環境變量創建LLM配置"""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name=os.getenv("OPENAI_MODEL", "gpt-4"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
    elif provider == "ollama":
        return LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name=os.getenv("OLLAMA_MODEL", "llama2:13b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
    elif provider == "claude":
        return LLMConfig(
            provider=LLMProvider.CLAUDE,
            model_name=os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
    elif provider == "groq":
        return LLMConfig(
            provider=LLMProvider.GROQ,
            model_name=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="高質量HR AI助手")
    parser.add_argument("command", choices=["analyze-employee", "analyze-team"])
    parser.add_argument("input_file", help="輸入JSON文件路徑")
    parser.add_argument("--output-file", help="輸出文件路徑")
    parser.add_argument("--provider", choices=["openai", "ollama", "claude", "groq"],
                       help="LLM提供商")
    parser.add_argument("--model", help="模型名稱")
    parser.add_argument("--quality-threshold", type=float, default=0.6,
                       help="質量閾值 (0.0-1.0)")
    
    args = parser.parse_args()
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # 創建LLM配置
        llm_config = create_llm_config_from_env()
        if args.provider:
            llm_config.provider = LLMProvider(args.provider)
        if args.model:
            llm_config.model_name = args.model
        
        # 創建HR AI實例
        hr_ai = AdvancedHRAI(llm_config)
        
        # 讀取輸入數據
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # 執行分析
        if args.command == "analyze-employee":
            result = hr_ai.analyze_employee(input_data, args.quality_threshold)
        else:
            result = hr_ai.analyze_team(input_data, args.quality_threshold)
        
        # 輸出結果
        output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"分析結果已保存到: {args.output_file}")
        else:
            print(output)
    
    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()