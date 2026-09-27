"""
Resume upload, analysis, and improvement endpoints.
NOTE: /user/{user_id} and /improve declared before /{resume_id} to prevent route shadowing.
"""

from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional

from app.services.resume_parser import parse_resume, get_resume_improvements
from app.core.database import get_resumes_collection
from app.core.config import settings

router = APIRouter()

MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# ── Upload & Parse ────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload_resume(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a resume (PDF/DOCX) and get AI analysis."""
    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files supported")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

    try:
        analysis = await parse_resume(user_id, file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

    # Save to MongoDB
    col = get_resumes_collection()
    doc = analysis.model_dump()
    doc["filename"] = file.filename
    result = await col.insert_one(doc)
    resume_id = str(result.inserted_id)

    return {
        "resume_id": resume_id,
        "analysis": analysis.model_dump(),
        "message": "Resume parsed successfully",
    }


# ── Resume Improvement ────────────────────────────────────────────────────────
class ImprovementRequest(BaseModel):
    resume_id: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None


@router.post("/improve")
async def improve_resume(request: ImprovementRequest):
    """
    Analyse a parsed resume and return specific actionable improvement suggestions.
    Includes: section scores, quick wins, ATS score, missing keywords, rewritten summary.
    """
    from bson import ObjectId
    col = get_resumes_collection()

    try:
        doc = await col.find_one({"_id": ObjectId(request.resume_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID")

    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Build resume data dict for the analyser
    resume_data = {
        "skills":       doc.get("skills") or [],
        "projects":     doc.get("projects") or [],
        "experiences":  doc.get("experiences") or [],
        "education":    doc.get("education") or [],
        "summary":      doc.get("summary") or "",
        "strengths":    doc.get("strengths") or [],
        "areas_of_improvement": doc.get("areas_of_improvement") or [],
    }

    try:
        improvements = await get_resume_improvements(
            resume_data=resume_data,
            target_role=request.target_role,
            target_company=request.target_company,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement analysis failed: {str(e)}")

    # Cache improvements in the resume doc
    await col.update_one(
        {"_id": ObjectId(request.resume_id)},
        {"$set": {"improvements": improvements, "improvements_updated": datetime.utcnow()}},
    )

    return {
        "resume_id": request.resume_id,
        "improvements": improvements,
    }


# ── GET routes — specific paths BEFORE wildcard /{resume_id} ─────────────────
@router.get("/user/{user_id}")
async def get_user_resumes(user_id: str):
    """Get all resumes for a user."""
    col = get_resumes_collection()
    docs = await col.find({"user_id": user_id}).sort("created_at", -1).to_list(length=10)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"resumes": docs}


@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """Fetch a previously analyzed resume."""
    from bson import ObjectId
    col = get_resumes_collection()
    doc = await col.find_one({"_id": ObjectId(resume_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    doc["id"] = str(doc.pop("_id"))
    return doc
