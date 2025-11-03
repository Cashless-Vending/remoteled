# RemoteLED Architecture

## Components
- Raspberry Pi (edge):
  - BLE peripheral (Node or Python), generates short UUIDs and `bleKey` per session.
  - nginx serves static kiosk at `http://localhost`.
  - Chromium in kiosk autostarts and renders QR code.
- Android App:
  - QR scanner to read deep link or handles deep link intents directly.
  - GATT client connects via MAC + UUIDs and sends JSON commands with `bleKey`.

## Data Flow
- BLE service/char UUIDs + 16‑bit `bleKey` are generated on Pi at start.
- Pi displays deep link `remoteled://connect/<MAC>/<svc16>/<char16>/<bleKey>` as a QR code on the kiosk.
- Android scans the QR and opens app via deep link; app connects to Pi GATT.
- App writes `{\"command\":\"ON|OFF|CONNECT\",\"bleKey\":\"xxxx\"}` to characteristic.
- Pi toggles GPIO and returns current state on read.

## Services on Pi
- `remoteled-node.service` or `remoteled-python.service` (mutually exclusive).
- `nginx` static server.
- Chromium autostart via Wayfire/LXDE.

## Ports
- Port `80` (nginx), BLE (HCI).

## Security Notes
- `bleKey` is a short session key; for production add pairing or stronger auth.
- Prefer service user + capabilities over `sudo node` for BLE access.
