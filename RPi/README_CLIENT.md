# WAVEGO Thrustmaster Client Setup

This document explains how to set up a second Raspberry Pi to act as a remote controller for the WAVEGO robot, using a Thrustmaster T248 racing wheel (or a similar joystick/controller).

## Setup Overview

*   **Robot Pi**: The main Raspberry Pi connected to the WAVEGO robot hardware, running the `wavego.service`.
*   **Client Pi**: A separate Raspberry Pi connected to your Thrustmaster T248 via USB. This Pi runs the `client.py` script.

The Client Pi reads the inputs from your controller and sends them over the network to the Robot Pi.

## Step 1: Client Pi Installation

On your second Raspberry Pi (the client), perform the following steps.

1.  **Install System Dependencies**:
    `pygame` requires some system libraries to function. Open a terminal and run:
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
    We will create a virtual environment to keep the dependencies clean.
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

## Step 2: Configure Your Controller

Every controller model can have a different layout for its axes and buttons. You need to find the correct numbers for your Thrustmaster T248.

1.  **Connect the Controller**: Plug your Thrustmaster T248 into a USB port on the Client Pi.

2.  **Run the Checker Script**: Make sure your virtual environment is active (`source venv/bin/activate`) and run the helper script:
    ```bash
    python check_joystick.py
    ```

3.  **Identify Your Axes**: The script will print the real-time status of all axes.
    *   Turn the steering wheel left and right and note which `Axis X` number changes. This is your `STEERING_AXIS`.
    *   Press the accelerator pedal and note which `Axis Y` number changes. This is your `ACCELERATOR_AXIS`.
    *   Press the brake pedal and note which `Axis Z` number changes. This is your `BRAKE_AXIS`.

4.  **Edit `client.py`**: Open the main client script for editing:
    ```bash
    nano client.py
    ```

5.  **Update Configuration**: Find the "Joystick Axis Configuration" section at the top of the file and replace the placeholder numbers with the correct axis numbers you found.
    ```python
    # Example:
    STEERING_AXIS = 0
    ACCELERATOR_AXIS = 4
    BRAKE_AXIS = 5
    ```
    Save and exit the editor (Ctrl+X, Y, Enter).

## Step 3: Run the Client

You are now ready to control the robot.

1.  **Ensure the Robot is On**: Your main WAVEGO robot and its Raspberry Pi must be powered on and the `wavego.service` must be running.

2.  **Start the Client**: On your Client Pi (with the venv active), run the main client script:
    ```bash
    python client.py
    ```

The script will attempt to connect to the robot at `ws://192.168.178.52:8888`. If successful, you will see a "Successfully connected" message. You can now control the WAVEGO robot using your Thrustmaster T248.

To stop the client, press `Ctrl+C` in the terminal.