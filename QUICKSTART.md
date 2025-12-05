# RemoteLED Quick Start Guide

This guide shows you how to quickly start the RemoteLED system with separate startup scripts for macOS (server) and Raspberry Pi (client).

## Architecture

- **macOS**: Runs PostgreSQL database + FastAPI backend server
- **Raspberry Pi**: Runs BLE peripheral + nginx kiosk
- **Network**: Pi connects to macOS backend at `192.168.1.99:9999`

## Setup Instructions

### On macOS (Server - Run First!)

1. **Clone the repo**:
   ```bash
   cd ~/Workspaces
   git clone <repo-url> remoteled
   cd remoteled
   ```

2. **Install dependencies**:
   ```bash
   # Install PostgreSQL if not already installed
   brew install postgresql@15
   brew services start postgresql@15

   # Create database
   createdb remoteled
   psql -d remoteled -f database/schema.sql
   psql -d remoteled -f database/seed.sql

   # Install Python dependencies
   uv sync
   ```

3. **Start the server**:
   ```bash
   ./start_server_macos.sh
   ```

   This script will:
   - ✓ Check PostgreSQL is running
   - ✓ Check Python dependencies are installed
   - ✓ Start FastAPI backend on port 9999
   - ✓ Show you the server IP address (e.g., `192.168.1.99`)

4. **Verify**:
   - Open http://localhost:9999/docs (Swagger UI)
   - Check http://localhost:9999/health

---

### On Raspberry Pi (Client - Run Second!)

1. **Clone the repo** (if not already there):
   ```bash
   cd ~/Documents
   git clone <repo-url> remoteled
   cd remoteled
   ```

2. **Update macOS IP** (if needed):
   Edit `start_pi.sh` and update this line if your Mac IP changed:
   ```bash
   MACOS_SERVER_IP="192.168.1.99"  # Update this to your Mac's IP
   ```

3. **Start the Pi**:
   ```bash
   ./start_pi.sh
   ```

   This script will:
   - ✓ Check device ID is set
   - ✓ Check nginx is running
   - ✓ **Verify macOS backend is reachable** (will fail if server isn't running)
   - ✓ Start BLE peripheral with connection to macOS backend
   - ✓ Generate QR code with detail URL

4. **Open the kiosk** (optional):
   ```bash
   cd pi && ./kiosk.sh
   ```
   This opens Chromium in kiosk mode showing the QR code at http://localhost

---

## Quick Workflow

### Daily startup:

1. **On macOS**:
   ```bash
   cd ~/Workspaces/remoteled && ./start_server_macos.sh
   ```
   Wait until you see "Backend API started successfully"

2. **On Pi**:
   ```bash
   cd ~/Documents/remoteled && ./start_pi.sh
   ```
   Wait until you see "Pi services started successfully!"

3. **Open kiosk on Pi**:
   ```bash
   cd ~/Documents/remoteled/pi && ./kiosk.sh
   ```

4. **Scan QR with Android app** and test!

---

## Stopping Services

### On Pi:
```bash
# Stop BLE
sudo pkill -f "python3 code.py"

# Stop nginx (optional)
sudo systemctl stop nginx
```

### On macOS:
```bash
# Stop backend
pkill -f "uvicorn app.main:app"

# Stop PostgreSQL (optional)
brew services stop postgresql@15
```

---

## Logs

### On Pi:
```bash
# BLE logs
sudo tail -f /tmp/remoteled_ble.log

# nginx logs
sudo tail -f /var/log/nginx/error.log
```

### On macOS:
```bash
# Backend logs
tail -f /tmp/remoteled_backend.log
```

---

## Troubleshooting

### Pi can't reach macOS backend
- Verify macOS IP: `ipconfig getifaddr en0` (on Mac)
- Update `start_pi.sh` with correct IP
- Check firewall on macOS allows port 9999
- Test connectivity: `curl http://192.168.1.99:9999/health` (from Pi)

### Backend won't start on macOS
- Check logs: `tail -f /tmp/remoteled_backend.log`
- Verify PostgreSQL: `psql -d remoteled -c "SELECT 1"`
- Check port 9999 is free: `lsof -i :9999`

### BLE won't start on Pi
- Check logs: `sudo tail -f /tmp/remoteled_ble.log`
- Verify Bluetooth: `sudo hciconfig hci0 up`
- Check permissions: Script needs sudo for Bluetooth access

### QR code not showing
- Check nginx: `sudo systemctl status nginx`
- Check QR data: `cat /var/www/html/qr_data.json`
- Check BLE generated URL in logs

---

## Device ID Configuration

The device ID is stored in `/usr/local/remoteled/device_id` on the Pi.

**Default device**: `d1111111-1111-1111-1111-111111111111` (Laundry Room A test device)

To change:
```bash
echo -n "your-device-uuid" | sudo tee /usr/local/remoteled/device_id
```

Then restart BLE: `sudo pkill -f "python3 code.py" && ./start_pi.sh`

---

## Network Configuration Summary

| Component | Location | Address |
|-----------|----------|---------|
| PostgreSQL | macOS | localhost:5432 |
| Backend API | macOS | 192.168.1.99:9999 |
| BLE Peripheral | Pi | Bluetooth only |
| Kiosk Web | Pi | http://localhost (nginx) |
| QR Detail URL | Points to → | http://192.168.1.99:9999/detail?... |

---

## Files Reference

- `start_server_macos.sh` - Start backend + DB on macOS
- `start_pi.sh` - Start BLE + kiosk on Pi
- `start_all.sh` - Legacy all-in-one script (if running everything on Pi)
- `pi/kiosk.sh` - Open Chromium kiosk showing QR code
- `/usr/local/remoteled/device_id` - Device UUID for this Pi
- `/var/www/html/qr_data.json` - Generated QR data for kiosk
