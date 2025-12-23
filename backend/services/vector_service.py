"""Vector Service using pgvector (PostgreSQL native)."""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import re

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("WARNING: sentence-transformers not installed - embeddings disabled")

from backend.models.document import Document


class VectorService:
    """Vector service for document embeddings using pgvector."""

    def __init__(self):
        """Initialize embedding model."""
        self.model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                # Using all-MiniLM-L6-v2 (384 dimensions, fast, good quality)
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Embedding model loaded: all-MiniLM-L6-v2")
            except Exception as e:
                print(f"⚠️ Failed to load embedding model: {e}")
                self.model = None

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Tuple[str, int]]:
        """
        Split text into overlapping chunks for better embeddings.

        Args:
            text: Input text to chunk
            chunk_size: Target chunk size in words
            overlap: Number of overlapping words between chunks

        Returns:
            List of (chunk_text, start_position) tuples
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()

        # Split into words
        words = text.split()

        if len(words) <= chunk_size:
            # Text is small enough - return as single chunk
            return [(text, 0)]

        chunks = []
        start = 0

        while start < len(words):
            # Extract chunk
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)

            chunks.append((chunk_text, start))

            # Move to next chunk with overlap
            if end >= len(words):
                break

            start += chunk_size - overlap

        return chunks

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.

        Args:
            text: Input text

        Returns:
            List of floats (384 dimensions) or None if model unavailable
        """
        if not self.model:
            return None

        try:
            # Generate embedding
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    async def add_document_embedding(
        self,
        session: AsyncSession,
        document: Document,
        use_chunking: bool = True,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> bool:
        """
        Generate and add embedding to document.

        For large documents (>500 words), splits into overlapping chunks
        and creates separate document records for each chunk to improve
        RAG search quality.

        Args:
            session: Database session
            document: Document instance (will be updated with first chunk or whole doc)
            use_chunking: Whether to split large documents into chunks
            chunk_size: Target chunk size in words
            overlap: Number of overlapping words between chunks

        Returns:
            True if successful, False otherwise
        """
        if not self.model:
            print("⚠️ Embedding model not available - skipping")
            return False

        try:
            word_count = len(document.content.split())

            # Use chunking for large documents
            if use_chunking and word_count > chunk_size:
                chunks = self.chunk_text(document.content, chunk_size, overlap)
                print(f"📄 Document has {word_count} words - splitting into {len(chunks)} chunks")

                # Update original document with first chunk
                first_chunk_text, _ = chunks[0]
                embedding = self.generate_embedding(first_chunk_text)

                if not embedding:
                    return False

                document.content = first_chunk_text
                document.embedding = embedding
                document.doc_metadata = document.doc_metadata or {}
                document.doc_metadata.update({
                    'is_chunk': True,
                    'chunk_index': 0,
                    'total_chunks': len(chunks),
                    'chunk_size': chunk_size,
                    'original_word_count': word_count
                })

                # Create additional document records for remaining chunks
                for idx, (chunk_text, start_pos) in enumerate(chunks[1:], 1):
                    chunk_embedding = self.generate_embedding(chunk_text)

                    if not chunk_embedding:
                        continue

                    from uuid import uuid4
                    chunk_doc = Document(
                        id=uuid4(),
                        user_id=document.user_id,
                        project_id=document.project_id,
                        type=document.type,
                        filename=document.filename,
                        url=document.url,
                        content=chunk_text,
                        embedding=chunk_embedding,
                        doc_metadata={
                            'is_chunk': True,
                            'chunk_index': idx,
                            'total_chunks': len(chunks),
                            'chunk_size': chunk_size,
                            'parent_id': str(document.id),
                            'start_position': start_pos,
                            'original_word_count': word_count
                        }
                    )
                    session.add(chunk_doc)

                await session.commit()
                print(f"✅ Added {len(chunks)} chunk embeddings for document {document.id}")
                return True

            else:
                # Small document - single embedding
                embedding = self.generate_embedding(document.content)

                if not embedding:
                    return False

                document.embedding = embedding
                document.doc_metadata = document.doc_metadata or {}
                document.doc_metadata.update({
                    'is_chunk': False,
                    'word_count': word_count
                })

                await session.commit()
                print(f"✅ Added embedding to document {document.id} (no chunking needed)")
                return True

        except Exception as e:
            print(f"❌ Error adding embedding: {e}")
            return False

    async def search_similar_documents(
        self,
        session: AsyncSession,
        query_text: str,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        limit: int = 5,
        distance_threshold: float = 1.0
    ) -> List[tuple[Document, float]]:
        """
        Search for similar documents using vector similarity.

        Args:
            session: Database session
            query_text: Search query
            user_id: User ID for filtering
            project_id: Optional project ID for filtering
            limit: Maximum number of results
            distance_threshold: Maximum cosine distance (0-2, lower is more similar)

        Returns:
            List of (Document, distance) tuples, ordered by similarity
        """
        if not self.model:
            print("⚠️ Embedding model not available - returning empty results")
            return []

        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query_text)
            if not query_embedding:
                return []

            # Build query with vector similarity using <=> operator (cosine distance)
            query = (
                select(
                    Document,
                    Document.embedding.cosine_distance(query_embedding).label('distance')
                )
                .where(Document.user_id == user_id)
                .where(Document.embedding.isnot(None))
            )

            # Filter by project if specified
            if project_id:
                query = query.where(Document.project_id == project_id)

            # Order by similarity and limit results
            query = (
                query
                .where(Document.embedding.cosine_distance(query_embedding) < distance_threshold)
                .order_by(Document.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )

            result = await session.execute(query)
            documents_with_distance = result.all()

            return [(doc, float(dist)) for doc, dist in documents_with_distance]

        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []

    async def get_document_context(
        self,
        session: AsyncSession,
        query_text: str,
        user_id: UUID,
        project_id: Optional[UUID] = None,
        limit: int = 3
    ) -> str:
        """
        Get relevant document context for RAG (Retrieval Augmented Generation).

        Args:
            session: Database session
            query_text: Search query
            user_id: User ID
            project_id: Optional project ID
            limit: Number of documents to retrieve

        Returns:
            Formatted context string with relevant document excerpts
        """
        similar_docs = await self.search_similar_documents(
            session=session,
            query_text=query_text,
            user_id=user_id,
            project_id=project_id,
            limit=limit
        )

        if not similar_docs:
            return ""

        # Format context
        context_parts = []
        for doc, distance in similar_docs:
            # Truncate long content
            content_preview = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
            source = doc.filename or doc.url or "text document"

            context_parts.append(
                f"[Source: {source}, Relevance: {(1-distance/2)*100:.1f}%]\n{content_preview}"
            )

        return "\n\n---\n\n".join(context_parts)


# Global instance
vector_service = VectorService()
