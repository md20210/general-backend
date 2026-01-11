# Multi-stage build with BuildKit cache mounts for faster deploys
# Build time: ~2-3 min (first), ~30-60 sec (subsequent code changes)
# IMPORTANT: Railway must have DOCKER_BUILDKIT=1 enabled

# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Dependencies layer (cached unless requirements.txt changes)
FROM base as dependencies

# Copy only requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies with BuildKit cache mount
# The cache mount persists pip cache between builds for faster reinstalls
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final application layer
FROM dependencies as application

# Copy application code
COPY . .

# Expose port (Railway sets PORT dynamically)
EXPOSE 8080

# No health check - Railway handles this
# Health checks with fixed ports don't work with dynamic PORT env var

# Start command (uses patch_and_start.py which handles bcrypt patch + migrations + uvicorn)
CMD ["python3", "patch_and_start.py"]
