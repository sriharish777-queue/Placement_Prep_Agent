

from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class InterviewType(str, Enum):
    TECHNICAL = "technical"
    HR = "hr"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    MIXED = "mixed"


class InterviewMessage(BaseModel):
    role: str           # "interviewer" | "candidate"
    content: str
    timestamp: Optional[datetime] = None
    evaluation: Optional[Dict] = None  # AI evaluation of candidate answer


class InterviewEvaluation(BaseModel):
    correctness: float         # 0–10
    relevance: float           # 0–10
    technical_depth: float     # 0–10
    communication: float       # 0–10
    confidence: float          # 0–10
    missing_concepts: List[str] = []
    strengths: List[str] = []
    improvements: List[str] = []
    overall_score: float       # 0–10
    feedback: str


class MockInterview(BaseModel):
    id: Optional[str] = None
    user_id: str
    interview_type: InterviewType
    target_role: str
    target_company: Optional[str] = None
    conversation: List[InterviewMessage] = []
    final_evaluation: Optional[InterviewEvaluation] = None
    duration_minutes: Optional[int] = None
    status: str = "active"    # active / completed
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class InterviewStartRequest(BaseModel):
    user_id: str
    interview_type: InterviewType
    target_role: str
    target_company: Optional[str] = None
    focus_topics: Optional[List[str]] = None


class InterviewMessageRequest(BaseModel):
    interview_id: str
    user_id: str
    message: str
