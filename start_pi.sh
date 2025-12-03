#!/bin/bash
# RemoteLED Pi Startup Script
# Run this to start the BLE peripheral and kiosk on a Raspberry Pi

echo "================================================"
echo "RemoteLED Pi Startup (BLE + Kiosk)"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVICE_ID_FILE="/usr/local/remoteled/device_id"
DEFAULT_DEVICE_ID="d1111111-1111-1111-1111-111111111111"
MACOS_SERVER_IP="192.168.1.99"
BACKEND_PORT=9999
PI_IP=$(hostname -I | awk '{print $1}')

echo -e "${YELLOW}Pi IP: ${PI_IP}${NC}"
echo -e "${YELLOW}macOS Server: ${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
echo ""

# Step 0: Check if uv is installed
echo -e "${YELLOW}[0/5] Checking uv installation...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv is not installed${NC}"
    echo ""
    echo "Install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Then run this script again."
    exit 1
fi
echo -e "${GREEN}✓ uv is installed: $(uv --version)${NC}"
echo ""

# Step 1: Sync dependencies (install Pi-specific packages)
echo -e "${YELLOW}[1/5] Syncing dependencies (uv sync --extra pi)...${NC}"
cd "$REPO_ROOT"
if uv sync --extra pi; then
    echo -e "${GREEN}✓ Dependencies synced${NC}"
else
    echo -e "${RED}✗ Failed to sync dependencies${NC}"
    echo "Try running manually: cd $REPO_ROOT && uv sync --extra pi"
    exit 1
fi
echo ""

# Step 2: Ensure device ID is set
echo -e "${YELLOW}[2/5] Checking device ID...${NC}"
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

# Step 3: Check nginx for kiosk
echo -e "${YELLOW}[3/5] Checking nginx...${NC}"
if ! systemctl is-active --quiet nginx 2>/dev/null; then
    echo "Starting nginx..."
    sudo systemctl start nginx 2>/dev/null || true
    sleep 1
fi
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo -e "${GREEN}✓ nginx is running${NC}"
else
    echo -e "${YELLOW}⚠ nginx not available (kiosk display may not work)${NC}"
fi
echo ""

# Step 4: Verify macOS backend is reachable
echo -e "${YELLOW}[4/5] Checking macOS backend...${NC}"
if curl -s -m 3 "http://${MACOS_SERVER_IP}:${BACKEND_PORT}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API reachable at http://${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
else
    echo -e "${RED}✗ Cannot reach backend at http://${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
    echo -e "${YELLOW}  Make sure the macOS server is running (use start_server_macos.sh)${NC}"
    exit 1
fi
echo ""

# Step 5: Start BLE Peripheral
echo -e "${YELLOW}[5/5] Starting BLE Peripheral...${NC}"

# Kill any existing BLE process
echo "  Stopping any existing BLE processes..."
sudo pkill -f "python.*code.py" 2>/dev/null || true
sleep 1

# Set up environment
export API_BASE_URL="http://${MACOS_SERVER_IP}:${BACKEND_PORT}"
export DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')

# Clear old log
sudo rm -f /tmp/remoteled_ble.log
sudo touch /tmp/remoteled_ble.log
sudo chmod 666 /tmp/remoteled_ble.log

# Start BLE using uv run (this ensures all dependencies are available)
echo "  Starting BLE service with uv run..."
cd "$REPO_ROOT"

# Run with sudo but use uv run to get the right Python environment
sudo -E DEVICE_ID="$DEVICE_ID" API_BASE_URL="$API_BASE_URL" \
    nohup $(which uv) run --extra pi python pi/python/code.py > /tmp/remoteled_ble.log 2>&1 &

echo "  Waiting for BLE to initialize (5 seconds)..."
sleep 5

# Check if the Python process is running
if pgrep -f "python.*code.py" > /dev/null; then
    BLE_PID=$(pgrep -f "python.*code.py" | head -1)
    echo -e "${GREEN}✓ BLE Peripheral started (PID: $BLE_PID)${NC}"
    echo -e "  Device ID: $DEVICE_ID"
    echo -e "  Backend URL: $API_BASE_URL"
else
    echo -e "${RED}✗ BLE Peripheral failed to start${NC}"
    echo ""
    echo "Last 30 lines of log:"
    echo "----------------------------------------"
    tail -30 /tmp/remoteled_ble.log
    echo "----------------------------------------"
    echo ""
    echo "Full log: sudo cat /tmp/remoteled_ble.log"
    exit 1
fi
echo ""

# Wait for QR code generation
echo -e "${YELLOW}Waiting for QR code generation...${NC}"
sleep 2

# Check if QR data is ready
if [ -f "/var/www/html/qr_data.json" ]; then
    QR_CONTENT=$(cat /var/www/html/qr_data.json 2>/dev/null)
    if echo "$QR_CONTENT" | grep -q "http"; then
        QR_URL=$(echo "$QR_CONTENT" | grep -o 'http[^"]*' | head -1)
        echo -e "${GREEN}✓ QR Code ready!${NC}"
        echo -e "  Detail URL: $QR_URL"
    else
        echo -e "${YELLOW}⚠ QR data exists but no URL yet${NC}"
        echo "  Content: $QR_CONTENT"
    fi
else
    echo -e "${YELLOW}⚠ QR data file not found${NC}"
fi
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}Pi services started successfully!${NC}"
echo "================================================"
echo ""
echo "Services:"
echo "  • nginx: $(systemctl is-active nginx 2>/dev/null || echo 'not available')"
echo "  • BLE Peripheral: running (PID: $BLE_PID)"
echo "  • Backend API: $API_BASE_URL (macOS)"
echo "  • Kiosk page: http://localhost"
echo ""
echo "Logs:"
echo "  • BLE: sudo tail -f /tmp/remoteled_ble.log"
echo ""
echo "To open kiosk in Chrome:"
echo "  cd $REPO_ROOT/pi && ./kiosk.sh"
echo ""
echo "To stop BLE service:"
echo "  sudo pkill -f 'python.*code.py'"
echo ""
echo "Monitoring BLE logs (Ctrl+C to stop, service keeps running)..."
echo ""

# Follow BLE logs
sudo tail -f /tmp/remoteled_ble.log
