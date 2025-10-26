# WAVEGO - Bionic Dog-Like Robot

WAVEGO is an open-source bionic dog-like robot powered by an ESP32 and a Raspberry Pi. This repository contains the Python software for the Raspberry Pi, enabling control and video streaming via a web interface.

This version has been updated to be compatible with modern Raspberry Pi OS releases (e.g., Debian 12 "Bookworm" and later).

## Prerequisites

*   **Hardware**:
    *   Raspberry Pi 4 or newer
    *   Raspberry Pi Camera Module
    *   Assembled WAVEGO robot hardware
*   **Software**:
    *   A fresh installation of **Raspberry Pi OS (64-bit)** is recommended. These instructions are not guaranteed to work on standard Debian or other operating systems.

## Installation

The setup process has been simplified into a single installation script.

### 1. Enable Camera and Serial Interfaces

Before running the installation, you must enable the necessary hardware interfaces on your Raspberry Pi.

1.  Open a terminal and run `sudo raspi-config`.
2.  Navigate to **3 Interface Options**.
3.  Select **I1 Legacy Camera** and choose **<Yes>** to enable legacy camera support.
4.  Go back to **3 Interface Options**.
5.  Select **I6 Serial Port**.
    *   When asked "Would you like a login shell to be accessible over serial?", choose **<No>**.
    *   When asked "Would you like the serial port hardware to be enabled?", choose **<Yes>**.
6.  Select **<Finish>** and reboot the Raspberry Pi when prompted.

### 2. Run the Installation Script

After rebooting, clone this repository and run the installation script.

```bash
# Clone the repository
git clone https://github.com/Devilwitha/robo.git
cd robo

# Make the installation script executable
chmod +x install.sh

# Run the script (do NOT use sudo)
./install.sh
```

The script will automatically:
*   Install all required system packages.
*   Create a dedicated Python virtual environment.
*   Install all necessary Python libraries.
*   Set up a `systemd` service to automatically start the robot's software on boot.

The script will prompt for your password (`sudo`) when needed. After it finishes, it is recommended to **reboot** one last time.

## Usage

After installation and reboot, the WAVEGO software will start automatically.

### Connecting to the Robot

1.  **Find the IP Address**: On your Raspberry Pi, open a terminal and find its IP address with the command:
    ```bash
    hostname -I
    ```
    It will look something like `192.168.1.XX`.

2.  **Access the Web Interface**: On a computer, phone, or tablet connected to the **same network**, open a web browser and navigate to:
    ```
    http://192.168.178.52:5000
    ```

You should now see the WAVEGO control interface with a live camera feed.

### Managing the Service

The robot's software runs as a background service called `wavego.service`. You can manage it with the following commands:

*   **Check the status**:
    ```bash
    sudo systemctl status wavego.service
    ```

*   **Restart the service** (e.g., after making code changes):
    ```bash
    sudo systemctl restart wavego.service
    ```

*   **Stop the service**:
    ```bash
    sudo systemctl stop wavego.service
    ```

*   **View live logs** for debugging:
    ```bash
    sudo journalctl -u wavego.service -f
    ```
