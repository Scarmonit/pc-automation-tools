#!/bin/bash
# Install Jan desktop app

echo "Installing Jan desktop app..."

# Download Jan AppImage
wget -O jan.AppImage https://github.com/janhq/jan/releases/latest/download/jan-linux-x86_64.AppImage
chmod +x jan.AppImage

# Start Jan API server
./jan.AppImage --serve --port 1337 &
sleep 5

# Verify Jan
curl http://localhost:1337/v1/models && echo "✓ Jan API running" || echo "⚠ Jan unavailable"