"""PrivateGxT Service - RAG-based document chat showcase."""
import os
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import BytesIO

# Heavy imports are deferred to first use to reduce startup memory and time
from backend.services.llm_gateway import llm_gateway


class PrivateGxTService:
    """Service for PrivateGxT - RAG-powered document chat showcase."""

    def __init__(self):
        """Defer heavy initialization until first use."""
        self._chroma_client = None
        self._collection = None

        # In-memory chat history (demo purposes)
        self.chat_history: List[Dict[str, Any]] = []

        # Chunking parameters
        self.chunk_size = 500  # characters per chunk
        self.chunk_overlap = 50  # overlap between chunks

    def _get_collection(self):
        """Lazy-initialize ChromaDB on first use."""
        if self._collection is None:
            import chromadb
            from chromadb.config import Settings
            self._chroma_client = chromadb.PersistentClient(
                path="./chroma_data/privategxt",
                settings=Settings(anonymized_telemetry=False)
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name="privategxt_demo",
                metadata={"description": "PrivateGxT Demo Collection"}
            )
        return self._collection

    @property
    def collection(self):
        return self._get_collection()

    @property
    def chroma_client(self):
        self._get_collection()
        return self._chroma_client

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF file."""
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(BytesIO(file_bytes))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    def extract_text_from_txt(self, file_bytes: bytes) -> str:
        """Extract text from TXT file."""
        try:
            return file_bytes.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Try other encodings
            try:
                return file_bytes.decode('latin-1').strip()
            except Exception as e:
                raise ValueError(f"Failed to decode text file: {str(e)}")

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """Extract text based on file extension."""
        ext = filename.lower().split('.')[-1]

        if ext == 'pdf':
            return self.extract_text_from_pdf(file_bytes)
        elif ext == 'docx':
            return self.extract_text_from_docx(file_bytes)
        elif ext == 'txt':
            return self.extract_text_from_txt(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Supported: PDF, DOCX, TXT")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > self.chunk_size // 2:  # Only if reasonable
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - self.chunk_overlap

        return [c for c in chunks if c]  # Remove empty chunks

    async def upload_document(
        self,
        file_bytes: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """
        Upload and process document.

        Args:
            file_bytes: Raw file bytes
            filename: Original filename

        Returns:
            Document metadata
        """
        # Extract text
        text = self.extract_text(file_bytes, filename)

        if not text or len(text) < 10:
            raise ValueError("Document appears to be empty or too short")

        # Generate document ID
        doc_id = str(uuid.uuid4())

        # Hash for deduplication
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Check if document already exists
        existing = self.collection.get(where={"hash": text_hash})
        if existing and existing['ids']:
            raise ValueError("This document has already been uploaded")

        # Chunk text
        chunks = self.chunk_text(text)

        # Prepare data for ChromaDB
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "hash": text_hash,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            for i in range(len(chunks))
        ]

        # Add to ChromaDB (embeddings generated automatically)
        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadatas
        )

        return {
            "doc_id": doc_id,
            "filename": filename,
            "chunks": len(chunks),
            "characters": len(text),
            "uploaded_at": datetime.utcnow().isoformat()
        }

    def get_documents(self) -> List[Dict[str, Any]]:
        """Get list of uploaded documents."""
        # Get all items from collection
        all_data = self.collection.get()

        if not all_data['metadatas']:
            return []

        # Group by document ID
        docs_dict = {}
        for metadata in all_data['metadatas']:
            doc_id = metadata['doc_id']
            if doc_id not in docs_dict:
                docs_dict[doc_id] = {
                    "doc_id": doc_id,
                    "filename": metadata['filename'],
                    "chunks": metadata['total_chunks'],
                    "uploaded_at": metadata['uploaded_at']
                }

        return list(docs_dict.values())

    async def delete_document(self, doc_id: str) -> bool:
        """Delete document and all its chunks."""
        # Get all chunks for this document
        results = self.collection.get(where={"doc_id": doc_id})

        if not results['ids']:
            return False

        # Delete all chunks
        self.collection.delete(ids=results['ids'])

        return True

    async def clear_all(self) -> Dict[str, int]:
        """Clear all documents and chat history."""
        # Get all IDs
        all_data = self.collection.get()
        deleted_chunks = len(all_data['ids']) if all_data['ids'] else 0

        # Delete all from collection
        if all_data['ids']:
            self.collection.delete(ids=all_data['ids'])

        # Clear chat history
        messages_cleared = len(self.chat_history)
        self.chat_history = []

        return {
            "documents_cleared": len(set(m['doc_id'] for m in all_data['metadatas'])) if all_data['metadatas'] else 0,
            "chunks_cleared": deleted_chunks,
            "messages_cleared": messages_cleared
        }

    async def chat(
        self,
        message: str,
        provider: str = "ollama",
        model: Optional[str] = None,
        temperature: float = 0.7,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Chat with RAG context.

        Args:
            message: User message
            provider: LLM provider (ollama, anthropic, grok)
            model: Optional model override
            temperature: Sampling temperature
            n_results: Number of chunks to retrieve

        Returns:
            Response with sources
        """
        # Query ChromaDB for relevant chunks
        results = self.collection.query(
            query_texts=[message],
            n_results=min(n_results, self.collection.count())
        )

        # Build context from retrieved chunks
        context_chunks = []
        sources = []

        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                context_chunks.append(f"[Source {i+1}: {metadata['filename']} - Chunk {metadata['chunk_index']+1}]\n{doc}")
                sources.append({
                    "filename": metadata['filename'],
                    "chunk_index": metadata['chunk_index'],
                    "doc_id": metadata['doc_id']
                })

        # Build prompt with context
        if context_chunks:
            context_text = "\n\n---\n\n".join(context_chunks)
            prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided document context.

Context from uploaded documents:
{context_text}

User Question: {message}

Instructions:
- Answer based on the context provided
- If the answer is not in the context, say so clearly
- Be concise and precise
- Reference specific sources when applicable"""
        else:
            prompt = f"""You are a helpful AI assistant. The user has not uploaded any documents yet.

User Question: {message}

Instructions:
- Politely inform them that no documents have been uploaded
- Suggest they upload documents to get contextual answers"""

        # Generate response using LLM Gateway
        llm_response = llm_gateway.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=1000
        )

        # Store in chat history
        chat_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": llm_response['response'],
            "provider": provider,
            "model": llm_response['model'],
            "sources": sources,
            "usage": llm_response['usage']
        }

        self.chat_history.append(chat_entry)

        return {
            "response": llm_response['response'],
            "sources": sources,
            "provider": provider,
            "model": llm_response['model'],
            "usage": llm_response['usage']
        }

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history."""
        return self.chat_history

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        all_data = self.collection.get()

        unique_docs = set()
        if all_data['metadatas']:
            unique_docs = set(m['doc_id'] for m in all_data['metadatas'])

        return {
            "documents": len(unique_docs),
            "chunks": len(all_data['ids']) if all_data['ids'] else 0,
            "messages": len(self.chat_history)
        }


# Global instance
privategxt_service = PrivateGxTService()
