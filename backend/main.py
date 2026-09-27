"""
AI Placement Preparation & Career Copilot
Main FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_db, close_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="AI Placement Prep & Career Copilot",
    description="An adaptive AI platform for personalized placement preparation.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Middleware ──────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
