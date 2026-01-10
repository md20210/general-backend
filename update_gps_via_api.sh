#!/bin/bash

# Update GPS coordinates for Bar Ca l'Elena via API
# GPS: 41°21'40.7"N 2°06'59.0"E = 41.361305556, 2.116388889

API_URL="https://general-backend-production-a734.up.railway.app"

echo "📍 Updating GPS coordinates via API..."
echo "   GPS: 41°21'40.7\"N 2°06'59.0\"E"
echo "   Decimal: 41.361305556, 2.116388889"
echo ""

# Get admin token
echo "🔑 Getting admin token..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senior"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get admin token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Token received"
echo ""

# Update bar info with correct GPS
echo "🔄 Updating bar info..."
UPDATE_RESPONSE=$(curl -s -X PUT "$API_URL/bar/admin/info" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Ca l'\''Elena",
    "location_lat": "41.361305556",
    "location_lng": "2.116388889"
  }')

echo "Response: $UPDATE_RESPONSE"
echo ""

# Verify update
echo "🔍 Verifying GPS update..."
VERIFY_RESPONSE=$(curl -s "$API_URL/bar/info")
LAT=$(echo $VERIFY_RESPONSE | grep -o '"location_lat":"[^"]*' | sed 's/"location_lat":"//')
LNG=$(echo $VERIFY_RESPONSE | grep -o '"location_lng":"[^"]*' | sed 's/"location_lng":"//')

echo "Current GPS: lat=$LAT, lng=$LNG"
echo ""

if [ "$LAT" = "41.361305556" ] && [ "$LNG" = "2.116388889" ]; then
  echo "✅ GPS coordinates updated successfully!"
else
  echo "⚠️  GPS coordinates don't match expected values"
fi
