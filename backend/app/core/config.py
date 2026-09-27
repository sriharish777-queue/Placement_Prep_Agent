"""
Application configuration — reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Placement Prep Copilot"
    DEBUG: bool = False
    SECRET_KEY: str = "changeme-super-secret-key"

    # ── Database ─────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "placement_prep"

    # ── Gemini (primary — fast & free) ───────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # ── OpenRouter (fallback) ────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_FALLBACK_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"

    # ── Vector DB ────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "placement_rag"

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ── File Upload ───────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
