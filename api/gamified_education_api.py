"""
遊戲化教學API
為遊戲化教學AI Agent提供Web API接口
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import random

from agents.gamified_education_agent import (
    GamifiedEducationAgent, 
    DifficultyLevel, 
    QuestionType,
    LearningSession,
    LearningProgress
)

# 創建路由器
gamification_router = APIRouter(prefix="/api/gamification", tags=["gamification"])

# 全局變量
gamification_agent: Optional[GamifiedEducationAgent] = None

# Pydantic 模型
class StartSessionRequest(BaseModel):
    user_id: Optional[str] = None  # Allow anonymous users
    topic: str
    difficulty: str = "初級"
    question_count: int = 5

class StartSessionResponse(BaseModel):
    session_id: str
    topic: str
    difficulty: str
    first_question: Dict[str, Any]
    total_questions: int

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str
    response_time: float = 30.0

class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    score: int
    feedback: str
    explanation: str
    new_achievements: List[Dict[str, Any]]
    level_up: Optional[Dict[str, Any]]
    session_completed: bool
    progress: Dict[str, Any]
    next_question: Optional[Dict[str, Any]] = None

class UserProgressResponse(BaseModel):
    user_id: str
    level: int
    experience: int
    streak: int
    best_streak: int
    accuracy: float
    achievements_count: int
    topics_mastered: List[str]
    recommendations: Dict[str, Any]

class LeaderboardEntry(BaseModel):
    user_id: str
    level: int
    experience: int
    accuracy: float
    achievements_count: int

class GenerateQuestionRequest(BaseModel):
    topic: str
    difficulty: str = "初級"

class LearningAnalyticsResponse(BaseModel):
    total_users: int
    total_questions_answered: int
    average_accuracy: float
    popular_topics: List[str]
    recent_achievements: List[Dict[str, Any]]

# 依賴注入
async def get_gamification_agent() -> GamifiedEducationAgent:
    """獲取遊戲化教學代理實例"""
    global gamification_agent
    if gamification_agent is None:
        raise HTTPException(status_code=503, detail="遊戲化教學系統尚未初始化")
    return gamification_agent

def initialize_gamification_agent(agent: GamifiedEducationAgent):
    """初始化遊戲化教學代理"""
    global gamification_agent
    gamification_agent = agent

# 學習會話管理
@gamification_router.post("/sessions/start", response_model=StartSessionResponse)
async def start_learning_session(
    request: StartSessionRequest,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """開始新的學習會話"""
    try:
        # Generate anonymous user ID if not provided
        user_id = request.user_id or f"anonymous_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
        
        # 轉換難度等級
        difficulty_map = {
            "初級": DifficultyLevel.BEGINNER,
            "中級": DifficultyLevel.INTERMEDIATE,
            "高級": DifficultyLevel.ADVANCED,
            "專家": DifficultyLevel.EXPERT
        }
        difficulty = difficulty_map.get(request.difficulty, DifficultyLevel.BEGINNER)
        
        session = await agent.start_learning_session(
            user_id=user_id,
            topic=request.topic,
            difficulty=difficulty,
            question_count=request.question_count
        )
        
        first_question = session.questions[0]
        
        return StartSessionResponse(
            session_id=session.session_id,
            topic=session.topic,
            difficulty=session.difficulty.value,
            first_question={
                "id": first_question.id,
                "question": first_question.question,
                "options": first_question.options,
                "type": first_question.question_type.value,
                "exp_reward": first_question.exp_reward
            },
            total_questions=len(session.questions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"創建學習會話失敗: {str(e)}")

@gamification_router.post("/sessions/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """提交問題答案"""
    try:
        result = await agent.submit_answer(
            session_id=request.session_id,
            answer=request.answer,
            response_time=request.response_time
        )
        
        return SubmitAnswerResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"提交答案失敗: {str(e)}")

@gamification_router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取學習會話狀態"""
    try:
        if session_id not in agent.active_sessions:
            raise HTTPException(status_code=404, detail="會話不存在")
        
        session = agent.active_sessions[session_id]
        
        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "difficulty": session.difficulty.value,
            "current_question": session.current_question_index,
            "total_questions": len(session.questions),
            "score": session.score,
            "is_completed": session.is_completed,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取會話狀態失敗: {str(e)}")

# 用戶進度管理
@gamification_router.get("/users/{user_id}/progress", response_model=UserProgressResponse)
async def get_user_progress(
    user_id: str,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取用戶學習進度"""
    try:
        progress = agent.get_user_progress(user_id)
        recommendations = await agent.get_learning_recommendations(user_id)
        
        return UserProgressResponse(
            user_id=progress.user_id,
            level=progress.current_level,
            experience=progress.total_experience,
            streak=progress.current_streak,
            best_streak=progress.best_streak,
            accuracy=progress.correct_answers / max(1, progress.questions_answered),
            achievements_count=len(progress.achievements),
            topics_mastered=progress.topics_mastered,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取用戶進度失敗: {str(e)}")

@gamification_router.get("/users/{user_id}/achievements")
async def get_user_achievements(
    user_id: str,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取用戶成就列表"""
    try:
        progress = agent.get_user_progress(user_id)
        unlocked_achievements = []
        locked_achievements = []
        
        for achievement in agent.achievements:
            achievement_data = {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "type": achievement.type.value,
                "reward_exp": achievement.reward_exp,
                "unlocked": achievement.id in progress.achievements
            }
            
            if achievement.id in progress.achievements:
                unlocked_achievements.append(achievement_data)
            else:
                locked_achievements.append(achievement_data)
        
        return {
            "unlocked": unlocked_achievements,
            "locked": locked_achievements,
            "total_unlocked": len(unlocked_achievements),
            "completion_rate": len(unlocked_achievements) / len(agent.achievements)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取用戶成就失敗: {str(e)}")

@gamification_router.get("/users/{user_id}/stats")
async def get_user_statistics(
    user_id: str,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取用戶詳細統計信息"""
    try:
        progress = agent.get_user_progress(user_id)
        
        # 計算各種統計指標
        accuracy = progress.correct_answers / max(1, progress.questions_answered)
        exp_to_next_level = ((progress.current_level) ** 2) * 100 - progress.total_experience
        
        return {
            "user_id": user_id,
            "current_level": progress.current_level,
            "total_experience": progress.total_experience,
            "exp_to_next_level": max(0, exp_to_next_level),
            "questions_answered": progress.questions_answered,
            "correct_answers": progress.correct_answers,
            "accuracy": accuracy,
            "current_streak": progress.current_streak,
            "best_streak": progress.best_streak,
            "topics_mastered": len(progress.topics_mastered),
            "achievements_unlocked": len(progress.achievements),
            "last_activity": progress.last_activity.isoformat(),
            "performance_rating": self._calculate_performance_rating(accuracy, progress.current_level)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取用戶統計失敗: {str(e)}")

def _calculate_performance_rating(accuracy: float, level: int) -> str:
    """計算表現評級"""
    score = accuracy * 100 + level * 5
    
    if score >= 95:
        return "卓越 🏆"
    elif score >= 85:
        return "優秀 🌟"
    elif score >= 75:
        return "良好 👏"
    elif score >= 65:
        return "不錯 👍"
    else:
        return "加油 💪"

# 問題生成
@gamification_router.post("/questions/generate")
async def generate_question(
    request: GenerateQuestionRequest,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """生成單個學習問題"""
    try:
        difficulty_map = {
            "初級": DifficultyLevel.BEGINNER,
            "中級": DifficultyLevel.INTERMEDIATE,
            "高級": DifficultyLevel.ADVANCED,
            "專家": DifficultyLevel.EXPERT
        }
        difficulty = difficulty_map.get(request.difficulty, DifficultyLevel.BEGINNER)
        
        questions = await agent._generate_questions(request.topic, difficulty, 1)
        
        if not questions:
            raise HTTPException(status_code=500, detail="無法生成問題")
        
        question = questions[0]
        
        return {
            "id": question.id,
            "question": question.question,
            "options": question.options,
            "type": question.question_type.value,
            "difficulty": question.difficulty.value,
            "topic": question.topic,
            "exp_reward": question.exp_reward,
            "preview_mode": True  # 標記為預覽模式，不計入統計
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成問題失敗: {str(e)}")

# 排行榜
@gamification_router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取排行榜"""
    try:
        # 獲取所有用戶進度並排序
        all_progress = list(agent.user_progress.values())
        
        # 按經驗值排序
        leaderboard = sorted(
            all_progress,
            key=lambda x: (x.total_experience, x.correct_answers / max(1, x.questions_answered)),
            reverse=True
        )[:limit]
        
        leaderboard_data = []
        for i, progress in enumerate(leaderboard):
            accuracy = progress.correct_answers / max(1, progress.questions_answered)
            
            leaderboard_data.append({
                "rank": i + 1,
                "user_id": progress.user_id[:8] + "***",  # 隱私保護
                "level": progress.current_level,
                "experience": progress.total_experience,
                "accuracy": accuracy,
                "achievements_count": len(progress.achievements),
                "streak": progress.current_streak
            })
        
        return {
            "leaderboard": leaderboard_data,
            "total_users": len(all_progress),
            "update_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取排行榜失敗: {str(e)}")

# 學習分析
@gamification_router.get("/analytics", response_model=LearningAnalyticsResponse)
async def get_learning_analytics(
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取學習分析數據"""
    try:
        all_progress = list(agent.user_progress.values())
        
        total_users = len(all_progress)
        total_questions = sum(p.questions_answered for p in all_progress)
        total_correct = sum(p.correct_answers for p in all_progress)
        average_accuracy = total_correct / max(1, total_questions)
        
        # 統計熱門主題
        topic_counter = {}
        for progress in all_progress:
            for topic in progress.topics_mastered:
                topic_counter[topic] = topic_counter.get(topic, 0) + 1
        
        popular_topics = sorted(topic_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        popular_topics = [topic for topic, count in popular_topics]
        
        # 最近解鎖的成就
        recent_achievements = []
        for progress in all_progress:
            if progress.achievements:
                for achievement_id in progress.achievements[-3:]:  # 最近3個成就
                    achievement = next((a for a in agent.achievements if a.id == achievement_id), None)
                    if achievement:
                        recent_achievements.append({
                            "user_id": progress.user_id[:8] + "***",
                            "achievement_name": achievement.name,
                            "achievement_icon": achievement.icon,
                            "unlock_date": progress.last_activity.isoformat()
                        })
        
        return LearningAnalyticsResponse(
            total_users=total_users,
            total_questions_answered=total_questions,
            average_accuracy=average_accuracy,
            popular_topics=popular_topics,
            recent_achievements=recent_achievements[-10:]  # 最近10個
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取學習分析失敗: {str(e)}")

# 學習建議
@gamification_router.get("/users/{user_id}/recommendations")
async def get_learning_recommendations(
    user_id: str,
    agent: GamifiedEducationAgent = Depends(get_gamification_agent)
):
    """獲取個性化學習推薦"""
    try:
        recommendations = await agent.get_learning_recommendations(user_id)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取學習推薦失敗: {str(e)}")

# 主題管理
@gamification_router.get("/topics")
async def get_available_topics():
    """獲取可用的學習主題"""
    topics = [
        {
            "id": "hr_basics",
            "name": "HR基礎概念",
            "description": "人力資源管理的基本概念和原理",
            "difficulty_levels": ["初級", "中級"],
            "estimated_questions": 20
        },
        {
            "id": "recruitment",
            "name": "招聘流程",
            "description": "招聘策略、面試技巧和人才選拔",
            "difficulty_levels": ["初級", "中級", "高級"],
            "estimated_questions": 25
        },
        {
            "id": "employee_relations",
            "name": "員工關係",
            "description": "員工溝通、衝突處理和團隊合作",
            "difficulty_levels": ["中級", "高級"],
            "estimated_questions": 18
        },
        {
            "id": "labor_law",
            "name": "勞動法規",
            "description": "勞動法律法規和合規要求",
            "difficulty_levels": ["中級", "高級", "專家"],
            "estimated_questions": 30
        },
        {
            "id": "compensation",
            "name": "薪資管理",
            "description": "薪資設計、績效評估和激勵制度",
            "difficulty_levels": ["中級", "高級", "專家"],
            "estimated_questions": 22
        },
        {
            "id": "training_development",
            "name": "培訓發展",
            "description": "員工培訓、職涯發展和學習規劃",
            "difficulty_levels": ["初級", "中級", "高級"],
            "estimated_questions": 20
        }
    ]
    
    return {
        "topics": topics,
        "total_topics": len(topics)
    }

# 遊戲化設定
@gamification_router.get("/config")
async def get_gamification_config():
    """獲取遊戲化配置信息"""
    return {
        "experience_system": {
            "level_formula": "level = floor(sqrt(experience / 100)) + 1",
            "exp_per_question": {
                "初級": "10-20",
                "中級": "20-35", 
                "高級": "35-50",
                "專家": "50-90"
            }
        },
        "achievement_categories": [
            {
                "type": "學習連續",
                "description": "連續學習天數相關成就"
            },
            {
                "type": "知識達人",
                "description": "掌握主題數量相關成就"
            },
            {
                "type": "快速學習者",
                "description": "回答速度相關成就"
            },
            {
                "type": "完美主義者",
                "description": "準確率相關成就"
            },
            {
                "type": "探索者",
                "description": "學習範圍相關成就"
            }
        ],
        "question_types": [
            "選擇題",
            "是非題", 
            "填空題",
            "簡答題",
            "情境題"
        ],
        "difficulty_levels": [
            "初級",
            "中級",
            "高級",
            "專家"
        ]
    }