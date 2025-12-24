#!/bin/bash
# General Backend - Comprehensive API Test Suite
# Run this after deployment to verify all endpoints

BASE_URL="https://general-backend-production-a734.up.railway.app"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==============================================="
echo "  🚀 General Backend - API Test Suite"
echo "  📅 $(date)"
echo "  🌐 $BASE_URL"
echo "==============================================="
echo ""

# Test counters
TOTAL=0
PASSED=0
FAILED=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local show_response="${4:-false}"

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $name... "

    response=$(curl -s -w "\n%{http_code}" -m 10 "$url" 2>/dev/null)
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        if [ "$show_response" = "true" ] && [ -n "$body" ]; then
            echo "    📄 $(echo "$body" | head -c 100)..."
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
        FAILED=$((FAILED + 1))
        echo "    ⚠️  $body"
    fi
}

# Core Endpoints
echo -e "${BLUE}=== 🏥 Core Endpoints ===${NC}"
test_endpoint "Health Check" "$BASE_URL/health" 200 true
test_endpoint "Root Endpoint" "$BASE_URL/" 200
test_endpoint "OpenAPI Spec" "$BASE_URL/openapi.json" 200
test_endpoint "Swagger UI" "$BASE_URL/docs" 200

# Translation Endpoints
echo ""
echo -e "${BLUE}=== 🌍 Translation Endpoints ===${NC}"
test_endpoint "Translations DE" "$BASE_URL/translations/de" 200
test_endpoint "Translations EN" "$BASE_URL/translations/en" 200
test_endpoint "Translations ES" "$BASE_URL/translations/es" 200
test_endpoint "Translation Key (app_title)" "$BASE_URL/translations/key/app_title?language=de" 200 true
test_endpoint "Translation Key (privategxt_title)" "$BASE_URL/translations/key/privategxt_title?language=de" 200 true

# PrivateGxT Endpoints
echo ""
echo -e "${BLUE}=== 📚 PrivateGxT Endpoints ===${NC}"
test_endpoint "Stats" "$BASE_URL/privategxt/stats" 200 true
test_endpoint "Documents List" "$BASE_URL/privategxt/documents" 200
test_endpoint "Chat History" "$BASE_URL/privategxt/chat/history" 200

# Crawler Endpoints
echo ""
echo -e "${BLUE}=== 🕷️  Crawler Endpoints ===${NC}"
test_endpoint "Crawler Health" "$BASE_URL/crawler/health" 200 true

# Protected Endpoints (should return 401)
echo ""
echo -e "${BLUE}=== 🔒 Protected Endpoints (Expect 401) ===${NC}"
test_endpoint "LLM Models" "$BASE_URL/llm/models" 401
test_endpoint "Documents List" "$BASE_URL/documents" 401
test_endpoint "Projects List" "$BASE_URL/projects" 401
test_endpoint "Admin Stats" "$BASE_URL/admin/stats" 401
test_endpoint "Current User" "$BASE_URL/users/me" 401

# Summary
echo ""
echo "==============================================="
echo "  📊 Test Summary"
echo "==============================================="
echo -e "Total Tests:  $TOTAL"
if [ $PASSED -gt 0 ]; then
    echo -e "${GREEN}✓ Passed:     $PASSED${NC}"
else
    echo -e "✓ Passed:     $PASSED"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed:     $FAILED${NC}"
else
    echo -e "✗ Failed:     $FAILED"
fi
echo -e "Success Rate: $((PASSED * 100 / TOTAL))%"
echo "==============================================="

# Detailed translation stats
if [ $PASSED -gt 0 ]; then
    echo ""
    echo -e "${BLUE}=== 📈 Translation Statistics ===${NC}"
    curl -s "$BASE_URL/translations/de" | python3 << 'PYEOF'
import sys, json
try:
    data = json.load(sys.stdin)
    trans = data.get('translations', {})

    print(f"\n  Total Translation Keys: {len(trans)}")

    # Count by prefix
    prefixes = {}
    for key in trans.keys():
        prefix = key.split('_')[0]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1

    print(f"\n  Top Prefixes:")
    for prefix, count in sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f"    {prefix:15} {count:3} keys")

    # Sample translations
    print(f"\n  Sample Translations (German):")
    samples = {
        'app_title': 'CV Matcher app title',
        'nav_about': 'Homepage navigation',
        'privategxt_title': 'PrivateGxT showcase',
        'upload_title': 'PrivateGxT upload',
        'hero_title': 'Homepage hero'
    }
    for key, desc in samples.items():
        value = trans.get(key, 'NOT FOUND')
        if len(value) > 40:
            value = value[:40] + "..."
        print(f"    {key:20} → {value}")

except Exception as e:
    print(f"  Error analyzing translations: {e}")
PYEOF
fi

echo ""
echo "✅ Test suite completed!"
