# Admin Frontend - Deployment zu Strato (www.dabrock.info)

## 📋 Voraussetzungen

- ✅ Backend deployed auf Railway
- ✅ Railway URL bekannt (z.B. `https://your-app.railway.app`)
- ✅ Strato SFTP Zugangsdaten

## 🔧 Schritt 1: Environment konfigurieren

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend/admin-frontend

# .env für Production erstellen
cat > .env <<EOF
VITE_API_URL=https://your-railway-url.railway.app
EOF

# WICHTIG: Ersetze "your-railway-url" mit deiner echten Railway URL!
```

## 📦 Schritt 2: Dependencies installieren & Build

```bash
# Node Modules installieren
npm install

# Production Build erstellen
npm run build

# dist/ Verzeichnis sollte jetzt existieren mit:
# - index.html
# - assets/
# - vite.svg
```

## 🌐 Schritt 3: Zu Strato deployen

### Option A: Via LFTP (empfohlen)

```bash
# SFTP Credentials setzen
export SFTP_USER="su403214"
export SFTP_PASS="dein-sftp-passwort"
export SFTP_HOST="5018735097.ssh.w2.strato.hosting"

# Upload mit lftp
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mirror -R --delete --verbose dist /htdocs/admin/"

# Erklärt:
# -R = Upload (Reverse mirror)
# --delete = Lösche alte Dateien auf Server
# --verbose = Zeige Progress
# dist/ = Lokales Verzeichnis
# /htdocs/admin/ = Zielverzeichnis auf Strato
```

### Option B: Via FileZilla

1. FileZilla öffnen
2. Verbindung:
   - **Host:** `sftp://5018735097.ssh.w2.strato.hosting`
   - **User:** `su403214`
   - **Password:** Dein SFTP Passwort
   - **Port:** 22
3. Verbinden
4. Lokal: Navigiere zu `dist/`
5. Server: Navigiere zu `/htdocs/admin/`
6. Drag & Drop alle Dateien aus `dist/` nach `/htdocs/admin/`

### Option C: Via SCP

```bash
scp -r dist/* su403214@5018735097.ssh.w2.strato.hosting:/htdocs/admin/
```

## 🔐 Schritt 4: .htaccess für SPA Routing (wichtig!)

React Router braucht ein .htaccess File für korrekte URL-Behandlung:

```bash
# Erstelle .htaccess lokal
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

# Upload auch das .htaccess
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; put -O /htdocs/admin/ dist/.htaccess"
```

## ✅ Schritt 5: Testen

1. **Öffne:** https://www.dabrock.info/admin
2. **Login mit Admin Credentials**
3. **Check:**
   - ✅ Dashboard lädt
   - ✅ Users Management (Admin only)
   - ✅ LLM Config (Admin only)
   - ✅ System Stats (Admin only)

## 🔄 Updates deployen

Bei jeder Änderung am Frontend:

```bash
cd /mnt/e/CodeLocalLLM/GeneralBackend/admin-frontend

# Code ändern, dann:
npm run build

# Upload zu Strato
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; mirror -R --delete --verbose dist /htdocs/admin/"
```

## 📂 Finale Dateistruktur auf Strato

```
/htdocs/
├── admin/                     # Admin Panel
│   ├── index.html
│   ├── .htaccess             # SPA Routing
│   ├── assets/
│   │   ├── index-xxx.js
│   │   └── index-xxx.css
│   └── vite.svg
└── ... (andere Dateien)
```

## 🐛 Troubleshooting

**"Failed to fetch" beim Login:**
```bash
# Check API URL in .env
cat .env
# Sollte sein: VITE_API_URL=https://your-railway-url.railway.app

# Rebuild
npm run build
# Re-upload
```

**"404 Not Found" beim Navigieren:**
```bash
# .htaccess fehlt oder falsch
# Prüfe ob .htaccess auf Server existiert:
lftp -c "open -u $SFTP_USER,$SFTP_PASS sftp://$SFTP_HOST; ls /htdocs/admin/.htaccess"

# Falls nicht vorhanden, upload erneut
```

**CORS Error:**
```bash
# Backend ALLOWED_ORIGINS prüfen
railway variables
# Sollte enthalten: https://www.dabrock.info

# Falls nicht:
railway variables set ALLOWED_ORIGINS="https://www.dabrock.info,https://api.dabrock.info"
railway restart
```

**Seite lädt aber zeigt nur weißen Bildschirm:**
```bash
# Browser Console öffnen (F12)
# Check Fehler
# Meist: API URL falsch in .env

# Fix:
# 1. .env korrigieren
# 2. npm run build
# 3. Re-upload
```

## 📊 Deployment Checklist

- [ ] Backend auf Railway deployed
- [ ] Railway URL in `.env` gesetzt
- [ ] `npm install` ausgeführt
- [ ] `npm run build` erfolgreich
- [ ] `dist/` Verzeichnis erstellt
- [ ] `.htaccess` in `dist/` erstellt
- [ ] Zu Strato uploaded (lftp/FileZilla)
- [ ] `.htaccess` uploaded
- [ ] https://www.dabrock.info/admin öffnet
- [ ] Login funktioniert
- [ ] Alle Features getestet

## 🎉 Fertig!

Admin Panel ist jetzt live auf:
- **URL:** https://www.dabrock.info/admin
- **API:** https://your-railway-url.railway.app (oder api.dabrock.info)

**Features:**
- ✅ Secure Login
- ✅ Dashboard mit Stats
- ✅ User Management
- ✅ LLM Configuration & Testing
- ✅ System Statistics
- ✅ Dark Mode Design
