#!/bin/bash
# File: rpi_serial_setup.sh
# Description: Raspberry Pi Serial Port Configuration and Troubleshooting

echo "=== WAVEGO Raspberry Pi Serial Setup & Troubleshooting ==="
echo "Date: $(date)"
echo

# Check current user
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script needs to be run as root (use sudo)"
    exit 1
fi

echo "✅ Running as root - proceeding with serial setup..."
echo

# 1. Check available serial ports
echo "🔍 Checking available serial ports..."
ls -la /dev/tty* | grep -E "(ttyS|ttyAMA|ttyUSB|ttyACM)" || echo "No standard serial ports found"
echo

# 2. Check current serial configuration
echo "🔧 Current serial configuration:"
if [ -f /boot/config.txt ]; then
    echo "--- /boot/config.txt serial settings ---"
    grep -E "(enable_uart|dtoverlay.*uart)" /boot/config.txt || echo "No UART settings found"
elif [ -f /boot/firmware/config.txt ]; then
    echo "--- /boot/firmware/config.txt serial settings ---"
    grep -E "(enable_uart|dtoverlay.*uart)" /boot/firmware/config.txt || echo "No UART settings found"
fi
echo

# 3. Check if serial console is enabled
echo "📟 Checking serial console configuration:"
if systemctl is-enabled serial-getty@ttyS0.service >/dev/null 2>&1; then
    echo "⚠️  Serial console is ENABLED on ttyS0"
    echo "   This can interfere with robot communication!"
    echo "   Run: sudo systemctl disable serial-getty@ttyS0.service"
else
    echo "✅ Serial console is disabled on ttyS0"
fi

if systemctl is-enabled serial-getty@ttyAMA0.service >/dev/null 2>&1; then
    echo "⚠️  Serial console is ENABLED on ttyAMA0"
    echo "   This can interfere with robot communication!"
    echo "   Run: sudo systemctl disable serial-getty@ttyAMA0.service"
else
    echo "✅ Serial console is disabled on ttyAMA0"
fi
echo

# 4. Check cmdline.txt for console settings
echo "🖥️  Checking kernel command line for serial console:"
if [ -f /boot/cmdline.txt ]; then
    CMDLINE_FILE="/boot/cmdline.txt"
elif [ -f /boot/firmware/cmdline.txt ]; then
    CMDLINE_FILE="/boot/firmware/cmdline.txt"
else
    CMDLINE_FILE=""
fi

if [ -n "$CMDLINE_FILE" ]; then
    if grep -q "console=serial" "$CMDLINE_FILE" || grep -q "console=tty" "$CMDLINE_FILE"; then
        echo "⚠️  Serial console found in $CMDLINE_FILE"
        echo "   Content: $(cat $CMDLINE_FILE)"
        echo "   You may need to remove console=ttyS0,115200 or similar"
    else
        echo "✅ No serial console configured in $CMDLINE_FILE"
    fi
fi
echo

# 5. Test serial ports
echo "🧪 Testing serial port accessibility..."

test_ports=("/dev/ttyS0" "/dev/ttyAMA0" "/dev/ttyUSB0" "/dev/ttyACM0")

for port in "${test_ports[@]}"; do
    if [ -e "$port" ]; then
        echo -n "Testing $port: "
        if [ -r "$port" ] && [ -w "$port" ]; then
            echo "✅ Accessible (read/write)"
            
            # Try to get port info
            if command -v setserial >/dev/null 2>&1; then
                echo "   Info: $(setserial -g $port 2>/dev/null || echo 'Info not available')"
            fi
        else
            echo "❌ Not accessible (check permissions)"
            ls -la "$port"
        fi
    else
        echo "$port: ❌ Does not exist"
    fi
done
echo

# 6. Check user permissions
echo "👤 Checking user permissions for serial access..."
WAVEGO_USER=$(who am i | awk '{print $1}' 2>/dev/null || echo "devil")

if groups "$WAVEGO_USER" | grep -q dialout; then
    echo "✅ User $WAVEGO_USER is in dialout group"
else
    echo "⚠️  User $WAVEGO_USER is NOT in dialout group"
    echo "   Run: sudo usermod -a -G dialout $WAVEGO_USER"
    echo "   Then log out and back in"
fi
echo

# 7. GPIO/Hardware info
echo "🔌 Hardware information:"
if command -v pinout >/dev/null 2>&1; then
    echo "GPIO/UART pins:"
    pinout | grep -A5 -B5 UART || echo "UART info not available via pinout"
else
    echo "Install gpio package for detailed pin info: sudo apt install python3-gpiozero"
fi
echo

# 8. Recommendations
echo "💡 RECOMMENDATIONS FOR WAVEGO:"
echo "================================"
echo
echo "1. ENABLE UART (required for robot communication):"

if [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
elif [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
fi

if [ -n "$CONFIG_FILE" ]; then
    echo "   Add to $CONFIG_FILE:"
    echo "   enable_uart=1"
    echo "   dtoverlay=disable-bt  # Optional: disable Bluetooth to free up /dev/ttyAMA0"
fi
echo
echo "2. DISABLE SERIAL CONSOLE (prevents interference):"
echo "   sudo systemctl disable serial-getty@ttyS0.service"
echo "   sudo systemctl disable serial-getty@ttyAMA0.service"
echo
echo "3. ADD USER TO DIALOUT GROUP:"
echo "   sudo usermod -a -G dialout $WAVEGO_USER"
echo
echo "4. REBOOT after making changes:"
echo "   sudo reboot"
echo
echo "5. TEST WAVEGO SERVICE after reboot:"
echo "   sudo systemctl restart wavego.service"
echo "   sudo journalctl -u wavego.service -f"
echo

# 9. Quick fix option
echo "🚀 QUICK FIX - Apply common fixes automatically? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Applying quick fixes..."
    
    # Add enable_uart to config.txt if not present
    if [ -n "$CONFIG_FILE" ]; then
        if ! grep -q "enable_uart=1" "$CONFIG_FILE"; then
            echo "enable_uart=1" >> "$CONFIG_FILE"
            echo "✅ Added enable_uart=1 to $CONFIG_FILE"
        fi
    fi
    
    # Disable serial consoles
    systemctl disable serial-getty@ttyS0.service 2>/dev/null && echo "✅ Disabled serial console on ttyS0"
    systemctl disable serial-getty@ttyAMA0.service 2>/dev/null && echo "✅ Disabled serial console on ttyAMA0"
    
    # Add user to dialout group
    usermod -a -G dialout "$WAVEGO_USER" 2>/dev/null && echo "✅ Added $WAVEGO_USER to dialout group"
    
    echo
    echo "🎉 Quick fixes applied! REBOOT required:"
    echo "   sudo reboot"
else
    echo "Skipping automatic fixes. Apply manually as needed."
fi

echo
echo "=== Serial Setup Check Complete ==="