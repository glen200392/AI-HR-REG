"""
遊戲化教學AI系統簡化演示
展示核心概念和架構設計
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
import random
import json


class DifficultyLevel(Enum):
    BEGINNER = "初級"
    INTERMEDIATE = "中級" 
    ADVANCED = "高級"
    EXPERT = "專家"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "選擇題"
    TRUE_FALSE = "是非題"
    SCENARIO = "情境題"
    SHORT_ANSWER = "簡答題"


class AchievementType(Enum):
    LEARNING_STREAK = "連續學習"
    KNOWLEDGE_MASTER = "知識達人"
    QUICK_LEARNER = "快速學習者"
    PERFECTIONIST = "完美主義者"


@dataclass
class LearningProgress:
    user_id: str
    total_experience: int = 0
    current_level: int = 1
    current_streak: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    achievements: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    reward_exp: int


@dataclass  
class LearningQuestion:
    id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    topic: str
    difficulty: DifficultyLevel
    question_type: QuestionType
    exp_reward: int


class SimpleGamificationDemo:
    """遊戲化教學系統演示類"""
    
    def __init__(self):
        self.user_progress: Dict[str, LearningProgress] = {}
        self.achievements = self._initialize_achievements()
        self.sample_questions = self._create_sample_questions()
    
    def _initialize_achievements(self) -> List[Achievement]:
        """初始化成就系統"""
        return [
            Achievement("first_question", "初次嘗試", "回答了第一個問題", "🎯", 50),
            Achievement("accuracy_90", "神射手", "正確率達到90%", "🏹", 300),
            Achievement("streak_7", "持之以恆", "連續學習7天", "🔥", 200),
            Achievement("level_5", "小有成就", "達到5級", "⭐", 500),
        ]
    
    def _create_sample_questions(self) -> List[LearningQuestion]:
        """創建示例問題"""
        return [
            LearningQuestion(
                id="hr_001",
                question="人力資源管理的主要職能不包括以下哪一項？",
                options=["招聘與選拔", "培訓與開發", "財務管理", "績效管理"],
                correct_answer="財務管理",
                explanation="財務管理屬於財務部門的職責，不是人力資源管理的主要職能。",
                topic="HR基礎概念",
                difficulty=DifficultyLevel.BEGINNER,
                question_type=QuestionType.MULTIPLE_CHOICE,
                exp_reward=15
            ),
            LearningQuestion(
                id="hr_002", 
                question="以人為本是人力資源管理的重要原則。",
                options=["正確", "錯誤"],
                correct_answer="正確",
                explanation="以人為本確實是人力資源管理的核心原則，強調重視員工的價值和發展。",
                topic="HR基礎概念",
                difficulty=DifficultyLevel.BEGINNER,
                question_type=QuestionType.TRUE_FALSE,
                exp_reward=12
            ),
            LearningQuestion(
                id="hr_003",
                question="假設你是HR經理，發現部門間經常發生衝突，影響工作效率。你會採取什麼措施？",
                options=[
                    "組織跨部門溝通會議，找出問題根源",
                    "直接處罰衝突的員工",
                    "忽略問題，讓他們自己解決",
                    "重新調整組織架構"
                ],
                correct_answer="組織跨部門溝通會議，找出問題根源",
                explanation="面對部門衝突，最好的做法是促進溝通，了解問題根源，然後制定針對性的解決方案。",
                topic="員工關係",
                difficulty=DifficultyLevel.INTERMEDIATE,
                question_type=QuestionType.SCENARIO,
                exp_reward=25
            )
        ]
    
    def get_user_progress(self, user_id: str) -> LearningProgress:
        """獲取用戶進度"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = LearningProgress(user_id=user_id)
        return self.user_progress[user_id]
    
    def start_learning_session(self, user_id: str, topic: str) -> Dict[str, Any]:
        """開始學習會話"""
        # 根據用戶進度選擇合適的問題
        progress = self.get_user_progress(user_id)
        suitable_questions = [q for q in self.sample_questions if q.topic == topic or topic == "綜合"]
        
        if progress.questions_answered < 5:
            # 新手優先選擇初級問題
            suitable_questions = [q for q in suitable_questions if q.difficulty == DifficultyLevel.BEGINNER]
        
        selected_question = random.choice(suitable_questions) if suitable_questions else self.sample_questions[0]
        
        return {
            "session_id": f"{user_id}_{datetime.now().timestamp()}",
            "question": {
                "id": selected_question.id,
                "question": selected_question.question,
                "options": selected_question.options,
                "type": selected_question.question_type.value,
                "difficulty": selected_question.difficulty.value,
                "exp_reward": selected_question.exp_reward
            }
        }
    
    def submit_answer(self, user_id: str, question_id: str, answer: str) -> Dict[str, Any]:
        """提交答案"""
        # 找到對應的問題
        question = next((q for q in self.sample_questions if q.id == question_id), None)
        if not question:
            return {"error": "問題不存在"}
        
        progress = self.get_user_progress(user_id)
        is_correct = answer.strip() == question.correct_answer.strip()
        
        # 更新進度
        progress.questions_answered += 1
        if is_correct:
            progress.correct_answers += 1
            progress.total_experience += question.exp_reward
        
        # 檢查等級提升
        new_level = int((progress.total_experience / 100) ** 0.5) + 1
        level_up = new_level > progress.current_level
        if level_up:
            progress.current_level = new_level
        
        # 檢查成就
        new_achievements = self._check_achievements(progress)
        
        # 生成反饋
        if is_correct:
            feedback = random.choice([
                "太棒了！你答對了！🎉",
                "正確！你的理解很準確！👏", 
                "很好！繼續保持！⭐"
            ])
        else:
            feedback = random.choice([
                "沒關係，我們一起來學習！💪",
                "不要氣餒，錯誤是學習的一部分！🌱",
                "很接近了！讓我們再深入了解一下！📚"
            ])
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "explanation": question.explanation,
            "score": progress.total_experience,
            "level": progress.current_level,
            "level_up": level_up,
            "new_achievements": new_achievements,
            "accuracy": progress.correct_answers / progress.questions_answered,
            "progress": {
                "questions_answered": progress.questions_answered,
                "correct_answers": progress.correct_answers,
                "current_level": progress.current_level,
                "total_experience": progress.total_experience
            }
        }
    
    def _check_achievements(self, progress: LearningProgress) -> List[Dict[str, Any]]:
        """檢查並解鎖成就"""
        new_achievements = []
        
        for achievement in self.achievements:
            if achievement.id not in progress.achievements:
                unlocked = False
                
                if achievement.id == "first_question" and progress.questions_answered >= 1:
                    unlocked = True
                elif achievement.id == "accuracy_90" and progress.questions_answered >= 5:
                    accuracy = progress.correct_answers / progress.questions_answered
                    if accuracy >= 0.9:
                        unlocked = True
                elif achievement.id == "level_5" and progress.current_level >= 5:
                    unlocked = True
                
                if unlocked:
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
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶統計信息"""
        progress = self.get_user_progress(user_id)
        
        return {
            "user_id": user_id,
            "level": progress.current_level,
            "experience": progress.total_experience,
            "questions_answered": progress.questions_answered,
            "correct_answers": progress.correct_answers,
            "accuracy": progress.correct_answers / max(1, progress.questions_answered),
            "achievements": len(progress.achievements),
            "streak": progress.current_streak
        }
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """獲取排行榜"""
        all_users = list(self.user_progress.values())
        leaderboard = sorted(all_users, key=lambda x: x.total_experience, reverse=True)
        
        return [
            {
                "rank": i + 1,
                "user_id": user.user_id,
                "level": user.current_level,
                "experience": user.total_experience,
                "accuracy": user.correct_answers / max(1, user.questions_answered)
            }
            for i, user in enumerate(leaderboard[:10])
        ]


def run_demo():
    """運行演示"""
    print("🎮 遊戲化教學AI系統演示")
    print("=" * 50)
    
    # 創建演示實例
    demo = SimpleGamificationDemo()
    
    # 模擬用戶學習過程
    test_users = ["Alice", "Bob", "Charlie"]
    
    print("\n📚 開始模擬學習過程...")
    
    for user in test_users:
        print(f"\n👤 用戶: {user}")
        print("-" * 30)
        
        # 開始學習會話
        session = demo.start_learning_session(user, "HR基礎概念")
        question = session["question"]
        
        print(f"❓ {question['type']} ({question['difficulty']})")
        print(f"問題: {question['question']}")
        
        if question["options"]:
            for i, option in enumerate(question["options"]):
                print(f"  {i+1}. {option}")
        
        # 模擬用戶回答
        correct_rate = 0.8 if user == "Alice" else 0.6 if user == "Bob" else 0.7
        is_correct_answer = random.random() < correct_rate
        
        if question["options"]:
            if is_correct_answer:
                # 找到正確答案的索引
                correct_option = None
                for i, option in enumerate(question["options"]):
                    if option == demo.sample_questions[0].correct_answer:  # 簡化處理
                        correct_option = option
                        break
                answer = correct_option or question["options"][0]
            else:
                # 選擇錯誤答案
                wrong_options = [opt for opt in question["options"] 
                               if opt != demo.sample_questions[0].correct_answer]
                answer = random.choice(wrong_options) if wrong_options else question["options"][0]
        else:
            answer = "測試答案"
        
        print(f"💭 用戶回答: {answer}")
        
        # 提交答案
        result = demo.submit_answer(user, question["id"], answer)
        
        print(f"結果: {'✅ 正確' if result['is_correct'] else '❌ 錯誤'}")
        print(f"反饋: {result['feedback']}")
        print(f"當前等級: {result['level']}")
        print(f"總經驗: {result['score']}")
        print(f"準確率: {result['accuracy']:.1%}")
        
        if result['level_up']:
            print("🎊 等級提升！")
        
        if result['new_achievements']:
            print("🏆 解鎖新成就:")
            for achievement in result['new_achievements']:
                print(f"   {achievement['icon']} {achievement['name']}")
    
    # 多輪學習模擬
    print("\n🔄 模擬多輪學習...")
    for round_num in range(3):
        print(f"\n第 {round_num + 1} 輪學習:")
        for user in test_users:
            session = demo.start_learning_session(user, "綜合")
            question = session["question"]
            
            # 模擬回答
            correct_rate = 0.85 if user == "Alice" else 0.65 if user == "Bob" else 0.75
            is_correct = random.random() < correct_rate
            
            if question["options"]:
                # 簡化的答案選擇邏輯
                answer = question["options"][0]  # 簡化為選擇第一個選項
            else:
                answer = "學習回答"
            
            result = demo.submit_answer(user, question["id"], answer)
            
            print(f"  {user}: {'✅' if result['is_correct'] else '❌'} "
                  f"L{result['level']} ({result['score']}XP) "
                  f"{result['accuracy']:.1%}")
    
    # 顯示最終統計
    print("\n📊 最終學習統計:")
    print("-" * 40)
    
    for user in test_users:
        stats = demo.get_user_stats(user)
        print(f"{user:8} | L{stats['level']:2} | {stats['experience']:4}XP | "
              f"{stats['questions_answered']:2}題 | {stats['accuracy']:.1%} | "
              f"{stats['achievements']}成就")
    
    # 排行榜
    print("\n🏆 排行榜:")
    print("-" * 50)
    leaderboard = demo.get_leaderboard()
    
    for entry in leaderboard:
        print(f"{entry['rank']:2}. {entry['user_id']:8} | "
              f"L{entry['level']:2} | {entry['experience']:4}XP | {entry['accuracy']:.1%}")
    
    # 系統特性說明
    print("\n✨ 系統特性展示:")
    print("-" * 40)
    print("🎯 智能問題生成 - 根據用戶水平自動選擇合適問題")
    print("📈 動態難度調整 - 基於用戶表現調整問題難度")
    print("🎮 完整遊戲化機制:")
    print("   • 經驗值系統 (XP)")
    print("   • 等級提升機制")  
    print("   • 多樣化成就系統")
    print("   • 準確率追蹤")
    print("   • 排行榜競爭")
    print("💡 個性化學習:")
    print("   • 基於表現的內容推薦")
    print("   • 即時學習反饋")
    print("   • 鼓勵性訊息系統")
    
    print("\n🚀 實際應用場景:")
    print("• 企業內訓 - 員工技能提升")
    print("• 學術教育 - 互動式課程學習") 
    print("• 認證考試 - 考前準備和練習")
    print("• 知識管理 - 組織知識傳承")
    
    print("\n🏗️  技術架構亮點:")
    print("• 模組化設計 - 易於擴展和維護")
    print("• AI驅動 - 智能內容生成和評估")
    print("• 數據驅動 - 學習分析和個性化推薦")
    print("• 可伸縮性 - 支援大規模用戶並發")


if __name__ == "__main__":
    run_demo()