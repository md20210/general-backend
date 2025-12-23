# General Backend - Zentrale Backend-Architektur

## 🎯 Vision

Ein zentrales Backend auf Railway, das alle Showcases (CV Matcher, PrivateGPT, TellMeLife) unterstützt mit:
- Benutzerverwaltung (Admin + Users)
- Multi-LLM Support (Ollama, GROK, Anthropic)
- Vector Store (ChromaDB + pgvector)
- PostgreSQL Database
- Admin Panel auf www.dabrock.info

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    www.dabrock.info                         │
│              (Strato - Static Homepage)                     │
│         ┌──────────────────────────────────────┐           │
│         │  Landing Page + Admin Button         │           │
│         └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CENTRAL BACKEND (Railway)                      │
│                  api.dabrock.info                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ FastAPI Core Services                               │    │
│  │  • Auth & User Management (JWT)                     │    │
│  │  • Admin Panel API                                  │    │
│  │  • LLM Gateway (Ollama, GROK, Anthropic)           │    │
│  │  • Document Processing                              │    │
│  │  • Vector Store (ChromaDB + pgvector)              │    │
│  │  • PostgreSQL Database                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Database Layer:                                            │
│  • PostgreSQL (Users, Projects, Documents, Chats)          │
│  • ChromaDB (Vector embeddings)                            │
│  • Redis (Session/Cache - optional)                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  CV Matcher  │   │  PrivateGPT  │   │ TellMeLife   │
│   (Railway)  │   │   (Railway)  │   │  (Railway)   │
│   Frontend   │   │   Frontend   │   │   Frontend   │
└──────────────┘   └──────────────┘   └──────────────┘
```

## 📚 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **fastapi-users** - Authentication system
- **JWT** - Token-based auth
- **ChromaDB** - Vector database
- **pgvector** - PostgreSQL extension for vectors
- **Pydantic** - Data validation
- **Python 3.11+**

### LLMs
- **Ollama** (Railway Volume) - qwen2.5:3b, llama3.2:3b, qwen3-coder:30b
- **GROK API** - xAI's model
- **Anthropic API** - Claude models
- **Extensible** - Easy to add more

### Frontend (Admin Panel)
- **React 19**
- **Vite**
- **Axios**
- **React Router**
- **TailwindCSS** or existing CSS

### Deployment
- **Railway** - Backend + Database
- **Docker** - Containerization
- **Strato** - Static homepage

## 📁 Projektstruktur

```
GeneralBackend/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI App Entry
│   ├── config.py              # Settings (DATABASE_URL, etc.)
│   ├── database.py            # SQLAlchemy setup
│   │
│   ├── models/                # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   ├── document.py       # Document model
│   │   ├── project.py        # Project model (Showcase instances)
│   │   └── chat.py           # Chat history model
│   │
│   ├── schemas/               # Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── project.py
│   │   └── chat.py
│   │
│   ├── auth/                  # Authentication
│   │   ├── __init__.py
│   │   ├── users.py          # fastapi-users setup
│   │   ├── jwt.py            # JWT configuration
│   │   └── dependencies.py   # Auth dependencies
│   │
│   ├── services/              # Business Logic
│   │   ├── __init__.py
│   │   ├── llm_gateway.py    # LLM abstraction layer
│   │   ├── vector_store.py   # ChromaDB + pgvector
│   │   ├── document_processor.py # PDF/DOCX/URL processing
│   │   └── admin.py          # Admin-specific logic
│   │
│   ├── api/                   # API Routes
│   │   ├── __init__.py
│   │   ├── auth.py           # Auth endpoints
│   │   ├── admin.py          # Admin endpoints (/admin/*)
│   │   ├── cv_matcher.py     # CV Matcher endpoints
│   │   ├── chat.py           # Chat endpoints (PrivateGPT)
│   │   ├── documents.py      # Document management
│   │   └── projects.py       # Project management
│   │
│   └── alembic/              # Database Migrations
│       ├── env.py
│       └── versions/
│
├── admin-frontend/            # React Admin Panel
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UserManagement.jsx
│   │   │   ├── LLMConfig.jsx
│   │   │   ├── SystemStats.jsx
│   │   │   └── Login.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/                      # Local development data
│   ├── chroma_db/
│   └── uploads/
│
├── tests/                     # Tests
│   ├── test_auth.py
│   ├── test_llm_gateway.py
│   └── test_api.py
│
├── .env.example              # Environment variables template
├── .gitignore
├── docker-compose.yml        # Local development
├── Dockerfile                # Railway deployment
├── railway.json              # Railway configuration
├── requirements.txt          # Python dependencies
├── alembic.ini              # Alembic config
├── README.md
└── ARCHITECTURE.md          # This file
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- 'cv_matcher', 'private_gpt', 'tell_me_life'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    config JSONB,  -- Showcase-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- 'pdf', 'docx', 'url', 'text'
    filename VARCHAR(255),
    url TEXT,
    content TEXT,
    metadata JSONB,
    vector_collection_id VARCHAR(255),  -- ChromaDB collection reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chats Table
```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Matches Table (CV Matcher specific)
```sql
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    employer_doc_ids UUID[],
    applicant_doc_ids UUID[],
    llm_type VARCHAR(50),
    match_score FLOAT,
    comparison JSONB,
    strengths JSONB,
    gaps JSONB,
    summary TEXT,
    recommendations JSONB,
    risk_assessment TEXT,
    development_potential TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 Authentication Flow

1. **Registration**: `POST /auth/register` → User created (is_active=False)
2. **Email Verification** (optional): `GET /auth/verify?token=...`
3. **Login**: `POST /auth/login` → Returns JWT access token
4. **Protected Routes**: Header: `Authorization: Bearer <token>`
5. **Admin Routes**: Additional check for `is_admin=True`

## 🚀 API Endpoints

### Auth
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout (invalidate token)
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

### Admin (Admin only)
- `GET /admin/users` - List all users
- `POST /admin/users` - Create user
- `GET /admin/users/{id}` - Get user details
- `PUT /admin/users/{id}` - Update user
- `DELETE /admin/users/{id}` - Delete user
- `GET /admin/stats` - System statistics
- `GET /admin/llm-config` - Get LLM configuration
- `PUT /admin/llm-config` - Update LLM configuration

### Projects
- `GET /projects` - List user's projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Documents
- `GET /documents` - List user's documents
- `POST /documents/upload` - Upload file
- `POST /documents/url` - Add URL
- `POST /documents/text` - Add text
- `GET /documents/{id}` - Get document
- `DELETE /documents/{id}` - Delete document

### CV Matcher
- `POST /cv-matcher/match` - Create new match
- `GET /cv-matcher/matches` - List matches
- `GET /cv-matcher/matches/{id}` - Get match details
- `DELETE /cv-matcher/matches/{id}` - Delete match
- `GET /cv-matcher/matches/{id}/report` - Download PDF report

### Chat (PrivateGPT)
- `POST /chat/{project_id}` - Send message
- `GET /chat/{project_id}` - Get chat history
- `DELETE /chat/{project_id}` - Clear chat history

### LLM
- `POST /llm/generate` - Generate response (generic)
- `GET /llm/models` - List available models
- `POST /llm/embed` - Generate embeddings

## 🔧 Configuration (Environment Variables)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/generalbackend

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM APIs
OLLAMA_BASE_URL=http://localhost:11434
GROK_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Railway
PORT=8000

# Admin
ADMIN_EMAIL=admin@dabrock.info
ADMIN_PASSWORD=change-me-in-production

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,https://www.dabrock.info
```

## 📦 Dependencies (requirements.txt)

```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Authentication
fastapi-users[sqlalchemy]==12.1.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic[email]==2.5.3

# LLM & Vector Store
openai>=1.0.0
requests>=2.31.0
chromadb>=0.4.22
sentence-transformers>=2.2.2
pgvector==0.2.4

# Document Processing
PyPDF2==3.0.1
python-docx==1.1.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# PDF Generation
reportlab>=4.0.0

# Utilities
python-dotenv==1.0.0
pydantic-settings==2.1.0

# Testing
pytest==7.4.3
httpx==0.26.0
```

## 🎯 Implementation Roadmap

### Phase 1: Core Backend Setup (Week 1)
- [ ] Initialize FastAPI project structure
- [ ] Setup PostgreSQL with SQLAlchemy
- [ ] Implement User model and migrations
- [ ] Setup fastapi-users authentication
- [ ] Create JWT token system
- [ ] Implement basic auth endpoints
- [ ] Add admin middleware/dependencies

**Aider Prompts:**
```
1. "Create a FastAPI project with PostgreSQL, SQLAlchemy, and fastapi-users.
   Schema: Users table with email, hashed_password, is_admin, is_active fields."

2. "Add JWT authentication with /auth/login, /auth/register, /auth/me endpoints.
   Use python-jose for JWT tokens."

3. "Create admin-only endpoints for user management:
   GET/POST/PUT/DELETE /admin/users with proper authorization checks."
```

### Phase 2: Database Models & Services (Week 1-2)
- [ ] Create Projects model
- [ ] Create Documents model
- [ ] Create Chats model
- [ ] Create Matches model
- [ ] Implement database migrations
- [ ] Add CRUD operations for each model

**Aider Prompts:**
```
4. "Create Projects, Documents, Chats, and Matches SQLAlchemy models
   with proper relationships and foreign keys."

5. "Implement CRUD services for all models with user isolation
   (users can only access their own data)."
```

### Phase 3: LLM Gateway (Week 2)
- [ ] Create LLM Gateway abstraction
- [ ] Implement Ollama client
- [ ] Implement GROK API client
- [ ] Implement Anthropic API client
- [ ] Add model selection logic
- [ ] Add error handling and retries

**Aider Prompts:**
```
6. "Create an LLM Gateway service that supports Ollama (Railway Volume),
   GROK, and Anthropic APIs. Make it easily extensible for new providers."

7. "Add endpoints /llm/generate and /llm/models with provider selection."
```

### Phase 4: Vector Store Integration (Week 2)
- [ ] Setup ChromaDB
- [ ] Add pgvector to PostgreSQL
- [ ] Implement vector store service
- [ ] Add embedding generation
- [ ] Implement semantic search
- [ ] Add per-user collection isolation

**Aider Prompts:**
```
8. "Integrate ChromaDB with per-user collections.
   Copy logic from /mnt/e/CodeLocalLLM/cvmatcher/backend/vector_store.py"

9. "Add pgvector to PostgreSQL and implement hybrid search
   (vector + keyword)."
```

### Phase 5: Document Processing (Week 3)
- [ ] Implement PDF extraction
- [ ] Implement DOCX extraction
- [ ] Implement URL scraping
- [ ] Add file upload handling
- [ ] Implement document chunking
- [ ] Add vector embeddings on upload

**Aider Prompts:**
```
10. "Add document processing service for PDF, DOCX, and URL extraction.
    Copy from /mnt/e/CodeLocalLLM/cvmatcher/backend/document_processor.py"

11. "Implement automatic vector embedding when documents are uploaded."
```

### Phase 6: CV Matcher Integration (Week 3)
- [ ] Port CV Matcher endpoints
- [ ] Migrate matching logic
- [ ] Update to use PostgreSQL instead of JSON
- [ ] Add user isolation
- [ ] Test with existing CV Matcher frontend

**Aider Prompts:**
```
12. "Create CV Matcher endpoints under /cv-matcher/*
    that use the centralized database and LLM gateway."

13. "Port the matching logic from
    /mnt/e/CodeLocalLLM/cvmatcher/backend/matcher.py"
```

### Phase 7: Admin Panel Frontend (Week 4)
- [ ] Initialize React app
- [ ] Create login page
- [ ] Create user management UI
- [ ] Create LLM configuration UI
- [ ] Add system statistics dashboard
- [ ] Implement API integration
- [ ] Deploy to www.dabrock.info/admin

**Aider Prompts:**
```
14. "Create a React admin dashboard with:
    - User Management (list, create, edit, delete)
    - LLM Configuration
    - System Statistics
    Use existing CSS from CV Matcher"

15. "Add authentication flow with JWT tokens and protected routes."
```

### Phase 8: Railway Deployment (Week 4)
- [ ] Create Dockerfile
- [ ] Setup docker-compose for local dev
- [ ] Configure railway.json
- [ ] Setup PostgreSQL on Railway
- [ ] Deploy backend service
- [ ] Setup Ollama on Railway Volume
- [ ] Configure environment variables
- [ ] Test deployment

### Phase 9: PrivateGPT Integration (Week 5)
- [ ] Port PrivateGPT chat logic
- [ ] Implement RAG with vector store
- [ ] Create chat endpoints
- [ ] Test with existing PrivateGPT frontend

### Phase 10: TellMeLife Integration (Week 5-6)
- [ ] Design TellMeLife schema
- [ ] Implement story/memory storage
- [ ] Add AI conversation logic
- [ ] Create API endpoints

## 🚂 Railway Configuration

**railway.json:**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

## 🧪 Testing Strategy

1. **Unit Tests** - Test individual services
2. **Integration Tests** - Test API endpoints
3. **Auth Tests** - Test authentication flow
4. **Database Tests** - Test CRUD operations
5. **LLM Tests** - Mock LLM responses

## 📊 Migration from CV Matcher

### Files to Reuse
✅ `document_processor.py` - Copy as-is
✅ `vector_store.py` - Adapt for multi-user
✅ `pdf_generator.py` - Copy as-is
✅ `llm_client.py` - Integrate into LLM Gateway
✅ `matcher.py` - Port to new service

### Files to Replace
❌ JSON file storage → PostgreSQL
❌ No auth → fastapi-users
❌ Single user → Multi-user

## 🎯 Success Criteria

- [ ] Users can register and login
- [ ] Admins can manage users
- [ ] CV Matcher works with new backend
- [ ] PrivateGPT works with new backend
- [ ] All data is isolated per user
- [ ] Vector search works
- [ ] Multiple LLMs supported
- [ ] Deployed on Railway
- [ ] Admin panel accessible at www.dabrock.info

## 📝 Next Steps

1. Review this architecture
2. Confirm approach
3. Start Phase 1 with Aider
4. Iterate and deploy

---

**Created:** 2025-12-21
**Last Updated:** 2025-12-21
**Status:** ✅ DEPLOYED & RUNNING

## 🎉 Deployment Status (2025-12-21 22:50 CET)

### ✅ Production Architecture - FULLY OPERATIONAL

```
┌─────────────────────────────────────────────────────────────┐
│                    www.dabrock.info                         │
│                  (Strato - SSL pending)                     │
│         ┌──────────────────────────────────────┐           │
│         │  Admin Panel: /admin/                 │           │
│         │  (React + Vite)                       │           │
│         └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTPS
┌─────────────────────────────────────────────────────────────┐
│              GENERAL BACKEND (Railway)                      │
│   https://general-backend-production-a734.up.railway.app   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ FastAPI Backend (general-backend)                  │    │
│  │  ✅ FastAPI + async SQLAlchemy                      │    │
│  │  ✅ fastapi-users Authentication                    │    │
│  │  ✅ JWT Tokens                                      │    │
│  │  ✅ Admin API                                       │    │
│  │  ✅ Document Management                             │    │
│  │  ✅ Project Management                              │    │
│  │  ✅ LLM Gateway (Multi-provider)                    │    │
│  │  ✅ Vector Search with pgvector                     │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                │
│              ┌─────────────┼─────────────┐                 │
│              ▼             ▼             ▼                  │
│  ┌─────────────────┐  ┌──────────┐  ┌──────────────┐      │
│  │ pgVector-Railway│  │  Ollama  │  │  Cloud APIs  │      │
│  │   PostgreSQL    │  │  Service │  │              │      │
│  │  + pgvector     │  │ (GDPR!)  │  │ • Anthropic  │      │
│  │                 │  │          │  │ • Grok       │      │
│  │ ✅ Users         │  │ ✅ llama  │  │              │      │
│  │ ✅ Projects      │  │  3.2:3b  │  │ (Optional)   │      │
│  │ ✅ Documents     │  │          │  │              │      │
│  │ ✅ Chats         │  │ CPU-opt  │  └──────────────┘      │
│  │ ✅ Matches       │  │ GDPR ✅  │                         │
│  │ ✅ Embeddings    │  │          │                         │
│  └─────────────────┘  └──────────┘                         │
│      (Private Network)                                     │
└─────────────────────────────────────────────────────────────┘
```

### 🚀 Live Services

**Railway Project:** Generalbackend

1. **general-backend** ✅ RUNNING
   - URL: `https://general-backend-production-a734.up.railway.app`
   - Health: `https://general-backend-production-a734.up.railway.app/health`
   - API Docs: `https://general-backend-production-a734.up.railway.app/docs`
   - FastAPI + async SQLAlchemy + pgvector
   - Auto-deploy from GitHub (SSH)

2. **pgVector-Railway** ✅ RUNNING
   - PostgreSQL 16 + pgvector extension
   - All tables created
   - Vector embeddings enabled
   - Private network: `postgres.railway.internal`

3. **ollama** ✅ RUNNING
   - Ollama server with qwen3-coder:30b
   - Model: 18.5GB, 30B parameters
   - GDPR-compliant (data stays in Railway EU)
   - Private network: `ollama.railway.internal:11434`
   - ⚠️ **NOTE**: CPU inference is slow (~2min timeout)
   - Recommendation: Use Claude/Grok for production until GPU available
   - Upgrade path: GPU support coming Q1 2026

4. **Admin Frontend** ✅ DEPLOYED
   - URL: `https://www.dabrock.info/admin/` (SSL pending)
   - React 19 + Vite
   - Hosted on Strato
   - Connected to Railway backend

### 🔧 Key Configuration Changes

**Vector Database Migration:**
- ❌ ChromaDB removed (NumPy 2.0 conflicts)
- ✅ pgvector implemented (PostgreSQL native)
- ✅ sentence-transformers for embeddings
- ✅ Cosine similarity search
- Model: `all-MiniLM-L6-v2` (384 dimensions)

**Database Schema Updates:**
- `documents.metadata` → `documents.doc_metadata` (SQLAlchemy reserved keyword)
- `chats.metadata` → `chats.chat_metadata` (SQLAlchemy reserved keyword)
- `documents.embedding` added: `Vector(384)` for pgvector
- `documents.vector_collection_id` removed (not needed with pgvector)

**LLM Architecture:**
- ✅ Ollama: Local, GDPR-compliant, free
- ✅ Anthropic: Premium quality (API key configured)
- ✅ Grok: Fast & cheap (API key configured)
- Provider selection via API parameter

---

## 📖 API Documentation

**Complete API Documentation:** See `API_DOCUMENTATION.md` for full endpoint reference with request/response examples.

**Interactive API Docs:**
- Swagger UI: https://general-backend-production-a734.up.railway.app/docs
- ReDoc: https://general-backend-production-a734.up.railway.app/redoc

### Quick API Reference

**Authentication (`/auth`):**
- `POST /auth/register` - Create new user
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/verify` - Verify email

**LLM (`/llm`):**
- `GET /llm/models` - List available models (Ollama, Claude, Grok)
- `POST /llm/generate` - Generate text with LLM
- `POST /llm/embed` - Generate embeddings

**Projects (`/projects`):**
- `POST /projects` - Create project
- `GET /projects` - List projects
- `GET /projects/{id}` - Get project
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Documents (`/documents`):**
- `POST /documents/upload` - Upload PDF/DOCX
- `POST /documents/url` - Scrape URL
- `POST /documents/text` - Add text
- `GET /documents` - List documents
- `GET /documents/search?query=...` - Semantic search (pgvector)
- `DELETE /documents/{id}` - Delete document

**Admin (`/admin`):**
- `GET /admin/stats` - System statistics (admin only)

All endpoints (except register/login) require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

**Deployment Improvements:**
- ✅ SSH Keys for GitHub (no token re-entry)
- ✅ Retry logic for database connection (30 attempts)
- ✅ pgvector extension auto-enabled on startup
- ✅ No Alembic migrations (tables auto-created via SQLAlchemy)
