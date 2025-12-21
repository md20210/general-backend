# 🚀 Deployment Schritte - General Backend

## ✅ Was bereits erledigt ist:

- ✅ Git Repository initialisiert
- ✅ Initialer Commit erstellt (45 files, 4846 lines)
- ✅ Railway-Dateien erstellt (railway.json, Procfile, nixpacks.toml)
- ✅ .gitignore konfiguriert
- ✅ Documentation erstellt

## 📋 Nächste Schritte (von Dir auszuführen):

### 1. GitHub Repository erstellen

**Option A: Via GitHub CLI (gh)**
```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend

# Login (falls noch nicht)
gh auth login

# Repository erstellen
gh repo create general-backend --public --source=. --remote=origin --push

# Fertig! Code ist auf GitHub
```

**Option B: Via GitHub Web UI**
```bash
# 1. Gehe zu https://github.com/new
# 2. Repository Name: general-backend
# 3. Public oder Private
# 4. Klicke "Create repository"

# 5. Dann lokal:
cd /mnt/e/CodeLocalLLM/GeneralBackend
git remote add origin https://github.com/DEIN_USERNAME/general-backend.git
git push -u origin main
```

### 2. Railway Deployment

**Schritt 1: Railway CLI installieren (falls noch nicht)**
```bash
npm i -g @railway/cli
```

**Schritt 2: Railway Login**
```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend
railway login
```

**Schritt 3: Projekt erstellen & PostgreSQL hinzufügen**
```bash
# Projekt erstellen
railway init

# PostgreSQL hinzufügen
railway add -d postgres

# Warte 30 Sekunden bis PostgreSQL bereit ist
```

**Schritt 4: Environment Variables setzen**
```bash
# SECRET_KEY generieren
SECRET_KEY=$(openssl rand -hex 32)

# Variables setzen
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ADMIN_EMAIL="admin@dabrock.info"
railway variables set ADMIN_PASSWORD="IhrSicheresPasswort123!"
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info"

# Optional: LLM APIs
railway variables set GROK_API_KEY="xai-your-grok-key"
railway variables set ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
railway variables set OLLAMA_BASE_URL="http://localhost:11434"
```

**Schritt 5: Deploy!**
```bash
railway up

# Oder via GitHub:
git push origin main
# Railway deployed automatisch bei jedem push (wenn GitHub connected)
```

**Schritt 6: Custom Domain (optional)**
```bash
# Via Railway Web UI:
# 1. Railway Dashboard → Dein Projekt → Settings → Domains
# 2. "Generate Domain" → z.B. general-backend-production.up.railway.app
# 3. Oder "Custom Domain" → api.dabrock.info

# Dann Strato DNS:
# CNAME: api → general-backend-production.up.railway.app
```

**Schritt 7: Logs checken**
```bash
railway logs
# Sollte zeigen:
# - "Starting General Backend..."
# - "Database tables created/verified"
# - "Application startup complete"
```

**Schritt 8: Health Check**
```bash
# Hole Railway URL
RAILWAY_URL=$(railway status | grep "URL" | awk '{print $2}')

# Test
curl $RAILWAY_URL/health

# Sollte zurückgeben:
# {"status":"healthy","database":"connected"}
```

### 3. Admin User erstellen

**Via API:**
```bash
# 1. Register Admin
curl -X POST $RAILWAY_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dabrock.info",
    "password": "IhrSicheresPasswort123!",
    "is_admin": true
  }'

# 2. Login & Token holen
TOKEN=$(curl -X POST $RAILWAY_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@dabrock.info","password":"IhrSicheresPasswort123!"}' \
  | jq -r '.access_token')

echo "Your JWT Token: $TOKEN"

# 3. Test Admin Endpoints
curl $RAILWAY_URL/admin/stats \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Admin Frontend erstellen

**Jetzt erstellen wir das React Admin Panel:**

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend
mkdir admin-frontend
cd admin-frontend

# Vite + React erstellen
npm create vite@latest . -- --template react

# Dependencies installieren
npm install axios react-router-dom

# Frontend Code wird erstellt (siehe nächste Schritte)
```

**Ich erstelle jetzt die Admin Frontend Dateien...**

---

## 🎯 Zusammenfassung Status

✅ **Fertig:**
- Git Repository initialisiert
- Code committed
- Railway-Konfiguration erstellt
- Deployment-Dokumentation geschrieben

⏳ **Nächste Schritte (Du):**
1. GitHub Repository erstellen & pushen
2. Railway CLI setup & deploy
3. Environment Variables setzen
4. Domain konfigurieren

⏭️ **Danach (Ich):**
1. Admin Frontend erstellen
2. Frontend zu Strato deployen
3. Integration testen

---

## 🐛 Troubleshooting

**"alembic: command not found"**
```bash
railway run pip install alembic
railway restart
```

**"ModuleNotFoundError: No module named 'backend'"**
```bash
# Prüfe ob requirements.txt installiert wurde
railway logs
# Sollte "pip install -r requirements.txt" zeigen
```

**"Connection refused" bei Database**
```bash
# Warte 1-2 Minuten nach PostgreSQL add
railway logs
# Sollte "Database tables created/verified" zeigen
```

**CORS Error**
```bash
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info,https://your-railway-url.railway.app"
railway restart
```
