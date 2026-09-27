"""
Job Description Intelligence Service
- Extract required skills, technologies, and experience requirements
- Compare with candidate resume
"""

import logging
from typing import Dict, List
from app.services.llm_client import chat_complete_json

logger = logging.getLogger(__name__)

JD_SYSTEM_PROMPT = """You are an expert job description analyzer and talent acquisition specialist.
Analyze the provided job description and extract structured information.
Return a valid JSON object with these exact keys:
{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", ...],
  "technologies": ["tech1", ...],
  "experience_years": "0-2 years / 2-5 years / etc.",
  "education_requirement": "B.Tech / MBA / etc.",
  "role_summary": "One paragraph summary of the role",
  "key_responsibilities": ["responsibility1", ...],
  "soft_skills": ["communication", ...],
  "domain": "backend / frontend / fullstack / data / devops / etc.",
  "seniority_level": "fresher / junior / mid / senior"
}
"""


async def analyze_job_description(jd_text: str) -> Dict:
    """Parse a job description into structured data."""
    messages = [
        {"role": "system", "content": JD_SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this job description:\n\n{jd_text[:6000]}"},
    ]
    return await chat_complete_json(messages, temperature=0.1)


async def compute_skill_match(
    resume_skills: List[str],
    jd_required: List[str],
    jd_preferred: List[str],
) -> Dict:
    """
    Compute match percentage and categorize skills.
    Returns: match_percentage, strong, moderate, weak, missing
    """
    prompt = f"""Given:
Candidate skills: {resume_skills}
Required skills: {jd_required}
Preferred skills: {jd_preferred}

Categorize each required/preferred skill for the candidate:
- strong: candidate clearly has it
- moderate: candidate has partial knowledge
- weak: candidate has minimal knowledge
- missing: not present at all

Return JSON:
{{
  "match_percentage": 72.5,
  "strong_skills": [...],
  "moderate_skills": [...],
  "weak_skills": [...],
  "missing_skills": [...],
  "analysis_summary": "..."
}}
"""
    messages = [
        {"role": "system", "content": "You are a technical skills assessment expert. Return only valid JSON."},
        {"role": "user", "content": prompt},
    ]
    return await chat_complete_json(messages, temperature=0.2)
