#!/bin/bash
# Test authentication API endpoints

API_BASE="http://localhost:8000"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="testpass123"

echo "=== Testing Authentication API ==="
echo ""

# Test 1: Register new user
echo "1. Testing POST /auth/register"
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"

# Extract token
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "✅ Registration successful, token received"
else
    echo "❌ Registration failed"
    exit 1
fi

echo ""
echo "2. Testing GET /auth/me (with token)"
curl -s "$API_BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "3. Testing POST /auth/login"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

echo "$LOGIN_RESPONSE" | python3 -m json.tool

NEW_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$NEW_TOKEN" ]; then
    echo "✅ Login successful"
else
    echo "❌ Login failed"
    exit 1
fi

echo ""
echo "4. Testing POST /auth/login (wrong password)"
WRONG_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"wrongpassword\"}")

HTTP_CODE=$(echo "$WRONG_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ Correctly rejected wrong password"
else
    echo "❌ Should have rejected wrong password"
fi

echo ""
echo "5. Testing POST /auth/logout"
curl -s -X POST "$API_BASE/auth/logout" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "6. Testing protected endpoint without token"
NO_AUTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$API_BASE/admin/devices/all")
HTTP_CODE=$(echo "$NO_AUTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ]; then
    echo "✅ Protected endpoint correctly requires authentication"
else
    echo "⚠️  Warning: Protected endpoint may not require authentication (HTTP $HTTP_CODE)"
fi

echo ""
echo "=== Authentication Tests Complete ==="

