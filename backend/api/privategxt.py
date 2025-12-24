"""PrivateGxT API endpoints."""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from backend.services.privategxt_service import privategxt_service


router = APIRouter(prefix="/privategxt", tags=["PrivateGxT"])


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    provider: str = "anthropic"
    model: Optional[str] = None
    temperature: float = 0.7


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF, DOCX, or TXT).

    The document will be processed, chunked, and stored in ChromaDB for RAG queries.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()

        # Process document
        result = await privategxt_service.upload_document(
            file_bytes=file_bytes,
            filename=file.filename or "unknown.txt"
        )

        return {
            "success": True,
            "document": result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents")
async def get_documents():
    """Get list of all uploaded documents."""
    try:
        documents = privategxt_service.get_documents()
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a specific document and all its chunks."""
    try:
        deleted = await privategxt_service.delete_document(doc_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "success": True,
            "message": "Document deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_all():
    """Clear all documents and chat history."""
    try:
        result = await privategxt_service.clear_all()
        return {
            "success": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with RAG context from uploaded documents.

    The message will be used to query relevant document chunks,
    which are then provided as context to the LLM.
    """
    try:
        result = await privategxt_service.chat(
            message=request.message,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature
        )

        return {
            "success": True,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/chat/history")
async def get_chat_history():
    """Get chat history."""
    try:
        history = privategxt_service.get_chat_history()
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get PrivateGxT statistics."""
    try:
        stats = privategxt_service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
