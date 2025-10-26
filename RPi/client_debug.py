import asyncio
import websockets
import pygame
import time

# --- Configuration ---
SERVER_IP = "192.168.178.52"
SERVER_PORT = 8888
WEBSOCKET_URI = f"ws://{SERVER_IP}:{SERVER_PORT}"

# --- Joystick Axis Configuration ---
STEERING_AXIS = 0  
ACCELERATOR_AXIS = 1 
BRAKE_AXIS = 6     

# --- Control Thresholds ---
STEERING_THRESHOLD = 0.5
PEDAL_THRESHOLD = 0.3  # Reduziert für bessere Erkennung

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
    print(f"Number of axes: {joystick.get_numaxes()}")
    print(f"Number of buttons: {joystick.get_numbuttons()}")

    # Show all axes for debugging
    print("\nAxis mapping - move controls and watch values:")
    for i in range(joystick.get_numaxes()):
        print(f"Axis {i}: {joystick.get_axis(i):.3f}")

    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print(f"Successfully connected to robot server at {WEBSOCKET_URI}")

            last_fb_command = None
            last_lr_command = None

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

                # Debug output every 10 loops
                if pygame.time.get_ticks() % 1000 < 50:  # roughly every second
                    print(f"Steering: {steering:.3f}, Accelerator: {accelerator:.3f}, Brake: {brake:.3f}")
                    print(f"All axes: {[joystick.get_axis(i) for i in range(min(8, joystick.get_numaxes()))]}")

                # --- Map Axes to Commands ---
                current_fb_command = None
                if brake > PEDAL_THRESHOLD:
                    current_fb_command = "backward"
                elif accelerator > PEDAL_THRESHOLD:
                    current_fb_command = "forward"
                else:
                    current_fb_command = "DS"

                current_lr_command = None
                if steering > STEERING_THRESHOLD:
                    current_lr_command = "right"
                elif steering < -STEERING_THRESHOLD:
                    current_lr_command = "left"
                else:
                    current_lr_command = "TS"

                # --- Send Commands if Changed ---
                if current_fb_command != last_fb_command:
                    await send_command(websocket, current_fb_command)
                    last_fb_command = current_fb_command

                if current_lr_command != last_lr_command:
                    await send_command(websocket, current_lr_command)
                    last_lr_command = current_lr_command

                await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(control_robot())
    except KeyboardInterrupt:
        print("Client stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")