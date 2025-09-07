#!/bin/bash
# Download LM Studio AppImage (for Linux)
wget -O lm-studio.AppImage https://releases.lmstudio.ai/linux/x86/stable/LM-Studio-linux-x86.AppImage
chmod +x lm-studio.AppImage

# Create desktop entry
cat > ~/.local/share/applications/lm-studio.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=LM Studio
Exec=$HOME/lm-studio.AppImage
Icon=lm-studio
Terminal=false
EOF

# Start LM Studio server (headless mode)
./lm-studio.AppImage server start --port 1234 --cors &

# Verify server
sleep 5
curl http://localhost:1234/v1/models && echo "✓ LM Studio running" || echo "✗ LM Studio failed"