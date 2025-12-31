"""Vector Service for Elasticsearch Showcase using pgvector (PostgreSQL).

This service provides a ChromaDB-compatible API but uses pgvector for persistent storage.
Unlike ChromaDB which stores data ephemerally in containers, pgvector data survives Railway redeploys.
"""
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.document import Document
from backend.services.vector_service import VectorService


class ElasticsearchVectorService:
    """
    Vector service for Elasticsearch Showcase using pgvector.

    Provides ChromaDB-compatible API:
    - add_documents() - Add CV documents with embeddings
    - query() - Semantic search for relevant chunks
    - delete_collection() - Delete all CV data for a user
    - is_available() - Check if service is ready
    """

    def __init__(self):
        """Initialize with pgvector embedding service."""
        self.vector_service = VectorService()

    def is_available(self) -> bool:
        """Check if embedding model is available."""
        return self.vector_service.model is not None

    async def add_documents(
        self,
        session: AsyncSession,
        user_id: UUID,
        documents: List[Dict[str, str]],
        project_id: Optional[UUID] = None,
        chunk_size: int = 500,
    ) -> int:
        """
        Add CV documents to pgvector with embeddings.

        Args:
            session: Database session
            user_id: User ID for isolation
            documents: List of dicts with 'id', 'content', and optional 'metadata'
            project_id: Optional project ID (not used for showcase - always None)
            chunk_size: Max characters per chunk

        Returns:
            Number of chunks added
        """
        if not self.is_available():
            return 0

        total_chunks = 0

        for doc in documents:
            doc_id = doc["id"]
            content = doc["content"]
            metadata = doc.get("metadata", {})

            # Split content into chunks (word-based)
            chunks = self.vector_service.chunk_text(
                content,
                chunk_size=chunk_size,
                overlap=50
            )

            # Add each chunk as a separate Document in pgvector
            for idx, (chunk_text, start_pos) in enumerate(chunks):
                # Generate embedding
                embedding = self.vector_service.generate_embedding(chunk_text)

                if not embedding:
                    continue

                # Create Document record
                chunk_doc = Document(
                    id=uuid4(),
                    user_id=user_id,
                    project_id=project_id,
                    type="cv_showcase",  # Special type for Elasticsearch Showcase
                    filename=f"{doc_id}_chunk_{idx}",
                    content=chunk_text,
                    embedding=embedding,
                    doc_metadata={
                        **metadata,
                        "original_doc_id": doc_id,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "start_position": start_pos,
                    }
                )

                session.add(chunk_doc)
                total_chunks += 1

        await session.commit()
        return total_chunks

    async def query(
        self,
        session: AsyncSession,
        user_id: UUID,
        query_text: str,
        project_id: Optional[UUID] = None,
        n_results: int = 5,
    ) -> List[Dict]:
        """
        Query pgvector for relevant CV chunks.

        Args:
            session: Database session
            user_id: User ID for isolation
            query_text: Query text
            project_id: Optional project ID (not used for showcase)
            n_results: Number of results to return

        Returns:
            List of dicts with 'content', 'metadata', 'distance'
        """
        if not self.is_available():
            return []

        try:
            # Generate query embedding
            query_embedding = self.vector_service.generate_embedding(query_text)

            if not query_embedding:
                return []

            # Cosine similarity search with pgvector
            # 1 - (embedding <=> query_embedding) = cosine similarity
            stmt = (
                select(
                    Document.content,
                    Document.doc_metadata,
                    (1 - Document.embedding.cosine_distance(query_embedding)).label("similarity")
                )
                .where(
                    and_(
                        Document.user_id == user_id,
                        Document.type == "cv_showcase",
                        Document.project_id.is_(None) if project_id is None else Document.project_id == project_id
                    )
                )
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(n_results)
            )

            result = await session.execute(stmt)
            rows = result.all()

            # Format results to match ChromaDB API
            context_chunks = []
            for content, metadata, similarity in rows:
                context_chunks.append({
                    "content": content,
                    "metadata": metadata or {},
                    "distance": 1 - similarity,  # Convert similarity to distance
                })

            return context_chunks

        except Exception as e:
            print(f"Error querying pgvector: {e}")
            return []

    async def delete_collection(
        self,
        session: AsyncSession,
        user_id: UUID,
        project_id: Optional[UUID] = None
    ):
        """
        Delete all CV showcase documents for a user from pgvector.

        Args:
            session: Database session
            user_id: User ID whose data should be deleted
            project_id: Optional project ID (not used for showcase)
        """
        try:
            stmt = delete(Document).where(
                and_(
                    Document.user_id == user_id,
                    Document.type == "cv_showcase",
                    Document.project_id.is_(None) if project_id is None else Document.project_id == project_id
                )
            )

            result = await session.execute(stmt)
            await session.commit()

            deleted_count = result.rowcount
            print(f"Deleted {deleted_count} CV showcase documents for user {user_id} from pgvector")

        except Exception as e:
            print(f"Error deleting collection from pgvector: {e}")
            raise
