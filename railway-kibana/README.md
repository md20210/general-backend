# Kibana Railway Deployment

This directory contains the configuration to deploy Kibana on Railway.

## Railway Setup Instructions

### 1. Create New Service in Railway

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Empty Service"**
3. Name it: `kibana`

### 2. Configure Service

**Settings → Environment Variables:**

```
ELASTICSEARCH_URL=http://elasticsearch.railway.internal:9200
```

**Important**: Replace `elasticsearch.railway.internal` with your actual Elasticsearch service name on Railway. Check your Elasticsearch service settings for the internal URL.

### 3. Deploy

**Option A: GitHub Deploy (Recommended)**

1. Connect this repository to Railway
2. Railway will automatically detect the `railway-kibana/Dockerfile`
3. Set **Root Directory** to `railway-kibana` in service settings
4. Deploy will trigger automatically

**Option B: Railway CLI Deploy**

```bash
cd /mnt/e/CodelocalLLM/GeneralBackend/railway-kibana
railway up
```

### 4. Configure Public URL

1. Go to **Settings → Networking**
2. Click **"Generate Domain"**
3. You'll get a public URL like: `kibana-production-xxxx.up.railway.app`

### 5. Access Kibana

1. Open the public URL in your browser
2. Kibana will take ~60 seconds to start
3. First-time setup will create `.kibana` index in Elasticsearch

## Post-Deployment Setup

### Create Index Pattern

1. Navigate to **Stack Management** → **Index Patterns**
2. Click **Create index pattern**
3. Index pattern name: `cv_rag_logs`
4. Time field: `timestamp`
5. Click **Create**

### Import Dashboard

1. Go to **Stack Management** → **Saved Objects**
2. Click **Import**
3. Upload file: `/mnt/e/CodelocalLLM/GeneralBackend/kibana_dashboards/rag_comparison_dashboard.ndjson`
4. Click **Import**

### View Dashboard

1. Navigate to **Dashboard**
2. Open: "RAG Comparison Dashboard - pgvector vs Elasticsearch"
3. Set time range to "Last 24 hours"
4. Enable auto-refresh (30 seconds)

## Troubleshooting

### Kibana won't start

**Check Elasticsearch URL:**
```bash
railway logs kibana
```

Look for: `Unable to connect to Elasticsearch`

**Fix**: Update `ELASTICSEARCH_URL` environment variable with correct internal URL

### "No index pattern found"

**Cause**: No data in `cv_rag_logs` index yet

**Fix**: Run some comparison queries through the frontend

### Dashboard import fails

**Cause**: Index pattern doesn't exist

**Fix**: Create index pattern first (see above)

## Configuration Files

- `Dockerfile` - Kibana Docker image configuration
- `kibana.yml` - Kibana settings (server, Elasticsearch connection)
- `railway.json` - Railway deployment configuration

## Health Check

Kibana exposes health check at: `/api/status`

Railway will automatically check this endpoint.

## Resources

- **Memory**: 512 MB minimum, 1 GB recommended
- **CPU**: 0.5 vCPU minimum
- **Startup time**: ~60 seconds
- **Port**: 5601

## Cost Estimate

Railway pricing (as of 2026):
- Free tier: $5 credit/month (enough for light usage)
- Hobby plan: $5/month base + usage
- Pro plan: $20/month base + usage

Kibana typically uses ~$2-5/month on Railway with light traffic.

## Security Notes

- Kibana is accessible via public URL (no authentication by default)
- Consider enabling Elasticsearch security features for production
- Railway's private network keeps Elasticsearch internal
- Use Railway's domain allowlisting if needed

## Alternative: Railway Template

Railway might add Kibana template in the future. Check:
https://railway.app/templates

Currently not available, so manual deployment required.
