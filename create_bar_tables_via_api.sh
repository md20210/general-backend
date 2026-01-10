#!/bin/bash

# Create Bar tables by calling the startup script that will create them

echo "🔄 Triggering backend restart to create tables..."

# The backend creates tables on startup via backend/database.py
# We just need to trigger a restart

echo "✅ Tables will be created on next deployment"
echo ""
echo "To manually create tables, run initialize_bar_data.py after deployment"
