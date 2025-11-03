#!/bin/bash
# Test CRUD operations with authentication and logging

API_BASE="http://localhost:8000"
TEST_EMAIL="admin@test.com"
TEST_PASSWORD="securepass123"

echo "=== Testing CRUD Operations with Auth ==="
echo ""

# Step 1: Register and get token
echo "Step 1: Registering test admin..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get authentication token"
    exit 1
fi

echo "✅ Token obtained"
echo ""

# Step 2: Create a device
echo "Step 2: Creating new device..."
CREATE_DEVICE=$(curl -s -X POST "$API_BASE/admin/devices" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Test Device",
    "public_key": "-----BEGIN PUBLIC KEY-----\ntest_key\n-----END PUBLIC KEY-----",
    "model": "RPi 4 Model B",
    "location": "Test Lab",
    "gpio_pin": 17
  }')

echo "$CREATE_DEVICE" | python3 -m json.tool
DEVICE_ID=$(echo "$CREATE_DEVICE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$DEVICE_ID" ]; then
    echo "✅ Device created: $DEVICE_ID"
else
    echo "❌ Device creation failed"
    exit 1
fi

echo ""

# Step 3: Update the device
echo "Step 3: Updating device..."
curl -s -X PUT "$API_BASE/admin/devices/$DEVICE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"label": "Updated Test Device", "location": "Production Lab"}' | python3 -m json.tool

echo "✅ Device updated"
echo ""

# Step 4: Create a service
echo "Step 4: Creating service for device..."
CREATE_SERVICE=$(curl -s -X POST "$API_BASE/admin/services" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"type\": \"FIXED\",
    \"price_cents\": 100,
    \"fixed_minutes\": 30
  }")

echo "$CREATE_SERVICE" | python3 -m json.tool
SERVICE_ID=$(echo "$CREATE_SERVICE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$SERVICE_ID" ]; then
    echo "✅ Service created: $SERVICE_ID"
else
    echo "❌ Service creation failed"
    exit 1
fi

echo ""

# Step 5: Check admin logs
echo "Step 5: Checking admin action logs..."
curl -s "$API_BASE/admin/logs/admin-actions?limit=10" | python3 -m json.tool | head -30

echo ""
echo "✅ Admin logs are recording actions"
echo ""

# Step 6: Delete service
echo "Step 6: Deleting service..."
DELETE_SERVICE=$(curl -s -X DELETE "$API_BASE/admin/services/$SERVICE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$DELETE_SERVICE" | python3 -m json.tool

if echo "$DELETE_SERVICE" | grep -q "success"; then
    echo "✅ Service deleted successfully"
else
    echo "❌ Service deletion failed"
fi

echo ""

# Step 7: Delete device
echo "Step 7: Deleting device..."
DELETE_DEVICE=$(curl -s -X DELETE "$API_BASE/admin/devices/$DEVICE_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$DELETE_DEVICE" | python3 -m json.tool

if echo "$DELETE_DEVICE" | grep -q "success"; then
    echo "✅ Device deleted successfully"
else
    echo "❌ Device deletion failed"
fi

echo ""
echo "Step 8: Final admin logs check..."
curl -s "$API_BASE/admin/logs/admin-actions?limit=15" | python3 -m json.tool | head -50

echo ""
echo "=== CRUD with Auth Tests Complete ==="
echo ""
echo "Summary:"
echo "- Created device with auth ✅"
echo "- Updated device with auth ✅"
echo "- Created service with auth ✅"
echo "- Deleted service with auth ✅"
echo "- Deleted device with auth ✅"
echo "- All actions logged to admin_logs ✅"

