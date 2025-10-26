#!/bin/bash
# setup_wavego.sh - Configure Raspberry Pi for WAVEGO robot

echo "=== WAVEGO Raspberry Pi Setup Script ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "1. Enabling UART/Serial communication..."

# Check if raspi-config is available
if command -v raspi-config >/dev/null 2>&1; then
    echo "   Using raspi-config to enable serial..."
    # Enable serial hardware, disable serial console
    raspi-config nonint do_serial 2
else
    echo "   Manually configuring UART in config.txt..."
    
    # Backup config.txt
    if [ -f /boot/config.txt ]; then
        CONFIG_FILE="/boot/config.txt"
    elif [ -f /boot/firmware/config.txt ]; then
        CONFIG_FILE="/boot/firmware/config.txt"
    else
        echo "   Error: Could not find config.txt"
        exit 1
    fi
    
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Add UART configuration if not present
    if ! grep -q "enable_uart=1" "$CONFIG_FILE"; then
        echo "enable_uart=1" >> "$CONFIG_FILE"
        echo "   Added enable_uart=1 to $CONFIG_FILE"
    else
        echo "   UART already enabled in $CONFIG_FILE"
    fi
fi

echo
echo "2. Configuring serial console..."

# Disable serial console on ttyS0/ttyAMA0
if [ -f /boot/cmdline.txt ]; then
    CMDLINE_FILE="/boot/cmdline.txt"
elif [ -f /boot/firmware/cmdline.txt ]; then
    CMDLINE_FILE="/boot/firmware/cmdline.txt"
else
    echo "   Warning: Could not find cmdline.txt"
    CMDLINE_FILE=""
fi

if [ -n "$CMDLINE_FILE" ]; then
    cp "$CMDLINE_FILE" "$CMDLINE_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove console=serial references
    sed -i 's/console=serial[0-9],[0-9]*\s*//g' "$CMDLINE_FILE"
    sed -i 's/console=ttyAMA[0-9],[0-9]*\s*//g' "$CMDLINE_FILE"
    sed -i 's/console=ttyS[0-9],[0-9]*\s*//g' "$CMDLINE_FILE"
    
    echo "   Removed serial console from boot parameters"
fi

echo
echo "3. Setting up serial device permissions..."

# Add dialout group permissions
usermod -a -G dialout devil 2>/dev/null || echo "   User 'devil' not found, skipping group assignment"

# Create udev rule for serial devices
cat > /etc/udev/rules.d/99-wavego-serial.rules << 'EOF'
# WAVEGO Robot serial device permissions
SUBSYSTEM=="tty", KERNEL=="ttyS0", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNEL=="ttyAMA0", GROUP="dialout", MODE="0666" 
SUBSYSTEM=="tty", KERNEL=="serial0", GROUP="dialout", MODE="0666"
SUBSYSTEM=="tty", KERNEL=="serial1", GROUP="dialout", MODE="0666"
EOF

echo "   Created udev rules for serial device permissions"

echo
echo "4. Installing/updating systemd service..."

# Copy service file to systemd directory
SERVICE_FILE="/etc/systemd/system/wavego.service"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$CURRENT_DIR/wavego.service" ]; then
    cp "$CURRENT_DIR/wavego.service" "$SERVICE_FILE"
    echo "   Copied wavego.service to systemd"
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable wavego.service
    echo "   Enabled wavego service"
else
    echo "   Warning: wavego.service not found in current directory"
fi

echo
echo "5. Installing Python dependencies..."

# Install system packages
apt update
apt install -y python3-serial python3-opencv python3-flask

# Install pip packages if needed
python3 -m pip install --upgrade pip
python3 -m pip install pyserial opencv-python flask

echo
echo "6. Testing serial configuration..."

# Run serial test if available
if [ -f "$CURRENT_DIR/test_serial.py" ]; then
    echo "   Running serial diagnostic..."
    python3 "$CURRENT_DIR/test_serial.py"
else
    echo "   Serial test script not found"
fi

echo
echo "=== Setup Complete ==="
echo
echo "IMPORTANT: You need to REBOOT for serial changes to take effect!"
echo
echo "After reboot:"
echo "1. Check serial status: python3 test_serial.py"
echo "2. Test robot module: python3 test_robot.py"
echo "3. Start service: sudo systemctl start wavego.service"
echo "4. Check service status: sudo systemctl status wavego.service"
echo
echo "To view logs: sudo journalctl -u wavego.service -f"
echo
read -p "Reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting..."
    reboot
else
    echo "Remember to reboot manually for changes to take effect!"
fi