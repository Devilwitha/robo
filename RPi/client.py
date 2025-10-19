import asyncio
import websockets
import pygame
import time

# --- Configuration ---
# The IP address of the WAVEGO robot server
SERVER_IP = "192.168.178.52"
SERVER_PORT = 8888
WEBSOCKET_URI = f"ws://{SERVER_IP}:{SERVER_PORT}"

# --- Joystick Axis Configuration ---
# These values will likely need to be adjusted for your Thrustmaster T248.
# Use the 'check_joystick.py' script to find the correct axis numbers.
STEERING_AXIS = 0  # Axis for steering (left/right)
ACCELERATOR_AXIS = 2 # Axis for the accelerator pedal
BRAKE_AXIS = 3     # Axis for the brake pedal

# --- Control Thresholds ---
# How far you need to turn the wheel or press the pedal to trigger a command.
STEERING_THRESHOLD = 0.5  # Range is -1.0 to 1.0
PEDAL_THRESHOLD = 0.5     # Range is -1.0 to 1.0 (unpressed to fully pressed)

async def send_command(websocket, command):
    """Sends a command to the WebSocket server."""
    print(f"Sending command: {command}")
    await websocket.send(command)

async def control_robot():
    """Main function to connect to the server and control the robot."""
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("Error: No joystick or controller detected.")
        return

    # Initialize the first detected joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Initialized Joystick: {joystick.get_name()}")

    async with websockets.connect(WEBSOCKET_URI) as websocket:
        print(f"Successfully connected to robot server at {WEBSOCKET_URI}")

        # Keep track of the last command to avoid sending duplicates
        last_fb_command = None # Forward/Backward
        last_lr_command = None # Left/Right

        running = True
        while running:
            # Process Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- Read Joystick Axes ---
            steering = joystick.get_axis(STEERING_AXIS)
            accelerator = joystick.get_axis(ACCELERATOR_AXIS)
            brake = joystick.get_axis(BRAKE_AXIS)

            # --- Map Axes to Commands ---

            # Forward/Backward control
            current_fb_command = None
            if brake > PEDAL_THRESHOLD:
                current_fb_command = "backward"
            elif accelerator > PEDAL_THRESHOLD:
                current_fb_command = "forward"
            else:
                current_fb_command = "DS" # Drive Stop

            # Left/Right control
            current_lr_command = None
            if steering > STEERING_THRESHOLD:
                current_lr_command = "right"
            elif steering < -STEERING_THRESHOLD:
                current_lr_command = "left"
            else:
                current_lr_command = "TS" # Turn Stop

            # --- Send Commands if Changed ---
            if current_fb_command != last_fb_command:
                await send_command(websocket, current_fb_command)
                last_fb_command = current_fb_command

            if current_lr_command != last_lr_command:
                await send_command(websocket, current_lr_command)
                last_lr_command = current_lr_command

            # Small delay to prevent flooding the server
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    try:
        asyncio.run(control_robot())
    except KeyboardInterrupt:
        print("Client stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")