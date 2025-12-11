#!/bin/bash
set -e

echo "================================================"
echo "RemoteLED macOS Server Startup"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Source uv environment if available
if [ -f "$HOME/.local/bin/env" ]; then
    source "$HOME/.local/bin/env"
fi

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=9999
MACOS_IP=$(ipconfig getifaddr en0 || hostname -I | awk '{print $1}')

# Find uv path
UV_PATH=$(which uv 2>/dev/null || echo "$HOME/.local/bin/uv")
if [ ! -x "$UV_PATH" ]; then
    echo -e "${RED}✗ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

echo -e "${YELLOW}Repository root: ${REPO_ROOT}${NC}"
echo -e "${YELLOW}macOS IP: ${MACOS_IP}${NC}"
echo -e "${YELLOW}Backend port: ${BACKEND_PORT}${NC}"
echo ""

# Step 1: Check PostgreSQL (Homebrew installation)
echo -e "${YELLOW}[1/3] Checking PostgreSQL...${NC}"

# Check if PostgreSQL is installed via Homebrew
if command -v brew &> /dev/null && brew list postgresql@15 &> /dev/null 2>&1; then
    echo "PostgreSQL 15 found via Homebrew"

    # Check if running
    if brew services list | grep postgresql@15 | grep started > /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is already running${NC}"
    else
        echo "Starting PostgreSQL via Homebrew..."
        brew services start postgresql@15
        sleep 3
    fi
else
    echo -e "${YELLOW}⚠ PostgreSQL@15 not found via Homebrew${NC}"
    echo "Install with: brew install postgresql@15"
    echo "Then run: brew services start postgresql@15"
    exit 1
fi

# Verify PostgreSQL is responding
if psql -d remoteled -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is responding${NC}"
else
    echo -e "${RED}✗ PostgreSQL database 'remoteled' not found or not accessible${NC}"
    echo "Create database with:"
    echo "  createdb remoteled"
    echo "  psql -d remoteled -f database/schema.sql"
    echo "  psql -d remoteled -f database/seed.sql"
    exit 1
fi
echo ""

# Step 2: Ensure dependencies are installed
echo -e "${YELLOW}[2/3] Checking Python dependencies...${NC}"
cd "$REPO_ROOT"

if [ ! -d ".venv" ]; then
    echo "Installing dependencies with uv..."
    "$UV_PATH" sync
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi
echo ""

# Step 3: Start Backend API
echo -e "${YELLOW}[3/3] Starting Backend API...${NC}"

# Kill any existing backend process
pkill -f "uvicorn app.main:app" || true
sleep 1

# Start backend in background
export API_BASE_URL="http://${MACOS_IP}:${BACKEND_PORT}"
cd "$REPO_ROOT/backend"

# Use the venv from repo root
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    echo -e "${RED}✗ Virtual environment not found at $REPO_ROOT/.venv${NC}"
    exit 1
fi

nohup "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} > /tmp/remoteled_backend.log 2>&1 &
BACKEND_PID=$!
echo "Waiting for backend to start..."
sleep 6

# Verify backend is running
if curl -s "http://localhost:${BACKEND_PORT}/health" > /dev/null; then
    HEALTH_RESPONSE=$(curl -s "http://localhost:${BACKEND_PORT}/health")
    echo -e "${GREEN}✓ Backend API started successfully (PID: $BACKEND_PID)${NC}"
    echo -e "  Health check: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Backend API failed to start${NC}"
    echo "Check logs: tail -f /tmp/remoteled_backend.log"
    exit 1
fi
echo ""

# Summary
echo "================================================"
echo -e "${GREEN}macOS server started successfully!${NC}"
echo "================================================"
echo ""
echo "Services:"
echo "  • PostgreSQL: running (Homebrew service)"
echo "  • Backend API: http://${MACOS_IP}:${BACKEND_PORT}"
echo ""
echo "Access from Pi:"
echo "  • Update Pi to use: http://${MACOS_IP}:${BACKEND_PORT}"
echo ""
echo "Logs:"
echo "  • Backend: tail -f /tmp/remoteled_backend.log"
echo ""
echo "API Documentation:"
echo "  • Swagger UI: http://localhost:${BACKEND_PORT}/docs"
echo "  • Health check: http://localhost:${BACKEND_PORT}/health"
echo ""
echo "To stop backend:"
echo "  pkill -f 'uvicorn app.main:app'"
echo ""
echo "To stop PostgreSQL:"
echo "  brew services stop postgresql@15"
echo ""
echo "Press Ctrl+C to monitor backend logs (service will keep running)..."
echo ""

# Follow backend logs
tail -f /tmp/remoteled_backend.log
