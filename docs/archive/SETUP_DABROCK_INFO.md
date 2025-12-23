# Setup www.dabrock.info - Multi-Domain Konfiguration

**Datum:** 22. Dezember 2025
**Ziel:** Separate Domain für Showcases (CV Matcher, PrivateGPT, TellMeLife)

---

## 🎯 Ziel-Architektur

### **Domain-Trennung:**
- **www.dabrock.eu** → Persönliche Homepage (bleibt unverändert)
- **www.dabrock.info** → Showcase-Plattform (NEU)

### **Verzeichnis-Struktur auf Strato:**

```
Strato SSH: 5018735097.ssh.w2.strato.hosting
User: su403214

/
├── htdocs/                    # www.dabrock.eu (Haupt-Domain)
│   ├── index.html             # Persönliche Homepage
│   ├── assets/
│   └── admin/                 # (optional: entfernen oder behalten)
│
├── dabrock-info/              # www.dabrock.info (NEU!)
│   ├── index.html             # Showcase Landing Page
│   ├── admin/                 # Admin Panel für Backend-Verwaltung
│   ├── cv-matcher/            # CV Matcher Showcase
│   ├── privategpt/            # PrivateGPT Showcase (geplant)
│   └── tellmelife/            # TellMeLife Showcase (geplant)
```

---

## 📋 Schritt 1: Strato Domain-Konfiguration

### **Im Strato Admin Panel:**

1. Login zu: https://www.strato.de/apps/CustomerService
2. **Domain-Verwaltung** → `www.dabrock.info` auswählen
3. **Webspace-Einstellungen**
4. **Zielverzeichnis ändern:**
   - Von: `/htdocs` (Standard)
   - Zu: `/dabrock-info` (NEU)
5. Speichern

**Wichtig:** Nach dieser Änderung zeigt `www.dabrock.info` auf `/dabrock-info/`

---

## 📁 Schritt 2: Verzeichnis-Struktur erstellen

### **Via SFTP/SSH:**

```bash
# SSH Credentials
export SFTP_USER="su403214"
export SFTP_PASS="dein-strato-passwort"
export SFTP_HOST="5018735097.ssh.w2.strato.hosting"

# SSH verbinden
ssh $SFTP_USER@$SFTP_HOST

# Im SSH Terminal:
cd /
mkdir -p dabrock-info/admin
mkdir -p dabrock-info/cv-matcher
mkdir -p dabrock-info/privategpt
mkdir -p dabrock-info/tellmelife

# Permissions setzen
chmod 755 dabrock-info
chmod 755 dabrock-info/*

# Logout
exit
```

### **Alternativ: Via LFTP:**

```bash
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mkdir -p dabrock-info/admin dabrock-info/cv-matcher dabrock-info/privategpt dabrock-info/tellmelife"
```

---

## 🌐 Schritt 3: Landing Page deployen

### **Erstelle Landing Page:**

```bash
cd /mnt/e/CodelocalLLM/GeneralBackend

# Landing Page erstellen
cat > dabrock-info-landing.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Michael Dabrock - AI Showcases</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            max-width: 1200px;
            padding: 2rem;
            text-align: center;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 3rem;
        }
        .showcases {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            transition: transform 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.2);
        }
        .card h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        .card p {
            opacity: 0.8;
            line-height: 1.6;
        }
        .badge {
            display: inline-block;
            background: #4CAF50;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 1rem;
        }
        .badge.coming {
            background: #FF9800;
        }
        .admin-link {
            margin-top: 3rem;
            opacity: 0.7;
            font-size: 0.9rem;
        }
        .admin-link a {
            color: white;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Showcases</h1>
        <p class="subtitle">Enterprise-Grade AI Applications by Michael Dabrock</p>

        <div class="showcases">
            <a href="/cv-matcher/" class="card">
                <span class="badge">Live</span>
                <h2>📄 CV Matcher</h2>
                <p>AI-powered resume analysis and job matching. Upload CVs and job descriptions to get intelligent matching scores and recommendations.</p>
            </a>

            <a href="/privategpt/" class="card">
                <span class="badge coming">Coming Soon</span>
                <h2>🔒 PrivateGPT</h2>
                <p>Privacy-first document chat with local LLM. Upload documents and chat with your data without sending it to external APIs.</p>
            </a>

            <a href="/tellmelife/" class="card">
                <span class="badge coming">Coming Soon</span>
                <h2>📖 TellMeLife</h2>
                <p>AI-assisted life story creation. Transform memories and experiences into beautifully written narratives.</p>
            </a>
        </div>

        <div class="admin-link">
            <a href="/admin/">Admin Panel</a> |
            <a href="https://www.dabrock.eu">Personal Website</a>
        </div>
    </div>
</body>
</html>
EOF
```

### **Upload Landing Page:**

```bash
# Upload als index.html
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; put -O /dabrock-info/ dabrock-info-landing.html -o index.html"
```

---

## 🛠️ Schritt 4: Admin Panel deployen

### **Build & Deploy:**

```bash
cd /mnt/e/CodelocalLLM/GeneralBackend/admin-frontend

# .env für dabrock.info updaten
cat > .env <<EOF
VITE_API_URL=https://general-backend-production-a734.up.railway.app
EOF

# Build
npm install
npm run build

# .htaccess für SPA Routing erstellen
cat > dist/.htaccess <<'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /admin/
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /admin/index.html [L]
</IfModule>
EOF

# Upload zu dabrock-info/admin/
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mirror -R --delete --verbose dist /dabrock-info/admin/"
```

---

## 🎨 Schritt 5: CV Matcher deployen

### **Später, wenn CV Matcher fertig ist:**

```bash
cd /mnt/e/CodelocalLLM/CV_Matcher

# Build
npm run build

# .htaccess erstellen
cat > dist/.htaccess <<'EOF'
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /cv-matcher/
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /cv-matcher/index.html [L]
</IfModule>
EOF

# Upload
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mirror -R --delete --verbose dist /dabrock-info/cv-matcher/"
```

---

## ✅ Schritt 6: Testen

### **Nach Deployment:**

1. **Landing Page:** https://www.dabrock.info/
2. **Admin Panel:** https://www.dabrock.info/admin/
3. **CV Matcher:** https://www.dabrock.info/cv-matcher/ (später)

### **DNS Propagation:**

- Kann bis zu 24h dauern (meist 1-2h)
- Checken mit: https://www.whatsmydns.net/#A/www.dabrock.info

---

## 🔧 Backend CORS Update

### **Railway Backend muss dabrock.info erlauben:**

```bash
# Set environment variable
export RAILWAY_SERVICE_ID=cda654be-31ba-4076-b3fd-fe9189e3dc57

railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://www.dabrock.eu,http://localhost:5173"

# Restart backend
railway restart
```

---

## 📊 Finale Struktur

### **Nach vollständigem Setup:**

**Domains:**
- ✅ **www.dabrock.eu** → Persönliche Homepage
- ✅ **www.dabrock.info** → Showcase-Plattform

**www.dabrock.info URLs:**
- ✅ `/` → Landing Page (Showcase-Übersicht)
- ✅ `/admin/` → Admin Panel
- ✅ `/cv-matcher/` → CV Matcher App
- 🔜 `/privategpt/` → PrivateGPT App
- 🔜 `/tellmelife/` → TellMeLife App

**Backend:**
- ✅ Railway: https://general-backend-production-a734.up.railway.app
- ✅ CORS: dabrock.info + dabrock.eu erlaubt

---

## 🚨 Troubleshooting

### **"403 Forbidden" bei dabrock.info:**
```bash
# Permissions prüfen
ssh $SFTP_USER@$SFTP_HOST "chmod 755 /dabrock-info && chmod 755 /dabrock-info/*"
```

### **"Domain zeigt noch alte Seite":**
```bash
# Browser Cache leeren
# ODER: Private/Incognito Mode
# ODER: Warten (DNS Propagation)
```

### **"Admin Panel zeigt weiße Seite":**
```bash
# Browser Console öffnen (F12)
# Check: API URL korrekt?
# Check: CORS erlaubt?
```

---

## 📝 Deployment Checklist

- [ ] Strato: Domain `www.dabrock.info` auf `/dabrock-info/` zeigen lassen
- [ ] SSH: Verzeichnisse erstellen (`dabrock-info/admin`, etc.)
- [ ] Landing Page deployen (`index.html`)
- [ ] Admin Panel bauen & deployen
- [ ] Backend CORS updaten (Railway)
- [ ] Testen: https://www.dabrock.info/
- [ ] Testen: https://www.dabrock.info/admin/
- [ ] CV Matcher deployen (wenn fertig)

---

**Erstellt:** 22. Dezember 2025
**Status:** Ready for Deployment
