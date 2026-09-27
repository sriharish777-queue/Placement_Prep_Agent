"""
Speed test — measures Gemini vs OpenRouter response times.
Run: python test_speed.py
"""
import asyncio
import time
import httpx


from app.core.config import settings

GEMINI_KEY = settings.GEMINI_API_KEY

async def test_gemini_speed():
    print(f"Testing Gemini ({settings.GEMINI_MODEL}) speed...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Generate 3 DSA medium interview questions about arrays. Return ONLY a JSON array."}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1500,
            "thinkingConfig": {"thinkingLevel": "LOW"}
        },
    }
    t = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload)
    elapsed = round(time.time() - t, 2)
    if r.status_code == 200:
        data = r.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
            text = "".join(p.get("text", "") for p in candidates[0]["content"]["parts"] if "text" in p)
            print(f"  Gemini: {elapsed}s  |  response length: {len(text)} chars")
            print(f"  Preview: {text[:120]}...")
        else:
            print(f"  Gemini returned: {data}")
    else:
        print(f"  Gemini FAILED {r.status_code}: {r.text[:150]}")

async def test_openrouter_speed():
    print(f"\nTesting OpenRouter ({settings.OPENROUTER_FALLBACK_MODEL}) speed...")
    t = time.time()
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={"model": settings.OPENROUTER_FALLBACK_MODEL,
                  "messages": [{"role": "user", "content": "Generate 3 DSA medium interview questions about arrays. Return ONLY a JSON array."}],
                  "max_tokens": 1500}
        )
    elapsed = round(time.time() - t, 2)
    if r.status_code == 200:
        text = r.json()["choices"][0]["message"]["content"]
        print(f"  OpenRouter: {elapsed}s  |  response length: {len(text)} chars")
    else:
        print(f"  OpenRouter FAILED {r.status_code}: {r.text[:150]}")

async def main():
    if not GEMINI_KEY or GEMINI_KEY == "PASTE_YOUR_KEY_HERE":
        print("ERROR: Please set GEMINI_API_KEY in backend/.env!")
        return
    print("=" * 50)
    await test_gemini_speed()
    await test_openrouter_speed()
    print("=" * 50)

asyncio.run(main())
