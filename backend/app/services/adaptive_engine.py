"""
Adaptive Learning Engine
- Tracks performance per topic
- Detects weak areas
- Dynamically adjusts next-day plan
- Recommends what to study next
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.services.llm_client import chat_complete_json
from app.core.database import get_performance_collection, get_plans_collection
from app.models.performance import ReadinessScore, TopicScore, WeaknessReport
from bson import ObjectId

logger = logging.getLogger(__name__)


async def compute_topic_scores(user_id: str) -> List[TopicScore]:
    """
    Aggregate performance data from DB and compute per-topic scores.
    """
    perf_col = get_performance_collection()
    sessions = await perf_col.find({"user_id": user_id}).to_list(length=500)

    topic_data: Dict[str, Dict] = {}
    for session in sessions:
        for topic in session.get("topics_covered", []):
            if topic not in topic_data:
                topic_data[topic] = {
                    "scores": [],
                    "attempts": 0,
                    "correct": 0,
                    "times": [],
                }
            topic_data[topic]["scores"].append(session.get("score", 0))
            topic_data[topic]["attempts"] += session.get("questions_attempted", 0)
            topic_data[topic]["correct"] += session.get("questions_correct", 0)
            topic_data[topic]["times"].append(session.get("duration_minutes", 0) * 60)

    results = []
    for topic, data in topic_data.items():
        scores = data["scores"]
        avg_score = sum(scores) / len(scores) if scores else 0
        # Simple trend: compare first half vs second half
        mid = len(scores) // 2
        if mid > 0:
            first_half_avg = sum(scores[:mid]) / mid
            second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
            trend = "improving" if second_half_avg > first_half_avg + 5 else \
                    "declining" if second_half_avg < first_half_avg - 5 else "stable"
        else:
            trend = "stable"

        results.append(
            TopicScore(
                topic=topic,
                score=round(avg_score, 1),
                questions_attempted=data["attempts"],
                questions_correct=data["correct"],
                average_time_seconds=sum(data["times"]) / len(data["times"]) if data["times"] else 0,
                trend=trend,
            )
        )
    return results


async def compute_readiness_score(user_id: str) -> ReadinessScore:
    """Compute overall placement readiness score from performance data."""
    topic_scores = await compute_topic_scores(user_id)

    if not topic_scores:
        return ReadinessScore(
            user_id=user_id,
            overall_score=0.0,
            interview_readiness=0.0,
            topic_scores=[],
            strengths=[],
            weaknesses=[],
            recommendation="Complete your profile and start practicing to get a readiness score.",
            computed_at=datetime.utcnow(),
        )

    topic_weights = {
        "DSA": 0.20, "Java": 0.12, "Python": 0.10, "SQL": 0.10,
        "DBMS": 0.08, "OS": 0.08, "CN": 0.07, "OOP": 0.08,
        "Aptitude": 0.07, "Communication": 0.05, "System Design": 0.05,
    }

    weighted_sum = 0.0
    total_weight = 0.0
    for ts in topic_scores:
        weight = topic_weights.get(ts.topic, 0.05)
        weighted_sum += ts.score * weight
        total_weight += weight

    overall = weighted_sum / total_weight if total_weight > 0 else 0.0
    interview_readiness = overall * 0.9  # slightly conservative

    strengths = [ts.topic for ts in topic_scores if ts.score >= 75]
    weaknesses = [ts.topic for ts in topic_scores if ts.score < 50]

    prompt = f"""
Student placement readiness:
- Overall score: {overall:.1f}%
- Strong topics: {strengths}
- Weak topics: {weaknesses}
- Topic breakdown: {[{"topic": t.topic, "score": t.score} for t in topic_scores]}

Generate a concise, encouraging recommendation (2-3 sentences) for what to focus on next.
Return JSON: {{"recommendation": "..."}}
"""
    try:
        rec_data = await chat_complete_json(
            [
                {"role": "system", "content": "You are a placement advisor. Return only JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        recommendation = rec_data.get("recommendation", "Keep practicing consistently!")
    except Exception:
        recommendation = "Focus on your weak areas and maintain consistent daily practice."

    return ReadinessScore(
        user_id=user_id,
        overall_score=round(overall, 1),
        interview_readiness=round(interview_readiness, 1),
        topic_scores=topic_scores,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendation=recommendation,
        computed_at=datetime.utcnow(),
    )


async def adapt_plan_for_next_day(
    user_id: str,
    plan_id: str,
    current_day: int,
    day_performance: Dict,
) -> Dict:
    """
    Adapt the next day's plan based on today's performance.
    Returns updated task list for next day.
    """
    topic_scores = await compute_topic_scores(user_id)
    weak_topics = [ts.topic for ts in topic_scores if ts.score < 60]

    prompt = f"""
Student completed Day {current_day} of their preparation plan.
Today's performance: {day_performance}
Currently weak topics: {weak_topics}

Generate an ADAPTED plan for Day {current_day + 1} that:
1. Increases focus on weak topics
2. Reduces difficulty if score < 40%
3. Increases difficulty if score > 80%
4. Balances breadth with depth

Return JSON:
{{
  "adapted_tasks": [
    {{
      "topic": "...",
      "subtopic": "...",
      "duration_minutes": 45,
      "difficulty": "easy|medium|hard",
      "practice_questions": 5,
      "reason": "why this was adjusted"
    }}
  ],
  "focus_message": "Encouraging message for the student",
  "adjustment_summary": "What changed and why"
}}
"""
    return await chat_complete_json(
        [
            {"role": "system", "content": "You are an adaptive learning system. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )


async def generate_weakness_report(user_id: str) -> WeaknessReport:
    """Generate a detailed weakness report with recommendations."""
    topic_scores = await compute_topic_scores(user_id)
    weak = [ts for ts in topic_scores if ts.score < 60]
    critical = [ts for ts in topic_scores if ts.score < 40]

    # Estimate days to readiness (score of 75+)
    estimated_days = 0
    for ts in topic_scores:
        if ts.score < 75:
            gap = 75 - ts.score
            estimated_days = max(estimated_days, int(gap / 2))  # ~2 points/day

    return WeaknessReport(
        user_id=user_id,
        weak_topics=[ts.topic for ts in weak],
        critical_gaps=[ts.topic for ts in critical],
        suggested_focus=[ts.topic for ts in sorted(weak, key=lambda x: x.score)[:3]],
        estimated_days_to_readiness=estimated_days,
        generated_at=datetime.utcnow(),
    )
