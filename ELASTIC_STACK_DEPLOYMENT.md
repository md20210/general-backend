# Elastic Stack Deployment auf Railway

## 🎯 Übersicht

Deployen von **Logstash** und **Kibana** als separate Services auf Railway.

**Aktuelle Services:**
- ✅ `general-backend` (FastAPI)
- ✅ `postgres` (PostgreSQL)
- ✅ `elasticsearch` (Elasticsearch)
- ➕ `logstash` (neu)
- ➕ `kibana` (neu)

---

## 📋 Schritt 1: Logstash Service erstellen

### Railway UI:

1. **Öffne dein Railway Project**
   - https://railway.app/project/your-project-id

2. **Neuen Service erstellen**
   - Click "+ New Service"
   - Select "GitHub Repo"
   - Wähle `md20210/general-backend`

3. **Service Konfiguration**
   - **Name:** `logstash`
   - **Root Directory:** `/logstash`
   - **Build Command:** (automatic via Dockerfile)
   - **Start Command:** `logstash`

4. **Environment Variables**
   ```
   ELASTICSEARCH_HOST=elasticsearch.railway.internal:9200
   LS_JAVA_OPTS=-Xmx1g -Xms1g
   ```

5. **Deploy**
   - Click "Deploy"
   - Warte ~5 Min auf Build

### Railway CLI (Alternative):

```bash
cd /mnt/e/CodelocalLLM/GeneralBackend
railway link  # Link to existing project
railway service create logstash
railway service set-root logstash
railway variables set ELASTICSEARCH_HOST=elasticsearch.railway.internal:9200
railway up
```

---

## 📋 Schritt 2: Kibana Service erstellen

### Railway UI:

1. **Neuen Service erstellen**
   - Click "+ New Service"
   - Select "GitHub Repo"
   - Wähle `md20210/general-backend`

2. **Service Konfiguration**
   - **Name:** `kibana`
   - **Root Directory:** `/kibana`
   - **Build Command:** (automatic via Dockerfile)
   - **Start Command:** `kibana`

3. **Environment Variables**
   ```
   ELASTICSEARCH_HOSTS=http://elasticsearch.railway.internal:9200
   ELASTIC_PASSWORD=changeme
   KIBANA_PUBLIC_URL=https://kibana-production.up.railway.app
   ```

4. **Public Domain**
   - Settings → Networking → Generate Domain
   - Notiere die URL (z.B. `https://kibana-production-xxx.up.railway.app`)

5. **Deploy**
   - Click "Deploy"
   - Warte ~5 Min

### Railway CLI (Alternative):

```bash
railway service create kibana
railway service set-root kibana
railway variables set ELASTICSEARCH_HOSTS=http://elasticsearch.railway.internal:9200
railway variables set ELASTIC_PASSWORD=changeme
railway up
```

---

## 🔌 Schritt 3: Service Connections

### Interne Railway Networking:

Railway Services können sich über interne DNS Namen erreichen:

```
elasticsearch.railway.internal:9200  ← Elasticsearch
logstash.railway.internal:8080       ← Logstash CV Pipeline
logstash.railway.internal:8081       ← Logstash Job Pipeline
logstash.railway.internal:8082       ← Logstash Enrichment
kibana.railway.internal:5601         ← Kibana
```

### Externe URLs (nach Deployment):

```
https://general-backend-production-a734.up.railway.app  ← FastAPI
https://logstash-production-xxx.up.railway.app         ← Logstash
https://kibana-production-xxx.up.railway.app           ← Kibana
```

---

## ✅ Verification

### 1. Check Logstash

```bash
curl https://logstash-production-xxx.up.railway.app/_node/stats
```

### 2. Check Kibana

Öffne im Browser:
```
https://kibana-production-xxx.up.railway.app
```

### 3. Check Elasticsearch Connection from Kibana

Kibana UI → Management → Stack Management → Index Management

---

## 🧪 Test Logstash Pipelines

### CV Parsing Pipeline:

```bash
curl -X POST https://logstash-production-xxx.up.railway.app:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "cv_text": "Senior Python Developer with 5 years experience. Skills: Python, Django, PostgreSQL, Docker, AWS."
  }'
```

### Job Parsing Pipeline:

```bash
curl -X POST https://logstash-production-xxx.up.railway.app:8081 \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test-job",
    "job_description": "Company: Elastic. Location: Barcelona. Remote: Hybrid. Required: 3+ years Python, Elasticsearch experience."
  }'
```

---

## 🚨 Troubleshooting

### Logs checken:

```bash
railway logs --service logstash
railway logs --service kibana
```

### Health Checks:

```bash
# Logstash
curl https://logstash-production-xxx.up.railway.app/_node/stats

# Kibana
curl https://kibana-production-xxx.up.railway.app/api/status
```

### Common Issues:

1. **Elasticsearch Connection Failed**
   - Check `ELASTICSEARCH_HOST` env var
   - Verify Elasticsearch is running
   - Check Railway internal networking

2. **Logstash OOM (Out of Memory)**
   - Increase `LS_JAVA_OPTS`: `-Xmx2g -Xms2g`
   - Railway free tier: 512MB-1GB RAM limit

3. **Kibana won't start**
   - Check Elasticsearch is accessible
   - Verify `ELASTIC_PASSWORD` matches
   - Check logs for errors

---

## 📊 Next Steps

Nach erfolgreichem Deployment:

1. ✅ Backend Endpoints für Logstash Integration
2. ✅ Demo-Daten Generator (Analyse × 100)
3. ✅ Frontend "Results Elastic" Tab
4. ✅ Kibana Dashboards erstellen

---

## 💡 Production Considerations

Für Production Deployment:

- [ ] Enable Elasticsearch security (x-pack)
- [ ] Set strong `ELASTIC_PASSWORD`
- [ ] Configure Kibana authentication
- [ ] Set up SSL/TLS certificates
- [ ] Enable monitoring & alerting
- [ ] Configure backup strategies
- [ ] Set resource limits appropriately
