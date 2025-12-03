#!/bin/bash
# Start React kiosk in production mode

cd "$(dirname "$0")"

# Build if needed
if [ ! -d "build" ]; then
    echo "Building React app..."
    npm install
    npm run build
fi

# IMPORTANT: Link state.json to where code.py writes it
# code.py writes to /var/www/html/state.json
# React kiosk expects /state.json (relative to build/)
STATE_SOURCE="/var/www/html/state.json"
STATE_LINK="build/state.json"

# Create initial state.json in /var/www/html if it doesn't exist
if [ ! -f "$STATE_SOURCE" ]; then
    echo "Creating initial state.json in $STATE_SOURCE..."
    sudo mkdir -p /var/www/html
    cat << 'EOF' | sudo tee "$STATE_SOURCE" > /dev/null
{
  "qr_url": "http://loading...",
  "status": "QR",
  "timestamp": 0
}
EOF
    sudo chmod 666 "$STATE_SOURCE"
fi

# Remove old state.json in build/ and create symlink to the real one
rm -f "$STATE_LINK"
ln -sf "$STATE_SOURCE" "$STATE_LINK"
echo "Linked $STATE_LINK -> $STATE_SOURCE"

# Serve on port 3000 using python
echo "Starting kiosk server on http://localhost:3000"
echo "State file: $STATE_SOURCE (symlinked)"
cd build
python3 -m http.server 3000
