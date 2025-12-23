# System Overview - Quick Onboarding After Crash

> **Purpose:** This document helps you (Claude Code) quickly understand the entire system architecture, key decisions, and how everything fits together after a system crash or context loss.

**Last Updated:** 2025-12-23  
**System Status:** Production (Railway + Strato)

---

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Key Components](#key-components)
3. [Critical Paths & Files](#critical-paths--files)
4. [Important Decisions & Rationale](#important-decisions--rationale)
5. [Common Operations](#common-operations)
6. [Known Issues & Workarounds](#known-issues--workarounds)
7. [Deployment Process](#deployment-process)
8. [Testing & Debugging](#testing--debugging)

---

## Project Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CV MATCHER SYSTEM                         │
│                   AI-Powered Resume Analysis                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   FRONTEND (React)   │────────▶│  BACKEND (FastAPI)   │
│   Strato SFTP Host   │  HTTP   │   Railway (Cloud)    │
│  dabrock.info/cv-    │         │  Auto-deploy from    │
│      matcher/        │         │      GitHub          │
└──────────────────────┘         └──────────────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────┐
                        │  EXTERNAL SERVICES           │
                        ├──────────────────────────────┤
                        │ • Local Llama (GDPR)         │
                        │ • Grok API (Fast)            │
                        │ • PostgreSQL (Railway)       │
                        │ • sentence-transformers      │
                        └──────────────────────────────┘
```

### Repository Structure

**Two Main Directories:**

1. **`/mnt/e/CodelocalLLM/GeneralBackend`** (Backend)
   - FastAPI application
   - Git: `github.com:md20210/general-backend.git`
   - Deploy: Railway auto-deploy on push
   - Live: `https://general-backend-production-a734.up.railway.app`

2. **`/mnt/e/CodelocalLLM/CV_Matcher`** (Frontend)
   - React + TypeScript + Vite
   - **No Git remote configured** (local only)
   - Deploy: Manual SFTP to Strato
   - Live: `https://www.dabrock.info/cv-matcher/`

---

## Key Components

### Backend Components (GeneralBackend/)

```
backend/
├── api/
│   ├── chat.py              # RAG chat endpoint (2 modes)
│   ├── translations.py      # i18n API (DE/EN/ES)
│   ├── llm.py               # LLM analysis endpoints
│   └── documents.py         # Document CRUD (optional)
├── services/
│   ├── translation_service.py   # ~70 UI translations
│   ├── vector_service.py        # RAG with embeddings
│   ├── llm_gateway.py           # Llama/Grok provider
│   └── rag_service.py           # (deprecated - use vector_service)
├── models/
│   └── user.py                  # SQLAlchemy User model
├── schemas/
│   └── chat.py                  # Pydantic schemas (InMemoryDocument!)
└── main.py                      # FastAPI app entry point

docs/
├── TRANSLATION_SERVICE.md       # i18n API docs
└── RAG_CHAT_SERVICE.md          # RAG implementation docs
```

### Frontend Components (CV_Matcher/)

```
src/
├── components/
│   ├── Chat.tsx              # RAG chat UI with source attribution
│   ├── MatchingView.tsx      # Match results + chat integration
│   ├── DocumentSection.tsx   # Upload UI (PDF/TXT/DOCX/URL)
│   └── LanguageToggle.tsx    # DE/EN/ES switcher
├── contexts/
│   └── LanguageContext.tsx   # Global i18n state
├── services/
│   ├── api.ts                # Axios instance with auth
│   ├── chat.ts               # Chat API wrapper (InMemoryDocument support)
│   ├── llm.ts                # Match analysis API
│   └── auth.ts               # Auto-login with test user
└── App.tsx                   # Main component

docs/
└── I18N_DOCUMENTATION.md     # Frontend i18n guide
```

---

## Critical Paths & Files

### When Backend Crashes

**Check these files first:**

1. **`backend/main.py`** - App initialization, router registration
2. **`backend/api/chat.py`** - Chat endpoint (most complex logic)
3. **`backend/services/vector_service.py`** - Embedding generation
4. **Railway logs** - Check deployment logs at railway.app

**Common crash causes:**
- Missing dependency: `sentence-transformers` not installed
- Database connection issues (PostgreSQL on Railway)
- FastAPI parameter errors (`Field()` vs `Path()` vs `Query()`)

### When Frontend Breaks

**Check these files first:**

1. **`src/components/MatchingView.tsx`** - Main app logic
2. **`src/services/chat.ts`** - API integration
3. **Browser console** - Network errors, CORS issues
4. **`dist/index.html`** - Verify correct asset paths after build

**Common frontend issues:**
- CORS errors → Check backend `ALLOWED_ORIGINS`
- Build errors → TypeScript type mismatches
- SFTP deployment fails → Wrong credentials or path

### Configuration Files

**Backend:**
- `.env` - Environment variables (API keys, DB URL)
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config

**Frontend:**
- `package.json` - Dependencies, scripts
- `vite.config.ts` - Build config
- `tsconfig.json` - TypeScript settings

---

## Important Decisions & Rationale

### Decision 1: Two RAG Modes (Database vs In-Memory)

**Problem:** CV Matcher doesn't persist documents, but we want RAG chat.

**Solution:** Implemented **In-Memory RAG** mode:
- Frontend sends documents with each chat request
- Backend generates embeddings on-the-fly
- No database storage (GDPR-compliant)
- Documents discarded after response

**Rationale:**
- ✅ GDPR compliance (no data persistence)
- ✅ No separate upload step
- ✅ Works without database setup
- ⚠️ Higher payload size (~200KB per request)

**When to use:**
- **Database RAG:** Long-term document storage, multi-session persistence
- **In-Memory RAG:** CV Matcher, privacy-sensitive apps, single-session workflows

**Implementation:**
- `backend/schemas/chat.py`: `InMemoryDocument` class
- `backend/services/vector_service.py`: `search_in_memory_documents()`
- `backend/api/chat.py`: Mode selection based on `request.documents`

### Decision 2: Backend Translation Service

**Problem:** Multi-language support (DE/EN/ES) needed across entire app.

**Solution:** Centralized backend translation API:
- ~70 UI translations in `backend/services/translation_service.py`
- REST endpoint: `GET /translations/{language}`
- Frontend caches in React Context

**Rationale:**
- ✅ Single source of truth
- ✅ Easy to add languages
- ✅ Variable interpolation (`{count}`, `{error}`)
- ✅ No frontend i18n library needed

**Alternatives rejected:**
- Frontend-only i18n (react-i18next) → Harder to maintain consistency
- Hardcoded strings → Not scalable

### Decision 3: Auto-Login for Showcase

**Problem:** Authentication required for backend, but this is a showcase app.

**Solution:** Auto-login on frontend mount:
```typescript
// src/App.tsx
await authService.login('test@dabrock.info', 'Test123Secure');
```

**Rationale:**
- ✅ No manual login for demo users
- ✅ Backend auth still functional
- ⚠️ Not production-ready (hardcoded credentials)

**Future:** Add proper auth UI when moving to production.

### Decision 4: Manual SFTP Deployment for Frontend

**Problem:** No CI/CD for Strato hosting.

**Solution:** Manual upload via curl/SFTP:
```bash
cd /mnt/e/CodelocalLLM/CV_Matcher/dist
curl -T "index.html" "sftp://HOST/path/" --user "USER:PASS"
```

**Rationale:**
- ✅ Simple, no extra infra needed
- ⚠️ Manual process (error-prone)
- ⚠️ SFTP credentials in commands (security risk)

**Future:** Set up GitHub Actions or Railway frontend hosting.

### Decision 5: Embedding Model (all-MiniLM-L6-v2)

**Problem:** Need semantic search for RAG.

**Solution:** Use `sentence-transformers/all-MiniLM-L6-v2`:
- 384 dimensions
- Fast on CPU (~50ms per doc)
- Good quality for English + German

**Rationale:**
- ✅ Runs on Railway free tier (no GPU needed)
- ✅ Good multilingual support
- ✅ Fast enough for in-memory RAG
- ⚠️ Not state-of-the-art (newer models exist)

**Alternatives:**
- OpenAI Embeddings → Costs money, external dependency
- SBERT multilingual → Larger, slower

---

## Common Operations

### 1. Add a New Translation Key

**Backend:**
```python
# backend/services/translation_service.py
UI_TRANSLATIONS = {
    "new_key": {
        "de": "Deutscher Text",
        "en": "English text",
        "es": "Texto español"
    }
}
```

**Frontend:**
```typescript
// Use anywhere
const { t } = useLanguage();
<button>{t('new_key')}</button>
```

**Deploy:**
```bash
cd /mnt/e/CodelocalLLM/GeneralBackend
git add backend/services/translation_service.py
git commit -m "Add new translation key"
git push  # Auto-deploys to Railway
```

### 2. Fix Backend Crash

**Step 1: Check Railway logs**
```bash
# Go to railway.app dashboard
# Or use Railway CLI: railway logs
```

**Step 2: Identify error**
- Import errors → Check `requirements.txt`
- FastAPI errors → Check parameter annotations (`Path`, `Query`, `Body`)
- Database errors → Check PostgreSQL connection

**Step 3: Fix and deploy**
```bash
cd /mnt/e/CodelocalLLM/GeneralBackend
# Fix the issue
git add .
git commit -m "Fix: [description]"
git push  # Auto-deploys
```

**Step 4: Wait 10 minutes for Railway build**

### 3. Update Frontend

**Step 1: Make changes**
```bash
cd /mnt/e/CodelocalLLM/CV_Matcher
# Edit files in src/
```

**Step 2: Test locally**
```bash
npm run dev  # Opens http://localhost:5173
```

**Step 3: Build**
```bash
npm run build  # Creates dist/
```

**Step 4: Deploy to Strato**
```bash
cd dist
# Upload via SFTP (credentials may change)
# See "Known Issues" section for current credentials
```

### 4. Test RAG Chat

**Prerequisites:**
- Backend deployed on Railway
- Frontend deployed on Strato
- Documents uploaded in CV Matcher

**Test flow:**
1. Go to `https://www.dabrock.info/cv-matcher/`
2. Upload employer doc (job requirements)
3. Upload applicant doc (CV)
4. Click "Match Starten"
5. Wait for analysis results
6. Scroll to chat section
7. Ask question: "Wie lange hat Michael bei IBM gearbeitet?"
8. **Expected:** AI answers based on CV content
9. **Sources shown:** Document filename + relevance score

**If chat fails:**
- Check browser console for errors
- Check `documents` array is passed to Chat component
- Check backend logs for embedding errors

### 5. Add New Language (e.g., French)

**Backend:**
```python
# backend/services/translation_service.py
Language = Literal["de", "en", "es", "fr"]  # Add "fr"

UI_TRANSLATIONS = {
    "app_title": {
        "de": "CV Matcher",
        "en": "CV Matcher",
        "es": "CV Matcher",
        "fr": "CV Matcher"  # Add French
    },
    # ... update all ~70 keys
}
```

**Frontend:**
```typescript
// src/components/LanguageToggle.tsx
const LANGUAGES = [
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },  // Add French
];
```

**Deploy both:**
```bash
# Backend
cd /mnt/e/CodelocalLLM/GeneralBackend
git push

# Frontend
cd /mnt/e/CodelocalLLM/CV_Matcher
npm run build
# Upload dist/ via SFTP
```

---

## Known Issues & Workarounds

### Issue 1: SFTP Credentials Change Frequently

**Symptom:** `curl: (67) Login denied` when deploying frontend

**Workaround:**
1. Check latest credentials in secure storage
2. Update command with new credentials
3. Consider switching to Railway frontend hosting

**Long-term fix:** Set up GitHub Actions with encrypted secrets

### Issue 2: Railway Free Tier Sleeping

**Symptom:** First request takes 30+ seconds

**Cause:** Railway free tier sleeps after 15 min inactivity

**Workaround:**
- Keep-alive ping (not implemented yet)
- Upgrade to paid tier
- Accept cold start delay

**Impact:** User experience, but acceptable for showcase

### Issue 3: Embedding Model Download on First Deploy

**Symptom:** Railway build fails with timeout

**Cause:** Downloading `all-MiniLM-L6-v2` model (~150MB)

**Workaround:**
- Increase Railway build timeout (if possible)
- Pre-download model in Docker image

**Status:** Works after first successful build

### Issue 4: CORS Errors in Browser Console

**Symptom:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Cause:** Frontend URL not in `ALLOWED_ORIGINS`

**Fix:**
```python
# backend/main.py (Railway environment variable)
ALLOWED_ORIGINS=https://www.dabrock.info,http://localhost:5173
```

**Redeploy backend after change.**

### Issue 5: Frontend Build Generates New Asset Names

**Symptom:** After `npm run build`, JS filename changes (e.g., `index-ABC123.js` → `index-XYZ789.js`)

**Impact:** Must update `index.html` and upload both files

**Workaround:** Upload entire `dist/` folder, not individual files

**Status:** Expected behavior (Vite content hashing)

---

## Deployment Process

### Backend Deployment (Automatic)

**Trigger:** `git push` to `github.com:md20210/general-backend.git`

**Process:**
1. GitHub webhook notifies Railway
2. Railway pulls latest code
3. Runs `pip install -r requirements.txt`
4. Starts `uvicorn backend.main:app`
5. Takes ~10 minutes total

**Monitoring:**
- Railway dashboard: `railway.app`
- Logs: Railway CLI or dashboard
- Health check: `GET https://general-backend-production-a734.up.railway.app/docs`

**Rollback:**
```bash
git revert HEAD
git push
```

### Frontend Deployment (Manual)

**Prerequisites:**
- SFTP credentials (user, pass, host)
- Built frontend in `dist/`

**Process:**
```bash
cd /mnt/e/CodelocalLLM/CV_Matcher
npm run build

cd dist
SFTP_USER="su403214"
SFTP_PASS="[ASK FOR CURRENT PASSWORD]"
SFTP_HOST="5018735097.ssh.w2.strato.hosting"

# Upload index.html
curl -T "index.html" \
  "sftp://$SFTP_HOST/dabrock-info/cv-matcher/index.html" \
  --user "$SFTP_USER:$SFTP_PASS" \
  --ftp-create-dirs -k

# Upload JS (filename changes with each build!)
curl -T "assets/index-HASH.js" \
  "sftp://$SFTP_HOST/dabrock-info/cv-matcher/assets/index-HASH.js" \
  --user "$SFTP_USER:$SFTP_PASS" \
  --ftp-create-dirs -k

# Upload CSS
curl -T "assets/index-HASH.css" \
  "sftp://$SFTP_HOST/dabrock-info/cv-matcher/assets/index-HASH.css" \
  --user "$SFTP_USER:$SFTP_PASS" \
  --ftp-create-dirs -k
```

**Verification:**
- Visit `https://www.dabrock.info/cv-matcher/`
- Check browser console for errors
- Test language toggle, document upload, match analysis

---

## Testing & Debugging

### Backend Testing

**Manual API testing:**
```bash
# Test translations endpoint
curl https://general-backend-production-a734.up.railway.app/translations/en

# Test chat (requires auth token)
curl -X POST https://general-backend-production-a734.up.railway.app/chat/message \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "documents": [...]}'
```

**Swagger UI:**
- Visit `https://general-backend-production-a734.up.railway.app/docs`
- Test all endpoints interactively

**Logs:**
```bash
# Railway dashboard → Logs tab
# Or Railway CLI: railway logs --tail
```

### Frontend Testing

**Local development:**
```bash
cd /mnt/e/CodelocalLLM/CV_Matcher
npm run dev  # Vite dev server on :5173
```

**Production testing:**
1. Open browser DevTools (F12)
2. Navigate to `https://www.dabrock.info/cv-matcher/`
3. Check Console for errors
4. Check Network tab for failed requests
5. Test user flow: Upload → Match → Chat

**Common debug points:**
- Language toggle not working? → Check `LanguageContext` in React DevTools
- Chat not answering? → Check `documents` prop in Chat component
- Upload failing? → Check CORS headers in Network tab

### Integration Testing

**Full RAG flow:**
```bash
# 1. Upload test documents
# 2. Start match analysis
# 3. Wait for results
# 4. Ask chat question referencing CV content
# 5. Verify answer includes CV details
# 6. Check sources show correct filename
```

**Expected behavior:**
- Chat answer references specific CV details (e.g., "IBM 2005-2008")
- Sources list shows `relevance_score` > 0.5
- No "No relevant documents found" errors

---

## Quick Reference

### Environment Variables (Backend)

```bash
# Railway environment
OPENAI_API_KEY=xxx           # For local Llama
OPENAI_BASE_URL=http://...   # Local Llama endpoint
XAI_API_KEY=xxx              # For Grok
DATABASE_URL=postgresql://...  # Railway PostgreSQL
ALLOWED_ORIGINS=https://www.dabrock.info,http://localhost:5173
```

### Important URLs

- **Frontend:** `https://www.dabrock.info/cv-matcher/`
- **Backend:** `https://general-backend-production-a734.up.railway.app`
- **Swagger:** `https://general-backend-production-a734.up.railway.app/docs`
- **Railway:** `railway.app` (dashboard)
- **GitHub:** `github.com:md20210/general-backend.git`

### Key Commands

```bash
# Backend
cd /mnt/e/CodelocalLLM/GeneralBackend
git status
git add .
git commit -m "..."
git push  # Auto-deploy to Railway

# Frontend
cd /mnt/e/CodelocalLLM/CV_Matcher
npm run dev      # Local dev server
npm run build    # Production build
npm run lint     # Type check

# Test backend locally
uvicorn backend.main:app --reload

# Check Railway logs
railway logs --tail
```

### Documentation Map

```
GeneralBackend/
├── SYSTEM_OVERVIEW.md        ← YOU ARE HERE
├── docs/
│   ├── TRANSLATION_SERVICE.md  # i18n API reference
│   └── RAG_CHAT_SERVICE.md     # RAG implementation guide

CV_Matcher/
├── README.md                   # Project overview
└── docs/
    └── I18N_DOCUMENTATION.md   # Frontend i18n guide
```

---

## After-Crash Checklist

When you (Claude) restart after a crash, follow this checklist:

### Step 1: Understand Context (5 min)
- [ ] Read this SYSTEM_OVERVIEW.md
- [ ] Check last user message for what we were working on
- [ ] Check Git logs: `git log --oneline -10`

### Step 2: Verify System Status (2 min)
- [ ] Check Railway: Is backend running?
- [ ] Check frontend: `https://www.dabrock.info/cv-matcher/` loads?
- [ ] Check last deployment time (Railway dashboard)

### Step 3: Identify Issue (if applicable)
- [ ] Review error messages from user
- [ ] Check Railway logs for crashes
- [ ] Check browser console for frontend errors

### Step 4: Plan Action
- [ ] Determine what needs fixing
- [ ] Check if it's backend (push to Git) or frontend (SFTP upload)
- [ ] Estimate impact (breaking vs non-breaking change)

### Step 5: Execute
- [ ] Make changes with clear commits
- [ ] Test locally if possible
- [ ] Deploy (auto for backend, manual for frontend)
- [ ] Verify fix in production

---

**Remember:** This document is your friend! Update it whenever you make important architectural decisions or discover new workarounds.

**Last Updated:** 2025-12-23 by Claude Code  
**Next Review:** When major changes are made to architecture
