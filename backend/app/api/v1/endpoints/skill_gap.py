"""
Skill Gap Analysis endpoints.
NOTE: specific routes (/analyze, /user/{user_id}) MUST be declared
before the wildcard /{skill_gap_id} route to avoid shadowing.
"""

from fastapi import APIRouter, HTTPException
from app.services.skill_gap_engine import run_skill_gap_analysis
from app.models.skill_gap import SkillGapRequest
from app.core.database import get_database
from datetime import datetime

router = APIRouter()


@router.post("/analyze")
async def analyze_skill_gap(request: SkillGapRequest):
    """Run a full skill gap analysis against a job description."""
    try:
        analysis = await run_skill_gap_analysis(
            user_id=request.user_id,
            resume_id=request.resume_id,
            job_description=request.job_description,
            target_role=request.target_role,
            target_company=request.target_company,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Persist to DB
    db = get_database()
    doc = analysis.dict()
    doc["created_at"] = datetime.utcnow()
    result = await db["skill_gaps"].insert_one(doc)
    analysis_id = str(result.inserted_id)

    return {
        "skill_gap_id": analysis_id,
        "analysis": analysis.dict(),
    }


# NOTE: /user/{user_id} MUST come before /{skill_gap_id}
@router.get("/user/{user_id}")
async def get_user_skill_gaps(user_id: str):
    """Get all skill gap analyses for a user."""
    db = get_database()
    docs = await db["skill_gaps"].find({"user_id": user_id}).sort("created_at", -1).to_list(length=20)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"skill_gaps": docs}


@router.get("/{skill_gap_id}")
async def get_skill_gap(skill_gap_id: str):
    """Fetch a skill gap analysis by ID."""
    from bson import ObjectId
    db = get_database()
    doc = await db["skill_gaps"].find_one({"_id": ObjectId(skill_gap_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Skill gap analysis not found")
    doc["id"] = str(doc.pop("_id"))
    return doc
