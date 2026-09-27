"""
Preparation Plan model schemas.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TopicCategory(str, Enum):
    DSA = "DSA"
    SQL = "SQL"
    JAVA = "Java"
    PYTHON = "Python"
    OOP = "OOP"
    DBMS = "DBMS"
    OS = "OS"
    CN = "CN"
    APTITUDE = "Aptitude"
    SYSTEM_DESIGN = "System Design"
    BEHAVIORAL = "Behavioral"
    COMMUNICATION = "Communication"
    SPRING_BOOT = "Spring Boot"
    REST_API = "REST API"


class DailyTask(BaseModel):
    # topic is a plain str so LLM-returned values like "Spring Boot" work without
    # needing to exactly match an enum member.
    topic: str
    subtopic: str
    duration_minutes: int
    resources: List[str] = []
    practice_questions: int = 5
    difficulty: str = "medium"   # plain str; LLM may return "easy"/"medium"/"hard"
    completed: bool = False
    score: Optional[float] = None


class DayPlan(BaseModel):
    day: int
    date: Optional[str] = None
    focus_areas: List[str] = []
    tasks: List[DailyTask] = []
    total_duration_minutes: int = 0
    completed: bool = False
    performance_score: Optional[float] = None


class PreparationPlan(BaseModel):
    id: Optional[str] = None
    user_id: str
    skill_gap_id: str
    target_role: str
    target_company: Optional[str] = None
    timeline_days: int  # 7, 14, or 30
    days: List[DayPlan] = []
    overall_progress: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    active: bool = True


class PlanGenerateRequest(BaseModel):
    user_id: str
    skill_gap_id: str
    timeline_days: int = 30
    hours_per_day: float = 3.0
