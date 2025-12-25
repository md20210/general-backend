# General Backend - Changelog

## [2024-12-25] LifeChronicle: Timeline-Farben & UI-Verbesserungen

### Added
- ✅ **PDF Timeline-Farben** - Farbige PDF-Exports mit 6-Farben-Palette
- ✅ **Processing Indicator Translation** - "Wird verarbeitet..." in DE/EN/ES
- ✅ **ReportLab Color Styling** - Table-basierte farbige Timeline im PDF

### Changed
- 🎨 **PDF-Export** - Lifecycle Timeline jetzt mit visuellen Farben
  - Purple (#e9d5ff / #c084fc / #581c87)
  - Teal (#ccfbf1 / #5eead4 / #134e4a)
  - Green (#d1fae5 / #6ee7b7 / #065f46)
  - Yellow (#fef3c7 / #fcd34d / #78350f)
  - Orange (#fed7aa / #fdba74 / #7c2d12)
  - Pink (#fce7f3 / #f9a8d4 / #831843)

### Technical Details

#### 1. PDF Timeline Colors (`lifechonicle_service.py:217-313`)
```python
# Timeline color palette (same as frontend)
TIMELINE_COLORS = [
    {'bg': '#e9d5ff', 'border': '#c084fc', 'text': '#581c87'},  # Purple
    {'bg': '#ccfbf1', 'border': '#5eead4', 'text': '#134e4a'},  # Teal
    {'bg': '#d1fae5', 'border': '#6ee7b7', 'text': '#065f46'},  # Green
    {'bg': '#fef3c7', 'border': '#fcd34d', 'text': '#78350f'},  # Yellow
    {'bg': '#fed7aa', 'border': '#fdba74', 'text': '#7c2d12'},  # Orange
    {'bg': '#fce7f3', 'border': '#f9a8d4', 'text': '#831843'},  # Pink
]

# ReportLab Table Styling
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(color_set['bg'])),
    ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor(color_set['border'])),
    ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor(color_set['border'])),
    # ... weitere Styling-Optionen
]))
```

#### 2. Translation Update (`translations/lifechonicle.py`)
```python
"lifechonicle_action_processing": {
    "de": "Wird verarbeitet...",
    "en": "Processing...",
    "es": "Procesando..."
}
```

### API Endpoints (Unchanged)
```
GET    /api/lifechonicle/entries                    # Alle Timeline-Einträge
POST   /api/lifechonicle/entries                    # Neuer Eintrag
DELETE /api/lifechonicle/entries/{id}               # Eintrag löschen
POST   /api/lifechonicle/entries/{id}/process       # LLM-Textveredelung
GET    /api/lifechonicle/export/pdf                 # PDF-Export (UPDATED mit Farben)
GET    /api/translations?app=lifechonicle&lang=de   # UI-Übersetzungen (UPDATED)
```

### Performance
- **PDF-Generierung:** ~2-3 Sekunden (8 Einträge)
- **Dateigröße:** 50-200 KB (abhängig von Entry-Anzahl)
- **No Performance Degradation:** Farbiges PDF hat gleiche Geschwindigkeit wie vorher

### User Impact
- **Problem gelöst:** "Der Pdf download enthaelt keine Farben!" → Jetzt mit 6 Timeline-Farben
- **Bessere UX:** Processing-Indikator mit Übersetzung während LLM-Verarbeitung
- **Visuelles Erlebnis:** PDF-Export jetzt professionell formatiert mit Farben

### Frontend Integration (LifeChronicle)
- **Live:** https://www.dabrock.info/lifechronicle/
- **Frontend-Commit:** `6015f4a` - "COMPLETE 1:1 copy of CV_Matcher header and layout structure"
- **Backend-Commit:** "Add timeline colors to PDF export"

### Deployment
- ✅ Railway Auto-Deploy erfolgreich
- ✅ Health-Check: OK
- ✅ Keine Downtime

---

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
