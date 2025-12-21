# ⚡ General Backend - Quick Deployment Guide

## 🚀 One-Command Deployment

Das Deployment nutzt die vorhandenen Strato-Credentials aus deinem michael-homepage Projekt.

### Schritt 1: Railway URL setzen

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend/admin-frontend

# WICHTIG: Ersetze mit deiner echten Railway URL nach dem Railway-Deploy!
echo "VITE_API_URL=https://your-railway-url.railway.app" > .env
```

### Schritt 2: Deployment ausführen

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend

# Full Deployment (Frontend + GitHub)
./deploy.sh

# Oder nur Frontend zu Strato
./deploy.sh --no-github

# Oder nur GitHub (ohne Strato)
./deploy.sh --no-strato

# Dry-Run (zeigt was passieren würde)
./deploy.sh --dry-run
```

Das Script:
- ✅ Baut Admin Frontend
- ✅ Erstellt .htaccess für SPA Routing
- ✅ Uploaded Frontend zu `/htdocs/admin/` via Strato SFTP
- ✅ Committed & pusht Backend zu GitHub
- ✅ Verifiziert Deployment

---

## 📋 Komplette Deployment-Reihenfolge

### 1. GitHub Repository erstellen

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend

# Option A: Via GitHub CLI
gh auth login
gh repo create general-backend --public --source=. --push

# Option B: Via Web UI
# 1. https://github.com/new
# 2. Create "general-backend"
# 3. Dann:
git remote add origin https://github.com/YOUR_USERNAME/general-backend.git
git push -u origin main
```

### 2. Railway Backend deployen

```bash
# Railway CLI installieren (falls nötig)
npm i -g @railway/cli

# Railway Login & Setup
railway login
railway init

# PostgreSQL hinzufügen
railway add -d postgres

# Environment Variables setzen
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set ADMIN_EMAIL="admin@dabrock.info"
railway variables set ADMIN_PASSWORD="DeinSicheresPasswort123!"
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info"

# Optional: LLM APIs
railway variables set GROK_API_KEY="xai-your-key"
railway variables set ANTHROPIC_API_KEY="sk-ant-your-key"

# Deploy!
railway up

# Railway URL holen
railway status
# Oder im Browser: Railway Dashboard → Deployments → Domain
```

### 3. Railway URL in Frontend setzen

```bash
cd admin-frontend

# Ersetze mit echter Railway URL
echo "VITE_API_URL=https://general-backend-production.up.railway.app" > .env

cd ..
```

### 4. Frontend deployen

```bash
# Deployment Script ausführen
./deploy.sh
```

Das war's! Das Script macht:
1. Build des Admin Frontends
2. Upload zu Strato `/htdocs/admin/`
3. Commit & Push zu GitHub

### 5. Admin User erstellen

```bash
# Railway URL holen
RAILWAY_URL="https://general-backend-production.up.railway.app"

# Admin registrieren
curl -X POST $RAILWAY_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dabrock.info",
    "password": "DeinPasswort123!",
    "is_admin": true
  }'

# Login testen
curl -X POST $RAILWAY_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@dabrock.info","password":"DeinPasswort123!"}'
```

### 6. Testen

- **Admin Frontend:** https://www.dabrock.info/admin
- **Backend API:** https://general-backend-production.up.railway.app/health
- **API Docs:** https://general-backend-production.up.railway.app/docs

**Login:**
- Email: admin@dabrock.info
- Password: DeinPasswort123!

---

## 🔄 Updates deployen

Bei Änderungen am Frontend:

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend

# Frontend neu bauen und uploaden
./deploy.sh
```

Bei Änderungen am Backend:

```bash
# Einfach zu GitHub pushen
git add .
git commit -m "Update: XYZ"
git push

# Railway deployed automatisch!
```

---

## 📂 Deployment-Struktur

### Strato (www.dabrock.info):
```
/htdocs/
├── admin/                    # Admin Panel (deployed via deploy.sh)
│   ├── index.html
│   ├── .htaccess
│   ├── assets/
│   └── vite.svg
├── privategpt/              # PrivateGPT (existing)
└── ... (andere Dateien)
```

### GitHub:
```
github.com/YOUR_USERNAME/general-backend
├── backend/                  # FastAPI Backend
├── admin-frontend/          # React Admin
├── alembic/                 # Migrations
└── ...
```

### Railway:
```
general-backend-production.up.railway.app
├── Backend API (auto-deployed from GitHub)
├── PostgreSQL Database
└── Environment Variables
```

---

## 🛠️ Deploy Script Optionen

```bash
# Alle Optionen
./deploy.sh --help

# Häufige Szenarien:

# 1. Full Deployment (empfohlen)
./deploy.sh

# 2. Nur Frontend aktualisieren
./deploy.sh --no-github

# 3. Nur Backend zu GitHub pushen
./deploy.sh --no-strato

# 4. Dry-Run (Test ohne Änderungen)
./deploy.sh --dry-run

# 5. Ohne Build (nutze existierenden Build)
./deploy.sh --skip-build
```

---

## ⚡ Verwendete Credentials

Das Script nutzt automatisch die Strato SFTP Credentials aus:
```
/mnt/e/Project20250615/portfolio-website/michael-homepage/.env.sftp
```

**Inhalt:**
- SFTP_HOST: 5018735097.ssh.w2.strato.hosting
- SFTP_USER: su403214
- SFTP_PASS: deutz15!2000
- SFTP_REMOTE_PATH: /htdocs/

**Kein manuelles Setup nötig!**

---

## 🎯 Checklist

- [ ] GitHub Repo erstellt
- [ ] Railway Projekt erstellt
- [ ] PostgreSQL zu Railway hinzugefügt
- [ ] Environment Variables auf Railway gesetzt
- [ ] Railway URL in `admin-frontend/.env` gesetzt
- [ ] `./deploy.sh` ausgeführt
- [ ] Admin User erstellt
- [ ] https://www.dabrock.info/admin getestet
- [ ] Backend API getestet

---

## 🐛 Troubleshooting

**"lftp: command not found"**
```bash
# Install lftp
sudo apt-get install lftp  # Ubuntu/Debian
brew install lftp          # macOS
```

**"Railway URL not set"**
```bash
# Check Railway status
railway status

# Get domain
railway domain
```

**"CORS Error im Frontend"**
```bash
# Check ALLOWED_ORIGINS
railway variables

# Sollte enthalten: https://www.dabrock.info
# Falls nicht:
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info,https://your-railway-url.railway.app"
railway restart
```

**"Admin Frontend zeigt weißen Bildschirm"**
```bash
# Check .env
cat admin-frontend/.env
# Sollte echte Railway URL haben, nicht localhost!

# Rebuild & redeploy
cd admin-frontend
npm run build
cd ..
./deploy.sh --skip-github  # Nur Frontend re-upload
```

---

## 📊 Deployment Log

Jedes Deployment erstellt ein Log:
```
deployment-20251221-HHMMSS.log
```

Bei Problemen: Check das Log für Details.

---

**Fertig! Alles ist mit einem Command deploybar:**
```bash
./deploy.sh
```
