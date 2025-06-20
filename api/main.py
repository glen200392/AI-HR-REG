"""
AI Talent Ecosystem Platform - Main API Gateway
基於FastAPI的微服務架構入口
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.master_orchestrator import MasterOrchestrator, AnalysisContext, Priority
from agents.brain_agent import BrainAgent
from agents.talent_agent import TalentAgent
from agents.culture_agent import CultureAgent
from agents.future_agent import FutureAgent
from agents.process_agent import ProcessAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Talent Ecosystem Platform",
    description="Multi-Agent HR AI Platform for Predictive Talent Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()

# Request/Response Models
class AnalysisRequest(BaseModel):
    employee_data: Dict[str, Any] = Field(..., description="Employee data for analysis")
    organizational_data: Dict[str, Any] = Field(..., description="Organizational context data")
    priority_goals: List[str] = Field(default=[], description="Priority business goals")
    time_horizon: str = Field(default="medium_term", description="Analysis time horizon")
    urgency_level: str = Field(default="medium", description="Urgency level")
    business_context: Dict[str, Any] = Field(default={}, description="Business context")

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: datetime
    recommendations: List[Dict[str, Any]]
    risks: List[str]
    opportunities: List[str]
    confidence_score: float
    data_quality_score: float
    processing_time_seconds: float
    agent_insights: Dict[str, Any]

class AgentAnalysisRequest(BaseModel):
    agent_type: str = Field(..., description="Type of agent analysis")
    context_data: Dict[str, Any] = Field(..., description="Context data for analysis")

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    agents_status: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None

# Global instances
master_orchestrator = None
individual_agents = {}

@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup"""
    global master_orchestrator, individual_agents
    
    logger.info("Initializing AI Talent Ecosystem Platform...")
    
    try:
        # Initialize Master Orchestrator
        master_orchestrator = MasterOrchestrator()
        
        # Initialize individual agents
        individual_agents = {
            'brain': BrainAgent(),
            'talent': TalentAgent(),
            'culture': CultureAgent(),
            'future': FutureAgent(),
            'process': ProcessAgent()
        }
        
        logger.info("All agents initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Talent Ecosystem Platform...")

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate authentication token"""
    # Implement your authentication logic here
    # For now, we'll accept any token for development
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"user_id": "demo_user", "permissions": ["read", "write"]}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    
    agents_status = {}
    
    # Check agent status
    if master_orchestrator:
        agents_status["master_orchestrator"] = "healthy"
    else:
        agents_status["master_orchestrator"] = "unavailable"
    
    for agent_name, agent in individual_agents.items():
        if agent:
            agents_status[agent_name] = "healthy"
        else:
            agents_status[agent_name] = "unavailable"
    
    return HealthCheckResponse(
        status="healthy" if all(status == "healthy" for status in agents_status.values()) else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        agents_status=agents_status
    )

# Main comprehensive analysis endpoint
@app.post("/api/v1/analyze/comprehensive", response_model=AnalysisResponse)
async def comprehensive_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform comprehensive multi-agent analysis
    """
    start_time = datetime.now()
    analysis_id = f"analysis_{start_time.strftime('%Y%m%d_%H%M%S')}_{current_user['user_id']}"
    
    try:
        logger.info(f"Starting comprehensive analysis {analysis_id}")
        
        if not master_orchestrator:
            raise HTTPException(status_code=503, detail="Master Orchestrator not available")
        
        # Convert priority level
        priority_map = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM, 
            "high": Priority.HIGH,
            "critical": Priority.CRITICAL
        }
        urgency_level = priority_map.get(request.urgency_level.lower(), Priority.MEDIUM)
        
        # Create analysis context
        context = AnalysisContext(
            employee_data=request.employee_data,
            organizational_data=request.organizational_data,
            priority_goals=request.priority_goals,
            time_horizon=request.time_horizon,
            urgency_level=urgency_level,
            business_context=request.business_context
        )
        
        # Perform comprehensive analysis
        integrated_strategy = await master_orchestrator.analyze_comprehensive(context)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=start_time,
            recommendations=(
                integrated_strategy.individual_recommendations +
                integrated_strategy.team_recommendations +
                integrated_strategy.organizational_recommendations
            ),
            risks=integrated_strategy.risk_mitigation,
            opportunities=[],  # Can be extracted from agent insights
            confidence_score=integrated_strategy.priority_score,
            data_quality_score=0.8,  # Could be calculated from individual agents
            processing_time_seconds=processing_time,
            agent_insights={
                "implementation_timeline": integrated_strategy.implementation_timeline,
                "success_metrics": integrated_strategy.success_metrics,
                "priority_score": integrated_strategy.priority_score
            }
        )
        
        # Log analysis completion
        background_tasks.add_task(log_analysis_completion, analysis_id, processing_time)
        
        logger.info(f"Completed comprehensive analysis {analysis_id} in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Individual agent analysis endpoints
@app.post("/api/v1/analyze/brain")
async def brain_agent_analysis(
    request: AgentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Brain Agent - Learning and cognitive analysis"""
    try:
        if 'brain' not in individual_agents:
            raise HTTPException(status_code=503, detail="Brain Agent not available")
        
        # Create mock context for individual agent
        context = type('Context', (), {
            'employee_data': request.context_data.get('employee_data', {}),
            'organizational_data': request.context_data.get('organizational_data', {}),
            'priority_goals': request.context_data.get('priority_goals', [])
        })()
        
        result = await individual_agents['brain'].analyze_context(context)
        
        return {
            "agent": "brain",
            "analysis_type": "cognitive_learning",
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Brain agent analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Brain agent analysis failed: {str(e)}")

@app.post("/api/v1/analyze/talent")
async def talent_agent_analysis(
    request: AgentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Talent Agent - Talent ecosystem management"""
    try:
        if 'talent' not in individual_agents:
            raise HTTPException(status_code=503, detail="Talent Agent not available")
        
        context = type('Context', (), {
            'employee_data': request.context_data.get('employee_data', {}),
            'organizational_data': request.context_data.get('organizational_data', {}),
            'priority_goals': request.context_data.get('priority_goals', [])
        })()
        
        result = await individual_agents['talent'].analyze_context(context)
        
        return {
            "agent": "talent",
            "analysis_type": "talent_ecosystem",
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Talent agent analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Talent agent analysis failed: {str(e)}")

@app.post("/api/v1/analyze/culture")
async def culture_agent_analysis(
    request: AgentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Culture Agent - Organizational culture monitoring"""
    try:
        if 'culture' not in individual_agents:
            raise HTTPException(status_code=503, detail="Culture Agent not available")
        
        context = type('Context', (), {
            'employee_data': request.context_data.get('employee_data', {}),
            'organizational_data': request.context_data.get('organizational_data', {}),
            'priority_goals': request.context_data.get('priority_goals', [])
        })()
        
        result = await individual_agents['culture'].analyze_context(context)
        
        return {
            "agent": "culture",
            "analysis_type": "organizational_culture",
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Culture agent analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Culture agent analysis failed: {str(e)}")

@app.post("/api/v1/analyze/future")
async def future_agent_analysis(
    request: AgentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Future Agent - Trend prediction and scenario planning"""
    try:
        if 'future' not in individual_agents:
            raise HTTPException(status_code=503, detail="Future Agent not available")
        
        context = type('Context', (), {
            'employee_data': request.context_data.get('employee_data', {}),
            'organizational_data': request.context_data.get('organizational_data', {}),
            'business_context': request.context_data.get('business_context', {}),
            'priority_goals': request.context_data.get('priority_goals', [])
        })()
        
        result = await individual_agents['future'].analyze_context(context)
        
        return {
            "agent": "future",
            "analysis_type": "future_trends",
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Future agent analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Future agent analysis failed: {str(e)}")

@app.post("/api/v1/analyze/process")
async def process_agent_analysis(
    request: AgentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process Agent - Workflow optimization"""
    try:
        if 'process' not in individual_agents:
            raise HTTPException(status_code=503, detail="Process Agent not available")
        
        context = type('Context', (), {
            'employee_data': request.context_data.get('employee_data', {}),
            'organizational_data': request.context_data.get('organizational_data', {}),
            'priority_goals': request.context_data.get('priority_goals', [])
        })()
        
        result = await individual_agents['process'].analyze_context(context)
        
        return {
            "agent": "process",
            "analysis_type": "workflow_optimization",
            "result": result,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Process agent analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Process agent analysis failed: {str(e)}")

# Utility endpoints
@app.get("/api/v1/agents/status")
async def get_agents_status(current_user: dict = Depends(get_current_user)):
    """Get status of all agents"""
    
    status = {
        "master_orchestrator": {
            "available": master_orchestrator is not None,
            "capabilities": ["comprehensive_analysis", "strategy_integration"] if master_orchestrator else []
        }
    }
    
    for agent_name, agent in individual_agents.items():
        status[agent_name] = {
            "available": agent is not None,
            "capabilities": agent._get_capabilities() if hasattr(agent, '_get_capabilities') else ["analysis"]
        }
    
    return {
        "timestamp": datetime.now(),
        "agents_status": status,
        "total_agents": len(individual_agents) + 1,
        "available_agents": sum(1 for s in status.values() if s["available"])
    }

@app.get("/api/v1/capabilities")
async def get_platform_capabilities():
    """Get platform capabilities"""
    
    return {
        "platform_name": "AI Talent Ecosystem Platform",
        "version": "1.0.0",
        "capabilities": {
            "comprehensive_analysis": {
                "description": "Multi-agent comprehensive talent analysis",
                "agents_involved": ["brain", "talent", "culture", "future", "process"],
                "output": "integrated_strategy_recommendations"
            },
            "cognitive_analysis": {
                "description": "Learning and cognitive pattern analysis",
                "agent": "brain",
                "output": "learning_pathways_and_predictions"
            },
            "talent_matching": {
                "description": "Talent ecosystem optimization and matching",
                "agent": "talent",
                "output": "talent_recommendations_and_development_plans"
            },
            "culture_monitoring": {
                "description": "Organizational culture health monitoring",
                "agent": "culture",
                "output": "culture_insights_and_improvement_recommendations"
            },
            "future_planning": {
                "description": "Trend prediction and scenario planning",
                "agent": "future",
                "output": "future_scenarios_and_skill_forecasts"
            },
            "process_optimization": {
                "description": "Workflow and process efficiency optimization",
                "agent": "process",
                "output": "process_improvements_and_automation_opportunities"
            }
        },
        "supported_analysis_types": [
            "individual_analysis", "team_analysis", "organizational_analysis",
            "predictive_analysis", "prescriptive_recommendations"
        ],
        "data_requirements": {
            "employee_data": ["skills", "performance", "behavior", "preferences"],
            "organizational_data": ["culture", "processes", "structure", "goals"],
            "business_context": ["industry", "strategy", "market_conditions"]
        }
    }

# Background tasks
async def log_analysis_completion(analysis_id: str, processing_time: float):
    """Log analysis completion for monitoring"""
    logger.info(f"Analysis {analysis_id} completed in {processing_time:.2f} seconds")
    
    # Here you could save to database, send metrics, etc.
    pass

# Development/Testing endpoints
@app.post("/api/v1/test/sample-analysis")
async def sample_analysis():
    """Sample analysis for testing purposes"""
    
    sample_request = AnalysisRequest(
        employee_data={
            "id": "emp_001",
            "skills": {"leadership": 0.7, "technical": 0.8, "communication": 0.6},
            "performance_history": [0.8, 0.85, 0.9],
            "learning_preferences": {"style": "visual", "pace": "fast"},
            "career_goals": ["team_lead", "technical_expert"]
        },
        organizational_data={
            "team_culture": {
                "innovation": 0.8,
                "collaboration": 0.7,
                "autonomy": 0.6
            },
            "current_challenges": ["skill_gaps", "retention", "productivity"],
            "strategic_priorities": {"digital_transformation": 0.9, "talent_development": 0.8}
        },
        priority_goals=["skill_development", "retention", "performance"],
        time_horizon="medium_term",
        urgency_level="high"
    )
    
    # Mock user for testing
    mock_user = {"user_id": "test_user", "permissions": ["read", "write"]}
    
    # Create background tasks instance
    background_tasks = BackgroundTasks()
    
    return await comprehensive_analysis(sample_request, background_tasks, mock_user)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )