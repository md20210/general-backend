"""Vector Store Service using ChromaDB."""
import os
from typing import List, Dict, Optional
from uuid import UUID

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("WARNING: ChromaDB not installed - vector store features disabled")

from backend.config import settings


class VectorStore:
    """Vector store for document embeddings using ChromaDB."""

    def __init__(self):
        """Initialize ChromaDB client."""
        if not CHROMADB_AVAILABLE:
            self.client = None
            return

        try:
            # Ensure persist directory exists
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            print(f"✅ ChromaDB initialized at {settings.CHROMA_PERSIST_DIRECTORY}")
        except Exception as e:
            print(f"⚠️  ChromaDB initialization failed: {e}")
            print("ChromaDB features will be disabled")
            self.client = None

    def is_available(self) -> bool:
        """Check if ChromaDB is available and initialized."""
        return self.client is not None

    def _get_collection_name(self, user_id: UUID, project_id: Optional[UUID] = None) -> str:
        """
        Generate collection name with user isolation.

        Format: user_{user_id}_project_{project_id}
        Or: user_{user_id}_global (if no project)
        """
        user_str = str(user_id).replace("-", "_")
        if project_id:
            project_str = str(project_id).replace("-", "_")
            return f"user_{user_str}_project_{project_str}"
        else:
            return f"user_{user_str}_global"

    def get_or_create_collection(self, user_id: UUID, project_id: Optional[UUID] = None):
        """Get or create a collection for user/project."""
        if not CHROMADB_AVAILABLE or not self.client:
            raise RuntimeError("ChromaDB not available")

        collection_name = self._get_collection_name(user_id, project_id)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "user_id": str(user_id),
                "project_id": str(project_id) if project_id else None
            }
        )

    def add_documents(
        self,
        user_id: UUID,
        documents: List[Dict[str, str]],
        project_id: Optional[UUID] = None,
        chunk_size: int = 500,
    ) -> int:
        """
        Add documents to vector store with chunking.

        Args:
            user_id: User ID for isolation
            documents: List of dicts with 'id', 'content', and optional metadata
            project_id: Optional project ID
            chunk_size: Max characters per chunk

        Returns:
            Number of chunks added
        """
        if not CHROMADB_AVAILABLE or not self.client:
            return 0

        collection = self.get_or_create_collection(user_id, project_id)
        total_chunks = 0

        for doc in documents:
            doc_id = doc["id"]
            content = doc["content"]
            metadata = doc.get("metadata", {})

            # Split content into chunks
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

            # Add each chunk
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{idx}"
                chunk_metadata = {
                    **metadata,
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                }

                collection.add(
                    documents=[chunk],
                    metadatas=[chunk_metadata],
                    ids=[chunk_id]
                )
                total_chunks += 1

        return total_chunks

    def query(
        self,
        user_id: UUID,
        query_text: str,
        project_id: Optional[UUID] = None,
        n_results: int = 5,
    ) -> List[Dict]:
        """
        Query vector store for relevant chunks.

        Args:
            user_id: User ID for isolation
            query_text: Query text
            project_id: Optional project ID
            n_results: Number of results to return

        Returns:
            List of dicts with content, metadata, distance
        """
        if not CHROMADB_AVAILABLE or not self.client:
            return []

        try:
            collection = self.get_or_create_collection(user_id, project_id)

            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )

            # Format results
            context_chunks = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results.get('distances') else None

                    context_chunks.append({
                        "content": doc,
                        "metadata": metadata,
                        "distance": distance
                    })

            return context_chunks

        except Exception as e:
            print(f"Error querying vector store: {e}")
            return []

    def delete_collection(self, user_id: UUID, project_id: Optional[UUID] = None):
        """Delete a user's collection."""
        if not CHROMADB_AVAILABLE or not self.client:
            return

        try:
            collection_name = self._get_collection_name(user_id, project_id)
            self.client.delete_collection(collection_name)
            print(f"Deleted collection: {collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")

    def delete_all_user_collections(self, user_id: UUID):
        """Delete all collections for a user."""
        if not CHROMADB_AVAILABLE or not self.client:
            return

        try:
            # List all collections
            collections = self.client.list_collections()
            user_prefix = f"user_{str(user_id).replace('-', '_')}_"

            # Delete collections matching user prefix
            for collection in collections:
                if collection.name.startswith(user_prefix):
                    self.client.delete_collection(collection.name)
                    print(f"Deleted collection: {collection.name}")

        except Exception as e:
            print(f"Error deleting user collections: {e}")

    def list_user_collections(self, user_id: UUID) -> List[str]:
        """List all collections for a user."""
        if not CHROMADB_AVAILABLE or not self.client:
            return []

        try:
            collections = self.client.list_collections()
            user_prefix = f"user_{str(user_id).replace('-', '_')}_"

            return [
                collection.name
                for collection in collections
                if collection.name.startswith(user_prefix)
            ]

        except Exception as e:
            print(f"Error listing collections: {e}")
            return []


# Global instance
vector_store = VectorStore()
