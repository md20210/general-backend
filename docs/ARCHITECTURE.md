# General Backend - Central Architecture & Services

**Last Updated:** 2025-12-21
**Status:** ✅ PRODUCTION READY
**Base URL:** https://general-backend-production-a734.up.railway.app

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Services](#services)
4. [API Documentation](#api-documentation)
5. [Use Case Integration](#use-case-integration)
6. [Database Schema](#database-schema)
7. [Deployment](#deployment)
8. [Configuration](#configuration)

---

## 🎯 Overview

General Backend ist ein zentrales, produktionsreifes Backend-System das alle Showcases (CV Matcher, PrivateGPT, TellMeLife) mit folgenden Services unterstützt:

### Core Features
- ✅ **Authentication & User Management** (JWT, Email Verification)
- ✅ **Multi-LLM Support** (Ollama, Claude, Grok)
- ✅ **Document Management** (PDF, DOCX, URL, Text)
- ✅ **Vector Search** (pgvector, Semantic Search)
- ✅ **Project Management** (Showcase Instances)
- ✅ **GDPR Compliant** (EU-Hosting, Local LLM Option)

### Tech Stack
- **Backend:** FastAPI + Python 3.12
- **Database:** PostgreSQL 16 + pgvector
- **LLMs:** Ollama (local), Anthropic Claude, Grok
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, 384 dims)
- **Deployment:** Railway (EU Region)
- **Frontend:** React 19 + Vite (Admin Panel)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     www.dabrock.info                            │
│                   (Strato - Static Hosting)                     │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  CV Matcher    │  │  PrivateGPT    │  │  TellMeLife    │   │
│  │  /cv-matcher/  │  │  /privategpt/  │  │  /tellmelife/  │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│           │                   │                   │             │
│           └───────────────────┼───────────────────┘             │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                    HTTPS (JWT Authentication)
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              GENERAL BACKEND (Railway Production)               │
│   https://general-backend-production-a734.up.railway.app       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ FastAPI Application (general-backend service)          │    │
│  │  • Authentication (/auth, /users)                      │    │
│  │  • LLM Gateway (/llm)                                  │    │
│  │  • Projects (/projects)                                │    │
│  │  • Documents (/documents)                              │    │
│  │  • Admin (/admin)                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         ▼                ▼                ▼                     │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────┐           │
│  │ PostgreSQL   │  │  Ollama  │  │  Cloud APIs    │           │
│  │ + pgvector   │  │  Service │  │                │           │
│  │              │  │          │  │  • Claude      │           │
│  │ Tables:      │  │ Models:  │  │  • Grok        │           │
│  │  • users     │  │  qwen3   │  │                │           │
│  │  • projects  │  │  -coder  │  │  (Optional)    │           │
│  │  • documents │  │  :30b    │  └────────────────┘           │
│  │  • chats     │  │          │                                │
│  │  • matches   │  │ GDPR ✅  │                                │
│  └──────────────┘  └──────────┘                                │
│   Private Network   Private Network                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Services

### 1. Authentication Service (`/auth`, `/users`)

**Purpose:** JWT-based authentication with user management

**Endpoints:**
- `POST /auth/register` - Create new user
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Get current user
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/request-verify-token` - Request email verification
- `POST /auth/verify` - Verify email
- `GET /users/{user_id}` - Get user by ID
- `PATCH /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user (admin)

**Authentication:**
All endpoints (except register/login) require JWT token:
```http
Authorization: Bearer <your_jwt_token>
```

**Example Usage:**
```bash
# Register
curl -X POST https://general-backend-production-a734.up.railway.app/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "is_active": true
  }'

# Login
curl -X POST https://general-backend-production-a734.up.railway.app/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=SecurePassword123!'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 2. LLM Service (`/llm`)

**Purpose:** Multi-provider LLM gateway with unified API

**Available Providers:**
1. **Ollama** (GDPR-compliant, local, free)
   - Model: qwen3-coder:30b (30B parameters, 18.5GB)
   - ⚠️ **Note:** CPU inference is slow (~2min timeout)
   - Recommendation: Use Claude/Grok until GPU available

2. **Anthropic Claude** (Premium quality)
   - claude-3-5-sonnet-20241022
   - claude-3-opus-20240229
   - claude-3-haiku-20240307

3. **Grok** (Fast & affordable)
   - grok-beta
   - grok-vision-beta

**Endpoints:**
- `GET /llm/models?provider=ollama` - List available models
- `POST /llm/generate` - Generate text
- `POST /llm/embed` - Generate embeddings (Ollama only)

**Example Usage:**
```bash
# List models
curl -X GET https://general-backend-production-a734.up.railway.app/llm/models \
  -H 'Authorization: Bearer <token>'

# Generate text (Claude)
curl -X POST https://general-backend-production-a734.up.railway.app/llm/generate \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "model": "claude-3-5-sonnet-20241022",
    "provider": "anthropic",
    "temperature": 0.7,
    "max_tokens": 500
  }'

# Response
{
  "response": "Quantum computing is...",
  "model": "claude-3-5-sonnet-20241022",
  "provider": "anthropic",
  "tokens_used": 342
}
```

**Integration for Use Cases:**
```javascript
// Frontend integration example
const generateText = async (prompt, model = "claude-3-5-sonnet-20241022") => {
  const response = await fetch(`${API_URL}/llm/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt,
      model,
      provider: 'anthropic',
      temperature: 0.7
    })
  });
  return await response.json();
};
```

---

### 3. Document Management Service (`/documents`)

**Purpose:** Upload, store, and search documents with automatic embedding generation

**Supported Types:**
- PDF files
- DOCX files
- URLs (web scraping)
- Raw text

**Features:**
- Automatic text extraction
- Vector embeddings (sentence-transformers)
- Semantic search (pgvector cosine similarity)
- Project-based organization

**Endpoints:**
- `POST /documents/upload` - Upload PDF/DOCX
- `POST /documents/url` - Scrape URL
- `POST /documents/text` - Add raw text
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document
- `GET /documents/search?query=...` - Semantic search
- `DELETE /documents/{id}` - Delete document

**Example Usage:**
```bash
# Upload PDF
curl -X POST https://general-backend-production-a734.up.railway.app/documents/upload \
  -H 'Authorization: Bearer <token>' \
  -F 'file=@resume.pdf' \
  -F 'project_id=<project-uuid>'

# Search documents
curl -X GET 'https://general-backend-production-a734.up.railway.app/documents/search?query=python+developer&limit=5' \
  -H 'Authorization: Bearer <token>'

# Response (ordered by relevance)
[
  {
    "id": "uuid",
    "filename": "resume.pdf",
    "content": "Senior Python Developer with 5 years...",
    "embedding": [0.123, -0.456, ...],
    ...
  }
]
```

**Integration for Use Cases:**
```javascript
// CV Matcher: Upload job description
const uploadJobDescription = async (file, projectId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', projectId);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return await response.json();
};

// PrivateGPT: Search documents
const searchDocuments = async (query) => {
  const response = await fetch(
    `${API_URL}/documents/search?query=${encodeURIComponent(query)}&limit=5`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return await response.json();
};
```

---

### 4. Project Management Service (`/projects`)

**Purpose:** Organize showcase instances (CV Matcher projects, PrivateGPT sessions, etc.)

**Project Types:**
- `cv_matcher` - CV matching projects
- `privategpt` - Private document chat sessions
- `tellmelife` - Life story projects

**Endpoints:**
- `POST /projects` - Create project
- `GET /projects` - List projects
- `GET /projects/{id}` - Get project
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project (cascades to documents/chats)

**Example Usage:**
```bash
# Create CV Matcher project
curl -X POST https://general-backend-production-a734.up.railway.app/projects \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Senior Developer Hiring Q1 2025",
    "description": "Hiring campaign for senior Python developers",
    "type": "cv_matcher",
    "config": {
      "llm_provider": "anthropic",
      "embedding_model": "all-MiniLM-L6-v2"
    }
  }'

# Response
{
  "id": "project-uuid",
  "user_id": "user-uuid",
  "name": "Senior Developer Hiring Q1 2025",
  "type": "cv_matcher",
  ...
}
```

**Integration for Use Cases:**
```javascript
// Create project for specific use case
const createProject = async (name, type, config) => {
  const response = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name, description: '', type, config })
  });
  return await response.json();
};

// Example: CV Matcher
const cvProject = await createProject(
  'Q1 Hiring Campaign',
  'cv_matcher',
  { llm_provider: 'anthropic' }
);

// Example: PrivateGPT
const chatProject = await createProject(
  'Document Analysis Session',
  'privategpt',
  { embedding_model: 'all-MiniLM-L6-v2' }
);
```

---

### 5. Admin Service (`/admin`)

**Purpose:** System monitoring and administration (admin users only)

**Endpoints:**
- `GET /admin/stats` - System statistics

**Example:**
```bash
curl -X GET https://general-backend-production-a734.up.railway.app/admin/stats \
  -H 'Authorization: Bearer <admin-token>'

# Response
{
  "total_users": 15,
  "total_projects": 42,
  "total_documents": 358,
  "total_chats": 1203,
  "system_health": "healthy"
}
```

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,  -- 'cv_matcher', 'privategpt', 'tellmelife'
    config JSONB DEFAULT '{}',
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
    doc_metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),  -- pgvector for semantic search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
```

### Chats Table
```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    chat_metadata JSONB DEFAULT '{}',
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

---

## 🚀 Use Case Integration

### CV Matcher Integration

```javascript
// 1. Create project
const project = await createProject('Q1 Hiring', 'cv_matcher', {});

// 2. Upload job description
const jobDoc = await uploadDocument(jobDescriptionFile, project.id);

// 3. Upload CVs
const cvDocs = await Promise.all(
  cvFiles.map(file => uploadDocument(file, project.id))
);

// 4. Find matching candidates (semantic search)
const candidates = await fetch(
  `${API_URL}/documents/search?query=${jobDoc.content}&project_id=${project.id}&limit=10`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

// 5. Generate detailed analysis with LLM
for (const candidate of candidates) {
  const analysis = await fetch(`${API_URL}/llm/generate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: `Compare this job description with this CV and provide a detailed analysis:\n\nJob: ${jobDoc.content}\n\nCV: ${candidate.content}`,
      model: 'claude-3-5-sonnet-20241022',
      provider: 'anthropic'
    })
  });
}
```

### PrivateGPT Integration

```javascript
// 1. Create chat session
const project = await createProject('Document Analysis', 'privategpt', {});

// 2. Upload documents
await uploadDocument(document1, project.id);
await uploadDocument(document2, project.id);

// 3. User asks question
const userQuestion = "What are the key findings in these documents?";

// 4. Search relevant context
const context = await fetch(
  `${API_URL}/documents/search?query=${encodeURIComponent(userQuestion)}&project_id=${project.id}&limit=3`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);

// 5. Generate response with context
const response = await fetch(`${API_URL}/llm/generate`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: `Context:\n${context.map(d => d.content).join('\n\n')}\n\nQuestion: ${userQuestion}`,
    model: 'claude-3-5-sonnet-20241022',
    provider: 'anthropic'
  })
});
```

### TellMeLife Integration

```javascript
// 1. Create life story project
const project = await createProject('My Life Story', 'tellmelife', {});

// 2. Add text entries
await fetch(`${API_URL}/documents/text`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Childhood Memories',
    content: 'I was born in...',
    project_id: project.id,
    metadata: { category: 'childhood', year: 1990 }
  })
});

// 3. Generate narrative with LLM
const narrative = await fetch(`${API_URL}/llm/generate`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Transform these life events into a compelling narrative...',
    model: 'claude-3-5-sonnet-20241022',
    provider: 'anthropic'
  })
});
```

---

## 🌐 Deployment

### Production Services (Railway)

**Project:** Generalbackend
**Region:** EU (Amsterdam, Netherlands)

1. **general-backend** ✅
   - URL: https://general-backend-production-a734.up.railway.app
   - Health: `/health`
   - API Docs: `/docs`
   - Auto-deploy from GitHub (main branch)

2. **pgVector-Railway** ✅
   - PostgreSQL 16 + pgvector extension
   - Private network: `postgres.railway.internal`
   - All tables created with vector indices

3. **ollama** ✅
   - Ollama server with qwen3-coder:30b
   - Private network: `ollama.railway.internal:11434`
   - GDPR-compliant (EU hosting)
   - ⚠️ CPU inference is slow (use Claude/Grok for production)

4. **Admin Frontend** ✅
   - URL: https://www.dabrock.info/admin/ (SSL pending)
   - React 19 + Vite
   - Hosted on Strato

### Environment Variables

**Backend Service:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres.railway.internal:5432/railway
OLLAMA_BASE_URL=http://ollama.railway.internal:11434
SECRET_KEY=<your-secret-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
GROK_API_KEY=<your-grok-key>
ALLOWED_ORIGINS=https://www.dabrock.info,http://localhost:5173
```

### Deployment Notes

**Key Fixes Applied:**
1. Bcrypt password hashing (72-byte limit patch)
2. ChromaDB removed → pgvector implemented
3. SQLAlchemy reserved keywords fixed (`metadata` → `doc_metadata`)
4. Auto-deploy from GitHub enabled
5. Database retry logic (30 attempts)

---

## ⚙️ Configuration

### Frontend Configuration

Create `.env` file in your use case frontend:

```env
VITE_API_URL=https://general-backend-production-a734.up.railway.app
```

### API Client Setup

```javascript
// api.js
const API_URL = import.meta.env.VITE_API_URL;

export class APIClient {
  constructor(token) {
    this.token = token;
    this.baseURL = API_URL;
  }

  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return await response.json();
  }

  // Authentication
  async register(email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, is_active: true })
    });
  }

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  // Projects
  async createProject(name, type, config = {}) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify({ name, description: '', type, config })
    });
  }

  // Documents
  async uploadDocument(file, projectId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);

    const response = await fetch(`${this.baseURL}/documents/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData
    });

    return await response.json();
  }

  async searchDocuments(query, projectId = null, limit = 5) {
    let url = `/documents/search?query=${encodeURIComponent(query)}&limit=${limit}`;
    if (projectId) url += `&project_id=${projectId}`;

    return this.request(url);
  }

  // LLM
  async generateText(prompt, model = 'claude-3-5-sonnet-20241022', provider = 'anthropic') {
    return this.request('/llm/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt, model, provider, temperature: 0.7 })
    });
  }

  async listModels(provider = null) {
    let url = '/llm/models';
    if (provider) url += `?provider=${provider}`;
    return this.request(url);
  }
}
```

### Usage Example

```javascript
// In your use case frontend
import { APIClient } from './api';

const api = new APIClient();

// Login
await api.login('user@example.com', 'password');

// Create project
const project = await api.createProject('My Project', 'cv_matcher');

// Upload document
const doc = await api.uploadDocument(file, project.id);

// Search
const results = await api.searchDocuments('python developer', project.id);

// Generate text
const response = await api.generateText('Analyze this document...');
```

---

## 📚 Additional Documentation

- **Full API Reference:** See `API_DOCUMENTATION.md`
- **Interactive API Docs:** https://general-backend-production-a734.up.railway.app/docs
- **ReDoc:** https://general-backend-production-a734.up.railway.app/redoc

---

## 🔒 Security

- JWT token authentication
- Password hashing with bcrypt
- CORS enabled for whitelisted origins only
- GDPR-compliant (EU hosting, local LLM option)
- Private network for database and Ollama

---

## 📞 Support

For issues or questions:
- Check `/docs` for interactive API documentation
- Review `API_DOCUMENTATION.md` for detailed examples
- Check Railway logs for deployment issues

---

**Created:** 2025-12-21
**Status:** ✅ PRODUCTION READY
**Version:** 1.0.0
