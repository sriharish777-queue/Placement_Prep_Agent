"""
Resume model schemas.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class Project(BaseModel):
    title: str
    description: str
    technologies: List[str] = []


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: str
    technologies: List[str] = []


class Education(BaseModel):
    institution: str
    degree: str
    field: str
    year: str
    cgpa: Optional[str] = None


class ResumeAnalysis(BaseModel):
    user_id: str
    raw_text: str
    skills: List[str] = []
    projects: List[Project] = []
    experiences: List[Experience] = []
    education: List[Education] = []
    certifications: List[str] = []
    languages: List[str] = []
    summary: Optional[str] = None
    strengths: List[str] = []
    areas_of_improvement: List[str] = []
    created_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


class ResumeUploadResponse(BaseModel):
    resume_id: str
    analysis: ResumeAnalysis
    message: str
