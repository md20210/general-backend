#!/bin/bash
echo "⏳ Warte auf Railway-Deployment des Login-Endpoints..."
for i in {1..40}; do
  sleep 5
  RESPONSE=$(timeout 10 curl -s -X POST "https://general-backend-production-a734.up.railway.app/api/mvp-auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"michael.dabrock@gmx.es","password":"test123"}' 2>&1)

  if echo "$RESPONSE" | grep -q "Not Found"; then
    printf "⏳ Versuch $i/40: Endpoint noch nicht deployed...\r"
  elif echo "$RESPONSE" | grep -q "logged_in"; then
    echo ""
    echo "✅ Login erfolgreich!"
    echo "$RESPONSE"
    exit 0
  elif echo "$RESPONSE" | grep -q "User not found\|Invalid password"; then
    echo ""
    echo "✅ Login-Endpoint deployed (Credentials falsch - erwartet)"
    echo "$RESPONSE"
    exit 0
  else
    echo ""
    echo "Versuch $i/40: Unerwartete Antwort:"
    echo "$RESPONSE"
  fi
done
echo ""
echo "⚠️ Timeout nach 40 Versuchen"
