# Ollama Service for Railway

GDPR-compliant local LLM service running on Railway.

## Features
- 🇪🇺 **GDPR Compliant** - Data stays in your infrastructure
- 🚀 **CPU-Optimized** - Uses llama3.2:3b (3 billion parameters)
- 🔒 **Private Networking** - Only accessible by backend service
- ⚡ **Fast** - Small model, quick inference even on CPU

## Model
- **llama3.2:3b** - Meta's latest small model
  - Size: ~2GB
  - Parameters: 3 billion
  - Quality: Good for most tasks
  - Speed: Fast on CPU

## Deployment

1. Create new service in Railway
2. Connect this directory
3. Service will auto-pull llama3.2:3b on first start
4. Connect to backend via private networking

## Environment Variables

None required - all configured in Dockerfile

## API Endpoint

Internal: `http://ollama.railway.internal:11434`

## Testing

```bash
curl http://ollama.railway.internal:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Why is the sky blue?"
}'
```

## Upgrade Path

When Railway adds GPU support:
- Switch to larger models (llama3.1:70b, etc.)
- Better performance
- Same API, no code changes needed!
