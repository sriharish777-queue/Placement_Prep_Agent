"""
Main API v1 router — collects all sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    resume,
    skill_gap,
    plan,
    questions,
    performance,
    mock_interview,
    rag,
    dashboard,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(skill_gap.router, prefix="/skill-gap", tags=["Skill Gap"])
api_router.include_router(plan.router, prefix="/plan", tags=["Preparation Plan"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
api_router.include_router(mock_interview.router, prefix="/interview", tags=["Mock Interview"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG Assistant"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
