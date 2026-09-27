"""
AI Mock Interview Service
- Technical, HR, Behavioral, System Design, Mixed interviews
- Follow-up questions based on previous answers
- Per-answer scoring + final evaluation
- Works with any OpenRouter model via chat_complete
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.services.llm_client import chat_complete, chat_complete_json
from app.models.mock_interview import (
    MockInterview, InterviewMessage, InterviewEvaluation, InterviewType,
)
from app.core.database import get_interviews_collection
from bson import ObjectId

logger = logging.getLogger(__name__)

# ── System prompts per interview type ────────────────────────────────────────
SYSTEM_PROMPTS = {
    InterviewType.TECHNICAL: """You are a senior software engineer conducting a real technical placement interview.
Rules:
- Ask ONE question at a time. Wait for the candidate to answer before asking the next.
- Follow up on incomplete answers: "Can you elaborate on...?" or "What is the time complexity?"
- Cover: data structures, algorithms, OS, DBMS, networking, language-specific questions.
- Be professional but conversational.
- Start with a warm-up then gradually increase difficulty.
- After each answer, give a brief acknowledgement then ask the next question.
Start by greeting the candidate and asking your first warm-up question.""",

    InterviewType.HR: """You are an HR manager conducting a placement screening interview.
Rules:
- Ask ONE question at a time.
- Use STAR method prompts for behavioral questions.
- Cover: background, strengths/weaknesses, career goals, teamwork, conflict resolution.
- Be friendly and encouraging.
- Ask follow-up questions based on candidate's answers.
Start by introducing yourself and asking the candidate to introduce themselves.""",

    InterviewType.BEHAVIORAL: """You are conducting a behavioral interview using the STAR method.
Rules:
- Ask about real past experiences: teamwork, leadership, failure, achievement, conflict.
- After each answer probe deeper: "What would you do differently?" or "Tell me more about..."
- ONE question at a time.
Start by explaining the STAR format briefly then ask your first behavioral question.""",

    InterviewType.SYSTEM_DESIGN: """You are a senior architect conducting a system design interview.
Rules:
- Present ONE design problem and guide the candidate through it.
- Probe on: requirements, high-level design, scalability, database choice, bottlenecks.
- Ask follow-up questions when the candidate misses important aspects.
- ONE question/prompt at a time.
Start by presenting a real-world system design problem (e.g., design a URL shortener).""",

    InterviewType.MIXED: """You are conducting a comprehensive placement round covering technical and HR aspects.
Rules:
- Mix technical questions (DSA, CS fundamentals) with behavioral and HR questions.
- ONE question at a time.
- Simulate a real company placement round.
- Gradually increase difficulty.
Start with a brief introduction and ask the candidate to introduce themselves.""",
}


async def start_interview(
    user_id: str,
    interview_type: InterviewType,
    target_role: str,
    target_company: Optional[str] = None,
    focus_topics: Optional[List[str]] = None,
) -> MockInterview:
    """Initialize a new mock interview and get opening message from AI."""

    base_prompt = SYSTEM_PROMPTS.get(interview_type, SYSTEM_PROMPTS[InterviewType.MIXED])

    # Add role/company context
    context = f"\nThe candidate is interviewing for: {target_role}"
    if target_company:
        context += f"\nTarget company: {target_company}"
    if focus_topics:
        context += f"\nFocus areas: {', '.join(focus_topics)}"

    system_prompt = base_prompt + context

    # Get opening message from AI
    try:
        opening = await chat_complete(
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": "Start the interview now."},
            ],
            temperature=0.7,
            max_tokens=300,
        )
    except Exception as e:
        logger.error("Failed to get opening message: %s", e)
        opening = (
            f"Hello! Welcome to your {interview_type.value} interview for the "
            f"{target_role} position{f' at {target_company}' if target_company else ''}. "
            "I'm glad you're here today. Let's start with a brief introduction — "
            "could you please tell me about yourself and your background?"
        )

    interview = MockInterview(
        user_id=user_id,
        interview_type=interview_type,
        target_role=target_role,
        target_company=target_company,
        conversation=[
            InterviewMessage(
                role="interviewer",
                content=opening,
                timestamp=datetime.utcnow(),
            )
        ],
        status="active",
        started_at=datetime.utcnow(),
    )

    col = get_interviews_collection()
    doc = interview.dict()
    doc["system_prompt"] = system_prompt   # store for conversation continuity
    result = await col.insert_one(doc)
    interview.id = str(result.inserted_id)
    return interview


async def send_message(interview_id: str, user_message: str) -> Dict:
    """Process candidate's message and return AI interviewer response + quick eval."""
    col = get_interviews_collection()
    doc = await col.find_one({"_id": ObjectId(interview_id)})
    if not doc:
        raise ValueError(f"Interview {interview_id} not found")

    system_prompt = doc.get("system_prompt", "You are a professional interviewer.")
    conversation = doc.get("conversation", [])

    # Build message history for the model
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation:
        role = "assistant" if msg["role"] == "interviewer" else "user"
        messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    # Get AI interviewer response
    try:
        interviewer_reply = await chat_complete(
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )
    except Exception as e:
        logger.error("Interview message failed: %s", e)
        interviewer_reply = (
            "Thank you for your answer. Let me ask you another question: "
            "Can you walk me through how you would approach a complex technical problem step by step?"
        )

    # Quick evaluation of candidate's answer
    quick_eval = await _quick_eval(
        question=_get_last_question(conversation),
        answer=user_message,
    )

    # Save both messages to DB
    now = datetime.utcnow()
    new_msgs = [
        {
            "role": "candidate",
            "content": user_message,
            "timestamp": now,
            "evaluation": quick_eval,
        },
        {
            "role": "interviewer",
            "content": interviewer_reply,
            "timestamp": now,
        },
    ]
    await col.update_one(
        {"_id": ObjectId(interview_id)},
        {"$push": {"conversation": {"$each": new_msgs}}},
    )

    return {
        "interviewer_message": interviewer_reply,
        "answer_evaluation": quick_eval,
    }


async def end_interview(interview_id: str) -> InterviewEvaluation:
    """End interview and generate comprehensive final evaluation."""
    col = get_interviews_collection()
    doc = await col.find_one({"_id": ObjectId(interview_id)})
    if not doc:
        raise ValueError(f"Interview {interview_id} not found")

    conversation = doc.get("conversation", [])
    candidate_answers = [
        m["content"] for m in conversation if m.get("role") == "candidate"
    ]

    if not candidate_answers:
        # No answers given — return default evaluation
        eval_data = _default_evaluation("No answers were provided during the interview.")
    else:
        prompt = f"""Evaluate this complete mock interview performance.
Interview type: {doc.get('interview_type', 'technical')}
Target role: {doc.get('target_role', 'Software Developer')}
Number of answers: {len(candidate_answers)}
Sample answers: {str(candidate_answers[:5])[:800]}

Return ONLY a JSON object with these exact keys:
{{
  "correctness": 7.0,
  "relevance": 7.5,
  "technical_depth": 6.5,
  "communication": 7.0,
  "confidence": 7.0,
  "missing_concepts": ["concept1"],
  "strengths": ["strength1"],
  "improvements": ["area1"],
  "overall_score": 7.0,
  "feedback": "2-3 sentences of honest, constructive feedback."
}}
All scores are out of 10."""

        try:
            raw = await chat_complete(
                messages=[
                    {"role": "system", "content": "You are a professional interview evaluator. Return ONLY JSON."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.2,
                max_tokens=600,
                json_mode=True,
            )
            from app.services.llm_client import _extract_json
            eval_data = _extract_json(raw) or _default_evaluation()
        except Exception as e:
            logger.error("Final evaluation failed: %s", e)
            eval_data = _default_evaluation()

    # Ensure all required fields exist with safe defaults
    eval_data = _sanitize_evaluation(eval_data)
    evaluation = InterviewEvaluation(**eval_data)

    await col.update_one(
        {"_id": ObjectId(interview_id)},
        {"$set": {
            "final_evaluation": eval_data,
            "status": "completed",
            "ended_at": datetime.utcnow(),
        }},
    )
    return evaluation


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_last_question(conversation: List[Dict]) -> str:
    """Get the most recent interviewer question from conversation."""
    for msg in reversed(conversation):
        if msg.get("role") == "interviewer":
            return msg.get("content", "")[:400]
    return ""


async def _quick_eval(question: str, answer: str) -> Dict:
    """Quick 1-sentence evaluation of a single answer."""
    if not question or not answer:
        return {}
    try:
        prompt = f"""Question: {question[:300]}
Answer: {answer[:400]}
Return ONLY JSON: {{"score": 7, "feedback": "one sentence", "missing": ["key concept if any"]}}"""
        raw = await chat_complete(
            messages=[
                {"role": "system", "content": "Evaluate briefly. Return ONLY JSON."},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.2,
            max_tokens=150,
            json_mode=True,
        )
        from app.services.llm_client import _extract_json
        return _extract_json(raw) or {}
    except Exception:
        return {}


def _default_evaluation(feedback: str = "Interview completed. Keep practicing!") -> Dict:
    return {
        "correctness": 6.0,
        "relevance": 6.0,
        "technical_depth": 6.0,
        "communication": 6.0,
        "confidence": 6.0,
        "missing_concepts": [],
        "strengths": ["Completed the interview"],
        "improvements": ["Practice more mock interviews"],
        "overall_score": 6.0,
        "feedback": feedback,
    }


def _sanitize_evaluation(data: Any) -> Dict:
    """Ensure all required fields are present with correct types."""
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        data = data[0]
    elif not isinstance(data, dict):
        data = {}
    else:
        data = dict(data)

    defaults = _default_evaluation()
    for key, default in defaults.items():
        if key not in data:
            data[key] = default
        # Ensure scores are floats
        if key in ("correctness","relevance","technical_depth","communication","confidence","overall_score"):
            try:
                data[key] = float(data[key])
            except (TypeError, ValueError):
                data[key] = 6.0
        # Ensure lists are lists
        if key in ("missing_concepts", "strengths", "improvements"):
            if not isinstance(data[key], list):
                data[key] = []
    return data
