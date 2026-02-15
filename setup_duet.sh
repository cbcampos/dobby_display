#!/bin/bash
# Dobby Display Setup Script for Chrome OS (Lenovo Duet)
# Run this on your Chrome OS device with Linux enabled

echo "Setting up Dobby Display..."

# Create the display directory
mkdir -p ~/dobby_display
cd ~/dobby_display

# Download the display script (placeholder - update with actual content)
echo "Creating start_display.sh..."

cat > start_display.sh << 'EOF'
#!/bin/bash
# Dobby Display Runner
# Add your display logic here

echo "Starting Dobby Display..."
echo "Display connected at http://localhost:8080"

# Example: Run a simple HTTP server
# python3 -m http.server 8080
EOF

chmod +x start_display.sh

echo "Setup complete! Run: ~/dobby_display/start_display.sh"
