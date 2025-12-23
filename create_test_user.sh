#!/bin/bash
API_URL="https://general-backend-production-a734.up.railway.app"
TEST_EMAIL="test@dabrock.info"
TEST_PASSWORD="Test123Secure"

echo "Creating test user..."
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"is_active\": true}" | python3 -m json.tool

echo ""
echo "Login Credentials:"
echo "Email: $TEST_EMAIL"
echo "Password: $TEST_PASSWORD"
