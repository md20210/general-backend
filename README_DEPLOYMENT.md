# General Backend - Deployment Guide

## 🚂 Railway Deployment

### 1. Voraussetzungen
- Railway Account: https://railway.app
- Railway CLI installiert: `npm i -g @railway/cli`
- GitHub Account

### 2. GitHub Repository erstellen

```bash
# Im GeneralBackend Verzeichnis
git add .
git commit -m "Initial commit: General Backend with Auth, LLM, Documents"

# GitHub Repository erstellen (via GitHub Web UI oder CLI)
# Dann:
git remote add origin https://github.com/YOUR_USERNAME/general-backend.git
git push -u origin main
```

### 3. Railway Projekt erstellen

**Option A: Via Railway CLI**
```bash
# Login
railway login

# Projekt erstellen
railway init

# PostgreSQL hinzufügen
railway add -d postgres

# Environment Variables setzen
railway variables set SECRET_KEY="your-super-secret-key-$(openssl rand -hex 32)"
railway variables set ADMIN_EMAIL="admin@dabrock.info"
railway variables set ADMIN_PASSWORD="your-secure-password"
railway variables set GROK_API_KEY="xai-your-key"
railway variables set ANTHROPIC_API_KEY="sk-ant-your-key"
railway variables set OLLAMA_BASE_URL="http://your-ollama-server:11434"
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info"

# Deploy
railway up
```

**Option B: Via Railway Web UI**
1. Gehe zu https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Wähle `general-backend` Repository
4. Add PostgreSQL Service
5. Environment Variables setzen (siehe unten)
6. Deploy

### 4. Environment Variables auf Railway

**Erforderlich:**
```env
# Database (automatisch von Railway gesetzt)
DATABASE_URL=${DATABASE_URL}

# JWT Secret (generiere mit: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-change-me

# Admin User
ADMIN_EMAIL=admin@dabrock.info
ADMIN_PASSWORD=your-secure-password

# CORS
ALLOWED_ORIGINS=https://www.dabrock.info,https://api.dabrock.info

# Port (automatisch von Railway gesetzt)
PORT=${PORT}
```

**Optional:**
```env
# LLM APIs
GROK_API_KEY=xai-your-grok-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
OLLAMA_BASE_URL=http://your-ollama-server:11434

# ChromaDB
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/data/uploads

# Logging
LOG_LEVEL=INFO
```

### 5. Domain Setup

**Railway Custom Domain:**
1. Railway Dashboard → Settings → Domains
2. "Generate Domain" → Bekomme `xxx.railway.app`
3. Oder "Custom Domain" → `api.dabrock.info`

**Strato DNS für api.dabrock.info:**
1. Strato DNS Manager
2. CNAME Record: `api` → `xxx.railway.app`
3. Warte auf DNS Propagation (5-60 Min)

### 6. Migrations auf Railway

Railway führt automatisch `alembic upgrade head` beim Start aus (siehe `railway.json`).

**Manuell triggern:**
```bash
railway run alembic upgrade head
```

### 7. Admin User erstellen

**Option A: Über API (nach Deployment)**
```bash
# 1. Register Admin User
curl -X POST https://api.dabrock.info/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dabrock.info",
    "password": "your-password",
    "is_admin": true
  }'

# 2. Login
curl -X POST https://api.dabrock.info/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@dabrock.info",
    "password": "your-password"
  }'
```

**Option B: Direkt in DB (via Railway Console)**
```sql
UPDATE users
SET is_admin = true
WHERE email = 'admin@dabrock.info';
```

### 8. Health Check

```bash
# Backend erreichbar?
curl https://api.dabrock.info/health

# Response:
# {"status":"healthy","database":"connected"}
```

### 9. Test API Endpoints

```bash
# Login
TOKEN=$(curl -X POST https://api.dabrock.info/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@dabrock.info","password":"your-password"}' \
  | jq -r '.access_token')

# List LLM Models
curl https://api.dabrock.info/llm/models \
  -H "Authorization: Bearer $TOKEN"

# Create Project
curl -X POST https://api.dabrock.info/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "type": "cv_matcher",
    "description": "Testing deployment"
  }'
```

## 🌐 Frontend Deployment auf Strato

### 1. Admin Frontend erstellen

```bash
# Admin Frontend wird in admin-frontend/ erstellt
# (siehe separate Anleitung)
cd admin-frontend
npm install
npm run build
```

### 2. Zu Strato hochladen

**Via SFTP (lftp):**
```bash
# SFTP Credentials aus Strato-Account holen
export SFTP_USER="su403214"
export SFTP_PASS="your-sftp-password"
export SFTP_HOST="5018735097.ssh.w2.strato.hosting"

# Upload
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mirror -R --delete --verbose dist /htdocs/admin/"
```

**Oder via FileZilla:**
1. Host: `sftp://5018735097.ssh.w2.strato.hosting`
2. User: `su403214`
3. Password: Dein SFTP Passwort
4. Upload `dist/` → `/htdocs/admin/`

### 3. URL Setup

- **Admin Panel**: https://www.dabrock.info/admin
- **API Backend**: https://api.dabrock.info

## 📊 Monitoring

**Railway Logs:**
```bash
railway logs
```

**Oder via Web UI:**
- Railway Dashboard → Deployments → View Logs

## 🔄 Updates deployen

```bash
# Code ändern, committen
git add .
git commit -m "Update: Feature XYZ"
git push

# Railway deployed automatisch bei jedem push!
```

## ⚠️ Wichtige Hinweise

1. **SECRET_KEY**: NIEMALS in Git committen! Nur auf Railway setzen
2. **DATABASE_URL**: Automatisch von Railway gesetzt
3. **CORS**: Unbedingt `ALLOWED_ORIGINS` auf Railway setzen
4. **Migrations**: Laufen automatisch bei jedem Deploy
5. **ChromaDB**: Nutzt Railway Volume für Persistenz (optional)
6. **File Uploads**: Nutze Railway Volume oder S3 für Production

## 🐛 Troubleshooting

**Backend startet nicht:**
```bash
railway logs
# Prüfe Fehlermeldungen
```

**Database Connection Error:**
```bash
railway variables
# Prüfe DATABASE_URL ist gesetzt
```

**Migrations failed:**
```bash
railway run alembic upgrade head
# Manuell ausführen
```

**CORS Error im Frontend:**
```bash
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info"
```

## 📞 Support

Bei Problemen siehe:
- Railway Docs: https://docs.railway.app
- Alembic Docs: https://alembic.sqlalchemy.org
- FastAPI Docs: https://fastapi.tiangolo.com
