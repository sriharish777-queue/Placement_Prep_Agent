"""
Skill Gap Engine
- Combines resume analysis + JD analysis
- Produces prioritized skill gaps
- Generates recommended study timeline
"""

import logging
from datetime import datetime
from app.services.jd_analyzer import analyze_job_description, compute_skill_match
from app.services.llm_client import chat_complete_json
from app.models.skill_gap import SkillGapAnalysis, SkillGapItem, SkillLevel
from app.core.database import get_resumes_collection
from bson import ObjectId

logger = logging.getLogger(__name__)


async def run_skill_gap_analysis(
    user_id: str,
    resume_id: str,
    job_description: str,
    target_role: str,
    target_company: str = None,
) -> SkillGapAnalysis:
    """
    Full skill gap analysis pipeline:
    1. Fetch resume from DB
    2. Analyze JD
    3. Compute skill match
    4. Generate priority order
    5. Return SkillGapAnalysis
    """
    # 1. Fetch resume
    resumes_col = get_resumes_collection()
    resume_doc = await resumes_col.find_one({"_id": ObjectId(resume_id)})
    if not resume_doc:
        raise ValueError(f"Resume {resume_id} not found")

    resume_skills = resume_doc.get("skills", [])

    # 2. Analyze JD
    jd_data = await analyze_job_description(job_description)
    required_skills = jd_data.get("required_skills", [])
    preferred_skills = jd_data.get("preferred_skills", [])

    # 3. Compute skill match
    match_data = await compute_skill_match(resume_skills, required_skills, preferred_skills)

    # 4. Generate priority order with AI
    priority_prompt = f"""
Given these skill gaps for role "{target_role}"{f" at {target_company}" if target_company else ""}:
- Weak skills: {match_data.get("weak_skills", [])}
- Missing skills: {match_data.get("missing_skills", [])}
- Moderate skills: {match_data.get("moderate_skills", [])}

Provide a JSON object:
{{
  "priority_order": ["skill1", "skill2", ...],  // most critical first
  "skill_gaps": [
    {{"skill": "...", "level": "weak|missing|moderate", "importance": "high|medium|low", "reason": "..."}}
  ],
  "recommended_timeline": "30 days",
  "analysis_summary": "..."
}}
"""
    priority_data = await chat_complete_json(
        [
            {"role": "system", "content": "You are a career coach. Return only JSON."},
            {"role": "user", "content": priority_prompt},
        ],
        temperature=0.2,
    )

    gap_items = []
    for g in priority_data.get("skill_gaps", []):
        level_map = {
            "strong": SkillLevel.STRONG,
            "moderate": SkillLevel.MODERATE,
            "weak": SkillLevel.WEAK,
            "missing": SkillLevel.MISSING,
        }
        gap_items.append(
            SkillGapItem(
                skill=g.get("skill", ""),
                level=level_map.get(g.get("level", "missing"), SkillLevel.MISSING),
                importance=g.get("importance", "medium"),
                reason=g.get("reason", ""),
            )
        )

    return SkillGapAnalysis(
        user_id=user_id,
        resume_id=resume_id,
        job_description=job_description,
        target_role=target_role,
        target_company=target_company,
        match_percentage=match_data.get("match_percentage", 0.0),
        strong_skills=match_data.get("strong_skills", []),
        moderate_skills=match_data.get("moderate_skills", []),
        weak_skills=match_data.get("weak_skills", []),
        missing_skills=match_data.get("missing_skills", []),
        skill_gaps=gap_items,
        priority_order=priority_data.get("priority_order", []),
        recommended_timeline=priority_data.get("recommended_timeline", "30 days"),
        analysis_summary=priority_data.get("analysis_summary", match_data.get("analysis_summary", "")),
    )
