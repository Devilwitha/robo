#!/bin/bash
# File name   : update_system.sh  
# Description : Script to update the robot system with fixed files

echo "=== WAVEGO System Update Script ==="
echo "This script will update the robot system with speed control fixes"
echo ""

# Define source and target paths
SOURCE_DIR="/c/Users/devil/Documents/GitHub/WAVEGO-main/robo/RPi"
TARGET_DIR="/home/devil/WAVEGO/RPi"

echo "Source directory: $SOURCE_DIR"
echo "Target directory: $TARGET_DIR"
echo ""

# Check if we're on the robot system
if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory $TARGET_DIR not found!"
    echo "This script should be run on the robot system."
    exit 1
fi

echo "Stopping wavego service..."
sudo systemctl stop wavego.service

echo ""
echo "Backing up original files..."
sudo cp "$TARGET_DIR/robot.py" "$TARGET_DIR/robot.py.backup.$(date +%Y%m%d_%H%M%S)"
sudo cp "$TARGET_DIR/camera_opencv.py" "$TARGET_DIR/camera_opencv.py.backup.$(date +%Y%m%d_%H%M%S)"
sudo cp "$TARGET_DIR/webServer.py" "$TARGET_DIR/webServer.py.backup.$(date +%Y%m%d_%H%M%S)"
sudo cp "$TARGET_DIR/app.py" "$TARGET_DIR/app.py.backup.$(date +%Y%m%d_%H%M%S)"

echo ""
echo "Copying updated files..."

# Copy the main fixed files
echo "- Copying robot.py (with integrated SpeedManager)..."
sudo cp "$SOURCE_DIR/robot.py" "$TARGET_DIR/"

echo "- Copying camera_opencv.py (with improved speed handling)..."
sudo cp "$SOURCE_DIR/camera_opencv.py" "$TARGET_DIR/"

echo "- Copying webServer.py (with speed debugging)..."
sudo cp "$SOURCE_DIR/webServer.py" "$TARGET_DIR/"

echo "- Copying app.py (with speed API endpoints)..."
sudo cp "$SOURCE_DIR/app.py" "$TARGET_DIR/"

echo "- Copying BollshiiOs.py (gyro balance system)..."
sudo cp "$SOURCE_DIR/BollshiiOs.py" "$TARGET_DIR/"

echo "- Copying test files..."
sudo cp "$SOURCE_DIR/simple_speed_test.py" "$TARGET_DIR/"

echo ""
echo "Setting correct permissions..."
sudo chown devil:devil "$TARGET_DIR"/*.py
sudo chmod +x "$TARGET_DIR"/*.py

echo ""
echo "Testing speed parsing..."
cd "$TARGET_DIR"
python3 simple_speed_test.py

echo ""
echo "Starting wavego service..."
sudo systemctl start wavego.service

echo ""
echo "Checking service status..."
sleep 3
sudo systemctl status wavego.service --no-pager -l

echo ""
echo "=== Update Complete ==="
echo ""
echo "To check if everything works:"
echo "1. Check service status: sudo systemctl status wavego.service"
echo "2. View logs: journalctl -u wavego.service -f"
echo "3. Test speed API: curl http://localhost:5000/api/speed/status"
echo "4. Open web interface and test speed slider"
echo ""