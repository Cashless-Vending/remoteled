#!/bin/bash
# Start React kiosk in production mode

cd "$(dirname "$0")"

# Build if needed
if [ ! -d "build" ]; then
    echo "Building React app..."
    npm install
    npm run build
fi

# Serve on port 3000 using python
echo "Starting kiosk server on http://localhost:3000"
cd build
python3 -m http.server 3000
