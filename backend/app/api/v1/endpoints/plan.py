"""
Preparation Plan endpoints.
NOTE: /generate and /user/{user_id} declared before /{plan_id}
to prevent route shadowing.
"""

from fastapi import APIRouter, HTTPException
from app.services.plan_generator import generate_preparation_plan
from app.services.adaptive_engine import adapt_plan_for_next_day
from app.models.preparation_plan import PlanGenerateRequest
from app.core.database import get_plans_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/generate")
async def generate_plan(request: PlanGenerateRequest):
    """Generate a personalized preparation plan from skill gap analysis."""
    try:
        plan = await generate_preparation_plan(
            user_id=request.user_id,
            skill_gap_id=request.skill_gap_id,
            timeline_days=request.timeline_days,
            hours_per_day=request.hours_per_day,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

    col = get_plans_collection()
    doc = plan.dict()
    result = await col.insert_one(doc)
    plan.id = str(result.inserted_id)

    return {"plan_id": plan.id, "plan": plan.dict()}


# NOTE: /user/{user_id} MUST come before /{plan_id}
@router.get("/user/{user_id}")
async def get_user_plans(user_id: str):
    """Get all plans for a user."""
    col = get_plans_collection()
    docs = await col.find({"user_id": user_id}).sort("created_at", -1).to_list(length=10)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"plans": docs}


@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    """Fetch a preparation plan."""
    col = get_plans_collection()
    doc = await col.find_one({"_id": ObjectId(plan_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Plan not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/{plan_id}/complete-day")
async def complete_day(plan_id: str, body: dict):
    """Mark a day as complete and adapt the next day's plan."""
    user_id = body.get("user_id")
    day = body.get("day")
    performance = body.get("performance", {})

    col = get_plans_collection()
    # Mark current day as complete
    await col.update_one(
        {"_id": ObjectId(plan_id), "days.day": day},
        {
            "$set": {
                "days.$.completed": True,
                "days.$.performance_score": performance.get("score", 0),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    # Adapt next day
    try:
        adapted = await adapt_plan_for_next_day(user_id, plan_id, day, performance)
    except Exception:
        adapted = {}

    # Recompute overall progress — initialize before the if block
    total = 0
    completed = 0
    plan_doc = await col.find_one({"_id": ObjectId(plan_id)})
    if plan_doc:
        total = len(plan_doc.get("days", []))
        completed = sum(1 for d in plan_doc.get("days", []) if d.get("completed"))
        progress = (completed / total * 100) if total > 0 else 0
        await col.update_one(
            {"_id": ObjectId(plan_id)},
            {"$set": {"overall_progress": round(progress, 1)}},
        )

    overall_progress = round((completed / total * 100) if total > 0 else 0, 1)
    return {
        "message": f"Day {day} completed",
        "adapted_next_day": adapted,
        "overall_progress": overall_progress,
    }
