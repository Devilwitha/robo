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

## Remote Control with a Joystick (Optional)

In addition to the web interface, you can control the WAVEGO robot using a joystick or racing wheel (e.g., a Thrustmaster T248) connected to a separate Raspberry Pi.

### Setup Overview

*   **Robot Pi**: The main Raspberry Pi on the WAVEGO robot, running the `wavego.service`.
*   **Client Pi**: A separate Raspberry Pi connected to your joystick via USB. This Pi runs the `RPi/client.py` script.

The Client Pi reads joystick inputs and sends them over the network to the Robot Pi.

### Step 1: Client Pi Installation

On your second Raspberry Pi (the client), perform the following steps.

1.  **Install System Dependencies**:
    `pygame` requires some system libraries. Open a terminal and run:
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv libsdl2-dev
    ```

2.  **Clone the Repository**:
    You need the client scripts on this Pi as well.
    ```bash
    git clone https://github.com/Devilwitha/robo.git
    cd robo/RPi
    ```

3.  **Set Up Python Environment**:
    Create a virtual environment to keep the dependencies clean.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Your terminal prompt should now start with `(venv)`.

4.  **Install Python Packages**:
    Install `pygame` for joystick support and `websockets` for network communication.
    ```bash
    pip install pygame websockets
    ```

### Step 2: Configure Your Controller

Every controller has a different layout. You need to find the correct axis and button numbers for your model.

1.  **Connect the Controller**: Plug your joystick or controller into a USB port on the Client Pi.

2.  **Run the Checker Script**: Make sure your virtual environment is active (`source venv/bin/activate`) and run the helper script:
    ```bash
    python check_joystick.py
    ```

3.  **Identify Your Axes**: The script will print the real-time status of all axes.
    *   Move the steering control left and right and note which `Axis X` number changes. This is your `STEERING_AXIS`.
    *   Move the accelerator/brake controls and note which `Axis Y/Z` numbers change. These are your `ACCELERATOR_AXIS` and `BRAKE_AXIS`.

4.  **Edit `client.py`**: Open the main client script for editing (`nano RPi/client.py`) and find the "Joystick Axis Configuration" section. Replace the placeholder numbers with the correct axis numbers you found.

### Step 3: Run the Client

1.  **Ensure the Robot is On**: Your WAVEGO robot and its Raspberry Pi must be powered on and the `wavego.service` must be running.

2.  **Start the Client**: On your Client Pi (with the venv active), run the main client script:
    ```bash
    python client.py
    ```

The script will attempt to connect to the robot. If successful, you can now control the WAVEGO robot using your joystick. To stop the client, press `Ctrl+C`.
