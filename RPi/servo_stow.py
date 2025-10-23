#!/usr/bin/env python3
# File name   : servo_stow.py
# Description : Servo stowing script for WAVEGO robot storage
# Author      : WAVEGO Enhanced

import time
import sys
import os

# Add the current directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import robot
    from camera_opencv import commandAct
except ImportError as e:
    print(f"Warning: Could not import robot modules: {e}")
    print("Running in simulation mode...")
    def commandAct(cmd, value=None):
        print(f"SIMULATION: Would execute command: {cmd} with value: {value}")

class ServoStow:
    def __init__(self):
        """Initialize servo stowing system"""
        self.stow_positions = {
            'camera_pan': 0,     # Center position for camera pan servo
            'camera_tilt': 0,    # Center position for camera tilt servo
            'head_servo': 90,    # Neutral position for head servo
            'arm_servo': 45,     # Safe storage position for arm
        }
        self.stow_speed = 50     # Slow speed for safe movements
        
    def set_servo_speed(self, speed=50):
        """Set servo movement speed for smooth operation"""
        try:
            commandAct(f'wsAD{speed}')  # Set speed for servo group A-D
            time.sleep(0.1)
            commandAct(f'wsBC{speed}')  # Set speed for servo group B-C
            time.sleep(0.1)
            print(f"Servo speed set to {speed}")
        except Exception as e:
            print(f"Error setting servo speed: {e}")
    
    def move_to_center(self):
        """Move camera servos to center position"""
        try:
            print("Moving camera to center position...")
            commandAct('lookcenter')
            time.sleep(1.0)
            print("Camera centered")
        except Exception as e:
            print(f"Error centering camera: {e}")
    
    def move_head_neutral(self):
        """Move head servo to neutral position"""
        try:
            print("Moving head to neutral position...")
            commandAct('up')
            time.sleep(1.0)
            print("Head in neutral position")
        except Exception as e:
            print(f"Error moving head: {e}")
    
    def stow_all_servos(self):
        """Execute complete servo stowing sequence"""
        print("=== SERVO STOWING SEQUENCE STARTED ===")
        
        try:
            # Step 1: Set slow speed for safe movements
            print("Step 1: Setting servo speed...")
            self.set_servo_speed(self.stow_speed)
            
            # Step 2: Move camera to center
            print("Step 2: Centering camera...")
            self.move_to_center()
            
            # Step 3: Move head to neutral
            print("Step 3: Moving head to neutral...")
            self.move_head_neutral()
            
            # Step 4: Additional servo commands for complete stowing
            print("Step 4: Additional servo positioning...")
            
            # Stop any ongoing movements
            commandAct('stop')
            time.sleep(0.5)
            
            # Ensure all servos are in safe positions
            commandAct('wsAD0')   # Additional positioning command
            time.sleep(0.2)
            commandAct('wsBC0')   # Additional positioning command
            time.sleep(0.2)
            
            print("=== SERVO STOWING SEQUENCE COMPLETED ===")
            print("Robot is now in storage position")
            return True
            
        except Exception as e:
            print(f"=== SERVO STOWING FAILED ===")
            print(f"Error during stowing sequence: {e}")
            return False
    
    def emergency_stop(self):
        """Emergency stop all servo movements"""
        try:
            print("EMERGENCY STOP: Stopping all servo movements...")
            commandAct('stop')
            print("All servo movements stopped")
        except Exception as e:
            print(f"Error during emergency stop: {e}")

def main():
    """Main function for standalone execution"""
    print("WAVEGO Robot Servo Stowing Script")
    print("=================================")
    
    stow_system = ServoStow()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'stow':
            success = stow_system.stow_all_servos()
            sys.exit(0 if success else 1)
        elif command == 'center':
            stow_system.move_to_center()
        elif command == 'neutral':
            stow_system.move_head_neutral()
        elif command == 'stop':
            stow_system.emergency_stop()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: stow, center, neutral, stop")
            sys.exit(1)
    else:
        # Default action: full stowing sequence
        success = stow_system.stow_all_servos()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()