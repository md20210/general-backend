# Document Summary Service

## Overview

The Document Summary Service provides comprehensive statistics and summaries of all user documents stored in the vector database. This service is crucial for the CV Matcher frontend's "Zusammenfassung" (Summary) feature, which displays aggregated information from ALL documents including PDFs, URLs, and text files.

## Problem it Solves

Previously, the CV Matcher frontend only showed summaries of **locally stored documents** (in browser memory). When users uploaded URLs (e.g., www.dabrock.eu), these were scraped, stored in the PostgreSQL vector database, but NOT included in the summary display. This led to incomplete summaries missing important information from URLs.

## Architecture

```
Frontend (DocumentSection.tsx)
    ↓
Frontend Service (documentService.getDocumentsSummary())
    ↓
Backend API (/documents/summary/all)
    ↓
Backend Service (document_summary_service.get_user_summary())
    ↓
PostgreSQL Database (documents table with pgvector)
```

## Backend Service

### File: `backend/services/document_summary_service.py`

#### Class: `DocumentSummaryService`

**Methods:**

1. **`get_user_summary(session, user_id, project_id=None)`**
   - Returns comprehensive summary of all user documents
   - **Returns:**
     ```python
     {
         "total_documents": int,  # Total count of documents
         "total_words": int,      # Aggregate word count
         "total_chars": int,      # Aggregate character count
         "documents_by_type": {   # Grouped by type
             "pdf": 2,
             "url": 1,
             "text": 1
         },
         "documents": [           # Individual document details
             {
                 "id": "uuid",
                 "filename": "CV.pdf" | "www.dabrock.eu",
                 "type": "pdf" | "url" | "text",
                 "word_count": 1500,
                 "char_count": 8000,
                 "content": "Full document content...",
                 "created_at": "2025-01-01T12:00:00"
             }
         ]
     }
     ```

2. **`get_documents_by_type(session, user_id, doc_type, project_id=None)`**
   - Returns all documents of a specific type (pdf, url, text, etc.)

### Singleton Instance

```python
from backend.services.document_summary_service import document_summary_service

summary = await document_summary_service.get_user_summary(
    session=session,
    user_id=user.id
)
```

## API Endpoint

### GET `/documents/summary/all`

**Description:** Get comprehensive summary of all user documents in vector database

**Query Parameters:**
- `project_id` (optional): Filter by project UUID

**Authentication:** Required (JWT token)

**Response:**
```json
{
    "total_documents": 4,
    "total_words": 5432,
    "total_chars": 28901,
    "documents_by_type": {
        "pdf": 2,
        "url": 1,
        "text": 1
    },
    "documents": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "filename": "www.dabrock.eu",
            "type": "url",
            "word_count": 1200,
            "char_count": 6500,
            "content": "Michael Dabrock worked at IBM from 2010-2015...",
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

**Usage Example (curl):**
```bash
curl -X GET "https://api.example.com/documents/summary/all" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Frontend Integration

### File: `src/services/document.ts`

Add method to document service:

```typescript
async getDocumentsSummary(projectId?: string): Promise<DocumentSummary> {
  const params = projectId ? { project_id: projectId } : {}
  const response = await api.get('/documents/summary/all', { params })
  return response.data
}
```

### File: `src/components/DocumentSection.tsx`

```typescript
const [backendSummary, setBackendSummary] = useState(null);

const loadBackendSummary = async () => {
  try {
    const summary = await documentService.getDocumentsSummary();
    setBackendSummary(summary);
  } catch (error) {
    console.error('Failed to load summary:', error);
  }
};

// Show combined summary (local docs + backend docs)
const totalDocs = docs.length + (backendSummary?.total_documents || 0);
const totalWords = localWords + (backendSummary?.total_words || 0);
```

## Use Cases

### 1. CV Matcher Summary Button

When user clicks "📊 Zusammenfassung" button:
1. Frontend calls `/documents/summary/all`
2. Backend aggregates ALL documents from vector DB
3. User sees complete summary including:
   - Uploaded PDFs: "Michael_CV.pdf"
   - Scraped URLs: "www.dabrock.eu" (with IBM information!)
   - Text documents: "Cover_Letter.txt"

### 2. Document Analytics

Track document usage:
```python
summary = await document_summary_service.get_user_summary(session, user.id)
print(f"User has {summary['documents_by_type']['url']} URLs stored")
```

### 3. Storage Optimization

```python
# Find documents by type for cleanup
urls = await document_summary_service.get_documents_by_type(
    session, user.id, DocumentType.URL
)
```

## Benefits

✅ **Complete Visibility**: Shows ALL documents including URLs from vector DB
✅ **Real-time Stats**: Accurate word/character counts
✅ **Type Breakdown**: See how many PDFs vs URLs vs texts
✅ **Full Content Access**: All scraped content available
✅ **User-specific**: Secure, only shows user's own documents

## Testing

### Test Backend Service

```python
from backend.services.document_summary_service import document_summary_service

async def test_summary():
    summary = await document_summary_service.get_user_summary(
        session=test_session,
        user_id=test_user_id
    )
    assert summary["total_documents"] > 0
    assert "documents_by_type" in summary
```

### Test API Endpoint

```bash
# Upload a URL first
curl -X POST "http://localhost:8000/documents/url" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.dabrock.eu"}'

# Get summary
curl -X GET "http://localhost:8000/documents/summary/all" \
  -H "Authorization: Bearer TOKEN"
```

## Future Enhancements

- [ ] Add filtering by date range
- [ ] Add search within summary
- [ ] Export summary as CSV/JSON
- [ ] Add document comparison
- [ ] LLM-generated summary text

## Related Documentation

- [Vector Service](VECTOR_SERVICE.md)
- [Document Processor](DOCUMENT_PROCESSOR.md)
- [RAG Chat Service](RAG_CHAT_SERVICE.md)
