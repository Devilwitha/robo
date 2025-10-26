#!/usr/bin/env python3
"""
Test the modified robot.py module to ensure it handles missing serial gracefully
"""

try:
    print("Testing robot module import...")
    import robot
    print("✓ Robot module imported successfully")
    
    print("\nTesting robot functions...")
    
    # Test movement functions
    print("Testing forward()...")
    robot.forward()
    
    print("Testing backward()...")
    robot.backward()
    
    print("Testing left()...")
    robot.left()
    
    print("Testing right()...")
    robot.right()
    
    print("Testing stop functions...")
    robot.stopLR()
    robot.stopFB()
    
    # Test look functions
    print("Testing look functions...")
    robot.lookUp()
    robot.lookDown()
    robot.lookLeft()
    robot.lookRight()
    robot.lookStopUD()
    robot.lookStopLR()
    
    # Test special functions
    print("Testing special functions...")
    robot.steadyMode()
    robot.jump()
    robot.handShake()
    
    # Test light control
    print("Testing light control...")
    robot.lightCtrl('red', None)
    robot.lightCtrl('off', None)
    
    # Test buzzer
    print("Testing buzzer...")
    robot.buzzerCtrl(1, None)
    
    print("\n✓ All robot functions tested successfully!")
    print("The web server should now start without serial errors.")
    
except Exception as e:
    print(f"✗ Error testing robot module: {e}")
    import traceback
    traceback.print_exc()