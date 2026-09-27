"""Quick test — Gemini integration check."""
import asyncio

async def test():
    print("=== Testing Gemini Integration ===\n")

    # 1. Config
    from app.core.config import settings
    key = settings.GEMINI_API_KEY
    print(f"  API Key   : {key[:12]}...{key[-4:]}")
    print(f"  Chat model: {settings.GEMINI_MODEL}")
    print(f"  Embed model: {settings.GEMINI_EMBEDDING_MODEL}")

    # 2. Import llm_client
    from app.services.llm_client import chat_complete, chat_complete_json, get_embedding
    print("  llm_client: imported OK\n")

    # 3. Live chat test
    print("  [1] Testing chat_complete ...")
    reply = await chat_complete(
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Reply in one word."},
            {"role": "user",   "content": "Say only the word WORKING"},
        ],
        temperature=0.1,
        max_tokens=100,
    )
    print(f"      Response: {reply.strip()}\n")

    # 4. JSON test
    print("  [2] Testing chat_complete_json ...")
    data = await chat_complete_json(
        messages=[
            {"role": "system", "content": "Return only valid JSON, nothing else."},
            {"role": "user",   "content": 'Return exactly: {"status": "ok", "model": "gemini"}'},
        ],
        temperature=0.1,
    )
    print(f"      JSON response: {data}\n")

    # 5. All backend imports
    print("  [3] Testing all backend imports ...")
    from app.api.v1.router import api_router
    print(f"      Routes loaded: {len(api_router.routes)}")

    print("\n=== ALL TESTS PASSED — Ready to run! ===")

asyncio.run(test())
