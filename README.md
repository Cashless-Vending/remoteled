# RemoteLED

Control a physical LED over Bluetooth Low Energy using a Raspberry Pi and an Android app. The Pi displays a QR code on a kiosk page; scanning it deep‑links the Android app, which connects to the Pi’s BLE peripheral and toggles a GPIO pin using a short per‑session key.

The project includes everything needed to provision a Raspberry Pi (web kiosk, MQTT broker, BLE peripheral in Node or Python, systemd services) and the Android client app (QR scanner + BLE GATT client).

## Overview
- Architecture: Pi runs a BLE peripheral and publishes a deep link to MQTT; a local web page renders the QR. Android scans the QR or opens the deep link directly, connects via BLE, and writes commands to toggle a GPIO.
- Deep link format: `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>`.
- BLE stacks on Pi: Node.js or Python (only one active at a time; systemd services are mutually exclusive).

## Repository Layout
- `pi/`: Raspberry Pi provisioning and runtime
  - `install.sh`: One‑shot provisioning of Node/Python deps, nginx, mosquitto, kiosk, and services
  - `kiosk.sh`: Launches Chromium in kiosk mode to `http://localhost`
  - `node/`: Node BLE peripheral (`main.js`), service unit and starter script
  - `python/`: Python BLE peripheral (`code.py`), service unit and starter script
  - `web/`: Static kiosk (`index.html`) that renders the QR from MQTT
- `android/RemoteLedBLE/`: Android app (deep link + BLE GATT + QR scanner)
- `docs/`: Architecture notes and planning

## Requirements
- Raspberry Pi with Bluetooth (tested on Raspberry Pi OS Bookworm, Wayfire/LXDE)
- Internet on first setup (to install packages)
- Android device (current app sets `minSdk=34`, i.e., Android 14+)

## Quick Start (Raspberry Pi)
1) Prepare the Pi
- Update OS packages and ensure Bluetooth is enabled.
- Optional dependency: if `dos2unix` is not installed, run `sudo apt-get install dos2unix`.

2) Run the installer
- Copy this repo (or just the `pi/` folder) onto the Pi.
- Execute: `bash pi/install.sh`
- What it does:
  - Installs Node 18, Python BLE deps, nginx, mosquitto
  - Copies code to `/usr/local/remoteled/`
  - Configures MQTT on `1883` (TCP) and `8083` (WebSockets), anonymous on localhost
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
  - Check mosquitto is running: `systemctl status mosquitto`
  - Check nginx: `systemctl status nginx`
  - Verify WebSockets listener `8083` is configured in `/etc/mosquitto/mosquitto.conf`
- Android cannot connect:
  - Ensure Bluetooth and Location permissions are granted
  - App requires Android 14+ as configured; consider lowering `minSdk` in `build.gradle.kts`
  - Ensure the active implementation (Node or Python) matches what you expect (`systemctl status`)
- GPIO not toggling:
  - Confirm the pin numbers match your hardware
  - For Node, change the pin in `pi/node/main.js` from `529` to a valid BCM number (e.g., `17`) for Raspberry Pi

## Security Notes
- Local only: MQTT is anonymous and bound locally; do not expose it to untrusted networks.
- Session key: `bleKey` is short (16‑bit) and rotates per session; fine for demos, not strong security. For production, use pairing or stronger authentication.
- Privileges: Node BLE currently runs with `sudo` to access HCI. Consider a dedicated service user and Linux capabilities (`CAP_NET_RAW`, `CAP_NET_ADMIN`).

## Reference
- Web kiosk subscribes to MQTT topic `qr` and renders the deep link as a QR.
- Pi publishes to `qr` and listens to `qr_backend` to prompt QR refresh.
- Services: `remoteled-node.service` and `remoteled-python.service` (conflicting).

## Notes
- Binaries (`remoteled.apk`, zipped artifacts) are included here for convenience during local development. Avoid committing binaries in a public repo; build from source instead.
- More background and diagrams: see `docs/ARCHITECTURE.md`.
