#!/bin/bash
source bt/bin/activate

# Restart loop for the BLE Python script
while true; do
  echo "Starting BLE Python script..."
  python3 code.py  # Replace `code.py` with your Python filename

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
