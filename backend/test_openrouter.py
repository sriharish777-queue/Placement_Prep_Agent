"""
Full test — OpenRouter + all backend imports.
Run: python test_openrouter.py
"""
import asyncio

async def test():
    print("=" * 55)
    print("  OpenRouter + Backend Integration Test")
    print("=" * 55)

    # 1. Config
    from app.core.config import settings
    print(f"\n[1] Config")
    print(f"    API Key : {settings.OPENROUTER_API_KEY[:20]}...{settings.OPENROUTER_API_KEY[-6:]}")
    print(f"    Model   : {settings.OPENROUTER_MODEL}")
    print(f"    Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"    MongoDB : {settings.MONGODB_URL[:40]}...")

    # 2. LLM client import
    from app.services.llm_client import chat_complete, chat_complete_json, get_embedding
    print(f"\n[2] llm_client imported OK")

    # 3. Live chat test
    print(f"\n[3] Testing chat_complete (live API call)...")
    reply = await chat_complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Reply in one sentence only."},
            {"role": "user",   "content": "Say: OpenRouter is working perfectly."},
        ],
        temperature=0.1,
        max_tokens=30,
    )
    print(f"    Response: {reply.strip()}")

    # 4. JSON test
    print(f"\n[4] Testing chat_complete_json...")
    data = await chat_complete_json(
        messages=[
            {"role": "system", "content": "Return only valid JSON, nothing else."},
            {"role": "user",   "content": 'Return this exact JSON: {"status": "ok", "model": "openrouter", "ready": true}'},
        ],
        temperature=0.1,
    )
    print(f"    JSON response: {data}")
    assert data.get("ready") == True, "JSON parse failed"

    # 5. Embedding test
    print(f"\n[5] Testing get_embedding (local)...")
    vec = await get_embedding("placement preparation test")
    print(f"    Embedding dims: {len(vec)}")
    assert len(vec) > 0, "Embedding returned empty"

    # 6. All backend imports
    print(f"\n[6] Testing all backend imports...")
    from app.api.v1.router import api_router
    from main import app
    print(f"    Routes loaded: {len(app.routes)}")
    assert len(app.routes) >= 30

    # 7. Resume parser import
    from app.services.resume_parser import parse_resume
    from app.services.skill_gap_engine import run_skill_gap_analysis
    from app.services.mock_interview_service import start_interview
    from app.services.plan_generator import generate_preparation_plan
    from app.services.adaptive_engine import compute_readiness_score
    from app.services.rag_service import rag_query
    print(f"    All services imported OK")

    print(f"\n{'=' * 55}")
    print(f"  ALL TESTS PASSED — Backend fully ready!")
    print(f"  Run: python -m uvicorn main:app --reload --port 8000")
    print(f"{'=' * 55}\n")


asyncio.run(test())
