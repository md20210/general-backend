# Phase 3: Document & Project Management - ABGESCHLOSSEN ✅

## Erstellte Dateien

### 1. Schemas
- ✅ `backend/schemas/project.py` - Project Schemas
  - ProjectCreate, ProjectUpdate, ProjectRead
- ✅ `backend/schemas/document.py` - Document Schemas
  - DocumentCreate, DocumentUpdate, DocumentRead
  - DocumentUploadRequest, DocumentUrlRequest, DocumentTextRequest

### 2. Project API
- ✅ `backend/api/projects.py` - Project CRUD Endpoints
  - POST `/projects` - Create project
  - GET `/projects` - List user's projects
  - GET `/projects/{id}` - Get project
  - PATCH `/projects/{id}` - Update project
  - DELETE `/projects/{id}` - Delete project + vector collection

### 3. Document API
- ✅ `backend/api/documents.py` - Document Management Endpoints
  - POST `/documents/upload` - Upload PDF/DOCX
  - POST `/documents/url` - Scrape URL
  - POST `/documents/text` - Add raw text
  - GET `/documents?project_id=...` - List documents
  - GET `/documents/{id}` - Get document
  - DELETE `/documents/{id}` - Delete document

### 4. Integration
- ✅ Automatic text extraction (PDF, DOCX, URL)
- ✅ Automatic embedding generation
- ✅ Automatic vector store integration
- ✅ User isolation (all operations user-scoped)
- ✅ Cascade deletion (Project → Documents → Vector Collection)

## API Endpoints (Neu)

### Projects

**POST `/projects`**
```json
{
  "name": "My CV Matching Project",
  "description": "Testing CV Matcher",
  "type": "cv_matcher",
  "config": {
    "llm_provider": "ollama",
    "model": "qwen2.5:3b"
  }
}
```

**GET `/projects`**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "name": "My CV Matching Project",
    "type": "cv_matcher",
    "created_at": "2025-12-21T...",
    "updated_at": "2025-12-21T..."
  }
]
```

**PATCH `/projects/{id}`**
```json
{
  "name": "Updated Project Name",
  "config": {"new_setting": true}
}
```

**DELETE `/projects/{id}`**
- Status: 204 No Content
- Deletes project, all documents, chats, matches, vector collection

### Documents

**POST `/documents/upload`**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@resume.pdf" \
  -F "project_id=uuid-here"
```

Response:
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "project_id": "uuid",
  "type": "pdf",
  "filename": "resume.pdf",
  "content": "Extracted text...",
  "vector_collection_id": "user_xxx_project_yyy",
  "metadata": {"original_size": 12345},
  "created_at": "2025-12-21T..."
}
```

**POST `/documents/url`**
```json
{
  "url": "https://www.dabrock.info",
  "project_id": "uuid-here",
  "metadata": {"source": "homepage"}
}
```

Response:
```json
{
  "id": "uuid",
  "type": "url",
  "url": "https://www.dabrock.info",
  "content": "Scraped content...",
  "metadata": {
    "title": "Michael Dabrock",
    "description": "Portfolio website",
    "source": "homepage"
  }
}
```

**POST `/documents/text`**
```json
{
  "content": "This is my raw text document about AI and ML.",
  "title": "AI Notes",
  "project_id": "uuid-here"
}
```

**GET `/documents?project_id=uuid`**
```json
[
  {
    "id": "uuid",
    "type": "pdf",
    "filename": "resume.pdf",
    "content": "...",
    "created_at": "..."
  },
  {
    "id": "uuid",
    "type": "url",
    "url": "https://...",
    "content": "...",
    "created_at": "..."
  }
]
```

**GET `/documents/{id}`**
- Returns single document (only if user owns it)

**DELETE `/documents/{id}`**
- Status: 204 No Content
- Note: Vector store chunks become orphaned (could add cleanup)

## Wichtige Features

### 1. Automatic Processing Pipeline

**PDF Upload Flow:**
```
1. Upload PDF file
2. Save temporarily to UPLOAD_DIR
3. Extract text with PyPDF2
4. Create Document in DB
5. Generate embeddings (Ollama nomic-embed-text)
6. Add chunks to vector store (500 chars)
7. Update vector_collection_id
8. Delete temp file
9. Return Document
```

**URL Scraping Flow:**
```
1. Scrape URL with BeautifulSoup
2. Extract title, description, content (max 10000 chars)
3. Create Document in DB
4. Generate embeddings
5. Add chunks to vector store
6. Return Document with metadata
```

### 2. User Isolation

Alle Operationen sind user-scoped:
```python
# User kann nur eigene Projekte sehen
select(Project).where(Project.user_id == user.id)

# User kann nur eigene Dokumente sehen
select(Document).where(Document.user_id == user.id)

# Vector collections sind per-user
user_{user_id}_project_{project_id}
```

### 3. Cascade Deletion

```
DELETE Project
  ↓
  Deletes Documents (CASCADE)
  ↓
  Deletes Chats (CASCADE)
  ↓
  Deletes Matches (CASCADE)
  ↓
  Deletes Vector Collection
```

### 4. Vector Store Integration

Bei jedem Document-Upload:
```python
# 1. Document in DB erstellen
document = Document(user_id=..., content=...)

# 2. Zu Vector Store hinzufügen
chunks_added = vector_store.add_documents(
    user_id=user.id,
    project_id=document.project_id,
    documents=[{
        "id": str(document.id),
        "content": document.content,
        "metadata": {...}
    }]
)

# 3. Collection ID speichern
document.vector_collection_id = "user_xxx_project_yyy"
```

### 5. File Upload Handling

```python
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    ...
):
    # Validate file type (.pdf, .docx)
    # Save to temp directory
    # Extract text
    # Create document + embeddings
    # Cleanup temp file
```

## Dateigrößen & Limits

- **MAX_UPLOAD_SIZE**: 10 MB (konfigurierbar in .env)
- **URL Content Limit**: 10,000 chars
- **Chunk Size**: 500 chars (vector store)
- **Overlap**: 50 chars (für bessere Retrieval)

## Error Handling

- ✅ 400 Bad Request - Invalid file type
- ✅ 403 Forbidden - Access denied (not owner)
- ✅ 404 Not Found - Project/Document not found
- ✅ 500 Internal Server Error - Processing failed
- ✅ Graceful degradation wenn ChromaDB nicht installiert

## Database Schema (vollständig)

### Projects Table ✅
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR (cv_matcher, private_gpt, tell_me_life, other),
    name VARCHAR(255),
    description TEXT,
    config JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Documents Table ✅
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR (pdf, docx, url, text),
    filename VARCHAR(255),
    url TEXT,
    content TEXT,
    metadata JSONB,
    vector_collection_id VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Testing

**1. Create Project:**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "type": "cv_matcher",
    "description": "Testing"
  }'
```

**2. Upload PDF:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@resume.pdf" \
  -F "project_id=$PROJECT_ID"
```

**3. Scrape URL:**
```bash
curl -X POST http://localhost:8000/documents/url \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.dabrock.info",
    "project_id": "'$PROJECT_ID'"
  }'
```

**4. Add Text:**
```bash
curl -X POST http://localhost:8000/documents/text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "My text document",
    "title": "Notes",
    "project_id": "'$PROJECT_ID'"
  }'
```

**5. List Documents:**
```bash
curl http://localhost:8000/documents?project_id=$PROJECT_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Nächste Schritte (Phase 4+)

### Phase 4: CV Matcher Integration
- Port CV Matcher Service (`backend/services/cv_matcher.py`)
- CV Matcher API Endpoints
- Match CRUD operations
- PDF Report Generation

### Phase 5: Chat Integration (PrivateGPT)
- Chat Service mit RAG
- Chat API Endpoints
- Vector store context retrieval
- Streaming responses (optional)

### Phase 6: Admin Frontend
- React Admin Panel
- User Management UI
- LLM Configuration UI
- System Statistics Dashboard

## Zusammenfassung

✅ **Projects API** - Full CRUD mit User-Isolation
✅ **Documents API** - Upload, URL, Text mit Auto-Processing
✅ **Vector Store** - Automatic embeddings bei jedem Upload
✅ **File Upload** - PDF & DOCX support mit temp file handling
✅ **URL Scraping** - BeautifulSoup mit 10k char limit
✅ **Cascade Deletion** - Project → Documents → Vector Collection
✅ **User Isolation** - Alle Operations user-scoped
✅ **Error Handling** - 400/403/404/500 mit clear messages

**Phase 3 vollständig abgeschlossen!** 🎉

**API Status:**
- Authentication: ✅
- User Management: ✅
- Admin: ✅
- LLM Gateway: ✅
- Projects: ✅
- Documents: ✅
- CV Matcher: ⏭️ (Phase 4)
- Chat/RAG: ⏭️ (Phase 5)
