"""
Full endpoint test — runs all 5 core AI features.
Run: python test_all_endpoints.py
"""
import asyncio
import sys

PASS = []
FAIL = []

def safe_str(s):
    if not s:
        return ""
    return str(s).encode('ascii', errors='replace').decode('ascii')


def ok(name):
    PASS.append(name)
    print(f"  [PASS] {safe_str(name)}")

def fail(name, err):
    FAIL.append(name)
    print(f"  [FAIL] {safe_str(name)}")
    print(f"     ERROR: {safe_str(err)}")


async def test_llm_client():
    print("\n[1] LLM Client — chat_complete + chat_complete_json")
    from app.services.llm_client import chat_complete, chat_complete_json, _extract_json

    # chat_complete
    try:
        reply = await chat_complete(
            messages=[
                {"role": "system", "content": "Reply in one word only."},
                {"role": "user",   "content": "Say WORKING"},
            ],
            temperature=0.1, max_tokens=100,
        )
        assert reply and len(reply.strip()) > 0
        ok(f"chat_complete — got: '{reply.strip()[:40]}'")
    except Exception as e:
        fail("chat_complete", e)

    # chat_complete_json
    try:
        data = await chat_complete_json(
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No other text."},
                {"role": "user",   "content": 'Return: {"status":"ok","score":9}'},
            ],
            temperature=0.1,
        )
        assert isinstance(data, dict)
        ok(f"chat_complete_json — got: {data}")
    except Exception as e:
        fail("chat_complete_json", e)

    # embedding
    try:
        from app.services.llm_client import get_embedding
        vec = await get_embedding("placement test")
        assert len(vec) > 0
        ok(f"get_embedding — dims: {len(vec)}")
    except Exception as e:
        fail("get_embedding", e)


async def test_question_generator():
    print("\n[2] Question Generator")
    from app.services.question_generator import generate_questions, evaluate_answer

    # Generate DSA questions
    try:
        qs = await generate_questions(
            category="DSA", difficulty="easy", count=2, subcategory="Arrays"
        )
        assert len(qs) > 0
        assert qs[0].question_text
        ok(f"generate_questions (DSA/Arrays) — got {len(qs)} questions")
        print(f"     Sample: {safe_str(qs[0].question_text[:80])}...")
    except Exception as e:
        fail("generate_questions DSA", e)

    # Generate SQL questions
    try:
        qs = await generate_questions(
            category="SQL", difficulty="medium", count=2
        )
        assert len(qs) > 0
        ok(f"generate_questions (SQL) — got {len(qs)} questions")
    except Exception as e:
        fail("generate_questions SQL", e)

    # Evaluate answer
    try:
        question = {
            "question_text": "What is a binary search tree?",
            "correct_answer": "A BST is a tree where left child < node < right child.",
            "question_type": "short_answer",
        }
        result = await evaluate_answer(
            question=question,
            user_answer="A BST is a tree data structure where each node's left child is smaller and right child is larger.",
            time_taken_seconds=45,
        )
        assert "score" in result
        ok(f"evaluate_answer — score: {result.get('score')}/10")
    except Exception as e:
        fail("evaluate_answer", e)


async def test_mock_interview():
    print("\n[3] Mock Interview")
    from app.services.mock_interview_service import start_interview, send_message, end_interview
    from app.models.mock_interview import InterviewType

    interview_id = None
    try:
        interview = await start_interview(
            user_id="test_user_001",
            interview_type=InterviewType.TECHNICAL,
            target_role="Software Developer",
            target_company="Test Corp",
        )
        assert interview.id
        assert interview.conversation[0].content
        interview_id = interview.id
        ok(f"start_interview — ID: {interview_id}")
        print(f"     Opening: {safe_str(interview.conversation[0].content[:80])}...")
    except Exception as e:
        fail("start_interview", e)
        return

    if interview_id:
        try:
            result = await send_message(
                interview_id=interview_id,
                user_message="I have 2 years of experience in Java and Python. I enjoy solving DSA problems.",
            )
            assert result.get("interviewer_message")
            ok(f"send_message — reply received")
            print(f"     Reply: {safe_str(result['interviewer_message'][:80])}...")
        except Exception as e:
            fail("send_message", e)

        try:
            evaluation = await end_interview(interview_id)
            assert evaluation.overall_score >= 0
            ok(f"end_interview — overall score: {evaluation.overall_score}/10")
        except Exception as e:
            fail("end_interview", e)


async def test_resume_parser():
    print("\n[4] Resume Parser")
    from app.services.resume_parser import parse_resume

    # Create a sample resume text
    sample_resume = b"""
John Doe
Software Developer
Email: john@example.com | Phone: 9876543210

EDUCATION
B.Tech Computer Science, XYZ College, 2024, CGPA: 8.5

SKILLS
Java, Python, SQL, Spring Boot, MongoDB, React, Docker, Git, REST APIs, Data Structures

PROJECTS
1. Fake News Detection System
   Built a ML model using Python, scikit-learn, NLP to detect fake news with 92% accuracy.
   Technologies: Python, NLTK, scikit-learn, Flask

2. E-Commerce Web App
   Full-stack app with React frontend and Spring Boot backend.
   Technologies: React, Spring Boot, MySQL, REST APIs

EXPERIENCE
Software Intern | ABC Company | 6 months
- Developed REST APIs using Spring Boot
- Worked with MySQL databases
- Implemented JWT authentication
"""

    try:
        analysis = await parse_resume("test_user_001", sample_resume, "resume.txt")
        assert analysis.user_id == "test_user_001"
        ok(f"parse_resume — extracted {len(analysis.skills)} skills, {len(analysis.projects)} projects")
        print(f"     Skills: {analysis.skills[:6]}")
        print(f"     Summary: {safe_str((analysis.summary or '')[:80])}...")
    except Exception as e:
        fail("parse_resume", e)


async def test_rag():
    print("\n[5] RAG Career Assistant")
    from app.services.rag_service import seed_knowledge_base, rag_query, search_knowledge_base

    # Seed
    try:
        count = await seed_knowledge_base()
        ok(f"seed_knowledge_base — seeded {count} documents")
    except Exception as e:
        fail("seed_knowledge_base", e)

    # Search
    try:
        results = await search_knowledge_base("binary search arrays", n_results=3)
        ok(f"search_knowledge_base — found {len(results)} results")
        if results:
            print(f"     Top result: {safe_str(results[0]['content'][:60])}...")
    except Exception as e:
        fail("search_knowledge_base", e)

    # Full RAG query
    try:
        result = await rag_query(
            query="How do I prepare for DSA interviews?",
            user_context={"target_role": "Software Developer", "weak_skills": ["DP", "Graphs"]},
        )
        assert result.get("answer")
        ok(f"rag_query — answer received ({len(result['answer'])} chars)")
        print(f"     Answer: {safe_str(result['answer'][:100])}...")
    except Exception as e:
        fail("rag_query", e)


async def main():
    print("=" * 60)
    print("  Backend Full Endpoint Test")
    print("=" * 60)

    from app.core.database import connect_db, close_db
    await connect_db()
    try:
        await test_llm_client()
        await test_question_generator()
        await test_mock_interview()
        await test_resume_parser()
        await test_rag()
    finally:
        await close_db()

    print("\n" + "=" * 60)
    print(f"  RESULTS: {len(PASS)} passed  |  {len(FAIL)} failed")
    print("=" * 60)

    if FAIL:
        print(f"\n  FAILED TESTS:")
        for f in FAIL:
            print(f"    [FAIL] {f}")
        print()
        sys.exit(1)
    else:
        print("\n  ALL TESTS PASSED — Backend is fully working!")
        print("  Run: python -m uvicorn main:app --reload --port 8000")
        print()


asyncio.run(main())
