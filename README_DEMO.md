# Remote LED Payment Demo - Quick Start Guide

## Architecture

```
Client (macOS)
  ↓ curl/HTTP POST
FastAPI Backend (macOS localhost:8000)
  ↓ payment validation
  ↓ BLE connection (via bleak)
Raspberry Pi BLE Peripheral
  ↓ GPIO control
3x LEDs (Green/Yellow/Red)
```

**Key Design:** Pi has NO network access - only Bluetooth. Client device (with internet) handles payment via cloud, then triggers Pi locally via BLE.

## LED Status Mapping

- **Green LED** (GPIO 17): Payment SUCCESS
- **Yellow LED** (GPIO 19): Payment PROCESSING
- **Red LED** (GPIO 27): Payment FAIL
- **Duration**: 10 seconds (all statuses)

## Quick Start

### 1. Install Dependencies

**macOS (Backend + BLE Client):**
```bash
uv sync
```

**Raspberry Pi:**
```bash
uv sync --extra pi
```

### 2. Start Pi BLE Peripheral

On Raspberry Pi:
```bash
python pi/python/code.py
```

**Copy the deep link from output:**
```
Generated Deep Link: remoteled://connect/{ADDRESS}/{SERVICE}/{CHAR}/{KEY}
Example: remoteled://connect/2C:CF:67:7C:DF:AB/C256/49A2/FB0E
```

### 3. Update Backend with Pi UUIDs

Edit `backend.py` lines 11-13 with values from deep link:
```python
SERVICE_UUID = "0000C256-0000-1000-8000-00805f9b34fb"  # Use C256 from link
CHAR_UUID = "000049A2-0000-1000-8000-00805f9b34fb"     # Use 49A2 from link
BLE_KEY = "FB0E"  # Use FB0E from link
```

### 4. Start FastAPI Backend

On macOS:
```bash
uv run --no-project uvicorn backend:app --reload
```

### 5. Test Payment → LED Pipeline

```bash
curl -X POST http://localhost:8000/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```

**Expected result:** LED lights up automatically for 10 seconds!

## Issues Encountered & Solutions

### 1. **UV Package Manager - macOS Incompatibility**
**Problem:** `pyproject.toml` included Pi-specific packages (RPi.GPIO, bluezero, dbus-python) causing `uv sync` to fail on macOS.

**Solution:**
- Moved Pi packages to optional dependencies: `[project.optional-dependencies]`
- macOS: `uv sync` (installs fastapi, bleak)
- Pi: `uv sync --extra pi` (installs everything)
- Added `[tool.hatch.build.targets.wheel]` with `packages = []` to fix hatchling build errors

### 2. **BLE Device Discovery - MAC Address Not Working on macOS**
**Problem:** Direct MAC address `2C:CF:67:7C:DF:AB` from Pi caused `BleakDeviceNotFoundError` on macOS.

**Root Cause:** macOS BLE uses its own UUID system, not MAC addresses (e.g., `652E4FC0-8407-CC7D-550E-05509B8EF420`).

**Solution:**
- Scan for devices and match by SERVICE_UUID
- Try advertised services first, fallback to connecting unnamed devices
- Implementation: `find_pi_device()` function

### 3. **BLE Device Name Not Found**
**Problem:** Scanning for device name "Remote LED" returned no results despite 27+ devices found.

**Root Cause:** Pi wasn't advertising with expected name or name was `None`.

**Solution:** Match by SERVICE_UUID instead of device name.

### 4. **Connection Dropping Between ON/OFF Commands**
**Problem:** First `curl` worked, LED turned ON, but OFF command failed with "Device not found".

**Root Cause:** Closing BLE connection after turning LED ON, then trying to reconnect after 10s failed (Pi not re-advertising quickly enough).

**Solution:** Keep single BLE connection open for entire duration:
```python
async with BleakClient(device_address) as client:
    await client.write_gatt_char(CHAR_UUID, ON_payload)  # Turn ON
    await asyncio.sleep(duration)                         # Wait
    await client.write_gatt_char(CHAR_UUID, OFF_payload)  # Turn OFF
```

### 5. **Pi BLE Peripheral Crashing After Each Request**
**Problem:** `code.py` on Pi exited after every BLE disconnect, requiring restart (causing UUID regeneration).

**Root Cause:** `on_disconnect()` callback triggered `trigger.set()`, causing main loop to exit.

**Solution:** Removed `trigger.set()` from disconnect callback - disconnects are normal, shouldn't exit program.

**File:** `pi/python/code.py` line 69
```python
def on_disconnect(cls, adapter_address, device_address):
    print(f"Disconnected from BLE device: {device_address}")
    # trigger.set()  # REMOVED - disconnects are normal
```

### 6. **Second Request Always Failed - BLE Cache Issue**
**Problem:** First `curl` worked, second immediately after always failed to find Pi.

**Root Cause:**
- After disconnect, Pi takes time to re-advertise
- macOS BLE cache showed stale address
- Scanning during this window returned no results

**Solution:** Cache Pi address after first successful connection:
```python
_cached_pi_address = None  # Global cache

async def find_pi_device():
    if _cached_pi_address:
        return _cached_pi_address  # Skip scanning, use cache

    # ... scan and find ...
    _cached_pi_address = address  # Cache it
    return address
```

**Result:**
- 1st request: Scans for Pi (~5-10s)
- 2nd+ requests: Uses cached address (instant!)
- Auto-clears cache on connection failure

## API Reference

### POST /payment

**Request:**
```json
{
  "amount": 100,
  "service": "premium"  // or "basic" (currently unused)
}
```

**Response:**
```json
{
  "status": "success",      // "success", "fail", or "processing" (70%/20%/10%)
  "led_color": "green",     // "green", "red", or "yellow"
  "duration": 10,           // seconds
  "message": "Payment success - Amount: $100.0"
}
```

**Side Effect:** LED automatically triggered in background via BLE.

### GET /health

**Response:**
```json
{"status": "ok"}
```

## File Structure

```
remoteled/
├── backend.py              # FastAPI server with BLE integration
├── ble_client.py           # Standalone BLE client for manual testing
├── pi/python/code.py       # Pi BLE peripheral + GPIO control
├── led                     # GPIO control script (bash)
├── TESTING.md             # Detailed testing guide
└── README_DEMO.md         # This file
```

## Troubleshooting

### Pi won't stay connected
- Check `code.py` line 69 - `trigger.set()` should be commented out
- Restart Pi peripheral: `python pi/python/code.py`

### "Device not found" after first request
- Fixed by caching - restart backend to reset cache
- Ensure Pi is still running (check Pi terminal)

### UUIDs changed
- Pi regenerates UUIDs on each restart
- Update `backend.py` lines 11-13 with new values from Pi output

### Slow first request
- Normal - scanning takes 5-10s
- Subsequent requests use cached address (instant)

### LED stays on forever
- Check Pi terminal for errors
- Verify BLE_KEY matches in both `backend.py` and Pi output

## Performance

- **First request:** ~5-10s (BLE scanning)
- **Subsequent requests:** ~0.5s (cached address)
- **LED duration:** 10s (configurable in `backend.py` line 131)
- **Connection stability:** Single connection for ON+OFF cycle

## Next Steps

- [ ] Integrate real Stripe payment processing
- [ ] Deploy backend to AWS/cloud (Pi stays local)
- [ ] Add authentication/authorization
- [ ] Persistent UUID configuration (avoid regeneration)
- [ ] Multiple concurrent LED requests handling
- [ ] Mobile app integration (Android/iOS)
