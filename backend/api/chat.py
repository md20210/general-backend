"""Chat API endpoints with RAG (Retrieval-Augmented Generation)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from backend.auth.dependencies import current_active_user
from backend.database import get_async_session
from backend.models.user import User
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse, DocumentSource
from backend.services.vector_service import vector_service
from backend.services.llm_gateway import LLMGateway


router = APIRouter(prefix="/chat", tags=["chat"])
llm_gateway = LLMGateway()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Send a chat message with RAG (Retrieval-Augmented Generation).

    Uses vector search to find relevant documents, then generates
    a response using the LLM with the retrieved context.

    Perfect for CV Matcher: Ask questions about match results,
    specific skills, requirements, etc.
    """
    try:
        # 1. Vector Search: Find relevant documents
        relevant_docs = await vector_service.search_similar_documents(
            session=session,
            query_text=request.message,
            user_id=user.id,
            project_id=request.project_id,
            limit=request.context_limit or 3
        )

        if not relevant_docs:
            # No documents found - answer without context
            context = "No relevant documents found in the database."
        else:
            # 2. Build context from top documents
            context_parts = []
            for idx, (doc, distance) in enumerate(relevant_docs, 1):
                # Truncate long content
                content_preview = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
                context_parts.append(f"[Document {idx}]: {content_preview}")

            context = "\n\n".join(context_parts)

        # 3. Build RAG prompt (auf Deutsch für bessere Ergebnisse)
        if request.system_context:
            # Include custom context (e.g., match result summary)
            rag_prompt = f"""System-Kontext:
{request.system_context}

Relevante Dokumente:
{context}

Benutzerfrage: {request.message}

Beantworte die Frage auf Deutsch basierend auf dem System-Kontext und den relevanten Dokumenten. Sei präzise und hilfreich. Zitiere spezifische Details aus den Dokumenten."""
        else:
            rag_prompt = f"""Kontext aus Dokumenten:
{context}

Benutzerfrage: {request.message}

Beantworte die Frage auf Deutsch basierend auf dem obigen Kontext. Wenn der Kontext keine relevanten Informationen enthält, sage es deutlich."""

        # 4. LLM Generation
        llm_response = llm_gateway.generate(
            prompt=rag_prompt,
            provider=request.provider or "ollama",
            model=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 500,
        )

        # 5. Build response with sources
        sources = [
            DocumentSource(
                document_id=str(doc.id),
                filename=doc.filename,
                type=doc.type,
                relevance_score=1.0 - distance  # Convert distance to similarity
            )
            for doc, distance in relevant_docs[:3]  # Top 3 sources
        ]

        return ChatMessageResponse(
            message=llm_response["response"],
            sources=sources,
            model=llm_response["model"],
            provider=llm_response["provider"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat message failed: {str(e)}"
        )
