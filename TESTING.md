# Remote LED Payment Testing Guide

## Architecture

```
curl (macOS client)
  → HTTP POST
FastAPI Backend (macOS)
  → Returns payment status
BLE Client (macOS)
  → Sends BLE command
Pi BLE Peripheral
  → Controls GPIO
LED Lights (Green/Yellow/Red)
```

## LED Status Mapping

- **Green LED** (GPIO 17): Payment SUCCESS
- **Yellow LED** (GPIO 19): Payment PROCESSING
- **Red LED** (GPIO 27): Payment FAIL

## Setup

### 1. Install Dependencies (macOS)

```bash
# Install using uv (recommended)
uv sync

# This installs: fastapi, uvicorn, bleak, paho-mqtt
# Pi-specific packages (RPi.GPIO, bluezero, dbus-python) are optional
```

### 2. Install Pi Dependencies (On Raspberry Pi)

On your Raspberry Pi:

```bash
# Install with Pi-specific optional dependencies
uv sync --extra pi
```

### 3. Start Pi BLE Peripheral

On your Raspberry Pi:

```bash
cd pi/python
python code.py
```

**IMPORTANT**: Note the UUIDs printed in the terminal:
```
New Service UUID: 0000XXXX-0000-1000-8000-00805f9b34fb
Characteristic UUID: 0000YYYY-0000-1000-8000-00805f9b34fb
bleKey: ZZZZ
```

### 4. Configure BLE Client (macOS)

Edit `ble_client.py` and update with Pi's UUIDs:

```python
SERVICE_UUID = "0000XXXX-0000-1000-8000-00805f9b34fb"  # From Pi
CHAR_UUID = "0000YYYY-0000-1000-8000-00805f9b34fb"     # From Pi
BLE_KEY = "ZZZZ"  # From Pi
```

## Testing

### Option 1: Full Pipeline Test

**Terminal 1 - Start FastAPI Backend:**
```bash
uvicorn backend:app --reload
```

**Terminal 2 - Test Payment:**
```bash
# Test success (70% chance)
curl -X POST http://localhost:8000/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "service": "premium"}'

# Response:
# {"status":"success","led_color":"green","duration":30,"message":"Payment success - Amount: $100.0"}
```

**Terminal 3 - Trigger LED via BLE:**
```bash
# Use the status from FastAPI response
python ble_client.py success 30

# Or test other statuses:
python ble_client.py fail 10
python ble_client.py processing 15
```

### Option 2: Direct LED Control

Test BLE → Pi → LED without FastAPI:

```bash
# Turn green LED on for 30 seconds
python ble_client.py success 30

# Turn red LED on for 10 seconds
python ble_client.py fail 10

# Turn yellow LED on for 15 seconds
python ble_client.py processing 15
```

## Troubleshooting

### "Device 'Remote LED' not found"
- Ensure Pi is running `code.py`
- Check Pi Bluetooth is enabled
- Verify macOS Bluetooth is on
- Pi and macOS must be in BLE range

### "ERROR: [Errno 61] Connection refused" (FastAPI)
- Start FastAPI backend: `uvicorn backend:app --reload`
- Check it's running on `http://localhost:8000`

### "ERROR: characteristic not found"
- Update UUIDs in `ble_client.py` with correct values from Pi
- Restart Pi `code.py` if UUIDs changed

### LED not turning on
- Check Pi GPIO connections (GPIO 17/19/27)
- Verify bleKey matches in `ble_client.py`
- Check Pi terminal for error messages

## API Endpoints

### POST /payment
Request:
```json
{
  "amount": 100,
  "service": "premium"  // or "basic"
}
```

Response:
```json
{
  "status": "success",     // "success", "fail", or "processing"
  "led_color": "green",    // "green", "red", or "yellow"
  "duration": 30,          // seconds
  "message": "Payment success - Amount: $100.0"
}
```

### GET /health
Response:
```json
{"status": "ok"}
```
