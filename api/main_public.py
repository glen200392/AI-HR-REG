"""
Public Educational Platform API
Allows anonymous access for anyone with the link
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn

from gamified_education_api import gamification_router, initialize_gamification_agent
from agents.gamified_education_agent import GamifiedEducationAgent
from agents.rag_agent import RAGKnowledgeAgent
from core.simple_llm import SimpleLLM

app = FastAPI(
    title="Public Educational Platform",
    description="Gamified learning platform accessible to anyone with the link",
    version="1.0.0"
)

# CORS middleware for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the gamification router
app.include_router(gamification_router)

@app.on_event("startup")
async def startup_event():
    """Initialize the gamification system on startup"""
    try:
        # Initialize simple LLM (you may need to configure this)
        llm = SimpleLLM()
        
        # Initialize RAG agent (simplified for demo)
        rag_agent = RAGKnowledgeAgent(llm=llm)
        
        # Initialize gamification agent
        gamification_agent = GamifiedEducationAgent(rag_agent=rag_agent)
        
        # Register the agent globally
        initialize_gamification_agent(gamification_agent)
        
        print("✅ Educational platform initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize platform: {e}")
        # Continue anyway for demo purposes

@app.get("/")
async def root():
    """Root endpoint with platform info"""
    return {
        "message": "Welcome to the Public Educational Platform! 🎓",
        "features": [
            "🎮 Gamified Learning Experience",
            "🏆 Achievement System", 
            "📊 Progress Tracking",
            "🎯 Adaptive Difficulty",
            "🤖 AI-Generated Questions"
        ],
        "endpoints": {
            "start_session": "/api/gamification/sessions/start",
            "topics": "/api/gamification/topics",
            "leaderboard": "/api/gamification/leaderboard"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    print("🚀 Starting Public Educational Platform...")
    uvicorn.run(
        "main_public:app",
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=True
    )