#!/bin/bash
set -e

DEVICE_ID_FILE="/usr/local/remoteled/device_id"
DEFAULT_DEVICE_ID="d1111111-1111-1111-1111-111111111111"

if [ -z "${DEVICE_ID:-}" ]; then
  if [ -f "$DEVICE_ID_FILE" ]; then
    export DEVICE_ID="$(tr -d ' \r\n' < "$DEVICE_ID_FILE")"
  else
    export DEVICE_ID="$DEFAULT_DEVICE_ID"
  fi
fi

echo "Starting BLE Python service with DEVICE_ID=${DEVICE_ID}"
source bt/bin/activate

# Restart loop for the BLE Python script
while true; do
  echo "Running code.py..."
  python3 code.py

  # Capture the exit status of the Python script
  exit_status=$?

  if [ $exit_status -eq 0 ]; then
    echo "Python script exited normally. Restarting..."
    sleep 1  # Short pause before restarting
  else
    echo "Python script exited with error code: $exit_status. Stopping loop."
    break  # Exit the loop if the exit code is not 0
  fi
done

echo "Script has stopped."
