# RemoteLED — Project Structure and Setup

This repository contains a complete Raspberry Pi + Android BLE demo that shows a QR on a Pi kiosk, deep‑links an Android app, and securely toggles a GPIO pin over BLE with a short per‑session key. The Pi uses MQTT to feed the QR into a local web page. There are two alternative BLE stacks on the Pi (Node.js or Python), controlled by systemd units that are mutually exclusive.

## What’s Here (Current State)
- `pi/`
  - `install.sh`: End‑to‑end Pi provisioning (Node.js, Python deps, nginx, mosquitto, kiosk splash, systemd units, chromium autostart).
  - `kiosk.sh`: Launches Chromium in kiosk mode to `http://localhost`.
  - `node/`: Node BLE peripheral + GPIO (`main.js`), `package.json`, systemd service + starter script.
  - `python/`: Python BLE peripheral (bluezero) + GPIO (`code.py`), systemd service + starter script.
  - `web/`: Static kiosk page (`index.html`) that renders the QR via MQTT over WebSockets.
- `android/RemoteLedBLE/`: Android app (deep link + BLE GATT), with QR scanner activity.
- Artifacts: `remoteled.apk`, `remoteled_android.zip` (built assets — should not be committed in GitHub).
- Notes: `boot from usb.txt` (Pi boot guidance).

## How It Works (High‑Level)
- Pi starts one BLE peripheral (Node or Python, not both). On start it:
  - Generates short 16‑bit UUIDs for service and characteristic, plus a short `bleKey`.
  - Uses MQTT to publish a deep link: `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>`.
- nginx serves the static `web/index.html`; Chromium autostarts in kiosk and subscribes to MQTT `qr` topic to render a QR of the deep link.
- Android app scans the QR (or opens the deep link directly), connects to the Pi by MAC + UUIDs, and writes JSON commands with the `bleKey` to toggle GPIO.
- MQTT is local only (anonymous allowed) to shuttle text for the QR and status.

## Recommended GitHub Structure
You can go monorepo or multi‑repo. For simplicity and team onboarding, I recommend starting with a monorepo, then splitting later if needed.

### Option A — Monorepo (recommended)
- `/android/RemoteLedBLE` — Android project.
- `/pi`
  - `/node` — Node BLE peripheral, `main.js`, `package.json`, `start.sh`, service unit template.
  - `/python` — Python BLE peripheral, `code.py`, `start.sh`, service unit template.
  - `/web` — kiosk UI assets.
  - `/install` — `install.sh`, `kiosk.sh`, images (e.g., `splash.png`).
  - `/systemd` — `remoteled-node.service`, `remoteled-python.service` (placeholders for user).
- `/docs` — architecture, diagrams, troubleshooting, security notes.
- `/scripts` — helper scripts (packaging, linting, release tooling).
- `.github/workflows` — CI (Android build, lint Python/Node, release artifacts).

Pros: single place for issues/PRs, shared versioning, easier cross‑component changes.

### Option B — Multi‑repo (split by component)
- `remoteled-pi` — everything in `remoteled_setup` (organized as above under `/pi`).
- `remoteled-android` — the Android app.
- `remoteled-web` — if the kiosk UI ever expands beyond static HTML; today it can live under the Pi repo.
- `remoteled-infra` — only if you add cloud/backend services later.

Pros: independent release cadences; targeted permissions. Cons: coordination overhead.

## What To Check In vs Ignore
- Check in:
  - All source: Android, Node, Python, web assets.
  - Systemd unit templates with `USERNAME_PLACEHOLDER` (leave placeholders; don’t hardcode your local user).
  - `install.sh`, `kiosk.sh`, and images used by the kiosk/splash.
  - `package-lock.json` (Node) to lock dependencies reproducibly.
- Don’t check in:
  - Built artifacts: `*.apk`, `*.aab`, zips/archives, OS files (`.DS_Store`).
  - Device state: Python venv (`pi/python/bt/`), `node_modules/`, Android `build/` outputs.
  - Machine configs under `/etc` (instead, keep templates in repo and write them during install).

A root `.gitignore` is added to cover these.

## Workspace Setup (Dev)
- Android:
  - Open `android/RemoteLedBLE` in Android Studio (Giraffe+). Current `minSdk=34` limits to Android 14+; consider lowering to 26–29 for broader device support.
  - Build and run. Deep links: `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>`.
- Node (dev):
  - Develop on Pi (preferred due to `hci-socket` + GPIO) or mock GPIO on non‑Pi.
  - From `pi/node`: `npm install`; run with `sudo node main.js`.
- Python (dev):
  - On Pi: create venv (installer does this as `bt/`), install deps, then `python3 code.py`.
- Web:
  - Static files in `pi/web`. Open in a browser with MQTT WS broker available at `ws://localhost:8083`.

## Raspberry Pi Provisioning
- Recommended: run `pi/install.sh` on a fresh Raspberry Pi OS (Wayland/Wayfire or LXDE).
  - Installs Node 18, Python deps, nginx, mosquitto; copies code to `/usr/local/remoteled/`.
  - Configures MQTT (anonymous, 1883 + WS 8083) and nginx to serve web.
  - Sets splash/wallpaper; wires Chromium to autostart the kiosk.
  - Installs systemd units for Node and Python; they have `Conflicts=` so only one runs at a time.
- Switch implementation (Node vs Python):
  - Enable Node: `sudo systemctl enable --now remoteled-node && sudo systemctl disable --now remoteled-python`.
  - Enable Python: `sudo systemctl enable --now remoteled-python && sudo systemctl disable --now remoteled-node`.
- Verify services:
  - `sudo systemctl status remoteled-node` or `remoteled-python`.
  - `sudo journalctl -u remoteled-node -f` (or python) to tail logs.

## Security Notes (Local‑only today)
- MQTT is configured as `allow_anonymous true` and exposed on `localhost`. Keep it local only. If you need remote access, add auth/TLS and firewall rules.
- BLE “key” (`bleKey`) is 16‑bit and changes per session. It prevents accidental control but is not cryptographically strong. For production, consider authenticated pairing or a stronger challenge/response.
- `sudo node main.js` is used to access BLE/HCI; consider a dedicated service user and CAP_NET_ADMIN/CAP_NET_RAW instead of full sudo.

## CI/CD (Suggested)
- Android: GitHub Actions to build Debug/Release, upload APKs as build artifacts, and publish tagged releases.
- Pi: Lint Python (ruff/flake8), Node (eslint), and package a tarball of `/pi` for releases.
- Optional: workflow to assemble a bootable image or Ansible playbook if you scale deployment.

## Next Steps I Recommend
- Choose monorepo vs multi‑repo (I can restructure the folders accordingly).
- Remove committed artifacts (`remoteled.apk`, `remoteled_android.zip`) before pushing to GitHub.
- Add `.github/workflows` for Android build + basic lint for Node/Python.
- Decide whether to default to Node or Python BLE on Pi; document a single default path in the README.
- Consider lowering `minSdk` for Android to reach more devices.

---
If you want, I can: 1) reorganize this directory into the monorepo layout above, 2) remove artifacts safely, and 3) add CI boilerplate and a developer‑focused docs/ARCHITECTURE.md.
