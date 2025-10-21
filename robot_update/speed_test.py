#!/usr/bin/env python3
"""
Speed Control Test Script
Tests the speed slider functionality independently
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import the modules
try:
    import robot
    from camera_opencv import commandAct
    
    print("=== SPEED CONTROL TEST ===")
    print("Testing speed control functionality...")
    
    # Test 1: Direct robot.speedSet function
    print("\n1. Testing direct robot.speedSet function:")
    test_speeds = [25, 50, 75, 100]
    
    for speed in test_speeds:
        print(f"   Setting speed to {speed}...")
        result = robot.speedSet(speed)
        current = robot.getSpeed()
        print(f"   Result: {result}, Current speed: {current}")
        
        if current == speed:
            print(f"   ✅ Speed {speed} set successfully")
        else:
            print(f"   ❌ Speed {speed} failed - expected {speed}, got {current}")
    
    # Test 2: CommandAct with wsB commands
    print("\n2. Testing commandAct with wsB commands:")
    wsb_commands = ["wsB 30", "wsB50", "wsB 80", "wsB100"]
    
    for cmd in wsb_commands:
        print(f"   Testing command: '{cmd}'")
        try:
            commandAct(cmd, None)
            current = robot.getSpeed()
            expected = int(cmd.replace('wsB', '').strip())
            
            if current == expected:
                print(f"   ✅ Command '{cmd}' successful - speed is {current}")
            else:
                print(f"   ❌ Command '{cmd}' failed - expected {expected}, got {current}")
        except Exception as e:
            print(f"   ❌ Command '{cmd}' caused error: {e}")
    
    # Test 3: Speed history
    print("\n3. Testing speed history:")
    history = robot.getSpeedHistory()
    print(f"   Speed history: {history}")
    print(f"   History length: {len(history)}")
    
    # Test 4: Current status
    print("\n4. Current robot status:")
    print(f"   Current speed: {robot.getSpeed()}")
    
    print("\n=== TEST COMPLETED ===")
    print("If you see ✅ symbols, the speed control is working correctly.")
    print("If you see ❌ symbols, there are issues with speed control.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure robot.py and camera_opencv.py are in the same directory")
except Exception as e:
    print(f"❌ Test error: {e}")