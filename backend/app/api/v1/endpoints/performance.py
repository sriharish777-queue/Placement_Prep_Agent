"""
Performance tracking and readiness score endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.services.adaptive_engine import compute_readiness_score, generate_weakness_report
from app.models.performance import PerformanceSession
from app.core.database import get_performance_collection
from datetime import datetime

router = APIRouter()


@router.post("/session")
async def log_session(session: PerformanceSession):
    """Log a practice session's performance data."""
    col = get_performance_collection()
    doc = session.dict()
    doc["started_at"] = doc.get("started_at") or datetime.utcnow()
    result = await col.insert_one(doc)
    return {"session_id": str(result.inserted_id), "message": "Session logged"}


@router.get("/readiness/{user_id}")
async def get_readiness_score(user_id: str):
    """Get the current placement readiness score for a user."""
    try:
        score = await compute_readiness_score(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return score.dict()


@router.get("/weakness/{user_id}")
async def get_weakness_report(user_id: str):
    """Get a weakness detection report for a user."""
    try:
        report = await generate_weakness_report(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return report.dict()


@router.get("/history/{user_id}")
async def get_performance_history(user_id: str, limit: int = 20):
    """Get performance session history for a user."""
    col = get_performance_collection()
    docs = await col.find({"user_id": user_id}).sort("started_at", -1).to_list(length=limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"sessions": docs, "count": len(docs)}


@router.get("/topics/{user_id}")
async def get_topic_breakdown(user_id: str):
    """Get per-topic score breakdown for a user."""
    from app.services.adaptive_engine import compute_topic_scores
    try:
        scores = await compute_topic_scores(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"topic_scores": [s.dict() for s in scores]}
