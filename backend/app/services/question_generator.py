"""
AI Question Generator
- Generates DSA, SQL, Java, Python, OOP, DBMS, OS, CN, Aptitude, System Design questions
- Robust JSON parsing with fallback manual extraction
- Works with any OpenRouter model
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from app.services.llm_client import chat_complete, chat_complete_json
from app.models.question import Question, QuestionType

logger = logging.getLogger(__name__)

CATEGORY_SUBTOPIC_MAP = {
    "DSA":           ["Arrays", "Strings", "Linked Lists", "Trees", "Graphs",
                      "Dynamic Programming", "Sorting", "Searching", "Recursion",
                      "Stacks & Queues", "Heaps", "Tries"],
    "SQL":           ["SELECT queries", "JOINs", "Aggregations", "Subqueries",
                      "Window Functions", "Indexes", "Normalization", "Transactions"],
    "Java":          ["OOP Concepts", "Collections", "Multithreading",
                      "Exception Handling", "Java 8 Features", "Design Patterns", "JVM Internals"],
    "Python":        ["Data Types", "List Comprehensions", "Decorators", "Generators",
                      "File I/O", "OOP in Python", "Standard Library"],
    "OOP":           ["Inheritance", "Polymorphism", "Encapsulation",
                      "Abstraction", "SOLID Principles", "Design Patterns"],
    "DBMS":          ["ER Diagrams", "Normalization", "Transactions", "ACID Properties",
                      "Indexing", "Query Optimization", "Concurrency Control"],
    "OS":            ["Process Management", "Memory Management", "File Systems",
                      "Deadlocks", "Scheduling Algorithms", "Virtual Memory"],
    "CN":            ["OSI Model", "TCP/IP", "HTTP/HTTPS", "DNS",
                      "Routing", "Socket Programming", "Network Security"],
    "Aptitude":      ["Quantitative", "Logical Reasoning", "Verbal Ability",
                      "Data Interpretation", "Number Systems"],
    "System Design": ["HLD", "LLD", "Scalability", "Caching",
                      "Load Balancing", "Database Design", "Microservices"],
    "Spring Boot":   ["REST Controllers", "Dependency Injection", "Spring Security",
                      "JPA/Hibernate", "Microservices with Spring"],
    "REST API":      ["HTTP Methods", "Status Codes", "Authentication",
                      "Pagination", "Versioning", "API Design"],
}

QUESTION_SYSTEM = """You are a technical interviewer. Generate interview questions as a JSON array.
Each object must have EXACTLY these keys:
question_text, question_type (mcq/short_answer/coding/sql), difficulty (easy/medium/hard),
options (array of 4 strings for mcq, null otherwise), correct_answer, explanation,
hints (array of 1-2 strings), tags (array), time_limit_seconds (integer).
Return ONLY the JSON array starting with [. No markdown, no explanation."""


def _parse_questions_safely(raw: str, category: str, difficulty: str) -> List[Dict]:
    """
    Try multiple strategies to extract a list of questions from model output.
    Always returns a list (may be empty on total failure).
    """
    # Clean fences
    import re
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Strategy 1 — direct parse as array
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Some models wrap in {"questions": [...]}
            for key in ("questions", "data", "items", "result"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
    except json.JSONDecodeError:
        pass

    # Strategy 2 — find outermost [ ... ] array
    try:
        start = text.index("[")
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return json.loads(text[start:i+1])
    except (ValueError, json.JSONDecodeError):
        pass

    # Strategy 3 — extract individual { } objects
    objects = []
    import re
    for match in re.finditer(r"\{[^{}]*\}", text, re.DOTALL):
        try:
            obj = json.loads(match.group())
            if "question_text" in obj:
                objects.append(obj)
        except json.JSONDecodeError:
            pass
    if objects:
        return objects

    logger.error("Could not parse questions from model output: %s", raw[:300])
    return []


async def generate_questions(
    category: str,
    difficulty: str = "medium",
    count: int = 5,
    subcategory: str = None,
    question_type: str = None,
    company: str = None,
) -> List[Question]:
    """Generate questions for a given category and difficulty."""

    subtopics = CATEGORY_SUBTOPIC_MAP.get(category, ["General"])
    subtopic_hint = (
        f"Focus specifically on: {subcategory}"
        if subcategory
        else f"Cover a mix of: {', '.join(subtopics[:4])}"
    )
    type_hint = f"Use question type: {question_type}" if question_type else "Use MCQ and short_answer types"
    company_hint = f"Include company tag: {company}" if company else ""

    user_prompt = f"""Generate exactly {count} {difficulty} {category} interview questions.
{subtopic_hint}. {type_hint}. {company_hint}
Return ONLY a JSON array of {count} objects. Start with ["""

    messages = [
        {"role": "system", "content": QUESTION_SYSTEM},
        {"role": "user",   "content": user_prompt},
    ]

    try:
        raw = await chat_complete(messages, temperature=0.7, max_tokens=3000, json_mode=True)
        questions_raw = _parse_questions_safely(raw, category, difficulty)
    except Exception as e:
        logger.error("Question generation failed: %s", e)
        questions_raw = []

    # If model returned nothing, return a hardcoded fallback question
    if not questions_raw:
        questions_raw = [{
            "question_text": f"Explain a key concept in {category} ({subcategory or 'general'}) at {difficulty} level.",
            "question_type": "short_answer",
            "difficulty": difficulty,
            "options": None,
            "correct_answer": "Open-ended — evaluate based on depth and accuracy.",
            "explanation": "This is a fallback question generated when the AI model was unavailable.",
            "hints": [f"Think about core {category} principles."],
            "tags": [category],
            "time_limit_seconds": 300,
        }]

    questions = []
    for q in questions_raw:
        if not q.get("question_text"):
            continue
        try:
            questions.append(Question(
                category=category,
                subcategory=subcategory or q.get("subcategory", "General"),
                question_text=q.get("question_text", ""),
                question_type=q.get("question_type", QuestionType.SHORT_ANSWER),
                difficulty=q.get("difficulty", difficulty),
                options=q.get("options") if isinstance(q.get("options"), list) else None,
                correct_answer=q.get("correct_answer"),
                explanation=q.get("explanation"),
                hints=q.get("hints", []) if isinstance(q.get("hints"), list) else [],
                tags=q.get("tags", []) if isinstance(q.get("tags"), list) else [],
                company_tags=[company] if company else [],
                time_limit_seconds=int(q.get("time_limit_seconds", 300)),
                created_at=datetime.utcnow(),
            ))
        except Exception as e:
            logger.warning("Skipping malformed question: %s", e)

    return questions


async def evaluate_answer(
    question: Dict,
    user_answer: str,
    time_taken_seconds: int,
) -> Dict:
    """AI evaluates a user's answer. Returns score + feedback dict."""
    if not user_answer or not user_answer.strip():
        return {
            "is_correct": False,
            "score": 0,
            "correctness": 0,
            "relevance": 0,
            "technical_depth": 0,
            "missing_concepts": [],
            "strengths": [],
            "improvements": ["No answer provided"],
            "detailed_feedback": "No answer was submitted.",
        }

    system_prompt = """You are a strict but fair technical interviewer evaluating a candidate's answer.
Return ONLY a valid JSON object with these exact keys:
{
  "is_correct": true or false,
  "score": 0-10,
  "correctness": 0-10,
  "relevance": 0-10,
  "technical_depth": 0-10,
  "missing_concepts": ["concept1"],
  "strengths": ["good point"],
  "improvements": ["improve this"],
  "detailed_feedback": "2-3 sentence feedback"
}"""

    user_prompt = f"""Question: {question.get('question_text', '')[:500]}
Expected Answer: {question.get('correct_answer', 'Not provided')[:300]}
Candidate Answer: {user_answer[:600]}
Time taken: {time_taken_seconds} seconds

Evaluate and return JSON only."""

    try:
        raw = await chat_complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=600,
            json_mode=True,
        )
        from app.services.llm_client import _extract_json
        result = _extract_json(raw)
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            result = result[0]
        if isinstance(result, dict) and "score" in result:
            return result
    except Exception as e:
        logger.error("Answer evaluation failed: %s", e)

    # Safe fallback
    return {
        "is_correct": False,
        "score": 5,
        "correctness": 5,
        "relevance": 5,
        "technical_depth": 5,
        "missing_concepts": [],
        "strengths": ["Answer submitted"],
        "improvements": ["Could not fully evaluate — please review manually"],
        "detailed_feedback": "Evaluation service was temporarily unavailable. Your answer has been recorded.",
    }
