# Aider Workflow für General Backend

Dieses Dokument beschreibt den empfohlenen Workflow für die Entwicklung mit Aider.

## 🚀 Aider starten

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend

# Mit Claude Sonnet 4 (empfohlen)
aider --model anthropic/claude-sonnet-4

# Oder mit Qwen-Coder (lokal)
aider --model qwen-coder
```

## 📋 Phase 1: Core Backend Setup

### Schritt 1: Projekt-Initialisierung

```bash
# In Aider:
/add requirements.txt

# Prompt:
Erstelle eine requirements.txt mit folgenden Dependencies:
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- sqlalchemy==2.0.25
- alembic==1.13.1
- psycopg2-binary==2.9.9
- asyncpg==0.29.0
- fastapi-users[sqlalchemy]==12.1.3
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- pydantic[email]==2.5.3
- python-dotenv==1.0.0
- pydantic-settings==2.1.0
```

### Schritt 2: Backend Basis-Struktur

```bash
/add backend/main.py
/add backend/config.py
/add backend/database.py

# Prompt:
Erstelle ein FastAPI Backend mit folgender Struktur:

1. backend/config.py:
   - Settings Klasse mit Pydantic BaseSettings
   - Lade alle Umgebungsvariablen aus .env
   - DATABASE_URL, SECRET_KEY, etc.

2. backend/database.py:
   - SQLAlchemy async engine setup
   - SessionLocal factory
   - Base class für Models
   - get_db dependency

3. backend/main.py:
   - FastAPI app Initialisierung
   - CORS Middleware mit ALLOWED_ORIGINS
   - Health check endpoint: GET /health
   - Lifespan context manager für DB connection
```

### Schritt 3: User Model & Authentication

```bash
/add backend/models/__init__.py
/add backend/models/user.py
/add backend/schemas/user.py

# Prompt:
Erstelle User Model und Schemas mit fastapi-users:

1. backend/models/user.py:
   - User Klasse erbt von SQLAlchemyBaseUserTableUUID
   - Felder: email, hashed_password, is_admin, is_active, is_verified
   - created_at, updated_at timestamps

2. backend/schemas/user.py:
   - UserRead, UserCreate, UserUpdate Schemas
   - Nutze fastapi-users schemas als Basis
   - Füge is_admin Feld hinzu
```

### Schritt 4: Authentication Endpoints

```bash
/add backend/auth/__init__.py
/add backend/auth/users.py
/add backend/auth/jwt.py
/add backend/api/auth.py

# Prompt:
Implementiere JWT Authentication mit fastapi-users:

1. backend/auth/users.py:
   - Setup UserManager
   - get_user_db dependency
   - get_user_manager dependency

2. backend/auth/jwt.py:
   - JWT Backend Configuration
   - SECRET_KEY aus config
   - Token lifetime: 30 Minuten

3. backend/api/auth.py:
   - Router mit fastapi-users auth_router
   - Endpoints: /auth/register, /auth/login, /auth/logout
   - GET /auth/me für current user

4. Integriere in backend/main.py:
   - Include auth router
```

### Schritt 5: Admin Middleware

```bash
/add backend/auth/dependencies.py
/add backend/api/admin.py

# Prompt:
Erstelle Admin-Funktionalität:

1. backend/auth/dependencies.py:
   - current_active_user dependency (from fastapi-users)
   - require_admin dependency (check is_admin=True)

2. backend/api/admin.py:
   - GET /admin/users - List all users (Admin only)
   - POST /admin/users - Create user (Admin only)
   - GET /admin/users/{id} - Get user (Admin only)
   - PUT /admin/users/{id} - Update user (Admin only)
   - DELETE /admin/users/{id} - Delete user (Admin only)
   - Alle Endpoints nutzen require_admin dependency
```

## 📋 Phase 2: Database Models

### Schritt 6: Remaining Models

```bash
/add backend/models/project.py
/add backend/models/document.py
/add backend/models/chat.py
/add backend/models/match.py
/add backend/schemas/project.py
/add backend/schemas/document.py
/add backend/schemas/chat.py
/add backend/schemas/match.py

# Prompt:
Erstelle die restlichen Models und Schemas gemäß ARCHITECTURE.md:

1. Projects Model:
   - id (UUID), user_id (FK), type, name, description, config (JSONB)
   - Relationship zu User (ForeignKey mit CASCADE)

2. Documents Model:
   - id (UUID), user_id (FK), project_id (FK), type, filename, url, content
   - metadata (JSONB), vector_collection_id
   - Relationships zu User und Project

3. Chats Model:
   - id (UUID), user_id (FK), project_id (FK), role, content
   - metadata (JSONB), created_at
   - Relationships zu User und Project

4. Matches Model (CV Matcher specific):
   - id (UUID), user_id (FK), project_id (FK)
   - employer_doc_ids (Array), applicant_doc_ids (Array)
   - llm_type, match_score, comparison (JSONB)
   - strengths, gaps, summary, etc.

Erstelle auch die entsprechenden Pydantic Schemas für jedes Model.
```

### Schritt 7: Alembic Migrations

```bash
/add alembic.ini
/add alembic/env.py

# Prompt:
Setup Alembic für Database Migrations:

1. Erstelle alembic.ini:
   - Konfiguration für SQLAlchemy
   - Nutze DATABASE_URL aus .env

2. Erstelle alembic/env.py:
   - Import Base und alle Models
   - Async migration support
   - Auto-generate migrations

3. Generiere erste Migration:
   - Alle Tables (users, projects, documents, chats, matches)

Gib mir dann die Bash-Befehle zum Ausführen der Migrations.
```

## 📋 Phase 3: LLM Gateway

### Schritt 8: LLM Gateway Service

```bash
/add backend/services/__init__.py
/add backend/services/llm_gateway.py

# Prompt:
Erstelle einen LLM Gateway Service der mehrere LLM Provider unterstützt:

1. backend/services/llm_gateway.py:
   - LLMGateway Klasse mit Methoden:
     - generate(prompt, model, provider) -> str
     - list_models() -> List[dict]
     - embed(text, model) -> List[float]

   - Provider Support:
     - Ollama (requests zu OLLAMA_BASE_URL)
     - GROK (OpenAI client mit base_url)
     - Anthropic (anthropic client)

   - Error Handling & Retries
   - Timeout support
   - Model mapping (user-friendly names → API names)

2. Kopiere hilfreiche Logik aus:
   /mnt/e/CodeLocalLLM/cvmatcher/backend/llm_client.py
```

### Schritt 9: LLM API Endpoints

```bash
/add backend/api/llm.py

# Prompt:
Erstelle LLM API Endpoints:

1. POST /llm/generate:
   - Body: {prompt, model?, provider?}
   - Returns: {response, model, provider, usage}
   - Requires authentication

2. GET /llm/models:
   - List available models from all providers
   - Returns: [{name, provider, description}]

3. POST /llm/embed:
   - Body: {text, model?}
   - Returns: {embedding: List[float]}
   - Requires authentication
```

## 📋 Phase 4: Vector Store

### Schritt 10: Vector Store Service

```bash
/add backend/services/vector_store.py

# Prompt:
Erstelle Vector Store Service mit ChromaDB:

1. backend/services/vector_store.py:
   - VectorStore Klasse
   - Per-user collections: "user_{user_id}_{project_id}"
   - Methoden:
     - add_documents(user_id, project_id, docs, metadata)
     - query(user_id, project_id, query, n_results=5)
     - delete_collection(user_id, project_id)

2. Kopiere und adaptiere:
   /mnt/e/CodeLocalLLM/cvmatcher/backend/vector_store.py

3. User-Isolation wichtig!
```

## 📋 Phase 5: Document Processing

### Schritt 11: Document Processor

```bash
/add backend/services/document_processor.py

# Prompt:
Erstelle Document Processing Service:

1. backend/services/document_processor.py:
   - extract_from_pdf(file_path) -> str
   - extract_from_docx(file_path) -> str
   - scrape_website(url) -> dict
   - chunk_text(text, chunk_size=500) -> List[str]

2. Kopiere direkt (funktioniert gut):
   /mnt/e/CodeLocalLLM/cvmatcher/backend/document_processor.py

3. Erhöhe URL content limit auf 10000 Zeichen
```

### Schritt 12: Document API Endpoints

```bash
/add backend/api/documents.py

# Prompt:
Erstelle Document Management Endpoints:

1. GET /documents?project_id={id}:
   - List user's documents (filtered by project if provided)
   - Only user's own documents

2. POST /documents/upload:
   - Upload PDF/DOCX file
   - Extract content
   - Store in DB
   - Generate embeddings
   - Add to vector store

3. POST /documents/url:
   - Scrape URL
   - Store content
   - Generate embeddings

4. POST /documents/text:
   - Store raw text
   - Generate embeddings

5. GET /documents/{id}:
   - Get document details
   - Only if user owns it

6. DELETE /documents/{id}:
   - Delete document
   - Remove from vector store
   - Only if user owns it
```

## 📋 Phase 6: CV Matcher Integration

### Schritt 13: CV Matcher Service

```bash
/add backend/services/cv_matcher.py
/add backend/api/cv_matcher.py

# Prompt:
Portiere CV Matcher Funktionalität:

1. backend/services/cv_matcher.py:
   - analyze_match(employer_docs, applicant_docs, llm_type, user_id)
   - Nutze LLMGateway statt direkten Ollama call
   - Speichere in PostgreSQL statt JSON
   - User-Isolation

2. Kopiere Logik aus:
   /mnt/e/CodeLocalLLM/cvmatcher/backend/matcher.py

3. backend/api/cv_matcher.py:
   - POST /cv-matcher/match
   - GET /cv-matcher/matches
   - GET /cv-matcher/matches/{id}
   - DELETE /cv-matcher/matches/{id}
   - GET /cv-matcher/matches/{id}/report (PDF)
```

### Schritt 14: PDF Generator

```bash
/add backend/services/pdf_generator.py

# Prompt:
Kopiere PDF Generator:

1. Kopiere direkt:
   /mnt/e/CodeLocalLLM/cvmatcher/backend/pdf_generator.py

2. Anpassungen:
   - Nutze Match Model statt dict
   - User info in Header
```

## 📋 Phase 7: Admin Frontend

### Schritt 15: React Admin Panel

```bash
# Neues Terminal / Aider Session für Frontend
cd admin-frontend
aider --model anthropic/claude-sonnet-4

/add package.json
/add vite.config.js
/add index.html

# Prompt:
Erstelle React Admin Panel mit Vite:

1. package.json:
   - react, react-dom, react-router-dom
   - axios
   - vite

2. Basis-Struktur:
   - src/App.jsx
   - src/main.jsx
   - src/components/Login.jsx
   - src/components/UserManagement.jsx
   - src/components/LLMConfig.jsx
   - src/components/SystemStats.jsx

3. Nutze existierende CSS aus:
   /mnt/e/CodeLocalLLM/cvmatcher/frontend/src/index.css
```

## 🔧 Nützliche Aider Befehle

```bash
# Dateien hinzufügen
/add <file>

# Dateien entfernen
/drop <file>

# Code Review
/code-review

# Tests ausführen
/test

# Git commit
/commit "Commit message"

# Hilfe
/help
```

## 💡 Best Practices mit Aider

1. **Kleine Schritte**: Füge nur relevante Files hinzu für aktuelle Aufgabe
2. **Klare Prompts**: Spezifisch was erstellt werden soll
3. **Code-Referenzen**: Zeige auf existierenden Code der kopiert werden kann
4. **Iterativ**: Review → Adjust → Commit
5. **Git**: Committe oft, kleine logische Einheiten

## 🎯 Wichtige Dateien für Aider Context

**Phase 1 (Core Backend):**
- backend/main.py
- backend/config.py
- backend/database.py
- backend/models/user.py
- backend/auth/*

**Phase 2 (Models):**
- backend/models/*
- backend/schemas/*
- alembic/

**Phase 3-4 (Services):**
- backend/services/llm_gateway.py
- backend/services/vector_store.py
- backend/services/document_processor.py

**Phase 5-6 (APIs):**
- backend/api/*

## 📝 Nach jeder Phase

```bash
# Tests schreiben
/add tests/test_<feature>.py
"Erstelle Tests für <feature>"

# Git commit
/commit "feat: implement <feature>"

# Dokumentation
/add README.md
"Update README mit neuen Features"
```

---

**Tipp:** Arbeite immer nur an EINER Sache gleichzeitig. Aider funktioniert am besten mit fokussiertem Context!
