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
echo "📦 Installing Python dependencies..."
pip3 install --user flask requests

# Install Tailscale if not present
if ! command -v tailscale &> /dev/null; then
    echo "📦 Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "✓ Tailscale already installed"
fi

# Create a start script
echo "📝 Creating start script..."

cat > start_display.sh << 'EOF'
#!/bin/bash
cd ~/dobby_display
echo "🚀 Starting Dobby Display..."
echo "Press Ctrl+C to stop"
python3 receiver.py
EOF

chmod +x start_display.sh

# Create Tailscale autostart script
cat > start_tailscale.sh << 'EOF'
#!/bin/bash
echo "🔐 Connecting to Tailscale..."
tailscale up --operator=root
echo "📍 Your Tailscale IP:"
tailscale ip -4
EOF

chmod +x start_tailscale.sh

# Create a systemd service file for auto-start
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/dobby-display.service << 'EOF'
[Unit]
Description=Dobby Display
After=network.target
Wants=network.target

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
echo "Step 1: Connect to Tailscale"
echo "  ~/dobby_display/start_tailscale.sh"
echo ""
echo "Step 2: Get your Tailscale IP"
echo "  tailscale ip -4"
echo ""
echo "Step 3: Start the display"
echo "  ~/dobby_display/start_display.sh"
echo ""
echo "The display will be at: http://<TAILSCALE_IP>:5000"
echo ""
echo "To auto-start on boot:"
echo "  systemctl --user enable dobby-display"
echo "  systemctl --user start dobby-display"
