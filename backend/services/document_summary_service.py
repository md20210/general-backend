"""
Document Summary Service

Provides aggregated statistics and summaries of all user documents
in the vector database.

This service is used by the CV Matcher frontend to show comprehensive
summaries of all uploaded documents (PDFs, URLs, text files).
"""
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document, DocumentType


class DocumentSummaryService:
    """
    Service for generating document summaries and statistics.

    Methods:
        - get_user_summary: Get aggregated statistics for all user documents
        - get_documents_by_type: Get documents grouped by type
    """

    async def get_user_summary(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_id: Optional[UUID] = None
    ) -> Dict:
        """
        Get comprehensive summary of all user documents.

        Args:
            session: Database session
            user_id: User ID
            project_id: Optional project filter

        Returns:
            Dictionary with:
            - total_documents: int
            - total_words: int
            - total_chars: int
            - documents_by_type: Dict[str, int]
            - documents: List[Dict] with filename, type, word_count, char_count, content
        """
        # Build base query
        query = select(Document).where(Document.user_id == user_id)

        if project_id:
            query = query.where(Document.project_id == project_id)

        query = query.order_by(Document.created_at.desc())

        # Execute query
        result = await session.execute(query)
        documents = result.scalars().all()

        if not documents:
            return {
                "total_documents": 0,
                "total_words": 0,
                "total_chars": 0,
                "documents_by_type": {},
                "documents": []
            }

        # Calculate statistics
        total_words = 0
        total_chars = 0
        documents_by_type: Dict[str, int] = {}
        document_details = []

        for doc in documents:
            # Count words (approximate)
            word_count = len(doc.content.split()) if doc.content else 0
            char_count = len(doc.content) if doc.content else 0

            total_words += word_count
            total_chars += char_count

            # Group by type
            doc_type = doc.type.value if isinstance(doc.type, DocumentType) else str(doc.type)
            documents_by_type[doc_type] = documents_by_type.get(doc_type, 0) + 1

            # Add to details
            document_details.append({
                "id": str(doc.id),
                "filename": doc.filename or doc.url or "Unnamed",
                "type": doc_type,
                "word_count": word_count,
                "char_count": char_count,
                "content": doc.content,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            })

        return {
            "total_documents": len(documents),
            "total_words": total_words,
            "total_chars": total_chars,
            "documents_by_type": documents_by_type,
            "documents": document_details
        }

    async def get_documents_by_type(
        self,
        session: AsyncSession,
        user_id: UUID,
        doc_type: DocumentType,
        project_id: Optional[UUID] = None
    ) -> List[Document]:
        """
        Get all documents of a specific type for a user.

        Args:
            session: Database session
            user_id: User ID
            doc_type: Document type (pdf, url, text, etc.)
            project_id: Optional project filter

        Returns:
            List of documents
        """
        query = select(Document).where(
            Document.user_id == user_id,
            Document.type == doc_type
        )

        if project_id:
            query = query.where(Document.project_id == project_id)

        query = query.order_by(Document.created_at.desc())

        result = await session.execute(query)
        return result.scalars().all()


# Singleton instance
document_summary_service = DocumentSummaryService()
