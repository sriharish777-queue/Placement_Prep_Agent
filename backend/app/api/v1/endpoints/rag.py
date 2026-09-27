"""
RAG Career Assistant endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.services.rag_service import rag_query, add_document, seed_knowledge_base

router = APIRouter()


class RAGQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    company: Optional[str] = None
    user_context: Optional[Dict] = None


class AddDocumentRequest(BaseModel):
    doc_id: str
    content: str
    metadata: Dict


@router.post("/query")
async def query_rag(request: RAGQueryRequest):
    """Ask the RAG career assistant a question."""
    try:
        result = await rag_query(
            query=request.query,
            user_context=request.user_context,
            company=request.company,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

    return result


@router.post("/seed")
async def seed_rag():
    """Seed the RAG knowledge base with foundational content."""
    try:
        count = await seed_knowledge_base()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")

    return {"message": f"Seeded {count} documents into knowledge base", "count": count}


@router.post("/documents")
async def add_knowledge_document(request: AddDocumentRequest):
    """Add a custom document to the RAG knowledge base."""
    try:
        await add_document(
            doc_id=request.doc_id,
            content=request.content,
            metadata=request.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

    return {"message": "Document added successfully", "doc_id": request.doc_id}
