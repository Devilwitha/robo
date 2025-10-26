#!/bin/bash

# WAVEGO Installation Script
# This script provides a reliable, modern way to set up the WAVEGO software.

# Ensure the script is run as a regular user, not root.
if [ "$EUID" -eq 0 ]; then
  echo "Please do not run this script as root. It will ask for sudo password when needed."
  exit 1
fi

echo "--- Starting WAVEGO Setup ---"

# --- Step 1: Install System Dependencies ---
echo "--> Installing required system packages with apt..."
sudo apt-get update
sudo apt-get install -y \
    python3-venv \
    python3-pip \
    git \
    libcap-dev \
    python3-libcamera
echo "--> System packages installed."

# --- Step 2: Set Up Python Virtual Environment ---
echo "--> Creating Python virtual environment..."
# Create venv in project root (not in RPi subdirectory)
cd "$(dirname "$0")"
python3 -m venv --system-site-packages venv
echo "--> Virtual environment created."

# --- Step 3: Install Python Packages ---
echo "--> Activating virtual environment and installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install psutil websockets Flask-Cors opencv-python pyserial imutils picamera2 pygame numpy
deactivate
echo "--> Python packages installed."

# --- Step 4: Set up and Enable the systemd Service ---
echo "--> Setting up the systemd service for auto-start..."
# Copy the corrected service file from RPi directory
sudo cp RPi/wavego.service /etc/systemd/system/wavego.service
sudo systemctl daemon-reload
sudo systemctl enable --now wavego.service
echo "--> systemd service enabled and started."

# --- Final Step: Configuration and Reboot ---
echo ""
echo "--- SETUP COMPLETE ---"
echo "The WAVEGO service has been started and will launch automatically on boot."
echo "Please REBOOT your Raspberry Pi now to ensure all changes take effect."
echo "To reboot now, run: sudo reboot"