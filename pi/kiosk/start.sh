#!/bin/bash
# Start React kiosk in production mode

cd "$(dirname "$0")"

# Build if needed
if [ ! -d "build" ]; then
    echo "Building React app..."
    npm install
    npm run build
fi

# Create initial state.json if it doesn't exist
if [ ! -f "build/state.json" ]; then
    echo "Creating initial state.json..."
    cat > build/state.json << 'EOF'
{
  "qr_url": "http://loading...",
  "status": "QR",
  "timestamp": 0
}
EOF
fi

# Serve on port 3000 using python
echo "Starting kiosk server on http://localhost:3000"
echo "State file: $(pwd)/build/state.json"
cd build
python3 -m http.server 3000
