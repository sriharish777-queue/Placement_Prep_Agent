"""
Performance & Readiness Score model schemas.
"""

from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class TopicScore(BaseModel):
    topic: str
    score: float           # 0–100
    questions_attempted: int
    questions_correct: int
    average_time_seconds: float
    trend: str             # improving / declining / stable
    weak_subtopics: List[str] = []


class ReadinessScore(BaseModel):
    id: Optional[str] = None
    user_id: str
    overall_score: float   # 0–100
    interview_readiness: float
    topic_scores: List[TopicScore] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str
    computed_at: Optional[datetime] = None


class PerformanceSession(BaseModel):
    id: Optional[str] = None
    user_id: str
    plan_id: Optional[str] = None
    day: Optional[int] = None
    session_type: str      # practice / mock_interview / quiz
    topics_covered: List[str] = []
    questions_attempted: int = 0
    questions_correct: int = 0
    score: float = 0.0
    duration_minutes: int = 0
    feedback: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class WeaknessReport(BaseModel):
    user_id: str
    weak_topics: List[str] = []
    critical_gaps: List[str] = []
    suggested_focus: List[str] = []
    estimated_days_to_readiness: int
    generated_at: Optional[datetime] = None
