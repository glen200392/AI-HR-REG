"""
Query Analyzer - 查詢分析器
自動判斷問題複雜度，動態調整檢索策略
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime


class QueryComplexity(Enum):
    """查詢複雜度等級"""
    SIMPLE = "simple"      # 簡單查詢 - 2個片段
    MODERATE = "moderate"  # 中等查詢 - 4個片段 (預設)
    COMPLEX = "complex"    # 複雜查詢 - 6個片段
    EXPERT = "expert"      # 專家級查詢 - 8個片段


@dataclass
class QueryAnalysis:
    """查詢分析結果"""
    original_query: str
    complexity: QueryComplexity
    keywords: List[str]
    topics: List[str]
    suggested_chunks: int
    confidence_score: float
    reasoning: str


class QueryAnalyzer:
    """
    查詢分析器 - 判斷問題複雜度和檢索策略
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 複雜度判斷規則
        self.complexity_rules = self._init_complexity_rules()
        
        # HR領域關鍵詞庫
        self.hr_keywords = self._init_hr_keywords()
    
    def _init_complexity_rules(self) -> Dict[str, Any]:
        """初始化複雜度判斷規則"""
        return {
            "simple_indicators": [
                # 單一概念查詢
                r"什麼是\s*(\w+)",
                r"(\w+)\s*是什麼",
                r"如何\s*(\w+)",
                r"(\w+)\s*天數",
                r"(\w+)\s*流程",
                r"(\w+)\s*規定",
                # 簡單計算
                r"計算\s*(\w+)",
                r"(\w+)\s*多少",
                r"費用\s*(\w+)",
            ],
            "moderate_indicators": [
                # 需要多方面考慮
                r"處理\s*(\w+)\s*問題",
                r"(\w+)\s*注意事項",
                r"(\w+)\s*最佳實踐",
                r"如何制定\s*(\w+)",
                r"(\w+)\s*政策\s*(\w+)",
                # 比較分析
                r"(\w+)\s*和\s*(\w+)\s*區別",
                r"(\w+)\s*優缺點",
            ],
            "complex_indicators": [
                # 多概念整合
                r"綜合\s*(\w+)",
                r"整體\s*(\w+)\s*策略",
                r"(\w+)\s*風險\s*評估",
                r"(\w+)\s*合規性\s*檢查",
                # 跨領域問題
                r"法律\s*(\w+)\s*問題",
                r"勞資\s*(\w+)",
                r"糾紛\s*處理",
                # 長期規劃
                r"長期\s*(\w+)",
                r"戰略\s*(\w+)",
            ],
            "expert_indicators": [
                # 專業法律問題
                r"法規\s*解釋",
                r"判例\s*分析",
                r"訴訟\s*風險",
                # 複雜政策制定
                r"制度\s*設計",
                r"體系\s*建立",
                r"全面\s*改革",
                # 複雜分析
                r"深度\s*分析",
                r"全方位\s*評估",
            ]
        }
    
    def _init_hr_keywords(self) -> Dict[str, List[str]]:
        """初始化HR關鍵詞庫"""
        return {
            "recruitment": ["招聘", "面試", "錄用", "人才", "選才"],
            "performance": ["績效", "考核", "評估", "KPI", "目標"],
            "compensation": ["薪資", "薪酬", "獎金", "福利", "津貼"],
            "leave": ["請假", "休假", "病假", "事假", "年假"],
            "labor_law": ["勞基法", "勞動法", "法規", "合規", "違法"],
            "discipline": ["懲戒", "處分", "違規", "警告", "解雇"],
            "training": ["培訓", "教育", "學習", "發展", "課程"],
            "employee_relations": ["員工關係", "溝通", "衝突", "協調", "調解"],
            "policy": ["政策", "制度", "規定", "辦法", "準則"],
            "compliance": ["合規", "稽核", "檢查", "監督", "風險"]
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        分析查詢複雜度
        
        Args:
            query: 用戶查詢文本
            
        Returns:
            QueryAnalysis: 分析結果
        """
        # 清理查詢文本
        cleaned_query = self._clean_query(query)
        
        # 提取關鍵詞
        keywords = self._extract_keywords(cleaned_query)
        
        # 識別HR主題
        topics = self._identify_topics(cleaned_query, keywords)
        
        # 判斷複雜度
        complexity, reasoning = self._determine_complexity(cleaned_query, keywords, topics)
        
        # 根據複雜度建議片段數量
        suggested_chunks = self._get_suggested_chunks(complexity)
        
        # 計算信心分數
        confidence = self._calculate_confidence(cleaned_query, complexity, keywords)
        
        return QueryAnalysis(
            original_query=query,
            complexity=complexity,
            keywords=keywords,
            topics=topics,
            suggested_chunks=suggested_chunks,
            confidence_score=confidence,
            reasoning=reasoning
        )
    
    def _clean_query(self, query: str) -> str:
        """清理查詢文本"""
        # 移除多餘空白
        cleaned = re.sub(r'\s+', ' ', query.strip())
        return cleaned
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取關鍵詞"""
        keywords = []
        
        # 使用正則表達式提取中文詞彙
        chinese_words = re.findall(r'[\u4e00-\u9fff]+', query)
        
        # 過濾長度
        keywords = [word for word in chinese_words if len(word) >= 2]
        
        return list(set(keywords))  # 去重
    
    def _identify_topics(self, query: str, keywords: List[str]) -> List[str]:
        """識別HR主題領域"""
        topics = []
        
        for topic, topic_keywords in self.hr_keywords.items():
            for keyword in keywords:
                if any(kw in keyword for kw in topic_keywords):
                    topics.append(topic)
                    break
        
        return list(set(topics))
    
    def _determine_complexity(self, query: str, keywords: List[str], topics: List[str]) -> Tuple[QueryComplexity, str]:
        """判斷查詢複雜度"""
        reasons = []
        
        # 檢查專家級指標
        expert_matches = self._check_pattern_matches(query, self.complexity_rules["expert_indicators"])
        if expert_matches:
            reasons.append(f"包含專家級關鍵詞: {expert_matches}")
            return QueryComplexity.EXPERT, "; ".join(reasons)
        
        # 檢查複雜級指標
        complex_matches = self._check_pattern_matches(query, self.complexity_rules["complex_indicators"])
        if complex_matches or len(topics) >= 3:
            if complex_matches:
                reasons.append(f"包含複雜級關鍵詞: {complex_matches}")
            if len(topics) >= 3:
                reasons.append(f"涉及多個領域: {topics}")
            return QueryComplexity.COMPLEX, "; ".join(reasons)
        
        # 檢查中等級指標
        moderate_matches = self._check_pattern_matches(query, self.complexity_rules["moderate_indicators"])
        if moderate_matches or len(keywords) >= 5 or len(topics) == 2:
            if moderate_matches:
                reasons.append(f"包含中等級關鍵詞: {moderate_matches}")
            if len(keywords) >= 5:
                reasons.append(f"關鍵詞較多: {len(keywords)}個")
            if len(topics) == 2:
                reasons.append(f"涉及兩個領域: {topics}")
            return QueryComplexity.MODERATE, "; ".join(reasons)
        
        # 檢查簡單級指標
        simple_matches = self._check_pattern_matches(query, self.complexity_rules["simple_indicators"])
        if simple_matches or len(keywords) <= 3:
            if simple_matches:
                reasons.append(f"包含簡單級關鍵詞: {simple_matches}")
            if len(keywords) <= 3:
                reasons.append(f"關鍵詞較少: {len(keywords)}個")
            return QueryComplexity.SIMPLE, "; ".join(reasons)
        
        # 預設為中等級
        reasons.append("預設中等複雜度")
        return QueryComplexity.MODERATE, "; ".join(reasons)
    
    def _check_pattern_matches(self, query: str, patterns: List[str]) -> List[str]:
        """檢查模式匹配"""
        matches = []
        for pattern in patterns:
            if re.search(pattern, query):
                matches.append(pattern)
        return matches
    
    def _get_suggested_chunks(self, complexity: QueryComplexity) -> int:
        """根據複雜度建議片段數量"""
        chunk_mapping = {
            QueryComplexity.SIMPLE: 2,
            QueryComplexity.MODERATE: 4,
            QueryComplexity.COMPLEX: 6,
            QueryComplexity.EXPERT: 8
        }
        return chunk_mapping.get(complexity, 4)  # 預設4個
    
    def _calculate_confidence(self, query: str, complexity: QueryComplexity, keywords: List[str]) -> float:
        """計算判斷信心分數"""
        base_confidence = 0.7
        
        # 根據關鍵詞數量調整
        if len(keywords) > 0:
            base_confidence += min(0.2, len(keywords) * 0.02)
        
        # 根據查詢長度調整
        query_length = len(query)
        if 10 <= query_length <= 50:
            base_confidence += 0.1
        elif query_length > 100:
            base_confidence -= 0.1
        
        return min(0.95, base_confidence)
    
    def get_analysis_summary(self, analysis: QueryAnalysis) -> str:
        """獲取分析摘要"""
        return f"""
查詢分析結果:
- 複雜度: {analysis.complexity.value}
- 建議片段數: {analysis.suggested_chunks}
- 信心分數: {analysis.confidence_score:.2f}
- 識別主題: {', '.join(analysis.topics) if analysis.topics else '無'}
- 關鍵詞: {', '.join(analysis.keywords) if analysis.keywords else '無'}
- 判斷原因: {analysis.reasoning}
        """.strip()


# 全域查詢分析器實例
query_analyzer = QueryAnalyzer()