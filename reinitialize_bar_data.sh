#!/bin/bash
# Script to reinitialize bar data with multilingual reviews
# This will update the database with the new multilingual structure

API_URL="https://general-backend-production-a734.up.railway.app"
ADMIN_USER="admin"
ADMIN_PASS="senior"

echo "Step 1: Logging in to get access token..."
TOKEN_RESPONSE=$(curl -s -X POST "${API_URL}/bar/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_USER}\",\"password\":\"${ADMIN_PASS}\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: Failed to get access token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Login successful!"
echo ""
echo "Step 2: Reinitializing bar data with multilingual reviews..."
REINIT_RESPONSE=$(curl -s -X POST "${API_URL}/bar/admin/reinitialize-data" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$REINIT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REINIT_RESPONSE"
echo ""
echo "✅ Bar data reinitialized with multilingual reviews!"
echo ""
echo "Please refresh your website to see the changes."
