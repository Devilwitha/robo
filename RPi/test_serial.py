#!/usr/bin/env python3
"""
Test script to check serial port availability and configuration
"""
import os
import serial
import glob

def check_serial_ports():
    """Check available serial ports on the system"""
    print("=== Serial Port Diagnostic ===")
    
    # Check if common Raspberry Pi serial devices exist
    possible_ports = ["/dev/ttyS0", "/dev/ttyAMA0", "/dev/serial0", "/dev/serial1"]
    
    print("\n1. Checking for serial device files:")
    for port in possible_ports:
        exists = os.path.exists(port)
        print(f"   {port}: {'EXISTS' if exists else 'NOT FOUND'}")
        
        if exists:
            try:
                # Check permissions
                readable = os.access(port, os.R_OK)
                writable = os.access(port, os.W_OK)
                print(f"      Permissions: Read={readable}, Write={writable}")
                
                # Try to get device info
                stat_info = os.stat(port)
                print(f"      Device type: {stat_info.st_mode}")
                
            except Exception as e:
                print(f"      Error checking {port}: {e}")
    
    print("\n2. Scanning for all tty devices:")
    tty_devices = glob.glob("/dev/tty*")
    serial_devices = [dev for dev in tty_devices if any(x in dev for x in ['USB', 'ACM', 'AMA', 'S0', 'S1'])]
    
    if serial_devices:
        for device in sorted(serial_devices):
            print(f"   Found: {device}")
    else:
        print("   No obvious serial devices found")
    
    print("\n3. Testing serial connection:")
    for port in possible_ports:
        if os.path.exists(port):
            try:
                print(f"   Testing {port}...")
                ser = serial.Serial(port, 115200, timeout=1)
                print(f"   ✓ Successfully opened {port}")
                ser.close()
                return port
            except serial.SerialException as e:
                print(f"   ✗ Failed to open {port}: {e}")
            except Exception as e:
                print(f"   ✗ Unexpected error with {port}: {e}")
    
    print("\n4. Raspberry Pi configuration check:")
    config_files = ["/boot/config.txt", "/boot/firmware/config.txt"]
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   Checking {config_file}...")
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'enable_uart' in content:
                        print("   Found UART configuration in config.txt")
                        # Look for enable_uart line
                        for line in content.split('\n'):
                            if 'enable_uart' in line and not line.strip().startswith('#'):
                                print(f"      {line.strip()}")
                    else:
                        print("   No UART configuration found in config.txt")
                        print("   You may need to add 'enable_uart=1' to enable serial")
            except Exception as e:
                print(f"   Error reading {config_file}: {e}")
    
    return None

if __name__ == "__main__":
    working_port = check_serial_ports()
    
    if working_port:
        print(f"\n✓ Serial communication should work with {working_port}")
    else:
        print("\n✗ No working serial port found!")
        print("\nTroubleshooting steps:")
        print("1. Enable UART in Raspberry Pi configuration:")
        print("   sudo raspi-config -> Interface Options -> Serial -> Enable")
        print("2. Or add 'enable_uart=1' to /boot/config.txt")
        print("3. Make sure the Arduino/microcontroller is connected")
        print("4. Check if another process is using the serial port")
        print("5. Reboot after configuration changes")