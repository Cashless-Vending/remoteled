# RemoteLED

Control a physical LED over Bluetooth Low Energy using a Raspberry Pi and an Android app. The Pi displays a QR code on a kiosk page; scanning it deep‑links the Android app, which connects to the Pi's BLE peripheral and toggles a GPIO pin using a short per‑session key.

The project includes everything needed to provision a Raspberry Pi (web kiosk, BLE peripheral in Node or Python, systemd services) and the Android client app (QR scanner + BLE GATT client).

> Important: Android emulators do not support real Bluetooth LE. Use a physical Android device for end‑to‑end testing.

## Overview
- Architecture: Pi runs a BLE peripheral and displays a deep link QR code on a local web page. Android scans the QR or opens the deep link directly, connects via BLE, and writes commands to toggle a GPIO.
- Deep link format: `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>`.
- BLE stacks on Pi: Node.js or Python (only one active at a time; systemd services are mutually exclusive).

## Repository Layout
- `pi/`: Raspberry Pi provisioning and runtime
  - `install.sh`: One‑shot provisioning of Node/Python deps, nginx, kiosk, and services
  - `kiosk.sh`: Launches Chromium in kiosk mode to `http://localhost`
  - `node/`: Node BLE peripheral (`main.js`), service unit and starter script
  - `python/`: Python BLE peripheral (`code.py`), service unit and starter script
  - `web/`: Static kiosk (`index.html`) that renders the QR code
- `android/RemoteLedBLE/`: Android app (deep link + BLE GATT + QR scanner)
- `docs/`: Architecture notes and planning

## Python Dependency Management

This project uses [uv](https://github.com/astral-sh/uv) for Python package management with a single `pyproject.toml` at the root.

**Installation:**
- **On macOS (development)**: `uv sync`
- **On Raspberry Pi OS**: `uv sync --extra pi`

The Pi-specific dependencies (RPi.GPIO, bluezero, dbus-python) are only installed when using the `--extra pi` flag.

## Requirements
- Raspberry Pi with Bluetooth (tested on Raspberry Pi OS Bookworm, Wayfire/LXDE)
- Internet on first setup (to install packages)
- Android device (current app sets `minSdk=34`, i.e., Android 14+)

## End‑to‑End Quick Start

### A. Raspberry Pi setup
1. Copy the `pi/` directory to the Pi and run the installer:

   ```bash
   bash pi/install.sh
   ```

   What the installer does:
   - Installs Node 18, Python BLE dependencies, and nginx
   - Copies code to `/usr/local/remoteled/`
   - Sets up the kiosk to show `http://localhost` in Chromium on boot
   - Creates two services (mutually exclusive): `remoteled-node.service` and `remoteled-python.service`

2. Choose ONE BLE implementation and enable it (Python recommended):

   ```bash
   # Python implementation (uses GPIO BCM 17)
   sudo systemctl disable --now remoteled-node.service 2>/dev/null || true
   sudo systemctl enable --now remoteled-python.service

   # or Node implementation (adjust GPIO pin in code if needed)
   # sudo systemctl disable --now remoteled-python.service
   # sudo systemctl enable --now remoteled-node.service
   ```

3. Ensure web server is running:

   ```bash
   sudo systemctl enable --now nginx
   sudo systemctl status nginx | cat
   ```

4. Reboot, then verify the kiosk shows a QR:

   ```bash
   sudo reboot
   # After reboot, on the Pi screen you should see "Scan QR" and a code
   ```

5. View logs for the BLE service until you see a deep link being generated:

   ```bash
   # For Python
   journalctl -u remoteled-python.service -f
   # For Node
   # journalctl -u remoteled-node.service -f
   ```

   You should see a line like:

   ```
   Generated Deep Link: remoteled://connect/AA:BB:CC:DD:EE:FF/abcd/ef01/1234
   ```

Hardware note: The LED should be connected to ground and GPIO BCM 17 (Python) or the pin configured in `pi/node/main.js` (Node). Add a series resistor.

### B. Android app setup
1. Use a physical device (Android 14+ given current config). Connect via USB with USB debugging enabled.
2. Open `android/RemoteLedBLE` in Android Studio.
3. Select your phone in the device dropdown and click Run. Grant Camera, Location, and Bluetooth permissions.
4. The app launches the QR scanner. Scan the kiosk QR.

Deep link alternative (without scanning):

```bash
adb shell am start -a android.intent.action.VIEW -d "remoteled://connect/AA:BB:CC:DD:EE:FF/abcd/ef01/1234"
```

If your phone runs an older Android version, lower `minSdk` in `android/RemoteLedBLE/app/build.gradle.kts` and rebuild.

## Quick Start (Raspberry Pi)
1) Prepare the Pi
- Update OS packages and ensure Bluetooth is enabled.
- Optional dependency: if `dos2unix` is not installed, run `sudo apt-get install dos2unix`.

2) Run the installer
- Copy this repo (or just the `pi/` folder) onto the Pi.
- Execute: `bash pi/install.sh`
- What it does:
  - Installs Node 18, Python BLE deps, and nginx
  - Copies code to `/usr/local/remoteled/`
  - Sets Chromium to autostart a kiosk at `http://localhost` and displays QR
  - Installs `remoteled-node.service` and `remoteled-python.service` (conflicting so only one runs)

3) Reboot and verify
- After reboot, the kiosk should show “Scan QR” with a code.
- Check services: `sudo systemctl status remoteled-node` or `sudo systemctl status remoteled-python`
- Tail logs: `sudo journalctl -u remoteled-node -f` (or `remoteled-python`)

4) Switch BLE implementation (optional)
- Prefer Node: `sudo systemctl enable --now remoteled-node && sudo systemctl disable --now remoteled-python`
- Prefer Python: `sudo systemctl enable --now remoteled-python && sudo systemctl disable --now remoteled-node`

## Quick Start (Android)
- Build from source: open `android/RemoteLedBLE` in Android Studio and run on a device (Android 14+ as configured).
- Or install the included debug APK: `remoteled.apk` (for local testing only; rebuild your own for distribution).
- Launch the app and scan the QR on the Pi. The app also handles deep links of the form `remoteled://connect/...` if opened directly.

Emulator note: The Android emulator does not support Bluetooth LE and the app declares BLE as a required feature in the manifest. Installation and BLE will fail on the emulator—use a real device.

## Using It
- Commands written to the BLE characteristic are JSON:
  - `{"command":"CONNECT","bleKey":"xxxx"}`: verifies the session
  - `{"command":"ON","bleKey":"xxxx"}`: turns the LED on
  - `{"command":"OFF","bleKey":"xxxx"}`: turns the LED off
- The `bleKey` is a 4‑hex‑digit value generated per session and included in the deep link/QR.

## GPIO Pins
- Python implementation: uses BCM pin `17` (`RPi.GPIO`). Change in `pi/python/code.py` if needed.
- Node implementation: uses `onoff` with pin `529` in `pi/node/main.js`. Adjust to your board’s GPIO numbering if you’re on a standard Raspberry Pi; common choice is BCM `17`.

## Run Manually (without systemd)
- Node BLE peripheral:
  - `cd /usr/local/remoteled/node && sudo node main.js`
- Python BLE peripheral:
  - `cd /usr/local/remoteled/python && source bt/bin/activate && python3 code.py`
- Kiosk page (already served by nginx): `http://localhost` on the Pi

## Troubleshooting
- No QR on kiosk:
  - Check nginx: `systemctl status nginx`
  - Verify BLE service is running (Python or Node)
- Bluetooth won't power on:
  - `rfkill list`, then `sudo rfkill unblock bluetooth && sudo hciconfig hci0 up`
- Can’t see a deep link in logs:
  - Confirm exactly one BLE service is active (Python OR Node)
  - Tail logs with `journalctl -u remoteled-python.service -f` (or Node)
- Android cannot connect:
  - Ensure Bluetooth and Location permissions are granted
  - App requires Android 14+ as configured; consider lowering `minSdk` in `build.gradle.kts`
  - Ensure the active implementation (Node or Python) matches what you expect (`systemctl status`)
- GPIO not toggling:
  - Confirm the pin numbers match your hardware
  - For Node, change the pin in `pi/node/main.js` from `529` to a valid BCM number (e.g., `17`) for Raspberry Pi

## How it works (one‑minute version)
- Pi generates random 16‑bit service/characteristic UUIDs and a short session key (`bleKey`), then displays a deep link as a QR code on the kiosk.
- The Android app scans the QR, reconstructs full 128‑bit UUIDs, connects over BLE, reads current state, then sends JSON commands including the `bleKey`.

## Security Notes
- Session key: `bleKey` is short (16‑bit) and rotates per session; fine for demos, not strong security. For production, use pairing or stronger authentication.
- Privileges: Node BLE currently runs with `sudo` to access HCI. Consider a dedicated service user and Linux capabilities (`CAP_NET_RAW`, `CAP_NET_ADMIN`).

## Reference
- Web kiosk displays the deep link as a QR code.
- Services: `remoteled-node.service` and `remoteled-python.service` (conflicting).

## Database Setup

RemoteLED uses PostgreSQL to store device information, services/products, orders, authorizations, and telemetry logs. The database supports the complete customer journey from QR scan to device activation.

### Quick Database Setup

1. **Install PostgreSQL 15+** (macOS with Homebrew):
   ```bash
   brew install postgresql@15
   export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
   brew services start postgresql@15
   ```

2. **Create and initialize the database**:
   ```bash
   createdb remoteled
   psql -d remoteled -f database/schema.sql
   psql -d remoteled -f database/seed.sql  # Optional: load test data
   ```

3. **Verify setup**:
   ```bash
   psql remoteled -c "SELECT * FROM v_devices_summary;"
   ```

### Database Schema Overview

The database consists of 6 main tables:

- **devices**: Raspberry Pi devices with their public keys for signature verification
- **services**: Products offered by each device (TRIGGER, FIXED, VARIABLE types)
- **orders**: Customer orders tracking the lifecycle (CREATED → PAID → RUNNING → DONE)
- **authorizations**: Cryptographically signed payloads sent to devices via BLE
- **logs**: Communication and telemetry logs between Pi and server
- **admins**: Administrative users managing the system

### Service Types

- **TRIGGER**: One-time activation (2 seconds) - e.g., vending machine dispense
- **FIXED**: Fixed duration - e.g., 40-minute laundry cycle ($2.50)
- **VARIABLE**: Pay-per-time - e.g., air compressor ($0.25 per 6 minutes)

### Order Lifecycle

```
CREATED → PAID → RUNNING → DONE
           ↓         ↓
         FAILED   FAILED
```

### Connection String

For application configuration:
```
postgresql://localhost:5432/remoteled
```

**📚 Complete database documentation**: See [`database/README.md`](database/README.md) for detailed schema, queries, and maintenance instructions.

## Testing

### Quick Testing Guide

**1. Install Dependencies**

macOS (development):
```bash
uv sync
```

Raspberry Pi:
```bash
uv sync --extra pi
```

**2. Start Pi BLE Peripheral**

On Raspberry Pi:
```bash
cd pi/python
python3 code.py
```

Note the UUIDs printed in the terminal:
```
Service UUID: 0000XXXX-0000-1000-8000-00805f9b34fb
Characteristic UUID: 0000YYYY-0000-1000-8000-00805f9b34fb
bleKey: ZZZZ
```

**3. Start FastAPI Backend**

On your development machine:
```bash
cd backend
uv run --no-project uvicorn app.main:app --reload
```

Backend will start on `http://localhost:8000`

**4. Test LED Control via Payment API**

```bash
# Test GREEN LED (payment success)
curl -X POST http://localhost:8000/api/payment/mock \
  -H "Content-Type: application/json" \
  -d '{"status": "success"}'

# Test RED LED (payment failed)
curl -X POST http://localhost:8000/api/payment/mock \
  -H "Content-Type: application/json" \
  -d '{"status": "failed"}'

# Test YELLOW LED (payment processing)
curl -X POST http://localhost:8000/api/payment/mock \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}'
```

**Expected Results:**
- Pi logs: `[LEDService] GREEN LED (GPIO 17) turned ON (exclusive)`
- Backend logs: `[BLE] ✓ green LED turned ON`
- Hardware: Correct LED lights up (Green=GPIO17, Yellow=GPIO19, Red=GPIO27)

**Troubleshooting:**
- "Device not found": Ensure Pi is running `code.py` and Bluetooth is enabled
- "Module not found" errors: Run `uv sync` (or `uv sync --extra pi` on Pi)
- Database connection errors: Ensure PostgreSQL is running and database is created

📚 **Detailed API documentation**: See [`backend/README.md`](backend/README.md) for complete API reference

## Further reading
- `docs/ARCHITECTURE.md`
- `docs/CODEBASE_OVERVIEW.md`
- `docs/UNDERSTANDING_REMOTELED_CORE_CONCEPTS.md`
- `docs/QR_FLOW.md`
- `docs/VENDINGMACHINE_DIAGRAMS.md`
- `database/README.md`

## Notes
- Binaries (`remoteled.apk`, zipped artifacts) are included here for convenience during local development. Avoid committing binaries in a public repo; build from source instead.
- More background and diagrams: see `docs/ARCHITECTURE.md`.
