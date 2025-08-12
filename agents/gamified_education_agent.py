"""
遊戲化教學AI Agent
結合RAG知識檢索與遊戲化教學元素，提供互動式學習體驗
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import random
import asyncio
from pathlib import Path

from .base import BaseAgent
from .rag_agent import RAGKnowledgeAgent


class DifficultyLevel(Enum):
    """難度等級"""
    BEGINNER = "初級"
    INTERMEDIATE = "中級" 
    ADVANCED = "高級"
    EXPERT = "專家"


class QuestionType(Enum):
    """問題類型"""
    MULTIPLE_CHOICE = "選擇題"
    TRUE_FALSE = "是非題"
    FILL_BLANK = "填空題"
    SHORT_ANSWER = "簡答題"
    SCENARIO = "情境題"


class AchievementType(Enum):
    """成就類型"""
    LEARNING_STREAK = "連續學習"
    KNOWLEDGE_MASTER = "知識達人"
    QUICK_LEARNER = "快速學習者"
    EXPLORER = "探索者"
    PERFECTIONIST = "完美主義者"


@dataclass
class LearningProgress:
    """學習進度"""
    user_id: str
    total_experience: int = 0
    current_level: int = 1
    current_streak: int = 0
    best_streak: int = 0
    topics_mastered: List[str] = field(default_factory=list)
    questions_answered: int = 0
    correct_answers: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    achievements: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    """成就"""
    id: str
    name: str
    description: str
    icon: str
    type: AchievementType
    condition: Dict[str, Any]
    reward_exp: int
    unlocked: bool = False
    unlock_date: Optional[datetime] = None


@dataclass
class LearningQuestion:
    """學習問題"""
    id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    topic: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    source_context: str
    exp_reward: int


@dataclass
class LearningSession:
    """學習會話"""
    session_id: str
    user_id: str
    topic: str
    difficulty: DifficultyLevel
    questions: List[LearningQuestion]
    current_question_index: int = 0
    score: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    is_completed: bool = False


class GamifiedEducationAgent(BaseAgent):
    """
    遊戲化教學AI Agent
    
    核心功能：
    1. 智能問題生成
    2. 適應性難度調整
    3. 積分系統與等級
    4. 成就系統
    5. 學習路徑推薦
    6. 互動式教學場景
    """
    
    def __init__(self, 
                 rag_agent: RAGKnowledgeAgent,
                 model_name: str = "gpt-4",
                 temperature: float = 0.7):
        super().__init__(model_name, temperature)
        
        self.rag_agent = rag_agent
        self.user_progress: Dict[str, LearningProgress] = {}
        self.achievements: List[Achievement] = []
        self.active_sessions: Dict[str, LearningSession] = {}
        
        # 初始化成就系統
        self._initialize_achievements()
        
        # 學習分析數據
        self.topic_difficulty_map = {}
        self.question_templates = self._load_question_templates()
        
    def _get_system_message(self):
        """返回遊戲化教學系統提示"""
        from langchain.schema import SystemMessage
        return SystemMessage(content="""
        你是一個專業的遊戲化教學AI助手，擅長：
        1. 根據用戶水平生成適當難度的問題
        2. 提供引人入勝的教學內容
        3. 給予鼓勵性的反饋
        4. 創造互動式學習體驗
        5. 分析學習進度並提供個性化建議
        
        請用友善、鼓勵的語調與學習者互動。
        """)
    
    def _initialize_achievements(self):
        """初始化成就系統"""
        achievements_data = [
            {
                "id": "first_question",
                "name": "初次嘗試",
                "description": "回答了第一個問題",
                "icon": "🎯",
                "type": AchievementType.LEARNING_STREAK,
                "condition": {"questions_answered": 1},
                "reward_exp": 50
            },
            {
                "id": "streak_7",
                "name": "持之以恆",
                "description": "連續學習7天",
                "icon": "🔥",
                "type": AchievementType.LEARNING_STREAK,
                "condition": {"streak_days": 7},
                "reward_exp": 200
            },
            {
                "id": "accuracy_90",
                "name": "神射手",
                "description": "正確率達到90%（至少回答20題）",
                "icon": "🎯",
                "type": AchievementType.PERFECTIONIST,
                "condition": {"accuracy": 0.9, "min_questions": 20},
                "reward_exp": 300
            },
            {
                "id": "topic_master",
                "name": "主題專家",
                "description": "完全掌握一個主題",
                "icon": "👑",
                "type": AchievementType.KNOWLEDGE_MASTER,
                "condition": {"topics_mastered": 1},
                "reward_exp": 500
            },
            {
                "id": "speed_demon",
                "name": "快速學習者",
                "description": "在30秒內回答正確",
                "icon": "⚡",
                "type": AchievementType.QUICK_LEARNER,
                "condition": {"response_time": 30},
                "reward_exp": 100
            }
        ]
        
        for achievement_data in achievements_data:
            achievement = Achievement(
                id=achievement_data["id"],
                name=achievement_data["name"],
                description=achievement_data["description"],
                icon=achievement_data["icon"],
                type=achievement_data["type"],
                condition=achievement_data["condition"],
                reward_exp=achievement_data["reward_exp"]
            )
            self.achievements.append(achievement)
    
    def _load_question_templates(self) -> Dict[QuestionType, List[str]]:
        """載入問題模板"""
        return {
            QuestionType.MULTIPLE_CHOICE: [
                "關於{topic}，下列哪個敘述是正確的？",
                "在{context}的情況下，最適當的做法是？",
                "{topic}的主要特徵是什麼？"
            ],
            QuestionType.TRUE_FALSE: [
                "以下關於{topic}的敘述是否正確：{statement}",
                "根據{context}，{statement}這個說法是對的嗎？"
            ],
            QuestionType.SCENARIO: [
                "假設你遇到以下情況：{scenario}。你會如何處理？",
                "在{context}的背景下，如果發生{scenario}，最好的解決方案是什麼？"
            ],
            QuestionType.SHORT_ANSWER: [
                "請簡要說明{topic}的重要性",
                "什麼是{concept}？請用自己的話解釋",
                "請舉例說明{topic}在實際工作中的應用"
            ]
        }
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        """處理學習任務"""
        # 解析任務類型
        if task.startswith("start_session"):
            return await self._handle_start_session(task)
        elif task.startswith("answer_question"):
            return await self._handle_answer_question(task)
        elif task.startswith("get_progress"):
            return await self._handle_get_progress(task)
        elif task.startswith("generate_question"):
            return await self._handle_generate_question(task)
        else:
            return await self._handle_general_inquiry(task)
    
    async def start_learning_session(self, 
                                   user_id: str, 
                                   topic: str, 
                                   difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
                                   question_count: int = 5) -> LearningSession:
        """開始學習會話"""
        
        session_id = f"{user_id}_{datetime.now().timestamp()}"
        
        # 獲取用戶進度
        progress = self.get_user_progress(user_id)
        
        # 根據進度調整難度
        adjusted_difficulty = self._adjust_difficulty(progress, topic, difficulty)
        
        # 生成問題
        questions = await self._generate_questions(topic, adjusted_difficulty, question_count)
        
        # 創建學習會話
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            topic=topic,
            difficulty=adjusted_difficulty,
            questions=questions
        )
        
        self.active_sessions[session_id] = session
        
        return session
    
    async def _generate_questions(self, 
                                topic: str, 
                                difficulty: DifficultyLevel, 
                                count: int) -> List[LearningQuestion]:
        """生成學習問題"""
        
        questions = []
        
        # 從RAG系統獲取相關知識
        knowledge_query = f"請提供關於{topic}的詳細資訊，包括定義、重要概念、實際應用和常見問題"
        rag_result = await self.rag_agent.query(knowledge_query)
        
        context = rag_result.answer
        source_docs = rag_result.source_documents
        
        for i in range(count):
            question_type = self._select_question_type(difficulty, i)
            question = await self._create_question(
                topic=topic,
                context=context,
                question_type=question_type,
                difficulty=difficulty,
                sources=source_docs
            )
            questions.append(question)
        
        return questions
    
    def _select_question_type(self, difficulty: DifficultyLevel, question_index: int) -> QuestionType:
        """根據難度選擇問題類型"""
        
        if difficulty == DifficultyLevel.BEGINNER:
            types = [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]
            weights = [0.7, 0.3]
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            types = [QuestionType.MULTIPLE_CHOICE, QuestionType.FILL_BLANK, QuestionType.SHORT_ANSWER]
            weights = [0.5, 0.3, 0.2]
        elif difficulty == DifficultyLevel.ADVANCED:
            types = [QuestionType.SCENARIO, QuestionType.SHORT_ANSWER, QuestionType.MULTIPLE_CHOICE]
            weights = [0.4, 0.4, 0.2]
        else:  # EXPERT
            types = [QuestionType.SCENARIO, QuestionType.SHORT_ANSWER]
            weights = [0.6, 0.4]
        
        return random.choices(types, weights=weights)[0]
    
    async def _create_question(self, 
                             topic: str, 
                             context: str, 
                             question_type: QuestionType,
                             difficulty: DifficultyLevel,
                             sources: List[str]) -> LearningQuestion:
        """創建具體問題"""
        
        # 選擇模板
        template = random.choice(self.question_templates[question_type])
        
        # 構建提示
        prompt = f"""
        基於以下資訊，創建一個{difficulty.value}難度的{question_type.value}：
        
        主題：{topic}
        相關知識：{context[:1000]}
        
        模板：{template}
        
        請按以下JSON格式回答：
        {{
            "question": "問題內容",
            "options": ["選項1", "選項2", "選項3", "選項4"] (僅選擇題需要),
            "correct_answer": "正確答案",
            "explanation": "詳細解釋為什麼這是正確答案",
            "key_concepts": ["關鍵概念1", "關鍵概念2"]
        }}
        """
        
        # 使用LLM生成問題
        response = await self.llm.ainvoke([self.system_message, {"role": "user", "content": prompt}])
        
        try:
            question_data = json.loads(response.content)
            
            # 計算經驗獎勵
            exp_reward = self._calculate_exp_reward(difficulty, question_type)
            
            question = LearningQuestion(
                id=f"{topic}_{datetime.now().timestamp()}",
                question=question_data["question"],
                options=question_data.get("options", []),
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                topic=topic,
                difficulty=difficulty,
                question_type=question_type,
                source_context=context[:500],
                exp_reward=exp_reward
            )
            
            return question
            
        except json.JSONDecodeError:
            # 如果JSON解析失敗，創建默認問題
            return self._create_fallback_question(topic, difficulty, question_type)
    
    def _calculate_exp_reward(self, difficulty: DifficultyLevel, question_type: QuestionType) -> int:
        """計算經驗獎勵"""
        base_reward = {
            DifficultyLevel.BEGINNER: 10,
            DifficultyLevel.INTERMEDIATE: 20,
            DifficultyLevel.ADVANCED: 35,
            DifficultyLevel.EXPERT: 50
        }
        
        type_multiplier = {
            QuestionType.TRUE_FALSE: 1.0,
            QuestionType.MULTIPLE_CHOICE: 1.2,
            QuestionType.FILL_BLANK: 1.3,
            QuestionType.SHORT_ANSWER: 1.5,
            QuestionType.SCENARIO: 1.8
        }
        
        return int(base_reward[difficulty] * type_multiplier[question_type])
    
    def _create_fallback_question(self, 
                                topic: str, 
                                difficulty: DifficultyLevel, 
                                question_type: QuestionType) -> LearningQuestion:
        """創建備用問題"""
        return LearningQuestion(
            id=f"fallback_{datetime.now().timestamp()}",
            question=f"請簡要說明{topic}的重要性",
            options=[],
            correct_answer="需要詳細解釋",
            explanation=f"這是關於{topic}的開放性問題，需要根據學習材料回答",
            topic=topic,
            difficulty=difficulty,
            question_type=QuestionType.SHORT_ANSWER,
            source_context="",
            exp_reward=self._calculate_exp_reward(difficulty, QuestionType.SHORT_ANSWER)
        )
    
    async def submit_answer(self, 
                          session_id: str, 
                          answer: str, 
                          response_time: float) -> Dict[str, Any]:
        """提交答案"""
        
        if session_id not in self.active_sessions:
            return {"error": "會話不存在"}
        
        session = self.active_sessions[session_id]
        current_question = session.questions[session.current_question_index]
        
        # 評估答案
        is_correct = await self._evaluate_answer(current_question, answer)
        
        # 更新會話狀態
        if is_correct:
            session.score += current_question.exp_reward
        
        # 更新用戶進度
        progress = self.get_user_progress(session.user_id)
        progress.questions_answered += 1
        if is_correct:
            progress.correct_answers += 1
            progress.total_experience += current_question.exp_reward
        
        # 檢查成就
        new_achievements = self._check_achievements(session.user_id, response_time, is_correct)
        
        # 檢查等級提升
        level_up = self._check_level_up(progress)
        
        # 準備回饋
        feedback = await self._generate_feedback(current_question, answer, is_correct)
        
        # 移動到下一題
        session.current_question_index += 1
        
        # 檢查會話是否完成
        if session.current_question_index >= len(session.questions):
            session.is_completed = True
            session.end_time = datetime.now()
            # 更新學習連續天數
            self._update_learning_streak(session.user_id)
        
        result = {
            "is_correct": is_correct,
            "score": session.score,
            "feedback": feedback,
            "explanation": current_question.explanation,
            "new_achievements": new_achievements,
            "level_up": level_up,
            "session_completed": session.is_completed,
            "progress": {
                "current_question": session.current_question_index,
                "total_questions": len(session.questions),
                "accuracy": progress.correct_answers / progress.questions_answered if progress.questions_answered > 0 else 0
            }
        }
        
        if not session.is_completed:
            # 提供下一題
            next_question = session.questions[session.current_question_index]
            result["next_question"] = {
                "id": next_question.id,
                "question": next_question.question,
                "options": next_question.options,
                "type": next_question.question_type.value,
                "difficulty": next_question.difficulty.value
            }
        
        return result
    
    async def _evaluate_answer(self, question: LearningQuestion, user_answer: str) -> bool:
        """評估用戶答案"""
        
        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]:
            # 直接比較答案
            return user_answer.strip().lower() == question.correct_answer.strip().lower()
        
        else:
            # 使用LLM評估開放性答案
            evaluation_prompt = f"""
            請評估以下答案是否正確：
            
            問題：{question.question}
            標準答案：{question.correct_answer}
            用戶答案：{user_answer}
            
            請回答 "正確" 或 "不正確"，並簡要說明原因。
            """
            
            response = await self.llm.ainvoke([{"role": "user", "content": evaluation_prompt}])
            
            return "正確" in response.content
    
    async def _generate_feedback(self, 
                               question: LearningQuestion, 
                               user_answer: str, 
                               is_correct: bool) -> str:
        """生成個性化反饋"""
        
        if is_correct:
            encouragements = [
                "太棒了！你答對了！🎉",
                "正確！你的理解很準確！👏",
                "很好！繼續保持！⭐",
                "答案完全正確！你真厲害！💪"
            ]
            base_feedback = random.choice(encouragements)
        else:
            encouragements = [
                "沒關係，我們一起來學習！💪",
                "不要氣餒，錯誤是學習的一部分！🌱",
                "很接近了！讓我們再深入了解一下！📚",
                "好的嘗試！讓我們一起探索正確答案！🔍"
            ]
            base_feedback = random.choice(encouragements)
        
        # 添加學習建議
        learning_tip = await self._generate_learning_tip(question, is_correct)
        
        return f"{base_feedback}\n\n{learning_tip}"
    
    async def _generate_learning_tip(self, question: LearningQuestion, is_correct: bool) -> str:
        """生成學習提示"""
        
        if is_correct:
            tip_prompt = f"""
            用戶正確回答了關於{question.topic}的問題。
            請提供一個相關的學習提示或擴展知識，幫助鞏固理解。
            保持簡潔且具有啟發性。
            """
        else:
            tip_prompt = f"""
            用戶回答錯誤了關於{question.topic}的問題。
            請提供一個有幫助的學習建議，幫助理解正確概念。
            要鼓勵性且具有指導意義。
            """
        
        response = await self.llm.ainvoke([{"role": "user", "content": tip_prompt}])
        return response.content.strip()
    
    def _check_achievements(self, user_id: str, response_time: float, is_correct: bool) -> List[Dict[str, Any]]:
        """檢查並解鎖成就"""
        progress = self.get_user_progress(user_id)
        new_achievements = []
        
        for achievement in self.achievements:
            if achievement.id not in progress.achievements:
                if self._check_achievement_condition(achievement, progress, response_time, is_correct):
                    # 解鎖成就
                    progress.achievements.append(achievement.id)
                    progress.total_experience += achievement.reward_exp
                    
                    new_achievements.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "reward_exp": achievement.reward_exp
                    })
        
        return new_achievements
    
    def _check_achievement_condition(self, 
                                   achievement: Achievement, 
                                   progress: LearningProgress, 
                                   response_time: float, 
                                   is_correct: bool) -> bool:
        """檢查成就解鎖條件"""
        
        condition = achievement.condition
        
        if "questions_answered" in condition:
            if progress.questions_answered < condition["questions_answered"]:
                return False
        
        if "accuracy" in condition:
            if progress.questions_answered < condition.get("min_questions", 1):
                return False
            accuracy = progress.correct_answers / progress.questions_answered
            if accuracy < condition["accuracy"]:
                return False
        
        if "streak_days" in condition:
            if progress.current_streak < condition["streak_days"]:
                return False
        
        if "response_time" in condition:
            if response_time > condition["response_time"]:
                return False
        
        if "topics_mastered" in condition:
            if len(progress.topics_mastered) < condition["topics_mastered"]:
                return False
        
        return True
    
    def _check_level_up(self, progress: LearningProgress) -> Optional[Dict[str, Any]]:
        """檢查等級提升"""
        # 經驗值等級公式：level = floor(sqrt(experience / 100)) + 1
        new_level = int((progress.total_experience / 100) ** 0.5) + 1
        
        if new_level > progress.current_level:
            old_level = progress.current_level
            progress.current_level = new_level
            return {
                "old_level": old_level,
                "new_level": new_level,
                "celebration": f"恭喜！你升級到第{new_level}級了！🎊"
            }
        
        return None
    
    def _update_learning_streak(self, user_id: str):
        """更新學習連續天數"""
        progress = self.get_user_progress(user_id)
        today = datetime.now().date()
        last_activity_date = progress.last_activity.date()
        
        if last_activity_date == today:
            # 今天已經學習過了，不更新連續天數
            return
        elif last_activity_date == today - timedelta(days=1):
            # 連續學習
            progress.current_streak += 1
            progress.best_streak = max(progress.best_streak, progress.current_streak)
        else:
            # 中斷了連續學習
            progress.current_streak = 1
        
        progress.last_activity = datetime.now()
    
    def get_user_progress(self, user_id: str) -> LearningProgress:
        """獲取用戶學習進度"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = LearningProgress(user_id=user_id)
        return self.user_progress[user_id]
    
    def _adjust_difficulty(self, 
                          progress: LearningProgress, 
                          topic: str, 
                          requested_difficulty: DifficultyLevel) -> DifficultyLevel:
        """根據用戶進度調整難度"""
        
        # 如果是新手，先從初級開始
        if progress.questions_answered < 5:
            return DifficultyLevel.BEGINNER
        
        # 計算準確率
        accuracy = progress.correct_answers / progress.questions_answered
        
        # 根據準確率調整難度
        if accuracy >= 0.8 and progress.current_level >= 3:
            # 準確率高且等級足夠，可以挑戰更高難度
            difficulty_order = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, 
                              DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
            
            try:
                current_index = difficulty_order.index(requested_difficulty)
                if current_index < len(difficulty_order) - 1:
                    return difficulty_order[current_index + 1]
            except ValueError:
                pass
        
        elif accuracy < 0.6:
            # 準確率較低，降低難度
            if requested_difficulty == DifficultyLevel.EXPERT:
                return DifficultyLevel.ADVANCED
            elif requested_difficulty == DifficultyLevel.ADVANCED:
                return DifficultyLevel.INTERMEDIATE
            elif requested_difficulty == DifficultyLevel.INTERMEDIATE:
                return DifficultyLevel.BEGINNER
        
        return requested_difficulty
    
    async def get_learning_recommendations(self, user_id: str) -> Dict[str, Any]:
        """獲取個性化學習推薦"""
        progress = self.get_user_progress(user_id)
        
        recommendations = {
            "next_topics": await self._recommend_topics(progress),
            "difficulty_suggestion": self._suggest_difficulty(progress),
            "study_plan": self._create_study_plan(progress),
            "motivational_message": self._get_motivational_message(progress)
        }
        
        return recommendations
    
    async def _recommend_topics(self, progress: LearningProgress) -> List[str]:
        """推薦學習主題"""
        # 基於已掌握的主題推薦相關主題
        if not progress.topics_mastered:
            return ["HR基礎概念", "招聘流程", "員工關係"]
        
        # TODO: 實現更智能的主題推薦算法
        all_topics = [
            "勞動法規", "薪資管理", "績效評估", "培訓發展",
            "員工福利", "組織文化", "人才管理", "衝突解決"
        ]
        
        # 排除已掌握的主題
        available_topics = [t for t in all_topics if t not in progress.topics_mastered]
        
        return available_topics[:3]
    
    def _suggest_difficulty(self, progress: LearningProgress) -> DifficultyLevel:
        """建議難度等級"""
        if progress.questions_answered == 0:
            return DifficultyLevel.BEGINNER
        
        accuracy = progress.correct_answers / progress.questions_answered
        
        if accuracy >= 0.85 and progress.current_level >= 5:
            return DifficultyLevel.EXPERT
        elif accuracy >= 0.75 and progress.current_level >= 3:
            return DifficultyLevel.ADVANCED
        elif accuracy >= 0.6:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _create_study_plan(self, progress: LearningProgress) -> Dict[str, Any]:
        """創建學習計劃"""
        return {
            "daily_target": max(3, min(10, progress.current_level * 2)),
            "weekly_goal": f"掌握{1 + progress.current_level // 3}個新主題",
            "focus_areas": self._identify_weak_areas(progress),
            "estimated_time": "15-30分鐘/天"
        }
    
    def _identify_weak_areas(self, progress: LearningProgress) -> List[str]:
        """識別薄弱環節"""
        # TODO: 實現基於答題歷史的薄弱環節分析
        return ["需要更多練習的領域"]
    
    def _get_motivational_message(self, progress: LearningProgress) -> str:
        """獲取激勵訊息"""
        messages = [
            f"你已經回答了{progress.questions_answered}個問題，繼續加油！",
            f"你的學習等級是{progress.current_level}級，真了不起！",
            f"連續學習{progress.current_streak}天，堅持就是勝利！",
            f"正確率{progress.correct_answers / max(1, progress.questions_answered):.1%}，你的進步很明顯！"
        ]
        
        return random.choice(messages)
    
    async def _handle_start_session(self, task: str) -> Dict[str, Any]:
        """處理開始學習會話請求"""
        # 解析參數
        parts = task.split("|")
        user_id = parts[1] if len(parts) > 1 else "default_user"
        topic = parts[2] if len(parts) > 2 else "HR基礎"
        difficulty = DifficultyLevel(parts[3]) if len(parts) > 3 else DifficultyLevel.BEGINNER
        
        session = await self.start_learning_session(user_id, topic, difficulty)
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "difficulty": session.difficulty.value,
            "first_question": {
                "id": session.questions[0].id,
                "question": session.questions[0].question,
                "options": session.questions[0].options,
                "type": session.questions[0].question_type.value
            },
            "total_questions": len(session.questions)
        }
    
    async def _handle_answer_question(self, task: str) -> Dict[str, Any]:
        """處理答案提交請求"""
        parts = task.split("|")
        session_id = parts[1] if len(parts) > 1 else ""
        answer = parts[2] if len(parts) > 2 else ""
        response_time = float(parts[3]) if len(parts) > 3 else 30.0
        
        return await self.submit_answer(session_id, answer, response_time)
    
    async def _handle_get_progress(self, task: str) -> Dict[str, Any]:
        """處理獲取進度請求"""
        parts = task.split("|")
        user_id = parts[1] if len(parts) > 1 else "default_user"
        
        progress = self.get_user_progress(user_id)
        recommendations = await self.get_learning_recommendations(user_id)
        
        return {
            "user_id": progress.user_id,
            "level": progress.current_level,
            "experience": progress.total_experience,
            "streak": progress.current_streak,
            "best_streak": progress.best_streak,
            "accuracy": progress.correct_answers / max(1, progress.questions_answered),
            "achievements_count": len(progress.achievements),
            "topics_mastered": progress.topics_mastered,
            "recommendations": recommendations
        }
    
    async def _handle_generate_question(self, task: str) -> Dict[str, Any]:
        """處理生成問題請求"""
        parts = task.split("|")
        topic = parts[1] if len(parts) > 1 else "HR"
        difficulty = DifficultyLevel(parts[2]) if len(parts) > 2 else DifficultyLevel.BEGINNER
        
        questions = await self._generate_questions(topic, difficulty, 1)
        question = questions[0] if questions else None
        
        if question:
            return {
                "id": question.id,
                "question": question.question,
                "options": question.options,
                "type": question.question_type.value,
                "difficulty": question.difficulty.value,
                "topic": question.topic,
                "exp_reward": question.exp_reward
            }
        
        return {"error": "無法生成問題"}
    
    async def _handle_general_inquiry(self, task: str) -> Dict[str, Any]:
        """處理一般查詢"""
        # 使用RAG系統回答一般問題，但加上遊戲化元素
        rag_result = await self.rag_agent.query(task)
        
        # 添加學習建議
        learning_suggestion = await self._suggest_related_learning(task)
        
        return {
            "answer": rag_result.answer,
            "confidence": rag_result.confidence_score,
            "sources": rag_result.source_documents,
            "learning_suggestion": learning_suggestion,
            "gamification_tip": "💡 想要測試你對這個主題的理解嗎？試試創建一個學習會話！"
        }
    
    async def _suggest_related_learning(self, query: str) -> str:
        """建議相關學習內容"""
        suggestion_prompt = f"""
        基於用戶的問題：{query}
        建議一個相關的學習主題或練習，讓用戶可以進一步深入學習。
        保持簡潔且具有吸引力。
        """
        
        response = await self.llm.ainvoke([{"role": "user", "content": suggestion_prompt}])
        return response.content.strip()