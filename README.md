# General Backend - Zentrale Backend-Lösung für alle Showcases

## 🎯 Überblick

Ein zentrales, wiederverwendbares Backend auf Railway, das alle Showcases (CV Matcher, PrivateGPT, TellMeLife) mit einem gemeinsamen Backend unterstützt.

**Hauptfeatures:**
- 🔐 Benutzerverwaltung (Admin + reguläre User)
- 🤖 Multi-LLM Support (Ollama, GROK, Anthropic)
- 📚 Vector Store (ChromaDB + pgvector)
- 🗄️ PostgreSQL Database
- 👨‍💼 Admin Panel auf www.dabrock.info
- 🚀 Railway Deployment

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

**Aktuell:** Planning Phase
**Nächster Schritt:** Phase 1 - Core Backend Setup

Siehe [ARCHITECTURE.md](./ARCHITECTURE.md) für detaillierten Roadmap.

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
