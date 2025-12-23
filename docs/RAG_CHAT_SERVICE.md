# RAG Chat Service Documentation

> **AI-Powered Chat with Retrieval-Augmented Generation (RAG)**

The RAG Chat Service provides intelligent Q&A capabilities by combining vector-based document search with LLM generation. Perfect for CV Matcher's interactive chat feature.

**Last Updated:** 2025-12-23

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Two RAG Modes](#two-rag-modes)
4. [API Reference](#api-reference)
5. [Frontend Integration](#frontend-integration)
6. [Vector Service](#vector-service)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The RAG Chat Service enables users to ask questions about documents and receive AI-generated answers based on relevant context. It uses:

- **Vector Embeddings** (sentence-transformers `all-MiniLM-L6-v2`) for semantic search
- **Cosine Similarity** to find relevant document chunks
- **LLM Generation** (Llama or Grok) to create natural language responses
- **Source Attribution** to show which documents were used

**Key Features:**
- ✅ Two RAG modes: Database-backed and In-Memory
- ✅ Embedding-based semantic search
- ✅ Multi-document support
- ✅ Source attribution with relevance scores
- ✅ GDPR-compliant (in-memory mode has no persistence)
- ✅ Multi-language LLM prompts (German default)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │   Chat Component                                  │       │
│  │   - User input                                    │       │
│  │   - Message history                               │       │
│  │   - Optional: InMemoryDocument[] (CV Matcher)    │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ▼ POST /chat/message
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │   Chat API (backend/api/chat.py)                  │       │
│  │   - Route: POST /chat/message                     │       │
│  │   - Accepts: ChatMessageRequest                   │       │
│  │   - Returns: ChatMessageResponse                  │       │
│  └──────────────────────────────────────────────────┘       │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │   Vector Service (backend/services/vector_service)│       │
│  │   - Mode 1: search_similar_documents() [DB]       │       │
│  │   - Mode 2: search_in_memory_documents() [RAM]    │       │
│  │   - Uses: sentence-transformers/all-MiniLM-L6-v2  │       │
│  └──────────────────────────────────────────────────┘       │
│                            ▼                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │   LLM Gateway (backend/services/llm_gateway.py)   │       │
│  │   - Providers: Ollama (Llama), Grok, Anthropic    │       │
│  │   - Builds RAG prompt with context                │       │
│  │   - Generates response                            │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Two RAG Modes

### Mode 1: Database RAG (Traditional)

**Use Case:** Long-term document storage, multi-session persistence

**Flow:**
1. Documents are uploaded via `/documents` endpoints
2. `vector_service.add_document_embedding()` generates embeddings
3. Embeddings stored in PostgreSQL with pgvector extension
4. Chat queries search database via `vector_service.search_similar_documents()`

**Pros:**
- Persistent storage across sessions
- Efficient for large document collections
- Supports multi-user document libraries

**Cons:**
- Requires database setup
- Not GDPR-compliant for sensitive data
- Extra upload step required

### Mode 2: In-Memory RAG (CV Matcher)

**Use Case:** Ephemeral document analysis, GDPR compliance, single-session workflows

**Flow:**
1. Frontend sends documents directly in chat request body
2. `vector_service.search_in_memory_documents()` generates embeddings on-the-fly
3. No database storage - documents discarded after response
4. Each chat request includes full document content

**Pros:**
- ✅ No persistence (GDPR-friendly)
- ✅ No database setup required
- ✅ No separate upload step
- ✅ Immediate availability

**Cons:**
- Higher payload size per request
- Embeddings regenerated each time
- Documents not reusable across sessions

**When to Use:**
- CV Matcher: Documents uploaded for single match analysis
- Privacy-sensitive applications
- Quick document Q&A without setup

---

## API Reference

### Endpoint: `POST /chat/message`

Send a chat message with RAG (Retrieval-Augmented Generation).

**Request Schema: `ChatMessageRequest`**

```python
class InMemoryDocument(BaseModel):
    """In-memory document for RAG without database storage."""
    filename: str  # e.g., "CV.pdf", "Requirements.docx"
    content: str   # Full document text
    type: str      # e.g., "employer", "applicant", "cv"

class ChatMessageRequest(BaseModel):
    message: str                          # Required: User's question
    project_id: Optional[UUID] = None     # For database RAG: scope search
    system_context: Optional[str] = None  # Extra context (e.g., match summary)
    documents: Optional[List[InMemoryDocument]] = None  # For in-memory RAG
    provider: Optional[str] = "ollama"    # "ollama", "grok", "anthropic"
    model: Optional[str] = None           # Model name (provider-specific)
    temperature: Optional[float] = 0.7    # Sampling temperature (0.0-2.0)
    max_tokens: Optional[int] = 500       # Max tokens to generate
    context_limit: Optional[int] = 3      # Number of documents to retrieve
```

**Response Schema: `ChatMessageResponse`**

```python
class DocumentSource(BaseModel):
    document_id: str           # Document ID or "memory_{idx}"
    filename: Optional[str]    # Document filename
    type: str                  # Document type
    relevance_score: float     # 0.0-1.0 (1.0 = perfect match)

class ChatMessageResponse(BaseModel):
    message: str                      # AI-generated response
    sources: List[DocumentSource]     # Documents used for context
    model: str                        # Model that generated response
    provider: str                     # Provider used
```

**Mode Selection:**
- **Database RAG:** Omit `documents` field, provide `project_id`
- **In-Memory RAG:** Provide `documents` field, omit `project_id`

---

## Frontend Integration

### TypeScript Interfaces

```typescript
// src/services/chat.ts

export interface InMemoryDocument {
  filename: string;
  content: string;
  type: string;
}

export interface ChatMessageRequest {
  message: string;
  project_id?: string;
  system_context?: string;
  documents?: InMemoryDocument[];  // NEW: For in-memory RAG
  provider?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  context_limit?: number;
}
```

### Chat Service Usage

```typescript
// Example: Send chat message with in-memory documents
const documents: InMemoryDocument[] = [
  {
    filename: "Michael_Dabrock_CV.pdf",
    content: "Michael Dabrock worked at IBM from 2005-2008...",
    type: "applicant"
  },
  {
    filename: "Job_Requirements.docx",
    content: "We are looking for 5+ years Python experience...",
    type: "employer"
  }
];

const response = await chatService.sendMessage(
  "Wie lange hat Michael bei IBM gearbeitet?",
  "grok",
  "Match Score: 75%",
  undefined,  // no project_id for in-memory mode
  documents   // pass documents directly
);

console.log(response.message);  // "Michael arbeitete 3 Jahre bei IBM (2005-2008)..."
console.log(response.sources);  // [{ filename: "Michael_Dabrock_CV.pdf", relevance_score: 0.89 }]
```

### React Component Integration

```tsx
// src/components/Chat.tsx
interface ChatProps {
  llmType: 'local' | 'grok';
  systemContext?: string;
  documents?: InMemoryDocument[];  // Optional in-memory docs
}

export const Chat: React.FC<ChatProps> = ({ llmType, systemContext, documents }) => {
  const handleSend = async (message: string) => {
    const response = await chatService.sendMessage(
      message,
      llmType,
      systemContext,
      undefined,  // no project_id
      documents   // pass documents
    );
    
    // Display response + sources
  };
};
```

### MatchingView Integration (CV Matcher)

```tsx
// Convert Document[] to InMemoryDocument[]
const inMemoryDocuments = useMemo((): InMemoryDocument[] => {
  return [
    ...employerDocs.map(doc => ({
      filename: doc.name,
      content: doc.content,
      type: 'employer'
    })),
    ...applicantDocs.map(doc => ({
      filename: doc.name,
      content: doc.content,
      type: 'applicant'
    }))
  ];
}, [employerDocs, applicantDocs]);

// Pass to Chat component
<Chat
  llmType={llmType}
  documents={inMemoryDocuments}
  systemContext={`Match Score: ${matchResult.overallScore}%`}
/>
```

---

## Vector Service

### Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Max Sequence:** 256 tokens
- **Speed:** ~3000 docs/sec on CPU
- **Quality:** Good for semantic search

### In-Memory Search Implementation

```python
# backend/services/vector_service.py

def search_in_memory_documents(
    self,
    query_text: str,
    documents: List[dict],
    limit: int = 3
) -> List[tuple[dict, float]]:
    """
    Search for similar documents in memory using embeddings.
    
    1. Generate query embedding
    2. Generate document embeddings
    3. Calculate cosine distances
    4. Return top K results sorted by relevance
    """
    query_embedding = self.generate_embedding(query_text)
    
    results = []
    for doc in documents:
        doc_embedding = self.generate_embedding(doc['content'])
        
        # Cosine distance = 1 - cosine_similarity
        distance = 1.0 - np.dot(query_vec, doc_vec) / (
            np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
        )
        
        results.append((doc, distance))
    
    results.sort(key=lambda x: x[1])  # Sort by distance (lower = better)
    return results[:limit]
```

### Database Search Implementation

```python
# backend/services/vector_service.py

async def search_similar_documents(
    self,
    session: AsyncSession,
    query_text: str,
    user_id: UUID,
    limit: int = 3
) -> List[tuple[Document, float]]:
    """
    Search for similar documents in PostgreSQL using pgvector.
    
    Uses cosine distance operator (<=>).
    """
    query_embedding = self.generate_embedding(query_text)
    
    query = (
        select(Document, Document.embedding.cosine_distance(query_embedding).label('distance'))
        .where(Document.user_id == user_id)
        .where(Document.embedding.isnot(None))
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    
    result = await session.execute(query)
    return [(doc, float(dist)) for doc, dist in result.all()]
```

---

## Examples

### Example 1: CV Matcher Chat (In-Memory RAG)

**Request:**
```json
POST /chat/message
{
  "message": "Wie lange hat Michael bei IBM gearbeitet?",
  "provider": "grok",
  "model": "grok-3",
  "system_context": "Match Analysis: Overall Score 75%",
  "documents": [
    {
      "filename": "Michael_Dabrock_CV.pdf",
      "content": "WORK EXPERIENCE\n\nIBM Corporation (2005-2008)\nSenior Software Engineer\n- Led development of enterprise Java applications\n- Managed team of 5 developers\n...",
      "type": "applicant"
    }
  ],
  "context_limit": 3
}
```

**Response:**
```json
{
  "message": "Michael Dabrock arbeitete 3 Jahre bei IBM Corporation, von 2005 bis 2008. In dieser Zeit war er als Senior Software Engineer tätig und leitete die Entwicklung von Enterprise-Java-Anwendungen sowie ein Team von 5 Entwicklern.",
  "sources": [
    {
      "document_id": "memory_1",
      "filename": "Michael_Dabrock_CV.pdf",
      "type": "applicant",
      "relevance_score": 0.91
    }
  ],
  "model": "grok-3",
  "provider": "grok"
}
```

### Example 2: Database RAG (Multi-User Document Library)

**Request:**
```json
POST /chat/message
{
  "message": "What are the Python requirements?",
  "project_id": "abc-123-def",
  "provider": "ollama",
  "model": "qwen2.5:3b"
}
```

**Backend Flow:**
1. Search user's documents in PostgreSQL with project_id filter
2. Find top 3 most relevant documents via embedding similarity
3. Build RAG prompt with document excerpts
4. Generate response using Llama

**Response:**
```json
{
  "message": "Based on the job requirements document, we need:\n- Python 3.8+\n- 5+ years experience\n- FastAPI or Django framework knowledge\n- PostgreSQL database skills",
  "sources": [
    {
      "document_id": "uuid-abc-123",
      "filename": "job_requirements.pdf",
      "type": "employer",
      "relevance_score": 0.87
    }
  ],
  "model": "qwen2.5:3b",
  "provider": "ollama"
}
```

---

## Troubleshooting

### Problem: "No relevant documents found"

**Cause:** Documents not provided (in-memory) or not in database

**Solutions:**
- **In-Memory RAG:** Check `documents` array is populated in request
- **Database RAG:** Verify documents uploaded and embeddings generated
- Check logs: `📄 In-Memory RAG mode: 2 documents provided`

### Problem: Low relevance scores (<0.5)

**Cause:** Query doesn't match document content semantically

**Solutions:**
- Rephrase question to match document language
- Check document content quality (OCR errors, formatting issues)
- Increase `context_limit` to retrieve more documents

### Problem: Embedding model not loaded

**Error:** `⚠️ Embedding model not available - returning all documents`

**Solutions:**
- Install `sentence-transformers`: `pip install sentence-transformers`
- Check logs for model download errors
- Verify sufficient RAM (model needs ~150MB)

### Problem: Chat returns generic answers (not using context)

**Cause:** Documents not reaching LLM prompt

**Solutions:**
- Check backend logs for RAG mode detection
- Verify `relevant_docs` is not empty
- Inspect LLM prompt (should include `[Document 1]` sections)

### Problem: SFTP deployment fails (Login denied)

**Workaround:** Manual deployment or update credentials

```bash
cd /mnt/e/CodelocalLLM/CV_Matcher/dist
# Update SFTP credentials and retry
```

---

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate embedding (1 doc) | ~50ms | CPU, 384 dimensions |
| In-memory search (3 docs) | ~150ms | 3 embeddings + cosine calc |
| Database search (1000 docs) | ~200ms | pgvector index scan |
| LLM generation (Llama local) | 10-30s | Depends on token count |
| LLM generation (Grok API) | 5-15s | Network latency included |
| Full RAG pipeline | 15-45s | Search + generation combined |

---

## Future Enhancements

- [ ] **Document Chunking:** Split large documents into smaller chunks for better retrieval
- [ ] **Hybrid Search:** Combine vector search with keyword search (BM25)
- [ ] **Reranking:** Use cross-encoder model to rerank retrieved documents
- [ ] **Caching:** Cache embeddings for frequently queried documents
- [ ] **Multi-Language:** Support embeddings for non-English documents
- [ ] **Streaming:** Stream LLM responses for better UX

---

**Documentation Version:** 1.0
**Last Updated:** 2025-12-23
**Maintained By:** Claude Code
