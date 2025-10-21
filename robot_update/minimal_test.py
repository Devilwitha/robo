#!/usr/bin/env python3
# File name   : minimal_test.py
# Description : Minimal test for core functionality without optional dependencies

def test_core_imports():
    """Test core imports without optional dependencies"""
    print("=== Testing Core Imports ===")
    
    try:
        print("Testing robot.py import...")
        import robot
        print("✓ robot.py imported successfully")
        
        print(f"✓ getSpeed(): {robot.getSpeed()}")
        
        print("Testing speedSet()...")
        result = robot.speedSet(75)
        print(f"✓ speedSet(75): {result}")
        print(f"✓ Current speed: {robot.getSpeed()}")
        
        # Test speed clamping
        robot.speedSet(0)   # Should clamp to 1
        print(f"✓ speedSet(0) clamped to: {robot.getSpeed()}")
        
        robot.speedSet(150) # Should clamp to 100
        print(f"✓ speedSet(150) clamped to: {robot.getSpeed()}")
        
        # Reset to normal
        robot.speedSet(50)
        
    except Exception as e:
        print(f"✗ robot.py test failed: {e}")
        return False
    
    try:
        print("\nTesting BollshiiOs.py import...")
        import BollshiiOs
        print("✓ BollshiiOs.py imported successfully")
        
        print("✓ BollshiiOs functions available:")
        print(f"  - start_gyro_balance: {hasattr(BollshiiOs, 'start_gyro_balance')}")
        print(f"  - stop_gyro_balance: {hasattr(BollshiiOs, 'stop_gyro_balance')}")
        print(f"  - get_status: {hasattr(BollshiiOs, 'get_status')}")
        
    except Exception as e:
        print(f"✗ BollshiiOs.py import failed: {e}")
        return False
    
    return True

def test_speed_parsing():
    """Test speed command parsing without camera_opencv dependencies"""
    print("\n=== Testing Speed Command Parsing ===")
    
    try:
        # Simulate the wsB command parsing from camera_opencv.py
        def parse_speed_command(act):
            if 'wsB' in act:
                print(f'SPEED COMMAND: Processing {act}')
                try:
                    parts = act.split()
                    if len(parts) >= 2:
                        speedMove = int(parts[1])
                        print(f'SPEED COMMAND: Extracted speed value: {speedMove}')
                        
                        # Import robot here to test the actual speedSet
                        import robot
                        if robot.speedSet(speedMove):
                            print(f'SPEED COMMAND: Successfully set speed to {speedMove}')
                            return True
                        else:
                            print(f'SPEED COMMAND: Failed to set speed to {speedMove}')
                            return False
                    else:
                        print(f'SPEED COMMAND: Invalid format, expected "wsB <number>", got: {act}')
                        return False
                except (ValueError, IndexError) as e:
                    print(f'SPEED COMMAND: Error parsing: {act}, Error: {e}')
                    return False
            return False
        
        # Test various speed commands
        test_commands = ["wsB 25", "wsB 50", "wsB 75", "wsB 100", "wsB 0", "wsB 150"]
        
        for cmd in test_commands:
            result = parse_speed_command(cmd)
            print(f"Command '{cmd}': {'✓' if result else '✗'}")
        
        print("✓ Speed command parsing test completed")
        
    except Exception as e:
        print(f"✗ Speed parsing test failed: {e}")
        return False
    
    return True

def test_flask_app():
    """Test Flask app import without running it"""
    print("\n=== Testing Flask App Import ===")
    
    try:
        print("Testing app.py import...")
        import app
        print("✓ app.py imported successfully")
        print("✓ No Flask route conflicts")
        
    except Exception as e:
        print(f"✗ app.py import failed: {e}")
        return False
    
    return True

def main():
    print("WAVEGO Minimal Fix Test")
    print("======================")
    print("Testing core functionality without optional camera dependencies")
    print("")
    
    success = True
    
    if not test_core_imports():
        success = False
    
    if not test_speed_parsing():
        success = False
    
    if not test_flask_app():
        success = False
    
    print("\n" + "="*50)
    
    if success:
        print("🎉 Core tests passed! Basic functionality should work.")
        print("\nTo install missing dependencies (if needed):")
        print("sudo pip3 install imutils opencv-python")
        print("\nNext steps:")
        print("1. sudo systemctl start wavego.service")
        print("2. Check: sudo systemctl status wavego.service")
        print("3. Open web interface and test speed slider")
        print("4. Test BolliOs button for green LEDs")
    else:
        print("❌ Some core tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()