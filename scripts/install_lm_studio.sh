#!/bin/bash
set -e  # Exit on any error

# Install LM Studio (for Linux)

echo "Installing LM Studio..."

# Check if wget is available
if ! command -v wget >/dev/null 2>&1; then
    echo "WARNING: wget not found, skipping LM Studio download"
    exit 0
fi

# Try alternative download URL for LM Studio  
echo "Downloading LM Studio AppImage..."
# Try multiple possible URLs
if ! wget -O lm-studio.AppImage "https://releases.lmstudio.ai/linux/x86/stable/LM-Studio-linux-x86.AppImage" 2>/dev/null; then
    echo "Primary download failed, trying alternative URL..."
    if ! wget -O lm-studio.AppImage "https://github.com/lmstudio-ai/LMStudio/releases/latest/download/LMStudio-linux-x86_64.AppImage" 2>/dev/null; then
        echo "WARNING: Could not download LM Studio from known URLs"
        echo "You may need to download manually from https://lmstudio.ai"
        exit 0  # Don't fail the entire script
    fi
fi

# Make executable
chmod +x lm-studio.AppImage

# Create desktop entry directory
mkdir -p ~/.local/share/applications

# Create desktop entry
cat > ~/.local/share/applications/lm-studio.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=LM Studio
Exec=$HOME/lm-studio.AppImage
Icon=lm-studio
Terminal=false
EOF

echo "✓ LM Studio downloaded successfully"
echo "Run with: ./lm-studio.AppImage"
echo "Note: Manual setup required for server mode"