# Railway Volume Setup für LifeChronicle Photo Storage

## 🚨 Problem

Fotos werden hochgeladen, aber nach einem Railway-Redeploy sind sie weg!

**Ursache**: Railway Container sind ephemeral (flüchtig). Dateien gehen bei Redeployment verloren.

**Lösung**: Railway Persistent Volume konfigurieren

## ✅ WICHTIG: Base64 Storage läuft bereits!

**Aktueller Status**: Fotos werden als Base64 in DB gespeichert (funktioniert ohne Volume).

**Dieses Setup ist OPTIONAL** - nur für Production-Optimierung (schneller, kleinere DB).

Für MVP/Testing: **Base64 ist perfekt!**

---

## 📋 Railway Volume Setup (WICHTIG!)

### Schritt 1: Railway Dashboard öffnen

1. Gehe zu: https://railway.app/
2. Login mit deinem Account
3. Öffne Projekt: **GeneralBackend**
4. Klicke auf Service: **general-backend-production-a734**

### Schritt 2: Environment Variables setzen

**Tab: "Variables"** → **"+ New Variable"**

**Variable 1** (Volume Name):
```
Key:   RAILWAY_VOLUME_NAME
Value: lifechonicle-photos
```

**Variable 2** (Upload Directory):
```
Key:   UPLOAD_DIR
Value: /app/uploads
```

**Wichtig**:
- `RAILWAY_VOLUME_NAME` ist **service-specific**!
- Jeder Service kann seinen eigenen Wert haben:
  - Ollama: `ollama-models`
  - n8n: `n8n-data`
  - GeneralBackend: `lifechonicle-photos` ← NEU

**Railway erstellt Volume automatisch** basierend auf `RAILWAY_VOLUME_NAME`!

### Schritt 4: Redeploy

1. Tab: **"Deployments"**
2. Railway deployt automatisch nach Volume-Änderung
3. Warte ~2-3 Minuten
4. Status sollte: **"Success"** zeigen

---

## ✅ Verification

### Test 1: Health Check

```bash
curl https://general-backend-production-a734.up.railway.app/health
```

**Erwartete Antwort**:
```json
{"status":"healthy","database":"connected"}
```

### Test 2: Upload Photo

```bash
# Get token
TOKEN=$(curl -s https://general-backend-production-a734.up.railway.app/demo/token | jq -r .access_token)

# Create entry with photo
curl -X POST "https://general-backend-production-a734.up.railway.app/lifechronicle/entries" \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Volume Test" \
  -F "date=2025-12-26" \
  -F "text=Testing volume persistence" \
  -F "photos=@/path/to/your/photo.jpg"
```

### Test 3: Check if Photo is Accessible

```bash
# Get photo URL from response above, then:
curl -I https://general-backend-production-a734.up.railway.app/uploads/lifechronicle/PHOTO_ID.jpg
```

**Erwartete Antwort**:
```
HTTP/2 200
content-type: image/jpeg
```

### Test 4: Redeploy & Check Persistence

1. Trigger ein Redeploy (z.B. git push mit Dummy-Änderung)
2. Nach Deployment: Teste Photo URL nochmal
3. **Sollte immer noch 200 zurückgeben** (nicht 404)

---

## 🐛 Troubleshooting

### Problem: "404 Not Found" bei Photo-URLs

**Check 1**: Ist Volume gemounted?
```bash
# Railway Dashboard → Service → Variables → Volumes
# Sollte zeigen: /app/uploads
```

**Check 2**: Ist UPLOAD_DIR Environment Variable gesetzt?
```bash
# Railway Dashboard → Service → Variables
# Sollte zeigen: UPLOAD_DIR=/app/uploads
```

**Check 3**: Sind StaticFiles korrekt gemounted in Code?
```python
# backend/main.py sollte enthalten:
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
```

### Problem: "Permission Denied" beim Schreiben

Railway Volume hat manchmal Permission-Probleme. Fix:

```python
# backend/api/lifechronicle.py
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads/lifechronicle"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Set permissions (Railway-Container läuft als non-root)
try:
    os.chmod(UPLOAD_DIR, 0o755)
except Exception as e:
    logger.warning(f"Could not set permissions on {UPLOAD_DIR}: {e}")
```

### Problem: Volume ist voll

Railway Free Tier: **1 GB** Volume

**Check Volume Usage**:
```bash
# SSH in Railway Container (falls möglich):
du -sh /app/uploads
```

**Cleanup alte Fotos**:
```python
# Cleanup-Script (manuell ausführen via Railway Shell)
import os
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads/lifechronicle")
all_files = list(UPLOAD_DIR.glob("*.jpg")) + list(UPLOAD_DIR.glob("*.png"))

print(f"Total files: {len(all_files)}")
print(f"Total size: {sum(f.stat().st_size for f in all_files) / 1024 / 1024:.2f} MB")
```

---

## 🔐 Alternative: Cloud Storage (S3/R2)

Falls Railway Volume nicht ausreicht, verwende Cloud Storage:

### Option 1: Cloudflare R2 (empfohlen)

```bash
pip install boto3

# Environment Variables setzen:
R2_ACCESS_KEY_ID=xxx
R2_SECRET_ACCESS_KEY=yyy
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
R2_BUCKET_NAME=lifechonicle-photos
```

```python
# backend/services/storage.py
import boto3
from botocore.config import Config

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    config=Config(signature_version='s3v4')
)

def upload_photo(file_data, filename):
    s3_client.put_object(
        Bucket=os.getenv('R2_BUCKET_NAME'),
        Key=f"lifechronicle/{filename}",
        Body=file_data,
        ContentType='image/jpeg'
    )
    return f"https://pub-xxx.r2.dev/lifechronicle/{filename}"
```

**Kosten**: R2 Free Tier = 10 GB gratis

### Option 2: AWS S3

Gleicher Code wie R2, aber mit S3 Endpoint:
```
S3_ENDPOINT_URL=https://s3.eu-central-1.amazonaws.com
```

**Kosten**: S3 Free Tier = 5 GB für 12 Monate

---

## 📊 Railway Volume Dashboard

### Monitoring

Railway Dashboard zeigt:
- **Volume Size**: Aktuell genutzt vs. Limit
- **Last Updated**: Wann letztes File geschrieben wurde
- **Mount Status**: Mounted / Unmounted

### Backup

**Manueller Backup**:
```bash
# Von Railway Container (falls SSH möglich):
tar -czf /tmp/uploads_backup.tar.gz /app/uploads
# Dann downloaden via Railway CLI
```

**Automatischer Backup** (via Cron-Job im Backend):
```python
# backend/tasks/backup.py
import tarfile
import boto3
from datetime import datetime

def backup_uploads():
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"

    with tarfile.open(f"/tmp/{backup_name}", "w:gz") as tar:
        tar.add("/app/uploads")

    # Upload zu S3
    s3.upload_file(f"/tmp/{backup_name}", "backups-bucket", backup_name)
```

---

## ✅ Nach Setup: Nächste Schritte

1. **Volume Setup abgeschlossen** ✅
2. **Redeploy durchgeführt** ✅
3. **Photo-Upload getestet** ✅
4. **Photo-Access getestet** ✅

Dann weiter mit:
- Frontend: Fotos in Timeline anzeigen
- PDF: Fotos im Export

---

**Zuletzt aktualisiert**: 2025-12-26
**Railway Docs**: https://docs.railway.app/guides/volumes
