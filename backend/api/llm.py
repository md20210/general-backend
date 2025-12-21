"""LLM API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.services.llm_gateway import llm_gateway
from backend.schemas.llm import (
    LLMGenerateRequest,
    LLMGenerateResponse,
    LLMEmbedRequest,
    LLMEmbedResponse,
    LLMModelsResponse,
    LLMModel,
)


router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/generate", response_model=LLMGenerateResponse)
async def generate_text(
    request: LLMGenerateRequest,
    user: User = Depends(current_active_user),
):
    """
    Generate text using specified LLM provider.

    Requires authentication.
    """
    try:
        result = llm_gateway.generate(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            timeout=request.timeout,
        )
        return LLMGenerateResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM generation failed: {str(e)}",
        )


@router.get("/models", response_model=LLMModelsResponse)
async def list_models(
    provider: Optional[str] = None,
    user: User = Depends(current_active_user),
):
    """
    List available LLM models.

    Optionally filter by provider (ollama, grok, anthropic).
    Requires authentication.
    """
    try:
        models = llm_gateway.list_models(provider=provider)
        return LLMModelsResponse(
            models=[LLMModel(**m) for m in models],
            total=len(models),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}",
        )


@router.post("/embed", response_model=LLMEmbedResponse)
async def create_embedding(
    request: LLMEmbedRequest,
    user: User = Depends(current_active_user),
):
    """
    Generate embeddings for text (using Ollama).

    Requires authentication.
    """
    try:
        embedding = llm_gateway.embed(
            text=request.text,
            model=request.model,
        )

        return LLMEmbedResponse(
            embedding=embedding,
            model=request.model or "nomic-embed-text",
            dimensions=len(embedding),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}",
        )
