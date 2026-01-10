#!/bin/bash

# Run Alembic cleanup first
echo "🧹 Running Alembic cleanup..."
python cleanup_alembic.py

# Then start the backend normally
echo "🚀 Starting backend..."
exec python -m backend.main
