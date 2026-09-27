"""
Question generation and answer evaluation endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.services.question_generator import generate_questions, evaluate_answer
from app.models.question import QuestionGenerateRequest, QuestionAttempt
from app.core.database import get_questions_collection, get_performance_collection
from datetime import datetime

router = APIRouter()


@router.post("/generate")
async def generate(request: QuestionGenerateRequest):
    """Generate questions for a given category, difficulty, and count."""
    try:
        questions = await generate_questions(
            category=request.category,
            difficulty=request.difficulty,
            count=request.count,
            subcategory=request.subcategory,
            question_type=request.question_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

    # Persist to DB and attach IDs
    col = get_questions_collection()
    enriched = []
    for q in questions:
        doc = q.model_dump()
        doc.pop("id", None)
        result = await col.insert_one(doc)
        q_dict = q.model_dump()
        q_dict["id"] = str(result.inserted_id)
        enriched.append(q_dict)

    return {
        "question_ids": [q["id"] for q in enriched],
        "questions": enriched,
        "count": len(enriched),
    }


@router.post("/attempt")
async def submit_attempt(attempt: QuestionAttempt):
    """Submit an answer to a question and get AI evaluation."""
    from bson import ObjectId
    col = get_questions_collection()

    q_doc = None
    if attempt.question_id:
        try:
            q_doc = await col.find_one({"_id": ObjectId(attempt.question_id)})
        except Exception:
            pass

    if q_doc:
        q_doc["id"] = str(q_doc.pop("_id"))
    else:
        q_doc = {"question_text": "", "question_type": "short_answer"}

    try:
        evaluation = await evaluate_answer(
            question=q_doc,
            user_answer=attempt.user_answer,
            time_taken_seconds=attempt.time_taken_seconds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

    # Save attempt to DB
    perf_col = get_performance_collection()
    attempt_doc = attempt.model_dump()
    attempt_doc["evaluation"] = evaluation
    attempt_doc["submitted_at"] = datetime.utcnow()
    await perf_col.insert_one(attempt_doc)

    return {
        "evaluation": evaluation,
        "correct_answer": q_doc.get("correct_answer"),
        "explanation": q_doc.get("explanation"),
    }


# NOTE: /categories MUST be before /{question_id}
@router.get("/categories")
async def get_categories():
    """Get all available question categories."""
    from app.services.question_generator import CATEGORY_SUBTOPIC_MAP
    return {
        "categories": [
            {"name": cat, "subtopics": subtopics}
            for cat, subtopics in CATEGORY_SUBTOPIC_MAP.items()
        ]
    }


@router.get("/{question_id}")
async def get_question(question_id: str):
    """Fetch a question by ID."""
    from bson import ObjectId
    col = get_questions_collection()
    doc = await col.find_one({"_id": ObjectId(question_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Question not found")
    doc["id"] = str(doc.pop("_id"))
    return doc
