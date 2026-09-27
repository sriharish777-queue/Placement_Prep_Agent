"""
Mock Interview endpoints.
NOTE: /start, /message, /user/{user_id} declared before /{interview_id}
to prevent route shadowing.
"""

from fastapi import APIRouter, HTTPException
from app.services.mock_interview_service import start_interview, send_message, end_interview
from app.models.mock_interview import InterviewStartRequest, InterviewMessageRequest

router = APIRouter()


@router.post("/start")
async def start(request: InterviewStartRequest):
    """Start a new mock interview session."""
    try:
        interview = await start_interview(
            user_id=request.user_id,
            interview_type=request.interview_type,
            target_role=request.target_role,
            target_company=request.target_company,
            focus_topics=request.focus_topics,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

    return {
        "interview_id": interview.id,
        "opening_message": interview.conversation[0].content if interview.conversation else "",
        "interview_type": interview.interview_type,
    }


@router.post("/message")
async def message(request: InterviewMessageRequest):
    """Send a candidate message and get interviewer response."""
    try:
        result = await send_message(
            interview_id=request.interview_id,
            user_message=request.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

    return result


# NOTE: /user/{user_id} MUST come before /{interview_id}
@router.get("/user/{user_id}")
async def get_user_interviews(user_id: str):
    """Get all interviews for a user."""
    from app.core.database import get_interviews_collection
    col = get_interviews_collection()
    docs = await col.find({"user_id": user_id}).sort("started_at", -1).to_list(length=20)
    for d in docs:
        d["id"] = str(d.pop("_id"))
        d.pop("system_prompt", None)
    return {"interviews": docs}


@router.post("/{interview_id}/end")
async def end(interview_id: str):
    """End the interview and get final evaluation."""
    try:
        evaluation = await end_interview(interview_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate interview: {str(e)}")

    return {"evaluation": evaluation.dict()}


@router.get("/{interview_id}")
async def get_interview(interview_id: str):
    """Get an interview session by ID."""
    from bson import ObjectId
    from app.core.database import get_interviews_collection
    col = get_interviews_collection()
    doc = await col.find_one({"_id": ObjectId(interview_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Interview not found")
    doc["id"] = str(doc.pop("_id"))
    doc.pop("system_prompt", None)
    return doc
