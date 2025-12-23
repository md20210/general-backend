# General Backend - Complete API Documentation

**Base URL:** `https://general-backend-production-a734.up.railway.app`
**API Docs:** `https://general-backend-production-a734.up.railway.app/docs`

## Authentication

All endpoints (except registration and login) require a JWT token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication Endpoints (`/auth`)

###  1.1 Register New User

**POST** `/auth/register`

Creates a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "is_admin": false
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "is_admin": false
}
```

---

### 1.2 Login

**POST** `/auth/login`

Login and get JWT access token.

**Request Body** (form-urlencoded):
```
username=user@example.com
password=SecurePassword123!
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 1.3 Get Current User

**GET** `/auth/me`

Get currently authenticated user's information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "is_admin": false
}
```

---

### 1.4 Logout

**POST** `/auth/logout`

Logout (invalidates JWT token on client side).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

---

### 1.5 Request Password Reset

**POST** `/auth/forgot-password`

Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response** (202 Accepted)

---

### 1.6 Reset Password

**POST** `/auth/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "password": "NewSecurePassword123!"
}
```

**Response** (200 OK)

---

### 1.7 Request Email Verification

**POST** `/auth/request-verify-token`

Request email verification token.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (202 Accepted)

---

### 1.8 Verify Email

**POST** `/auth/verify`

Verify email using token.

**Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

**Response** (200 OK)

---

## 2. User Management Endpoints (`/users`)

### 2.1 Get User by ID

**GET** `/users/{user_id}`

Get user details (admin only or own user).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false,
  "is_admin": false
}
```

---

### 2.2 Update User

**PATCH** `/users/{user_id}`

Update user (admin only or own user).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "password": "NewPassword123!",
  "is_active": true
}
```

**Response** (200 OK): Updated user object

---

### 2.3 Delete User

**DELETE** `/users/{user_id}`

Delete user (admin only).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

---

## 3. LLM Endpoints (`/llm`)

### 3.1 List Available Models

**GET** `/llm/models?provider=ollama`

List all available LLM models.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `provider` (optional): Filter by provider (`ollama`, `anthropic`, `grok`)

**Response** (200 OK):
```json
{
  "models": [
    {
      "name": "llama3.2:3b",
      "provider": "ollama",
      "description": "Local Ollama model - CPU optimized"
    },
    {
      "name": "claude-3-5-sonnet-20241022",
      "provider": "anthropic",
      "description": "Claude 3.5 Sonnet - Most intelligent model"
    },
    {
      "name": "grok-beta",
      "provider": "grok",
      "description": "GROK Beta - X.AI's frontier model"
    }
  ],
  "total": 3
}
```

---

### 3.2 Generate Text (LLM Inference)

**POST** `/llm/generate`

Generate text using specified LLM model.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "prompt": "Write a Python function to add two numbers",
  "model": "llama3.2:3b",
  "provider": "ollama",
  "temperature": 0.7,
  "max_tokens": 500,
  "timeout": 120
}
```

**Request Fields:**
- `prompt` (string, required): The prompt text
- `model` (string, optional): Model name (default: provider's default)
- `provider` (string, optional): Provider name (`ollama`, `anthropic`, `grok`)
- `temperature` (float, optional): 0.0-2.0, default 0.7
- `max_tokens` (int, optional): Max response length
- `timeout` (int, optional): Request timeout in seconds

**Response** (200 OK):
```json
{
  "response": "def add_numbers(a, b):\n    return a + b",
  "model": "llama3.2:3b",
  "provider": "ollama",
  "tokens_used": 25
}
```

---

### 3.3 Generate Embeddings

**POST** `/llm/embed`

Generate vector embeddings for text (uses Ollama).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "text": "This is a sample text to embed",
  "model": "nomic-embed-text"
}
```

**Response** (200 OK):
```json
{
  "embedding": [0.123, -0.456, 0.789, ...],
  "model": "nomic-embed-text",
  "dimensions": 768
}
```

---

## 4. Project Management Endpoints (`/projects`)

### 4.1 Create Project

**POST** `/projects`

Create a new project.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "name": "My CV Matcher Project",
  "description": "Project for matching job applicants",
  "type": "cv_matcher",
  "config": {
    "llm_provider": "ollama",
    "embedding_model": "nomic-embed-text"
  }
}
```

**Request Fields:**
- `name` (string, required): Project name
- `description` (string, optional): Project description
- `type` (string, required): `cv_matcher`, `privategpt`, or `tellmelife`
- `config` (object, optional): Project-specific configuration

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "name": "My CV Matcher Project",
  "description": "Project for matching job applicants",
  "type": "cv_matcher",
  "config": {
    "llm_provider": "ollama",
    "embedding_model": "nomic-embed-text"
  },
  "created_at": "2025-12-21T21:00:00Z",
  "updated_at": "2025-12-21T21:00:00Z"
}
```

---

### 4.2 List Projects

**GET** `/projects`

List all user's projects.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
[
  {
    "id": "uuid-1",
    "user_id": "user-uuid",
    "name": "Project 1",
    "description": "First project",
    "type": "cv_matcher",
    "config": {},
    "created_at": "2025-12-21T21:00:00Z",
    "updated_at": "2025-12-21T21:00:00Z"
  },
  ...
]
```

---

### 4.3 Get Project by ID

**GET** `/projects/{project_id}`

Get specific project details.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK): Single project object

---

### 4.4 Update Project

**PATCH** `/projects/{project_id}`

Update project.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "config": {
    "new_setting": "value"
  }
}
```

**Response** (200 OK): Updated project object

---

### 4.5 Delete Project

**DELETE** `/projects/{project_id}`

Delete project and all associated data (documents, chats, etc.).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

---

## 5. Document Management Endpoints (`/documents`)

### 5.1 Upload Document (PDF/DOCX)

**POST** `/documents/upload`

Upload PDF or DOCX file. Automatically extracts text and creates embeddings.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file, required): PDF or DOCX file
- `project_id` (string, optional): UUID of project

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "project_id": "project-uuid",
  "type": "pdf",
  "filename": "resume.pdf",
  "url": null,
  "content": "Extracted text content...",
  "doc_metadata": {
    "original_size": 12345
  },
  "embedding": [0.123, -0.456, ...],
  "created_at": "2025-12-21T21:00:00Z"
}
```

---

### 5.2 Add Document from URL

**POST** `/documents/url`

Scrape website and create document.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "project_id": "project-uuid",
  "metadata": {
    "category": "research"
  }
}
```

**Response** (201 Created): Document object with scraped content

---

### 5.3 Add Text Document

**POST** `/documents/text`

Create document from raw text.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "title": "My Notes",
  "content": "This is the document content...",
  "project_id": "project-uuid",
  "metadata": {
    "category": "notes"
  }
}
```

**Response** (201 Created): Document object

---

### 5.4 List Documents

**GET** `/documents?project_id=uuid`

List all user's documents.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `project_id` (optional): Filter by project UUID

**Response** (200 OK):
```json
[
  {
    "id": "uuid-1",
    "user_id": "user-uuid",
    "project_id": "project-uuid",
    "type": "pdf",
    "filename": "resume.pdf",
    "url": null,
    "content": "...",
    "doc_metadata": {},
    "embedding": [...],
    "created_at": "2025-12-21T21:00:00Z"
  },
  ...
]
```

---

### 5.5 Get Document by ID

**GET** `/documents/{document_id}`

Get specific document.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK): Single document object

---

### 5.6 Search Documents (Vector/Semantic Search)

**GET** `/documents/search?query=python+programming&limit=5`

Search documents using semantic similarity (pgvector).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `query` (string, required): Search query (min 3 characters)
- `project_id` (string, optional): Filter by project UUID
- `limit` (int, optional): Max results (default: 5)

**Response** (200 OK):
```json
[
  {
    "id": "uuid-1",
    "content": "Document about Python...",
    "doc_metadata": {},
    ...
  },
  ...
]
```

**Note:** Results are ordered by relevance (cosine similarity).

---

### 5.7 Delete Document

**DELETE** `/documents/{document_id}`

Delete document.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (204 No Content)

---

## 6. Admin Endpoints (`/admin`)

### 6.1 Get Admin Dashboard Stats

**GET** `/admin/stats`

Get system statistics (admin only).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "total_users": 10,
  "total_projects": 25,
  "total_documents": 150,
  "total_chats": 500,
  "system_health": "healthy"
}
```

---

## 7. Reports Endpoints (`/reports`)

### 7.1 Generate PDF Report

**POST** `/reports/generate`

Generate PDF report for CV match analysis with chat history.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "match_result": {
    "overallScore": 85,
    "strengths": [
      "10+ years Python experience",
      "AWS certification",
      "Team leadership experience"
    ],
    "gaps": [
      "No Kubernetes experience",
      "Limited frontend skills"
    ],
    "recommendations": [
      "Consider Kubernetes training",
      "Pair with frontend developer"
    ],
    "comparison": [
      {
        "requirement": "Python 5+ years",
        "applicant_match": "10 years Python",
        "details": "Exceeds requirement significantly",
        "match_level": "full",
        "confidence": 95
      }
    ],
    "detailedAnalysis": "Candidate shows strong backend skills..."
  },
  "chat_history": [
    {
      "role": "user",
      "content": "Warum ist der Match Score 85%?",
      "timestamp": "2025-12-23T18:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Der Match Score ist 85%, weil...",
      "timestamp": "2025-12-23T18:30:15Z"
    }
  ]
}
```

**Response** (200 OK):
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=cv_match_report.pdf`
- PDF file as binary stream

**PDF Contents:**
1. Overall match score with color-coded indicator
2. 2-column layout: Strengths | Gaps
3. Recommendations (if available)
4. Detailed comparison table with confidence %
5. Detailed analysis text
6. Complete chat conversation history

**Errors:**
- 401: Unauthorized (missing/invalid JWT)
- 500: PDF generation failed

---

## 8. Chat Endpoints (`/chat`)

### 8.1 Send Chat Message with RAG

**POST** `/chat/message`

Send a chat message with Retrieval-Augmented Generation (RAG).

Uses vector search to find relevant documents, then generates response using LLM with retrieved context.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hat der Bewerber AWS Erfahrung?",
  "project_id": "uuid-here",
  "system_context": "Match Analysis Summary: Overall Score: 85%...",
  "provider": "ollama",
  "model": "qwen2.5:3b",
  "temperature": 0.7,
  "max_tokens": 500,
  "context_limit": 3
}
```

**Response** (200 OK):
```json
{
  "message": "Ja, der Bewerber hat 5 Jahre AWS Erfahrung mit...",
  "sources": [
    {
      "document_id": "uuid-here",
      "filename": "cv.pdf",
      "type": "pdf",
      "relevance_score": 0.89
    }
  ],
  "model": "qwen2.5:3b",
  "provider": "ollama"
}
```

**Features:**
- German language responses by default
- Vector search across uploaded documents
- Top 3 most relevant sources included
- Relevance scores show search quality
- Optional system context for custom instructions

---

## Error Responses

All endpoints may return these error codes:

**400 Bad Request:**
```json
{
  "detail": "Invalid input data"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Unauthorized"
}
```

**403 Forbidden:**
```json
{
  "detail": "Access denied"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. This may be added in future versions.

---

## CORS

CORS is enabled for configured origins. Frontend applications must be whitelisted in backend configuration.

---

## Health Check

**GET** `/health`

Check if API is running.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Interactive API Documentation

Full interactive API documentation with request/response examples:
- **Swagger UI:** `https://general-backend-production-a734.up.railway.app/docs`
- **ReDoc:** `https://general-backend-production-a734.up.railway.app/redoc`
