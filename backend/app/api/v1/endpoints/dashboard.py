"""
Dashboard summary endpoint — aggregates everything for the home screen.
"""

from fastapi import APIRouter, HTTPException
from app.core.database import (
    get_resumes_collection,
    get_plans_collection,
    get_performance_collection,
    get_interviews_collection,
    get_database,
)
from app.services.adaptive_engine import compute_readiness_score
from bson import ObjectId

router = APIRouter()


@router.get("/{user_id}")
async def get_dashboard(user_id: str):
    """
    Return a consolidated dashboard view:
    - Latest resume
    - Active plan progress
    - Readiness score
    - Recent sessions
    - Interview history summary
    """
    # Readiness score
    try:
        readiness = await compute_readiness_score(user_id)
        readiness_data = readiness.dict()
    except Exception:
        readiness_data = {"overall_score": 0, "interview_readiness": 0, "topic_scores": []}

    # Latest resume
    resume_col = get_resumes_collection()
    latest_resume = await resume_col.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )
    resume_summary = None
    if latest_resume:
        resume_summary = {
            "id": str(latest_resume["_id"]),
            "skills": latest_resume.get("skills", [])[:10],
            "skills_count": len(latest_resume.get("skills", [])),
            "projects_count": len(latest_resume.get("projects", [])),
        }

    # Active plan
    plan_col = get_plans_collection()
    active_plan = await plan_col.find_one(
        {"user_id": user_id, "active": True},
        sort=[("created_at", -1)],
    )
    plan_summary = None
    if active_plan:
        days = active_plan.get("days", [])
        completed_days = [d for d in days if d.get("completed")]
        today_day = len(completed_days) + 1
        today_plan = next((d for d in days if d.get("day") == today_day), None)
        plan_summary = {
            "id": str(active_plan["_id"]),
            "target_role": active_plan.get("target_role"),
            "target_company": active_plan.get("target_company"),
            "timeline_days": active_plan.get("timeline_days"),
            "overall_progress": active_plan.get("overall_progress", 0),
            "current_day": today_day,
            "today_focus": today_plan.get("focus_areas", []) if today_plan else [],
            "today_tasks_count": len(today_plan.get("tasks", [])) if today_plan else 0,
        }

    # Recent sessions
    perf_col = get_performance_collection()
    recent_sessions = await perf_col.find(
        {"user_id": user_id}
    ).sort("started_at", -1).to_list(length=5)
    for s in recent_sessions:
        s["id"] = str(s.pop("_id"))

    # Interview stats
    interview_col = get_interviews_collection()
    total_interviews = await interview_col.count_documents({"user_id": user_id})
    completed_interviews = await interview_col.count_documents(
        {"user_id": user_id, "status": "completed"}
    )

    # Streak (consecutive days with sessions)
    all_sessions = await perf_col.find(
        {"user_id": user_id}
    ).sort("started_at", -1).to_list(length=100)
    streak = _compute_streak(all_sessions)

    return {
        "readiness": readiness_data,
        "resume": resume_summary,
        "active_plan": plan_summary,
        "recent_sessions": recent_sessions,
        "stats": {
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "practice_streak_days": streak,
            "total_sessions": len(all_sessions),
        },
    }


def _compute_streak(sessions: list) -> int:
    """Compute consecutive days of practice."""
    from datetime import datetime, timedelta
    if not sessions:
        return 0
    dates = set()
    for s in sessions:
        started = s.get("started_at")
        if started:
            if isinstance(started, str):
                try:
                    started = datetime.fromisoformat(started)
                except Exception:
                    continue
            dates.add(started.date())

    today = datetime.utcnow().date()
    streak = 0
    check_date = today
    while check_date in dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak
