"""
LLM Client — Gemini 2.0 Flash (primary) + OpenRouter (fallback)

Gemini 2.0 Flash:
  - Free tier: 1,500 requests/day, 1,000,000 tokens/min
  - Response time: 2-4 seconds (vs 15-30s on OpenRouter free)
  - Uses Google's generateContent REST API directly via httpx

OpenRouter (fallback):
  - Used only when Gemini quota is exceeded (429) or key is missing
  - Same httpx approach, no openai package needed
"""

import json
import re
import logging
from typing import List, Dict, Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Gemini REST endpoint ──────────────────────────────────────────────────────
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# ── OpenRouter endpoint (fallback) ───────────────────────────────────────────
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# ── JSON cleaner ──────────────────────────────────────────────────────────────
def _clean_json(text: str) -> str:
    """Strip markdown code fences and leading noise from model output."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Remove any text before the first { or [
    match = re.search(r"[{\[]", text)
    if match:
        text = text[match.start():]
    return text.strip()


def _extract_json(text: str) -> Optional[Dict]:
    """Try multiple strategies to extract valid JSON from model output."""
    cleaned = _clean_json(text)

    # Strategy 1 — direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 2 — find outermost { } block
    try:
        start = cleaned.index("{")
        depth = 0
        for i, ch in enumerate(cleaned[start:], start):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(cleaned[start:i + 1])
    except (ValueError, json.JSONDecodeError):
        pass

    # Strategy 3 — find outermost [ ] block
    try:
        start = cleaned.index("[")
        depth = 0
        for i, ch in enumerate(cleaned[start:], start):
            if ch == "[": depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return json.loads(cleaned[start:i + 1])
    except (ValueError, json.JSONDecodeError):
        pass

    return None


# ── Gemini call ───────────────────────────────────────────────────────────────
async def _call_gemini(
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Call Gemini 2.0 Flash REST API."""
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "PASTE_YOUR_GEMINI_KEY_HERE":
        raise ValueError("Gemini API key not set")

    # Convert OpenAI-style messages to Gemini format
    # Gemini uses "user" and "model" roles
    parts_text = []
    system_text = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_text = content
        elif role == "assistant":
            parts_text.append(f"[Assistant]: {content}")
        else:
            parts_text.append(content)

    full_prompt = ""
    if system_text:
        full_prompt = f"{system_text}\n\n"
    full_prompt += "\n".join(parts_text)

    if json_mode:
        full_prompt += "\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown fences, no explanation. Start directly with { or [."

    url = GEMINI_URL.format(model=settings.GEMINI_MODEL, key=settings.GEMINI_API_KEY)

    gen_config = {
        "temperature": temperature,
        "maxOutputTokens": max(max_tokens, 2048) if "gemini-3" in settings.GEMINI_MODEL else max(max_tokens, 256),
    }
    if json_mode:
        gen_config["responseMimeType"] = "application/json"
    if "gemini-3" in settings.GEMINI_MODEL:
        gen_config["thinkingConfig"] = {"thinkingLevel": "LOW"}

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": gen_config,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)

    if response.status_code == 429:
        raise ValueError("Gemini quota exceeded — switching to fallback")

    if response.status_code != 200:
        err = response.text[:200]
        raise ValueError(f"Gemini error {response.status_code}: {err}")

    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini returned no candidates: {data}")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        finish_reason = candidates[0].get("finishReason", "UNKNOWN")
        raise ValueError(f"No parts in Gemini response (finishReason: {finish_reason})")

    text_parts = [p.get("text", "") for p in parts if "text" in p]
    if not text_parts:
        raise ValueError("No text found in Gemini response parts")
    return "".join(text_parts)


# ── OpenRouter fallback call ──────────────────────────────────────────────────
async def _call_openrouter(
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Call OpenRouter as fallback."""
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not set")

    msgs = list(messages)
    if json_mode:
        msgs = msgs + [{
            "role": "user",
            "content": "IMPORTANT: Respond with ONLY valid JSON. No markdown, no explanation. Start with { or [.",
        }]

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Placement Prep Copilot",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENROUTER_FALLBACK_MODEL,
                "messages": msgs,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    if response.status_code != 200:
        err = response.json().get("error", {}).get("message", response.text[:200])
        raise ValueError(f"OpenRouter error {response.status_code}: {err}")

    return response.json()["choices"][0]["message"]["content"]


# ── Public API ────────────────────────────────────────────────────────────────
async def chat_complete(
    messages: List[Dict[str, str]],
    model: str = None,          # ignored — Gemini model comes from config
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    """
    Send messages to Gemini 2.0 Flash.
    Falls back to OpenRouter if Gemini key is missing or quota exceeded.
    """
    # Try Gemini first (fast — 2-4s)
    try:
        return await _call_gemini(messages, temperature, max_tokens, json_mode)
    except ValueError as e:
        if "quota" in str(e).lower() or "key not set" in str(e).lower():
            logger.warning("Gemini unavailable (%s) — trying OpenRouter fallback", e)
        else:
            logger.warning("Gemini failed (%s) — trying OpenRouter fallback", e)
    except Exception as e:
        logger.warning("Gemini exception (%s) — trying OpenRouter fallback", e)

    # Fallback to OpenRouter
    try:
        return await _call_openrouter(messages, temperature, max_tokens, json_mode)
    except Exception as e:
        logger.error("Both Gemini and OpenRouter failed. Last error: %s", e)
        raise ValueError(f"All AI providers failed. Last: {e}")


async def chat_complete_json(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.3,
) -> Dict:
    """Chat completion that always returns a parsed Python dict."""
    raw = await chat_complete(
        messages=messages,
        temperature=temperature,
        json_mode=True,
        max_tokens=3000,
    )

    result = _extract_json(raw)
    if result is not None:
        return result

    logger.error("Could not extract JSON.\nRaw: %s", raw[:400])
    raise ValueError(f"Model returned invalid JSON: {raw[:150]}")


async def get_embedding(text: str) -> List[float]:
    """Local embeddings via chromadb sentence-transformers (free, offline)."""
    try:
        from chromadb.utils import embedding_functions
        ef = embedding_functions.DefaultEmbeddingFunction()
        result = ef([text[:2000]])
        return list(result[0])
    except Exception as e:
        logger.error("Embedding error: %s", e)
        return [0.0] * 384
