# RemoteLED Kiosk - React Edition

Simple React app to replace nginx+HTML+JSON approach.

## Setup on Pi

```bash
# Install Node.js if not already installed
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Copy kiosk folder to Pi
scp -r kiosk/ pi@<pi-ip>:~/remoteled/

# On Pi, build and start
cd ~/remoteled/kiosk
npm install
npm run build

# Make start script executable
chmod +x start.sh

# Create systemd service for kiosk server
sudo tee /etc/systemd/system/kiosk-server.service > /dev/null <<EOF
[Unit]
Description=RemoteLED Kiosk Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/remoteled/kiosk/build
ExecStart=/usr/bin/python3 -m http.server 3000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable kiosk-server
sudo systemctl start kiosk-server

# Update nginx to proxy state.json to /var/www/html/state.json
# Or just have Python code write to kiosk/build/state.json instead
```

## How it works

1. **BLE code writes to state.json**:
   - `{'qr_url': 'http://...', 'status': 'QR'}` - Shows QR code
   - `{'status': 'CONNECTED'}` - Shows "Connected" message
   - `{'status': 'RUNNING', 'duration_seconds': 30}` - Shows countdown timer
   - The state file defaults to `/var/www/html/state.json` (override with `KIOSK_STATE_FILE`).

2. **React polls state.json every second** and updates UI

3. **Countdown runs locally** in React (no internet needed)

4. **When timer ends**, automatically returns to QR code

## Simpler than before

Before: nginx → static HTML → polls JSON → renders QR with JS
After: React → polls state.json → renders everything

Everything in one React app, no separate HTML/CSS/JS files!
