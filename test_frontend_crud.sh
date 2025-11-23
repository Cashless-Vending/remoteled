#!/bin/bash

# Comprehensive Frontend CRUD Test
# Simulates user actions from the browser

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

BASE_URL="http://localhost:8000"
TIMESTAMP=$(date +%s)

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║   RemoteLED - Comprehensive Frontend CRUD Test Suite     ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Login
echo -e "${BLUE}📝 Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@remoteled.com","password":"password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}✗ Login failed${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Login successful${NC}\n"

# Test counters
PASS=0
FAIL=0

# Test Device Models CRUD
echo -e "${BOLD}${BLUE}═══ Device Models CRUD ═══${NC}"

# CREATE
MODEL_NAME="Frontend Test Model ${TIMESTAMP}"
echo -e "${BLUE}→ Creating device model: ${MODEL_NAME}${NC}"
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/admin/device-models" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${MODEL_NAME}\",\"description\":\"Created via frontend test\"}")
HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
  MODEL_ID=$(echo $RESPONSE_BODY | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo -e "${GREEN}  ✓ CREATE: Success (201) - ID: ${MODEL_ID}${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ CREATE: Failed (${HTTP_CODE})${NC}"
  echo -e "${YELLOW}    Response: ${RESPONSE_BODY}${NC}"
  ((FAIL++))
  MODEL_ID=""
fi

# READ
echo -e "${BLUE}→ Reading all device models${NC}"
READ_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/admin/device-models" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$READ_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}  ✓ READ: Success (200)${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ READ: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# UPDATE
if [ ! -z "$MODEL_ID" ]; then
  echo -e "${BLUE}→ Updating device model${NC}"
  UPDATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${BASE_URL}/admin/device-models/${MODEL_ID}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"description":"UPDATED via frontend test"}')
  HTTP_CODE=$(echo "$UPDATE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ UPDATE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ UPDATE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
  
  # DELETE
  echo -e "${BLUE}→ Deleting device model${NC}"
  DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/admin/device-models/${MODEL_ID}" \
    -H "Authorization: Bearer $TOKEN")
  HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ DELETE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ DELETE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
fi

# Test Locations CRUD
echo -e "\n${BOLD}${BLUE}═══ Locations CRUD ═══${NC}"

# CREATE
LOCATION_NAME="Frontend Test Location ${TIMESTAMP}"
echo -e "${BLUE}→ Creating location: ${LOCATION_NAME}${NC}"
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/admin/locations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${LOCATION_NAME}\",\"description\":\"Created via frontend test\"}")
HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
  LOCATION_ID=$(echo $RESPONSE_BODY | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo -e "${GREEN}  ✓ CREATE: Success (201) - ID: ${LOCATION_ID}${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ CREATE: Failed (${HTTP_CODE})${NC}"
  echo -e "${YELLOW}    Response: ${RESPONSE_BODY}${NC}"
  ((FAIL++))
  LOCATION_ID=""
fi

# READ
echo -e "${BLUE}→ Reading all locations${NC}"
READ_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/admin/locations" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$READ_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}  ✓ READ: Success (200)${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ READ: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# UPDATE
if [ ! -z "$LOCATION_ID" ]; then
  echo -e "${BLUE}→ Updating location${NC}"
  UPDATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${BASE_URL}/admin/locations/${LOCATION_ID}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"description":"UPDATED via frontend test"}')
  HTTP_CODE=$(echo "$UPDATE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ UPDATE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ UPDATE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
  
  # DELETE
  echo -e "${BLUE}→ Deleting location${NC}"
  DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/admin/locations/${LOCATION_ID}" \
    -H "Authorization: Bearer $TOKEN")
  HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ DELETE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ DELETE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
fi

# Test Service Types READ (CREATE only works with enum values)
echo -e "\n${BOLD}${BLUE}═══ Service Types ═══${NC}"
echo -e "${BLUE}→ Reading all service types${NC}"
READ_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/admin/service-types" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$READ_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}  ✓ READ: Success (200)${NC}"
  echo -e "${YELLOW}  ℹ Note: Service type codes must be TRIGGER, FIXED, or VARIABLE${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ READ: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# Test Services CRUD
echo -e "\n${BOLD}${BLUE}═══ Services CRUD ═══${NC}"

# CREATE
echo -e "${BLUE}→ Creating service (TRIGGER type)${NC}"
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/admin/services" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"TRIGGER","price_cents":100,"active":true}')
HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  SERVICE_ID=$(echo $RESPONSE_BODY | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo -e "${GREEN}  ✓ CREATE: Success (200) - ID: ${SERVICE_ID}${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ CREATE: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
  SERVICE_ID=""
fi

# READ
echo -e "${BLUE}→ Reading all services${NC}"
READ_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/admin/services/all" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$READ_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}  ✓ READ: Success (200)${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ READ: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# UPDATE
if [ ! -z "$SERVICE_ID" ]; then
  echo -e "${BLUE}→ Updating service${NC}"
  UPDATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${BASE_URL}/admin/services/${SERVICE_ID}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"price_cents":150,"active":false}')
  HTTP_CODE=$(echo "$UPDATE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ UPDATE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ UPDATE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
  
  # DELETE
  echo -e "${BLUE}→ Deleting service${NC}"
  DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/admin/services/${SERVICE_ID}" \
    -H "Authorization: Bearer $TOKEN")
  HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ DELETE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ DELETE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
fi

# Test Devices CRUD
echo -e "\n${BOLD}${BLUE}═══ Devices CRUD ═══${NC}"

# CREATE
DEVICE_LABEL="Frontend Test Device ${TIMESTAMP}"
echo -e "${BLUE}→ Creating device: ${DEVICE_LABEL}${NC}"
CREATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/admin/devices" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"label\":\"${DEVICE_LABEL}\",\"public_key\":\"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAETestKey\n-----END PUBLIC KEY-----\",\"model\":\"Test Model\",\"location\":\"Test Location\",\"gpio_pin\":18}")
HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  DEVICE_ID=$(echo $RESPONSE_BODY | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo -e "${GREEN}  ✓ CREATE: Success (200) - ID: ${DEVICE_ID}${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ CREATE: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
  DEVICE_ID=""
fi

# READ
echo -e "${BLUE}→ Reading all devices${NC}"
READ_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/admin/devices/all" \
  -H "Authorization: Bearer $TOKEN")
HTTP_CODE=$(echo "$READ_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}  ✓ READ: Success (200)${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ READ: Failed (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# UPDATE
if [ ! -z "$DEVICE_ID" ]; then
  echo -e "${BLUE}→ Updating device${NC}"
  UPDATE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "${BASE_URL}/admin/devices/${DEVICE_ID}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"location":"UPDATED Location","status":"MAINTENANCE"}')
  HTTP_CODE=$(echo "$UPDATE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ UPDATE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ UPDATE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
  
  # DELETE
  echo -e "${BLUE}→ Deleting device${NC}"
  DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/admin/devices/${DEVICE_ID}" \
    -H "Authorization: Bearer $TOKEN")
  HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}  ✓ DELETE: Success (200)${NC}"
    ((PASS++))
  else
    echo -e "${RED}  ✗ DELETE: Failed (${HTTP_CODE})${NC}"
    ((FAIL++))
  fi
fi

# Test duplicate handling
echo -e "\n${BOLD}${BLUE}═══ Duplicate Entry Handling ═══${NC}"
echo -e "${BLUE}→ Testing duplicate location name${NC}"
DUP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/admin/locations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Location-1","description":"Duplicate test"}')
HTTP_CODE=$(echo "$DUP_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$DUP_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "409" ]; then
  echo -e "${GREEN}  ✓ Duplicate handling: Correct (409 Conflict)${NC}"
  echo -e "${YELLOW}    Message: $(echo $RESPONSE_BODY | python3 -c "import sys, json; print(json.load(sys.stdin).get('detail', 'N/A'))" 2>/dev/null)${NC}"
  ((PASS++))
else
  echo -e "${RED}  ✗ Duplicate handling: Unexpected (${HTTP_CODE})${NC}"
  ((FAIL++))
fi

# Summary
TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))

echo -e "\n${BOLD}${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║                     Test Summary                          ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}✓ Passed: ${PASS}/${TOTAL}${NC}"
echo -e "${RED}✗ Failed: ${FAIL}/${TOTAL}${NC}"
echo -e "${BLUE}Success Rate: ${PERCENT}%${NC}\n"

if [ $FAIL -eq 0 ]; then
  echo -e "${BOLD}${GREEN}🎉 All tests passed! Frontend CRUD operations are working correctly.${NC}"
  echo -e "${BLUE}Dashboard URL: http://localhost/admin/dashboard${NC}\n"
  exit 0
else
  echo -e "${BOLD}${RED}⚠️  Some tests failed. Please review the errors above.${NC}\n"
  exit 1
fi

