"""
Question model schemas.
"""

from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum
from datetime import datetime


class QuestionType(str, Enum):
    MCQ = "mcq"
    CODING = "coding"
    SHORT_ANSWER = "short_answer"
    SQL = "sql"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class Question(BaseModel):
    id: Optional[str] = None
    category: str  # DSA, SQL, Java, etc.
    subcategory: str  # Arrays, Joins, OOP, etc.
    question_text: str
    question_type: QuestionType
    difficulty: str  # easy / medium / hard
    options: Optional[List[str]] = None        # for MCQ
    correct_answer: Optional[str] = None       # for MCQ / short
    explanation: Optional[str] = None
    hints: List[str] = []
    tags: List[str] = []
    company_tags: List[str] = []
    time_limit_seconds: int = 300
    created_at: Optional[datetime] = None


class QuestionGenerateRequest(BaseModel):
    user_id: Optional[str] = None   # optional — not required for generation
    category: str
    subcategory: Optional[str] = None
    difficulty: str = "medium"
    count: int = 5
    question_type: Optional[QuestionType] = None


class QuestionAttempt(BaseModel):
    user_id: str
    question_id: Optional[str] = ""   # optional — in-session questions may not be in DB
    session_id: str
    user_answer: str
    time_taken_seconds: int
    is_correct: Optional[bool] = None
    ai_score: Optional[float] = None
    ai_feedback: Optional[str] = None
    submitted_at: Optional[datetime] = None
