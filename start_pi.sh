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
QR_DATA_FILE="/var/www/html/qr_data.json"

echo -e "${YELLOW}Pi IP: ${PI_IP}${NC}"
echo -e "${YELLOW}macOS Server: ${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
echo ""

# =============================================================================
# STEP 0: CLEANUP - Do this FIRST before anything else
# =============================================================================
echo -e "${YELLOW}[0/7] Preparing environment (cleanup)...${NC}"

# Kill any existing BLE processes FIRST
echo "  → Stopping any existing BLE processes..."
sudo pkill -f "python.*code.py" 2>/dev/null || true
sleep 1

# Enable BlueZ experimental features (required for BLE peripheral/GATT server)
echo "  → Enabling BlueZ experimental features..."
sudo mkdir -p /etc/systemd/system/bluetooth.service.d/
echo -e '[Service]\nExecStart=\nExecStart=/usr/libexec/bluetooth/bluetoothd --experimental' | sudo tee /etc/systemd/system/bluetooth.service.d/experimental.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart bluetooth
sleep 2
if ps aux | grep -q "[b]luetooth.*--experimental"; then
    echo -e "${GREEN}✓ BlueZ experimental features enabled${NC}"
else
    echo -e "${YELLOW}⚠ BlueZ experimental features may not be enabled${NC}"
fi

# Create directories
echo "  → Creating required directories..."
sudo mkdir -p /var/www/html
sudo mkdir -p /usr/local/remoteled
sudo mkdir -p /tmp

# AGGRESSIVELY clear the QR data file
echo "  → Clearing stale QR data..."
sudo rm -f "$QR_DATA_FILE" 2>/dev/null || true
sudo rm -f "${QR_DATA_FILE}.tmp" 2>/dev/null || true

# Write fresh empty state with timestamp 0
echo '{"message":"Loading...","timestamp":0}' | sudo tee "$QR_DATA_FILE" > /dev/null
sudo chmod 666 "$QR_DATA_FILE"

# Clear BLE log
echo "  → Clearing old logs..."
sudo rm -f /tmp/remoteled_ble.log
sudo touch /tmp/remoteled_ble.log
sudo chmod 666 /tmp/remoteled_ble.log

# Verify QR file is clean
QR_CHECK=$(cat "$QR_DATA_FILE" 2>/dev/null)
if echo "$QR_CHECK" | grep -q "Loading"; then
    echo -e "${GREEN}✓ QR data file cleared successfully${NC}"
    echo "  Content: $QR_CHECK"
else
    echo -e "${RED}✗ Failed to clear QR data file${NC}"
    echo "  Content: $QR_CHECK"
fi
echo ""

# =============================================================================
# STEP 1: Check uv installation
# =============================================================================
echo -e "${YELLOW}[1/7] Checking uv installation...${NC}"
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

# =============================================================================
# STEP 2: Sync dependencies
# =============================================================================
echo -e "${YELLOW}[2/7] Syncing dependencies (uv sync --extra pi)...${NC}"
cd "$REPO_ROOT"
if uv sync --extra pi 2>&1 | tail -5; then
    echo -e "${GREEN}✓ Dependencies synced${NC}"
else
    echo -e "${RED}✗ Failed to sync dependencies${NC}"
    echo "Try running manually: cd $REPO_ROOT && uv sync --extra pi"
    exit 1
fi
echo ""

# =============================================================================
# STEP 3: Check device ID
# =============================================================================
echo -e "${YELLOW}[3/7] Checking device ID...${NC}"
if [ ! -f "$DEVICE_ID_FILE" ]; then
    echo "Device ID file not found. Creating with default ID..."
    echo -n "$DEFAULT_DEVICE_ID" | sudo tee "$DEVICE_ID_FILE" > /dev/null
    echo -e "${GREEN}✓ Created device ID file: $DEFAULT_DEVICE_ID${NC}"
else
    DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')
    echo -e "${GREEN}✓ Device ID: $DEVICE_ID${NC}"
fi
export DEVICE_ID=$(cat "$DEVICE_ID_FILE" | tr -d ' \r\n')
echo ""

# =============================================================================
# STEP 4: Check/start nginx
# =============================================================================
echo -e "${YELLOW}[4/7] Checking nginx...${NC}"
# Restart nginx to clear any caches
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "  Restarting nginx to clear cache..."
    sudo systemctl restart nginx 2>/dev/null || true
    sleep 1
else
    echo "  Starting nginx..."
    sudo systemctl start nginx 2>/dev/null || true
    sleep 1
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    echo -e "${GREEN}✓ nginx is running${NC}"
else
    echo -e "${YELLOW}⚠ nginx not available (kiosk display may not work)${NC}"
fi
echo ""

# =============================================================================
# STEP 5: Check backend connectivity
# =============================================================================
echo -e "${YELLOW}[5/7] Checking macOS backend...${NC}"
if curl -s -m 3 "http://${MACOS_SERVER_IP}:${BACKEND_PORT}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API reachable at http://${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
else
    echo -e "${RED}✗ Cannot reach backend at http://${MACOS_SERVER_IP}:${BACKEND_PORT}${NC}"
    echo -e "${YELLOW}  Make sure the macOS server is running (use start_server_macos.sh)${NC}"
    exit 1
fi
echo ""

# =============================================================================
# STEP 6: Start BLE Peripheral
# =============================================================================
echo -e "${YELLOW}[6/7] Starting BLE Peripheral...${NC}"

# Set up environment
export API_BASE_URL="http://${MACOS_SERVER_IP}:${BACKEND_PORT}"

# Double-check QR file is still clean before starting
echo "  → Verifying QR data is clean..."
QR_PRE=$(cat "$QR_DATA_FILE" 2>/dev/null)
echo "    Pre-start content: $QR_PRE"

# Start BLE using uv run
echo "  → Starting BLE service..."
cd "$REPO_ROOT"

sudo -E DEVICE_ID="$DEVICE_ID" API_BASE_URL="$API_BASE_URL" \
    nohup $(which uv) run --extra pi python pi/python/code.py > /tmp/remoteled_ble.log 2>&1 &

echo "  → Waiting for BLE to initialize (6 seconds)..."
sleep 6

# Check if the Python process is running
if pgrep -f "python.*code.py" > /dev/null; then
    BLE_PID=$(pgrep -f "python.*code.py" | head -1)
    echo -e "${GREEN}✓ BLE Peripheral started (PID: $BLE_PID)${NC}"
else
    echo -e "${RED}✗ BLE Peripheral failed to start${NC}"
    echo ""
    echo "Last 30 lines of log:"
    echo "----------------------------------------"
    tail -30 /tmp/remoteled_ble.log
    echo "----------------------------------------"
    exit 1
fi
echo ""

# =============================================================================
# STEP 7: Verify BLE Advertisement
# =============================================================================
echo -e "${YELLOW}[7/7] Verifying BLE advertisement...${NC}"
sleep 3  # Give BLE peripheral time to start advertising
if timeout 5 sudo hcitool lescan 2>&1 | grep -q "Remote LED\|2C:CF"; then
    echo -e "${GREEN}✓ BLE peripheral is advertising${NC}"
else
    echo -e "${YELLOW}⚠ BLE advertisement not detected (may still work)${NC}"
fi
echo ""

# =============================================================================
# VERIFY QR CODE
# =============================================================================
echo -e "${YELLOW}Verifying QR code generation...${NC}"
QR_READY=false
for i in 1 2 3 4 5 6 7 8 9 10; do
    QR_CONTENT=$(cat "$QR_DATA_FILE" 2>/dev/null)
    if echo "$QR_CONTENT" | grep -q "http.*detail"; then
        QR_URL=$(echo "$QR_CONTENT" | grep -o 'http[^"]*' | head -1)
        echo -e "${GREEN}✓ QR Code ready!${NC}"
        echo -e "  URL: $QR_URL"
        QR_READY=true
        break
    fi
    echo "  Attempt $i/10: $(echo "$QR_CONTENT" | head -c 50)..."
    sleep 1
done

if [ "$QR_READY" = false ]; then
    echo -e "${RED}✗ QR code generation failed${NC}"
    echo "  Final content: $(cat "$QR_DATA_FILE")"
    echo ""
    echo "BLE Log (last 20 lines):"
    tail -20 /tmp/remoteled_ble.log
fi
echo ""

# =============================================================================
# SUMMARY
# =============================================================================
echo "================================================"
if [ "$QR_READY" = true ]; then
    echo -e "${GREEN}✓ Pi services started successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Pi started but QR code may have issues${NC}"
fi
echo "================================================"
echo ""
echo "Services:"
echo "  • nginx: $(systemctl is-active nginx 2>/dev/null || echo 'not available')"
echo "  • Bluetooth: $(ps aux | grep -q '[b]luetooth.*--experimental' && echo 'experimental enabled' || echo 'standard mode')"
echo "  • BLE Peripheral: running (PID: $BLE_PID)"
echo "  • Backend: $API_BASE_URL"
echo ""
echo "QR Data File: $QR_DATA_FILE"
echo "Content: $(cat "$QR_DATA_FILE" 2>/dev/null)"
echo ""
echo "Commands:"
echo "  • View logs: sudo tail -f /tmp/remoteled_ble.log"
echo "  • Open kiosk: cd $REPO_ROOT/pi && ./kiosk.sh"
echo "  • Stop BLE: sudo pkill -f 'python.*code.py'"
echo ""
echo "Monitoring BLE logs (Ctrl+C to stop)..."
echo ""

sudo tail -f /tmp/remoteled_ble.log
