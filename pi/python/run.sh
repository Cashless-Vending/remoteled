#!/bin/bash
# Run code.py with environment from .env file only
# This script ensures no shell-exported variables override .env

cd "$(dirname "$0")"

# Kill any running instances
pkill -f "python.*code.py" || true
sleep 1

# Unset any exported API variables that might override .env
unset API_BASE_URL
unset MACHINE_ID
unset DEVICE_ID

# Run with clean environment
echo "Starting code.py with .env configuration..."
uv run code.py
