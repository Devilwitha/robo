#!/usr/bin/env python3
# File name   : quick_fix_test.py
# Description : Quick test to verify the fixes work

def test_imports():
    """Test if all imports work correctly"""
    print("=== Testing Imports ===")
    
    try:
        print("Testing robot.py import...")
        import robot
        print("✓ robot.py imported successfully")
        
        print(f"✓ getSpeed(): {robot.getSpeed()}")
        
        print("Testing speedSet()...")
        result = robot.speedSet(50)
        print(f"✓ speedSet(50): {result}")
        print(f"✓ Current speed: {robot.getSpeed()}")
        
    except Exception as e:
        print(f"✗ robot.py import failed: {e}")
        return False
    
    try:
        print("\nTesting camera_opencv.py import...")
        import camera_opencv
        print("✓ camera_opencv.py imported successfully")
        
    except Exception as e:
        print(f"✗ camera_opencv.py import failed: {e}")
        return False
    
    try:
        print("\nTesting BollshiiOs.py import...")
        import BollshiiOs
        print("✓ BollshiiOs.py imported successfully")
        
    except Exception as e:
        print(f"✗ BollshiiOs.py import failed: {e}")
        return False
    
    try:
        print("\nTesting app.py import...")
        import app
        print("✓ app.py imported successfully")
        
    except Exception as e:
        print(f"✗ app.py import failed: {e}")
        return False
    
    try:
        print("\nTesting webServer.py import...")
        import webServer
        print("✓ webServer.py imported successfully")
        
    except Exception as e:
        print(f"✗ webServer.py import failed: {e}")
        return False
    
    return True

def test_speed_commands():
    """Test speed command processing"""
    print("\n=== Testing Speed Commands ===")
    
    try:
        from camera_opencv import commandAct
        
        # Test speed commands
        test_commands = ["wsB 25", "wsB 50", "wsB 75", "wsB 100"]
        
        for cmd in test_commands:
            print(f"Testing command: {cmd}")
            commandAct(cmd, None)
            
        print("✓ All speed commands processed without errors")
        
    except Exception as e:
        print(f"✗ Speed command test failed: {e}")
        return False
    
    return True

def main():
    print("WAVEGO Speed Control Fix - Quick Test")
    print("=====================================")
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_speed_commands():
        success = False
    
    if success:
        print("\n🎉 All tests passed! The fix should work correctly.")
        print("\nNext steps:")
        print("1. sudo systemctl start wavego.service")
        print("2. Open web interface and test speed slider")
        print("3. Test BolliOs button for green LEDs")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()