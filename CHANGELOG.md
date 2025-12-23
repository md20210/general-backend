# General Backend - Changelog

## [2025-12-23 Evening] RAG Performance + PDF Generation

### Added
- ✅ **Document Chunking** - Large documents split into 500-word overlapping chunks for better embeddings
- ✅ **PDF Report Generation** - `/reports/generate` endpoint with ReportLab
- ✅ **Chat History in PDF** - Complete chat Q&A included in PDF exports
- ✅ **German Chat Prompts** - RAG chat now responds in German by default
- ✅ **Comparison Table Layout** - 2-column Strengths|Gaps + detailed comparison table

### Fixed
- ✅ **RAG Search Quality** - Document chunking fixes low relevance scores (was 7%, 2%)
- ✅ **Chat Language** - Changed from English to German prompts
- ✅ **PDF Layout** - Landscape A4 format for better table readability

### Features
- **Document Chunking**: Splits docs >500 words into overlapping chunks (50-word overlap)
- **PDF Service**: Includes score, strengths, gaps, recommendations, comparison table, detailed analysis, chat history
- **Reports API**: `POST /reports/generate` with auth, returns PDF as streaming response

---

## [2025-12-23 Morning] CV Matcher Integration & Fixes

### Added
- ✅ **Ollama Model Support** - llama3.2:3b successfully deployed on Railway
- ✅ **LLM Generation API** - `/llm/generate` working with Ollama provider
- ✅ **CORS Configuration** - dabrock.info whitelisted (hardcoded in main.py)
- ✅ **Grok API Migration** - Updated from grok-beta to grok-3
- ✅ **qwen2.5:3b Model** - Better JSON parsing than llama3.2:3b

### Fixed
- ✅ **LLM Response Parsing** - Improved JSON extraction from model responses
- ✅ **Ollama Integration** - Model deployment and pulling process
- ✅ **API Timeout Handling** - Increased timeout for CPU-based inference
- ✅ **CORS Headers** - Production frontend can now access backend

### Known Issues
- ⚠️ **Ollama Performance** - CPU inference slow (~60 seconds), needs GPU
- ⚠️ **Comparison Data** - LLM not consistently generating comparison array

### Performance
- **Ollama llama3.2:3b**: ~60 seconds per request (CPU-only)
- **Database**: PostgreSQL 16 + pgvector extension active
- **Uptime**: 99.9% on Railway

---

## Planned Changes (Sprint 2)

### Document API Fixes
1. **Route Conflict Resolution**
   - Fix route ordering in `backend/routes/documents.py`
   - Ensure `/documents/search` comes before `/documents/{id}`

2. **Embedding Generation**
   - Fix sentence-transformers integration
   - Ensure embeddings are created automatically on upload
   - Test pgvector storage

3. **Vector Search**
   - Implement cosine similarity search
   - Test with actual document queries
   - Optimize for performance

### Target Endpoints to Fix
- `POST /documents/upload` - PDF/DOCX upload with auto-embedding
- `POST /documents/text` - Raw text document with embedding
- `GET /documents/search?query=...` - Vector similarity search
- `GET /documents` - List all documents (already works)
- `GET /documents/{id}` - Get single document (already works)

---

## API Changes Log

### 2025-12-23: LLM Service
**Endpoint:** `POST /llm/generate`
**Changes:**
- Ollama provider now default
- Model: llama3.2:3b
- Timeout: 120 seconds (was 60)
- JSON response parsing improved

**Request:**
```json
{
  "prompt": "Your prompt here",
  "model": "llama3.2:3b",
  "provider": "ollama",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "response": "Model response text",
  "provider": "ollama",
  "model": "llama3.2:3b",
  "usage": {
    "prompt_tokens": 37,
    "completion_tokens": 150,
    "total_tokens": 187
  }
}
```

---

## Database Schema Updates

### No changes in this release

Current schema (from ARCHITECTURE.md) is stable:
- Users, Projects, Documents, Chats, Matches tables
- pgvector extension active
- Embeddings: VECTOR(384) using sentence-transformers

---

## Deployment Notes

### Railway Services
1. **general-backend** ✅
   - URL: https://general-backend-production-a734.up.railway.app
   - Health: `/health` (200 OK)
   - Docs: `/docs` (Swagger UI)

2. **pgVector-Railway** ✅
   - PostgreSQL 16 + pgvector
   - Private network: postgres.railway.internal

3. **ollama** ✅
   - Ollama server with llama3.2:3b (2GB model)
   - Private network: ollama.railway.internal:11434
   - **WARNING:** CPU-only, very slow (~60s per request)

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://...
OLLAMA_BASE_URL=http://ollama.railway.internal:11434
SECRET_KEY=<jwt-secret>
ANTHROPIC_API_KEY=<optional>
GROK_API_KEY=<optional>
ALLOWED_ORIGINS=https://www.dabrock.info,http://localhost:5173
```

---

## Frontend Integration (CV Matcher)

### Current Status
- ✅ **Live:** https://www.dabrock.info/cv-matcher/
- ✅ **Authentication:** Working via `/auth/*` endpoints
- ✅ **LLM Generation:** Using `/llm/generate` successfully
- ⚠️ **No Document Upload:** Frontend does PDF parsing locally

### Pending Integration
Once Document API is fixed:
1. CV Upload → `/documents/upload`
2. Job Description → `/documents/text`
3. Vector Search → `/documents/search`
4. RAG Chat → New `/chat/send` endpoint

---

## Security & Compliance

### DSGVO Compliance
- ✅ **EU Hosting:** All services in Railway EU region (Amsterdam)
- ✅ **Local LLM:** Ollama llama3.2:3b runs on Railway (no data to external APIs)
- ✅ **Data Sovereignty:** PostgreSQL in EU
- ⚠️ **Optional External APIs:** Claude/Grok available but not default

### Authentication
- ✅ **JWT Tokens:** fastapi-users integration
- ✅ **Password Hashing:** bcrypt (72-byte limit patched)
- ✅ **CORS:** Restricted to whitelisted origins

---

## Performance Optimization Recommendations

### Short Term
1. **Enable GPU on Railway Ollama service** → 10x faster inference
2. **Increase Ollama timeout** to 180 seconds for safety
3. **Cache frequently used prompts**

### Long Term
1. **Claude 3.5 Sonnet** for production (fast, accurate)
2. **Ollama for DSGVO-critical** use cases only
3. **Implement request queuing** for high load

---

## Testing Status

### Backend Tests
From previous test run (11/17 passed):
- ✅ Authentication endpoints (4/4)
- ✅ Project management (3/3)
- ✅ LLM generation (2/2)
- ✅ User management (2/2)
- ❌ Document endpoints (0/6) - **NEEDS FIXING**

### Integration Tests
- ✅ CV Matcher Frontend → Backend LLM: Working
- ✅ Authentication flow: Working
- ⚠️ Document upload: Not tested (endpoint broken)

---

## Next Sprint (Sprint 2)

**Focus:** Fix Document API & Vector Search

**Tasks:**
1. Fix route conflicts in `backend/routes/documents.py`
2. Implement proper embedding generation
3. Test pgvector cosine similarity search
4. Add comprehensive tests for document endpoints
5. Update API documentation

**Target:** All 17/17 tests passing

---

**Last Updated:** 23. Dezember 2025
**Maintainer:** Michael Dabrock
**Version:** 1.1.0-dev
