#!/bin/bash
set -e

echo "================================================"
echo "RemoteLED Complete Startup Script"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVICE_ID_FILE="/usr/local/remoteled/device_id"
DEFAULT_DEVICE_ID="d1111111-1111-1111-1111-111111111111"
BACKEND_PORT=9999
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${YELLOW}Repository root: ${REPO_ROOT}${NC}"
echo -e "${YELLOW}Local IP: ${LOCAL_IP}${NC}"
echo ""

# Step 1: Ensure device ID is set
echo -e "${YELLOW}[1/6] Checking device ID...${NC}"
if [ ! -f "$DEVICE_ID_FILE" ]; then
    echo "Device ID file not found. Creating with default ID..."
    sudo mkdir -p /usr/local/remoteled
    echo -n "$DEFAULT_DEVICE_ID" | sudo tee "$DEVICE_ID_FILE" > /dev/null
    echo -e "${GREEN}✓ Created device ID file: $DEFAULT_DEVICE_ID${NC}"
else
    DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')
    echo -e "${GREEN}✓ Device ID already set: $DEVICE_ID${NC}"
fi
export DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')
echo ""

# Step 2: Check PostgreSQL
echo -e "${YELLOW}[2/6] Checking PostgreSQL...${NC}"
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
fi
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    exit 1
fi
echo ""

# Step 3: Check nginx
echo -e "${YELLOW}[3/6] Checking nginx...${NC}"
if ! systemctl is-active --quiet nginx; then
    echo "Starting nginx..."
    sudo systemctl start nginx
    sleep 1
fi
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ nginx is running${NC}"
else
    echo -e "${RED}✗ nginx failed to start${NC}"
    exit 1
fi
echo ""

# Step 4: Start Backend API
echo -e "${YELLOW}[4/6] Starting Backend API...${NC}"
cd "$REPO_ROOT"

# Ensure uv dependencies are installed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies with uv..."
    uv sync
fi

# Kill any existing backend process
pkill -f "uvicorn app.main:app" || true
sleep 1

# Start backend in background using uv run
export API_BASE_URL="http://${LOCAL_IP}:${BACKEND_PORT}"
cd "$REPO_ROOT/backend"
nohup uv run --no-project uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} > /tmp/remoteled_backend.log 2>&1 &
BACKEND_PID=$!
echo "Waiting for backend to start..."
sleep 6

# Verify backend is running
if curl -s "http://localhost:${BACKEND_PORT}/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend API started (PID: $BACKEND_PID)${NC}"
    echo -e "  URL: http://${LOCAL_IP}:${BACKEND_PORT}"
    echo -e "  Logs: tail -f /tmp/remoteled_backend.log"
else
    echo -e "${RED}✗ Backend API failed to start${NC}"
    echo "Check logs: tail -f /tmp/remoteled_backend.log"
    exit 1
fi
echo ""

# Step 5: Start BLE Peripheral
echo -e "${YELLOW}[5/6] Starting BLE Peripheral...${NC}"
cd "$REPO_ROOT/pi/python"

# Kill any existing BLE process
sudo pkill -f "python3 code.py" || true
sleep 1

# Start BLE in background with proper environment
export API_BASE_URL="http://${LOCAL_IP}:${BACKEND_PORT}"
export DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')
nohup sudo -E bash -c "cd $REPO_ROOT/pi/python && DEVICE_ID=$DEVICE_ID API_BASE_URL=$API_BASE_URL python3 code.py" > /tmp/remoteled_ble.log 2>&1 &
BLE_PID=$!
sleep 3

# Check if BLE started
if ps -p $BLE_PID > /dev/null; then
    echo -e "${GREEN}✓ BLE Peripheral started (PID: $BLE_PID)${NC}"
    echo -e "  Device ID: $DEVICE_ID"
    echo -e "  Logs: tail -f /tmp/remoteled_ble.log"
else
    echo -e "${RED}✗ BLE Peripheral failed to start${NC}"
    echo "Check logs: sudo tail -f /tmp/remoteled_ble.log"
    exit 1
fi
echo ""

# Step 6: Wait for QR code generation and display kiosk
echo -e "${YELLOW}[6/6] Waiting for QR code generation...${NC}"
sleep 2

# Check if QR data is ready
if [ -f "/var/www/html/qr_data.json" ]; then
    QR_URL=$(cat /var/www/html/qr_data.json | grep -o 'http[^"]*' | head -1)
    echo -e "${GREEN}✓ QR Code ready!${NC}"
    echo -e "  Detail URL: $QR_URL"
else
    echo -e "${YELLOW}⚠ QR data not yet generated, check BLE logs${NC}"
fi
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}All services started successfully!${NC}"
echo "================================================"
echo ""
echo "Services:"
echo "  • PostgreSQL: running"
echo "  • nginx: running"
echo "  • Backend API: http://${LOCAL_IP}:${BACKEND_PORT}"
echo "  • BLE Peripheral: running"
echo "  • Kiosk page: http://localhost"
echo ""
echo "Logs:"
echo "  • Backend: tail -f /tmp/remoteled_backend.log"
echo "  • BLE: sudo tail -f /tmp/remoteled_ble.log"
echo ""
echo "To open kiosk in Chrome:"
echo "  cd $REPO_ROOT/pi && ./kiosk.sh"
echo ""
echo "To stop all services:"
echo "  pkill -f 'uvicorn app.main:app'"
echo "  sudo pkill -f 'python3 code.py'"
echo ""
echo "Press Ctrl+C to monitor BLE logs (services will keep running)..."
echo ""

# Follow BLE logs
sudo tail -f /tmp/remoteled_ble.log
