#!/bin/bash

# General Backend - Complete API Test Suite
# Tests all endpoints with realistic data

set -e

API_URL="https://general-backend-production-a734.up.railway.app"
TEST_EMAIL="testuser-$(date +%s)@example.com"
TEST_PASSWORD="SecureTestPassword123!"
TOKEN=""
USER_ID=""
PROJECT_ID=""
DOCUMENT_ID=""

echo "=================================="
echo "General Backend API Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_passed() {
    echo -e "${GREEN}✓ PASSED:${NC} $1"
}

test_failed() {
    echo -e "${RED}✗ FAILED:${NC} $1"
    echo "Response: $2"
}

# ==========================================
# 1. Health Check
# ==========================================
echo "1. Testing Health Check..."
RESPONSE=$(curl -s -X GET "$API_URL/health")
if echo "$RESPONSE" | grep -q "healthy"; then
    test_passed "Health check"
else
    test_failed "Health check" "$RESPONSE"
fi
echo ""

# ==========================================
# 2. User Registration
# ==========================================
echo "2. Testing User Registration..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"is_active\": true,
    \"is_superuser\": false,
    \"is_verified\": false,
    \"is_admin\": false
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ]; then
    USER_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    test_passed "User registration (HTTP 201)"
    echo "   User ID: $USER_ID"
else
    test_failed "User registration (Expected 201, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 3. User Login
# ==========================================
echo "3. Testing User Login..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    TOKEN=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    test_passed "User login (HTTP 200)"
    echo "   Token: ${TOKEN:0:50}..."
else
    test_failed "User login (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 4. Get Current User
# ==========================================
echo "4. Testing Get Current User..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "Get current user (HTTP 200)"
else
    test_failed "Get current user (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 5. List LLM Models
# ==========================================
echo "5. Testing List LLM Models..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/llm/models?provider=ollama" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "List LLM models (HTTP 200)"
    echo "$BODY" | python3 -m json.tool
else
    test_failed "List LLM models (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 6. Generate Text with Ollama (llama3.2:3b)
# ==========================================
echo "6. Testing LLM Text Generation (Ollama - llama3.2:3b)..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/llm/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to add two numbers. Just code, no explanation.",
    "provider": "ollama",
    "temperature": 0.3,
    "max_tokens": 200
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "LLM text generation - Ollama (HTTP 200)"
    echo "$BODY" | python3 -m json.tool
else
    test_failed "LLM text generation - Ollama (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 7. Create Project
# ==========================================
echo "7. Testing Create Project..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CV Matcher Project",
    "description": "Test project for API testing",
    "type": "cv_matcher",
    "config": {
      "llm_provider": "ollama",
      "embedding_model": "nomic-embed-text"
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ]; then
    PROJECT_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    test_passed "Create project (HTTP 201)"
    echo "   Project ID: $PROJECT_ID"
else
    test_failed "Create project (Expected 201, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 8. List Projects
# ==========================================
echo "8. Testing List Projects..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/projects" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "List projects (HTTP 200)"
else
    test_failed "List projects (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 9. Get Project by ID
# ==========================================
echo "9. Testing Get Project by ID..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "Get project by ID (HTTP 200)"
else
    test_failed "Get project by ID (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 10. Create Text Document
# ==========================================
echo "10. Testing Create Text Document..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/documents/text" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Resume\",
    \"content\": \"John Doe - Senior Python Developer with 5 years experience in FastAPI, PostgreSQL, and Docker. Expert in backend development and microservices.\",
    \"project_id\": \"$PROJECT_ID\",
    \"metadata\": {
      \"category\": \"resume\",
      \"candidate\": \"John Doe\"
    }
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ]; then
    DOCUMENT_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    test_passed "Create text document (HTTP 201)"
    echo "   Document ID: $DOCUMENT_ID"
else
    test_failed "Create text document (Expected 201, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 11. List Documents
# ==========================================
echo "11. Testing List Documents..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/documents?project_id=$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "List documents (HTTP 200)"
else
    test_failed "List documents (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 12. Get Document by ID
# ==========================================
echo "12. Testing Get Document by ID..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/documents/$DOCUMENT_ID" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "Get document by ID (HTTP 200)"
else
    test_failed "Get document by ID (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 13. Search Documents (Semantic Search)
# ==========================================
echo "13. Testing Semantic Document Search..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/documents/search?query=Python+developer&project_id=$PROJECT_ID&limit=5" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "Semantic document search (HTTP 200)"
    echo "$BODY" | python3 -m json.tool
else
    test_failed "Semantic document search (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 14. Update Project
# ==========================================
echo "14. Testing Update Project..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH "$API_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated test project description"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    test_passed "Update project (HTTP 200)"
else
    test_failed "Update project (Expected 200, got $HTTP_CODE)" "$BODY"
fi
echo ""

# ==========================================
# 15. Delete Document
# ==========================================
echo "15. Testing Delete Document..."
HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE "$API_URL/documents/$DOCUMENT_ID" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" = "204" ]; then
    test_passed "Delete document (HTTP 204)"
else
    test_failed "Delete document (Expected 204, got $HTTP_CODE)" ""
fi
echo ""

# ==========================================
# 16. Delete Project
# ==========================================
echo "16. Testing Delete Project..."
HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE "$API_URL/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" = "204" ]; then
    test_passed "Delete project (HTTP 204)"
else
    test_failed "Delete project (Expected 204, got $HTTP_CODE)" ""
fi
echo ""

# ==========================================
# 17. Logout
# ==========================================
echo "17. Testing Logout..."
HTTP_CODE=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/auth/logout" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" = "204" ]; then
    test_passed "Logout (HTTP 204)"
else
    test_failed "Logout (Expected 204, got $HTTP_CODE)" ""
fi
echo ""

echo "=================================="
echo "All API tests completed!"
echo "=================================="
