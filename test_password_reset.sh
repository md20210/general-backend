#!/bin/bash
echo "⏳ Warte auf Railway-Deployment..."
sleep 120

echo ""
echo "🧪 Teste Passwort-Reset-Anfrage..."
RESPONSE=$(timeout 10 curl -s -X POST \
  "https://general-backend-production-a734.up.railway.app/api/mvp-auth/password-reset-request" \
  -H "Content-Type: application/json" \
  -d '{"email":"michael.dabrock@gmx.es"}')

echo "Response: $RESPONSE"
echo ""
echo "✅ Anfrage gesendet!"
echo "📧 Prüfen Sie Ihr E-Mail-Postfach: michael.dabrock@gmx.es"
echo "   (Auch Spam-Ordner prüfen!)"
echo ""
echo "Absender: onboarding@resend.dev"
