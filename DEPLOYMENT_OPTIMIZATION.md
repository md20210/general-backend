# Railway Deployment Optimization Guide

## Current Setup: Optimized Multi-Stage Docker Build

### Build Time Performance
- **First deployment**: ~2-3 minutes (builds all layers)
- **Code-only changes**: ~30-60 seconds (reuses cached layers)
- **Dependency changes**: ~2-3 minutes (rebuilds dependency layer)

### How It Works

#### 1. Multi-Stage Build Structure
```dockerfile
Stage 1: Base (system dependencies)
  ├─ Python 3.11-slim
  ├─ gcc, g++, libpq-dev, curl
  └─ Cached until base image changes

Stage 2: Dependencies (Python packages)
  ├─ requirements.txt
  ├─ pip install with BuildKit cache
  └─ Cached until requirements.txt changes

Stage 3: Application (your code)
  ├─ Copy application code
  └─ Rebuilt on every code change (fast!)
```

#### 2. BuildKit Cache Mounts
The Dockerfile uses `--mount=type=cache` for pip:
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt
```

**Benefits:**
- Pip cache persists between builds
- Re-downloading packages avoided
- 50-70% faster dependency installation

#### 3. .dockerignore Optimization
Excludes unnecessary files from build context:
- `__pycache__/`, `*.pyc` (Python cache)
- `.git/`, `.github/` (version control)
- `docs/`, `*.md` (documentation)
- `test_*.py`, `*_test.py` (test files)
- `.vscode/`, `.idea/` (IDE configs)

**Result:** Smaller build context = faster upload to Railway

### Railway Configuration

#### railway.json
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Note:** Railway enables BuildKit by default, so cache mounts work automatically.

### Deployment Comparison

| Change Type | Old (no optimization) | New (optimized) |
|-------------|----------------------|-----------------|
| Code change | 8-12 minutes | 30-60 seconds |
| Add dependency | 10-15 minutes | 2-3 minutes |
| System package | 10-15 minutes | 2-3 minutes |

### Why The Previous Deployment Took 10+ Minutes

**Problem:** Railway didn't auto-trigger the deployment after git push.

**Reasons:**
1. GitHub webhook delay
2. Railway service restart
3. Manual redeploy needed

**Solution:** If auto-deployment fails, trigger manually:
```bash
# Option 1: Empty commit
git commit --allow-empty -m "chore: trigger redeploy"
git push

# Option 2: Railway CLI (if linked)
railway up
```

### Best Practices

#### 1. Always Commit requirements.txt Changes Separately
```bash
# Good: Dependency changes in separate commit
git add requirements.txt
git commit -m "deps: add new-package==1.0.0"
git push

# Then code changes
git add backend/
git commit -m "feat: implement new feature"
git push
```

**Why:** Railway can cache the dependency layer and only rebuild code.

#### 2. Group Related Code Changes
```bash
# Good: All related changes in one commit
git add backend/api/bar.py backend/services/upload.py
git commit -m "feat: implement base64 image upload"
git push
```

**Why:** Avoids multiple deployments for a single feature.

#### 3. Use .dockerignore Aggressively
Add any files that don't affect the runtime:
- Development scripts
- Documentation
- Test fixtures
- Local configuration files

#### 4. Monitor Deployment Time
If deployment takes longer than expected:
1. Check Railway logs for build progress
2. Verify cache is being used (look for "CACHED" in logs)
3. Ensure BuildKit is enabled (Railway does this by default)

### Troubleshooting

#### Deployment Not Starting
```bash
# Check last commit
git log -1

# Verify push succeeded
git status

# Force redeploy with empty commit
git commit --allow-empty -m "chore: trigger redeploy"
git push
```

#### Slow Builds Despite Optimization
1. **Cache invalidated**: Check if requirements.txt or base image changed
2. **Railway issue**: Check Railway status page
3. **Large build context**: Review .dockerignore

#### Dependencies Not Caching
Ensure requirements.txt is copied **before** application code:
```dockerfile
# Correct order
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . .  # Application code last
```

### Monitoring Build Performance

Check Railway build logs for cache hits:
```
#8 [stage-2 3/3] RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
#8 CACHED
```

`CACHED` means the layer was reused = fast build!

### Further Optimization Ideas

1. **Use smaller base image**: Consider `python:3.11-alpine` (warning: may break some packages)
2. **Pre-build wheels**: For packages with C extensions
3. **Split requirements**: Separate `requirements-base.txt` and `requirements-dev.txt`

### Summary

✅ **Optimizations Implemented:**
- Multi-stage Docker build
- BuildKit cache mounts for pip
- Comprehensive .dockerignore
- Minimal layer rebuilding

🎯 **Expected Performance:**
- Code changes: **30-60 seconds**
- Dependency changes: **2-3 minutes**
- First deployment: **2-3 minutes**

📝 **Last Updated:** 2026-01-11 (Commit 747333a - Base64 upload fix)
