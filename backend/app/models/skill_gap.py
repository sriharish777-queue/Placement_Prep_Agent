"""
Skill Gap Analysis model schemas.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class SkillLevel(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    MISSING = "missing"


class SkillGapItem(BaseModel):
    skill: str
    level: SkillLevel
    importance: str  # high / medium / low
    reason: str


class SkillGapAnalysis(BaseModel):
    user_id: str
    resume_id: str
    job_description: str
    target_role: str
    target_company: Optional[str] = None
    match_percentage: float
    strong_skills: List[str] = []
    moderate_skills: List[str] = []
    weak_skills: List[str] = []
    missing_skills: List[str] = []
    skill_gaps: List[SkillGapItem] = []
    priority_order: List[str] = []
    recommended_timeline: str  # e.g. "30 days"
    analysis_summary: str


class SkillGapRequest(BaseModel):
    user_id: str
    resume_id: str
    job_description: str
    target_role: str
    target_company: Optional[str] = None
