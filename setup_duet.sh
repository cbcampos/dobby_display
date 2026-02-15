#!/bin/bash
# Dobby Display Setup Script for Chrome OS (Lenovo Duet)
# Run this on your Chrome OS device with Linux enabled

set -e

echo "🔧 Setting up Dobby Display..."

# Create the display directory
mkdir -p ~/dobby_display
cd ~/dobby_display

# Check if git is available, clone repo if not already present
if [ ! -d ".git" ]; then
    echo "📦 Cloning dobby_display repository..."
    git clone https://github.com/cbcampos/dobby_display.git .
else
    echo "📦 Updating dobby_display repository..."
    git pull origin master
fi

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3 install --user flask requests

# Create a start script
echo "📝 Creating start script..."

cat > start_display.sh << 'EOF'
#!/bin/bash
cd ~/dobby_display
echo "🚀 Starting Dobby Display on http://localhost:5000"
echo "Press Ctrl+C to stop"
python3 receiver.py
EOF

chmod +x start_display.sh

# Create a systemd service file (optional, for auto-start)
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/dobby-display.service << 'EOF'
[Unit]
Description=Dobby Display
After=network.target

[Service]
Type=simple
ExecStart=%h/dobby_display/start_display.sh
Restart=on-failure

[Install]
WantedBy=default.target
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the display manually:"
echo "  ~/dobby_display/start_display.sh"
echo ""
echo "To auto-start on boot (optional):"
echo "  systemctl --user enable dobby-display"
echo "  systemctl --user start dobby-display"
echo ""
echo "The display will be available at:"
echo "  http://localhost:5000"
echo ""
echo "To push content from OpenClaw, set:"
echo "  export DOBBY_DISPLAY_URL=http://YOUR_DUET_IP:5000"
