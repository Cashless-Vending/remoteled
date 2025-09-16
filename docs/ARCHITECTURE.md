# RemoteLED Architecture

## Components
- Raspberry Pi (edge):
  - BLE peripheral (Node or Python), generates short UUIDs and `bleKey` per session.
  - MQTT broker (mosquitto) local only: `1883` (TCP) and `8083` (WebSockets).
  - nginx serves static kiosk at `http://localhost`.
  - Chromium in kiosk autostarts and renders QR code from MQTT.
- Android App:
  - QR scanner to read deep link or handles deep link intents directly.
  - GATT client connects via MAC + UUIDs and sends JSON commands with `bleKey`.

## Data Flow
- BLE service/char UUIDs + 16‑bit `bleKey` are generated on Pi at start.
- Pi publishes deep link `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>` to MQTT `qr`.
- Kiosk subscribes to `qr` over WebSockets and renders a QR.
- Android scans the QR and opens app via deep link; app connects to Pi GATT.
- App writes `{\"command\":\"ON|OFF|CONNECT\",\"bleKey\":\"xxxx\"}` to characteristic.
- Pi toggles GPIO and returns current state on read.

## Services on Pi
- `remoteled-node.service` or `remoteled-python.service` (mutually exclusive).
- `mosquitto` broker.
- `nginx` static server.
- Chromium autostart via Wayfire/LXDE.

## Topics and Ports
- MQTT topics: `qr` (UI), `qr_backend` (ping).
- Ports: `1883` (TCP), `8083` (WS), `80` (nginx), BLE (HCI).

## Security Notes
- MQTT anonymous on localhost only; do not expose publicly without auth/TLS.
- `bleKey` is a short session key; for production add pairing or stronger auth.
- Prefer service user + capabilities over `sudo node` for BLE access.
