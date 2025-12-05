#!/bin/bash

# ============================================================
# RemoteLED Demo - Complete Order Flow Simulation
# ============================================================
# This script simulates what the Android app does:
# 1. Create Order (CREATED)
# 2. Process Payment → (PAID)
# 3. Start Service → (RUNNING)
# 4. Wait for service duration
# 5. Complete Service → (DONE)
# ============================================================

API_BASE="http://localhost:8000"
DEVICE_ID="${1:-d1111111-1111-1111-1111-111111111111}"  # Laundry Room A
SERVICE_ID="${2:-11111111-1111-1111-1111-111111111111}" # FIXED service (40 min for $2.50)
AMOUNT_CENTS="${3:-250}"  # $2.50
SERVICE_DURATION="${4:-30}"  # seconds (for demo, use 30 seconds instead of 40 minutes)

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          RemoteLED Demo - Order Flow Simulation            ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Device: $DEVICE_ID"
echo "║  Service: $SERVICE_ID"
echo "║  Amount: \$$(echo "scale=2; $AMOUNT_CENTS/100" | bc)"
echo "║  Duration: ${SERVICE_DURATION}s (demo mode)"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Create Order
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Step 1: Creating Order..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ORDER_RESPONSE=$(curl -s -X POST "$API_BASE/orders" \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"$DEVICE_ID\",
    \"service_id\": \"$SERVICE_ID\",
    \"amount_cents\": $AMOUNT_CENTS
  }")

ORDER_ID=$(echo $ORDER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$ORDER_ID" ]; then
  echo "❌ Failed to create order!"
  echo "Response: $ORDER_RESPONSE"
  exit 1
fi

echo "✅ Order Created!"
echo "   Order ID: $ORDER_ID"
echo "   Status: CREATED"
echo ""
echo "👀 Check Admin Console → Live Orders panel"
echo ""
read -p "Press Enter to continue to payment processing..."

# Step 2: Simulate Payment Processing (PAID)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💳 Step 2: Processing Payment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update order to PAID
PAID_RESPONSE=$(curl -s -X PATCH "$API_BASE/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "PAID"}')

echo "✅ Payment Received!"
echo "   Status: PAID"
echo ""
echo "👀 Check Admin Console → Order should show 'Payment Received'"
echo ""
read -p "Press Enter to start the service (RUNNING)..."

# Step 3: Start Service (RUNNING)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ Step 3: Starting Service (e.g., Laundry Running)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update order to RUNNING
RUNNING_RESPONSE=$(curl -s -X PATCH "$API_BASE/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "RUNNING"}')

echo "✅ Service Running!"
echo "   Status: RUNNING"
echo "   Duration: ${SERVICE_DURATION} seconds"
echo ""
echo "👀 Check Admin Console → Order should show 'Service Running' with green pulse"
echo ""

# Countdown timer
echo "⏱️  Service in progress..."
for i in $(seq $SERVICE_DURATION -1 1); do
  printf "\r   Time remaining: %02d seconds " $i
  sleep 1
done
echo ""
echo ""

# Step 4: Complete Service (DONE)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Step 4: Service Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update order to DONE
DONE_RESPONSE=$(curl -s -X PATCH "$API_BASE/orders/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "DONE"}')

echo "✅ Order Completed!"
echo "   Status: DONE"
echo "   Order ID: $ORDER_ID"
echo ""
echo "👀 Check Admin Console → Order moved to 'Recently Completed'"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Demo Complete! 🎉                       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  The order went through the complete lifecycle:            ║"
echo "║    📝 CREATED → 💳 PAID → ⚡ RUNNING → ✅ DONE            ║"
echo "║                                                            ║"
echo "║  Check the Admin Console to see the order in history!      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

