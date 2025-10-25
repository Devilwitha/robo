import pygame
import time

# This helper script initializes a connected joystick and prints the status of its axes and buttons
# in real-time. This allows you to easily identify which axis or button number corresponds
# to which physical control on your Thrustmaster T248 (or any other controller).

# --- How to Use ---
# 1. Connect your Thrustmaster T248 to the Raspberry Pi.
# 2. Run this script: python check_joystick.py
# 3. The script will print the name of your controller.
# 4. Move the steering wheel, press the pedals, and press buttons one at a time.
# 5. Observe the output in the terminal. The values for the corresponding axis or button will change.
# 6. Note down the axis/button numbers for steering, accelerator, etc.
# 7. Open client.py and update the configuration variables at the top of the file with the numbers you found.

def check_joystick():
    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("Error: No joystick or controller detected. Please connect your controller.")
        return

    # Initialize the first detected joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"--- Joystick Checker Initialized ---")
    print(f"Joystick Name: {joystick.get_name()}")
    print(f"Number of Axes: {joystick.get_numaxes()}")
    print(f"Number of Buttons: {joystick.get_numbuttons()}")
    print(f"Number of Hats: {joystick.get_numhats()}")
    print("\nMove the steering wheel, press pedals, and press buttons to see their values change.")
    print("Press Ctrl+C to exit.")
    print("-" * 40)

    try:
        while True:
            # Process Pygame events to keep the connection alive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # --- Display Axis Status ---
            axis_states = []
            for i in range(joystick.get_numaxes()):
                axis_val = joystick.get_axis(i)
                # Format to always show sign and have a fixed width for better alignment
                axis_states.append(f"Axis {i}: {axis_val:+.4f}")

            # --- Display Button Status ---
            button_states = []
            for i in range(joystick.get_numbuttons()):
                button_val = joystick.get_button(i)
                button_states.append(f"Button {i}: {button_val}")

            # Print the states on a single line, overwriting the previous one
            # The '\r' character moves the cursor to the beginning of the line
            print(" | ".join(axis_states) + " | " + " | ".join(button_states), end='\r')

            # Small delay to keep the script from using 100% CPU
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n--- Exiting Joystick Checker ---")
    finally:
        pygame.quit()

if __name__ == "__main__":
    check_joystick()