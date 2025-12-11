# RemoteLED Kiosk Setup

## Quick Start on Pi

After git pull:

```bash
cd ~/remoteled/pi/kiosk

# First time only
npm install
npm run build
chmod +x start.sh

# Start server
./start.sh
```

Server runs on `http://localhost:3000`

## State File Location

**Important**: BLE Python code writes to:
```
~/remoteled/pi/kiosk/build/state.json
```

The start.sh script creates this file automatically if it doesn't exist.

## Development on macOS

Test locally:
```bash
cd /Users/yj/Workspaces/remoteled/pi/kiosk
npm install
npm start  # Dev server on localhost:3000
```

Then commit and push, pull on Pi.

## State File Format

React polls `state.json` every second:

**Show QR code**:
```json
{
  "qr_url": "http://192.168.1.158:9999/detail?...",
  "status": "QR",
  "timestamp": 1732842398230
}
```

**Show "Connected"**:
```json
{
  "status": "CONNECTED",
  "timestamp": 1732842398230
}
```

**Show countdown timer**:
```json
{
  "status": "RUNNING",
  "duration_seconds": 30,
  "timestamp": 1732842398230
}
```

Timer runs locally in React, no internet needed.
