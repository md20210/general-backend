# General Backend - Zentrale Backend-Lösung für alle Showcases

## 🎯 Überblick

Ein zentrales, wiederverwendbares Backend auf Railway, das alle Showcases (CV Matcher, PrivateGPT, TellMeLife, Bar Ca l'Elena) mit einem gemeinsamen Backend unterstützt.

**Hauptfeatures:**
- 🔐 Benutzerverwaltung (Admin + reguläre User)
- 🤖 Multi-LLM Support (Ollama, GROK, Anthropic)
- 📚 Vector Store (ChromaDB + pgvector)
- 🗄️ PostgreSQL Database
- 👨‍💼 Admin Panel auf www.dabrock.info
- 🚀 Railway Deployment (Auto-deploy from GitHub)
- 🌍 Multi-language Support (5 languages: CA, ES, EN, DE, FR)
- 📰 Newsletter Management with automatic translation
- 🍽️ Restaurant/Bar Management System

## 📚 Dokumentation

Siehe [ARCHITECTURE.md](./ARCHITECTURE.md) für:
- Detaillierte Architektur
- Tech Stack
- Database Schema
- API Endpoints
- Implementation Roadmap
- Aider Prompts für jede Phase

## 🚀 Quick Start

### Voraussetzungen
- Python 3.11+
- PostgreSQL 15+
- Ollama (optional, für lokale LLMs)
- Railway Account
- Aider installiert

### Installation (Lokal)

```bash
# 1. Repository klonen / Verzeichnis nutzen
cd /mnt/e/CodeLocalLLM/GeneralBackend

# 2. Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Environment Variables setzen
cp .env.example .env
# .env bearbeiten mit deinen Werten

# 5. PostgreSQL Datenbank erstellen
createdb generalbackend

# 6. Migrationen ausführen
alembic upgrade head

# 7. Server starten
uvicorn backend.main:app --reload --port 8000
```

### Mit Aider entwickeln

```bash
# Aider mit Claude starten
aider --model anthropic/claude-sonnet-4

# In Aider - Beispiel Prompts:
/add backend/main.py
"Erstelle die FastAPI Basis-Struktur mit Health-Check Endpoint"

/add backend/models/user.py
"Erstelle das User Model mit SQLAlchemy und fastapi-users Integration"
```

## 📁 Projektstruktur

```
GeneralBackend/
├── backend/              # Backend Code
├── admin-frontend/       # Admin Panel (React)
├── tests/               # Tests
├── data/                # Local data (gitignored)
├── ARCHITECTURE.md      # Detaillierte Architektur
├── README.md            # Diese Datei
└── requirements.txt     # Python Dependencies
```

## 🔧 Environment Variables

Siehe `.env.example` für alle verfügbaren Variablen.

Wichtigste:
- `DATABASE_URL` - PostgreSQL Connection String
- `SECRET_KEY` - JWT Secret
- `OLLAMA_BASE_URL` - Ollama API URL
- `GROK_API_KEY` - GROK API Key
- `ANTHROPIC_API_KEY` - Anthropic API Key

## 🚂 Railway Deployment

```bash
# 1. Railway CLI installieren
npm i -g @railway/cli

# 2. Login
railway login

# 3. Projekt erstellen
railway init

# 4. PostgreSQL hinzufügen
railway add postgresql

# 5. Environment Variables setzen
railway variables set SECRET_KEY=...
railway variables set GROK_API_KEY=...
railway variables set ANTHROPIC_API_KEY=...

# 6. Deploy
railway up
```

## 📊 Status

**Aktuell:** Production - Multiple Live Projects

### Live Projects:
1. **Bar Ca l'Elena** - ✅ Fully Deployed and Live
   - Frontend: https://www.dabrock.info/morningbar/
   - Backend: Railway (auto-deploy from main branch)
   - Database: PostgreSQL on Render
   - Features: Multi-language, RAG chat, newsletter, admin panel

2. **CV Matcher** - 🚧 In Development
3. **PrivateGPT** - 🚧 In Development
4. **TellMeLife** - ⏳ Planned

Siehe [ARCHITECTURE.md](./ARCHITECTURE.md) für detaillierten Roadmap.

## 🆕 Recent Updates (2026-01-10)

### Bar Ca l'Elena Module
- ✅ Implemented comprehensive Newsletter Management system
- ✅ Added 170+ multilingual translation keys
- ✅ Fixed GPS coordinates (41.359276, 2.124410)
- ✅ Made all admin UI components fully multilingual
- ✅ Upgraded to Grok 3 model
- ✅ Implemented automatic translation for:
  - Featured items
  - News/events
  - Newsletters
  - Customer reviews

### Database Schema
- ✅ Added `language` column to `bar_newsletter` table
- ✅ Migration: `20260110_newsletter_language.py`

### API Endpoints
See `/docs` for full API documentation:
- Public Bar API: `/bar/*`
- Admin Bar API: `/bar/admin/*`
- Translation API: `/translations/{lang}`

### Deployment
- Backend: Automatic deployment via Railway on push to `main`
- Frontend: Manual deployment via SFTP to Strato
- Database: PostgreSQL on Render with automatic backups

## 🤝 Entwicklung mit Aider

Dieses Projekt ist optimiert für Entwicklung mit Aider + Claude.

Siehe [ARCHITECTURE.md - Phase 1-10](./ARCHITECTURE.md#-implementation-roadmap) für fertige Aider Prompts für jede Phase.

## 📝 Showcase Integration

### CV Matcher
- Endpoints: `/cv-matcher/*`
- Frontend nutzt zentrales Backend via API

### PrivateGPT
- Endpoints: `/chat/*`
- Frontend nutzt zentrales Backend via API

### TellMeLife
- Endpoints: `/stories/*` (TBD)
- Frontend nutzt zentrales Backend via API

### Bar Ca l'Elena
- **Status**: ✅ Fully Implemented and Live
- **Frontend**: https://www.dabrock.info/morningbar/
- **Endpoints**: `/bar/*`, `/bar/admin/*`
- **Features**:
  - Multi-language website (CA, ES, EN, DE, FR)
  - RAG Chatbot with bar information (Ollama/Grok)
  - Menu management (PDF, JPG, PNG uploads)
  - News & Events with automatic translation
  - Featured items with images and multilingual descriptions
  - Online reservations
  - Newsletter management:
    - Email subscription with language selection
    - Admin panel to create and send newsletters
    - Automatic translation to all 5 languages
    - Language-specific delivery
  - Customer reviews (multilingual)
  - Google Maps integration
  - GDPR compliant (default to Ollama)

**Admin Panel**: `/admin` tab on https://www.dabrock.info/morningbar/
- Settings (LLM provider, auto-speak, contact email)
- Menu Upload
- Featured Items Management
- News Management
- Newsletter Management

## 🔐 Admin Panel

Zugriff: `https://www.dabrock.info/admin`

Features:
- User Management
- LLM Configuration
- System Statistics
- Project Overview

## 📞 Support

Bei Fragen siehe [ARCHITECTURE.md](./ARCHITECTURE.md) oder kontaktiere den Maintainer.

---

**Erstellt:** 2025-12-21
**Maintainer:** Michael Dabrock
# Trigger deployment to run Klassentreffen migration
# Trigger Railway deploy
