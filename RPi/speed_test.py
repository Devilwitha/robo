#!/usr/bin/env python3
# File name   : speed_test.py
# Description : Test script for speed control debugging

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import robot
from camera_opencv import commandAct

def test_speed_control():
    print("=== Speed Control Test ===")
    
    # Test 1: Check initial speed
    print(f"Initial speed: {robot.getSpeed()}")
    
    # Test 2: Set speed using robot.speedSet
    print("\nTesting robot.speedSet(50)...")
    result = robot.speedSet(50)
    print(f"Result: {result}")
    print(f"Current speed: {robot.getSpeed()}")
    
    # Test 3: Test commandAct with wsB command
    print("\nTesting commandAct('wsB 75')...")
    commandAct('wsB 75')
    print(f"Current speed: {robot.getSpeed()}")
    
    # Test 4: Test movement with different speeds
    print("\nTesting movement commands...")
    robot.speedSet(25)
    print(f"Speed set to 25, testing forward...")
    robot.forward()
    
    print(f"Speed set to 75, testing left...")
    robot.speedSet(75)
    robot.left()
    
    # Test 5: Test invalid speed values
    print("\nTesting invalid speed values...")
    result1 = robot.speedSet(0)
    print(f"speedSet(0): {result1}")
    
    result2 = robot.speedSet(150)
    print(f"speedSet(150): {result2}")
    
    print(f"Final speed: {robot.getSpeed()}")
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_speed_control()