#!/bin/bash
set -e  # Exit on any error

echo "Setting up Jan desktop app..."

# Check if wget is available
if ! command -v wget >/dev/null 2>&1; then
    echo "ERROR: wget is required but not installed"
    exit 1
fi

# Download Jan AppImage
echo "Downloading Jan AppImage..."
wget -O jan.AppImage https://github.com/janhq/jan/releases/latest/download/jan-linux-x86_64.AppImage || {
    echo "ERROR: Failed to download Jan AppImage"
    exit 1
}

# Make executable
chmod +x jan.AppImage || {
    echo "ERROR: Failed to make Jan AppImage executable"
    exit 1
}

# Start Jan API server
echo "Starting Jan API server..."
./jan.AppImage --serve --port 1337 &
sleep 5

# Verify Jan
if curl -s http://localhost:1337/v1/models >/dev/null 2>&1; then
    echo "✓ Jan API running on http://localhost:1337"
else
    echo "⚠ Jan downloaded but API server not responding"
    echo "Try running manually: ./jan.AppImage"
fi