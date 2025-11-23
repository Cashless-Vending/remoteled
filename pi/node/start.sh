#!/bin/bash
set -e

DEVICE_ID_FILE="/usr/local/remoteled/device_id"
DEFAULT_DEVICE_ID="d1111111-1111-1111-1111-111111111111"

if [ -z "${DEVICE_ID:-}" ]; then
  if [ -f "$DEVICE_ID_FILE" ]; then
    DEVICE_ID="$(tr -d ' \r\n' < "$DEVICE_ID_FILE")"
  else
    DEVICE_ID="$DEFAULT_DEVICE_ID"
  fi
fi

echo "Starting Node BLE service with DEVICE_ID=${DEVICE_ID}"
sudo DEVICE_ID="$DEVICE_ID" node main.js
echo "Script has stopped."
