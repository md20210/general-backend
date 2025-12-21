"""Document Management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import os
import shutil

from backend.auth.dependencies import current_active_user
from backend.database import get_async_session
from backend.models.user import User
from backend.models.document import Document, DocumentType
from backend.schemas.document import (
    DocumentRead,
    DocumentCreate,
    DocumentUpdate,
    DocumentUrlRequest,
    DocumentTextRequest,
)
from backend.services.document_processor import document_processor
from backend.services.vector_store import vector_store, CHROMADB_AVAILABLE
from backend.config import settings


router = APIRouter(prefix="/documents", tags=["documents"])


async def _add_to_vector_store(user_id: UUID, document: Document):
    """Helper to add document to vector store."""
    if not CHROMADB_AVAILABLE:
        return

    try:
        chunks_added = vector_store.add_documents(
            user_id=user_id,
            project_id=document.project_id,
            documents=[{
                "id": str(document.id),
                "content": document.content,
                "metadata": {
                    "type": document.type.value,
                    "filename": document.filename or "",
                    "url": document.url or "",
                    **(document.metadata or {})
                }
            }]
        )

        # Update vector_collection_id
        collection_name = vector_store._get_collection_name(user_id, document.project_id)
        document.vector_collection_id = collection_name

        print(f"Added {chunks_added} chunks to vector store for document {document.id}")
    except Exception as e:
        print(f"Warning: Failed to add to vector store: {e}")


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Upload PDF or DOCX file.

    Automatically extracts text, creates embeddings, and adds to vector store.
    """
    # Validate file type
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        doc_type = DocumentType.PDF
    elif filename.endswith('.docx'):
        doc_type = DocumentType.DOCX
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported"
        )

    # Save file temporarily
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{user.id}_{file.filename}")

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        with open(temp_path, "rb") as f:
            if doc_type == DocumentType.PDF:
                content = document_processor.extract_from_pdf(f)
            else:
                content = document_processor.extract_from_docx(f)

        # Create document
        document = Document(
            user_id=user.id,
            project_id=UUID(project_id) if project_id else None,
            type=doc_type,
            filename=file.filename,
            content=content,
            metadata={"original_size": os.path.getsize(temp_path)}
        )

        session.add(document)
        await session.commit()
        await session.refresh(document)

        # Add to vector store
        await _add_to_vector_store(user.id, document)
        await session.commit()

        return document

    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/url", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def add_url_document(
    request: DocumentUrlRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Scrape URL and create document.

    Automatically extracts text, creates embeddings, and adds to vector store.
    """
    try:
        # Scrape website
        scraped_data = document_processor.scrape_website(request.url)

        # Create document
        document = Document(
            user_id=user.id,
            project_id=request.project_id,
            type=DocumentType.URL,
            url=request.url,
            content=scraped_data["content"],
            metadata={
                "title": scraped_data["title"],
                "description": scraped_data["description"],
                **(request.metadata or {})
            }
        )

        session.add(document)
        await session.commit()
        await session.refresh(document)

        # Add to vector store
        await _add_to_vector_store(user.id, document)
        await session.commit()

        return document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape URL: {str(e)}"
        )


@router.post("/text", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def add_text_document(
    request: DocumentTextRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Create document from raw text.

    Automatically creates embeddings and adds to vector store.
    """
    # Create document
    document = Document(
        user_id=user.id,
        project_id=request.project_id,
        type=DocumentType.TEXT,
        content=request.content,
        metadata={
            "title": request.title,
            **(request.metadata or {})
        }
    )

    session.add(document)
    await session.commit()
    await session.refresh(document)

    # Add to vector store
    await _add_to_vector_store(user.id, document)
    await session.commit()

    return document


@router.get("", response_model=List[DocumentRead])
async def list_documents(
    project_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    List user's documents.

    Optionally filter by project_id.
    """
    query = select(Document).where(Document.user_id == user.id)

    if project_id:
        query = query.where(Document.project_id == project_id)

    query = query.order_by(Document.created_at.desc())

    result = await session.execute(query)
    documents = result.scalars().all()

    return documents


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get document by ID (only if user owns it)."""
    document = await session.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Delete document (only if user owns it)."""
    document = await session.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Note: Vector store chunks will remain but become orphaned
    # Could implement cleanup if needed

    await session.delete(document)
    await session.commit()

    return None
