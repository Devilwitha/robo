#!/usr/bin/env python3
"""
Debug script for Motion Tracking issues
"""

def test_imports():
    print("=== Testing Imports ===")
    
    # Test BollshiiOs import
    try:
        import BollshiiOs
        print("✅ BollshiiOs imported successfully")
        print(f"   gyro_balance_active: {getattr(BollshiiOs, 'gyro_balance_active', 'NOT_FOUND')}")
        print(f"   Available functions: {[f for f in dir(BollshiiOs) if not f.startswith('_')]}")
    except ImportError as e:
        print(f"❌ BollshiiOs import failed: {e}")
        return False
    
    # Test MotionTracker import
    try:
        import MotionTracker
        print("✅ MotionTracker imported successfully")
        print(f"   Available functions: {[f for f in dir(MotionTracker) if not f.startswith('_')]}")
        
        # Test motion_tracker instance
        if hasattr(MotionTracker, 'motion_tracker'):
            tracker = MotionTracker.motion_tracker
            print(f"   motion_tracker.is_active: {tracker.is_active}")
        else:
            print("   motion_tracker instance not found")
            
    except ImportError as e:
        print(f"❌ MotionTracker import failed: {e}")
        return False
    
    return True

def test_bollios_status():
    print("\n=== Testing BolliOs Status ===")
    
    try:
        import BollshiiOs
        
        print(f"Current status: {BollshiiOs.get_status()}")
        
        # Test activation
        print("Testing BolliOs activation...")
        BollshiiOs.start_gyro_balance()
        print(f"After start: gyro_balance_active = {BollshiiOs.gyro_balance_active}")
        
        # Wait a moment
        import time
        time.sleep(1)
        
        print(f"Status check: {BollshiiOs.get_status()}")
        
        return True
        
    except Exception as e:
        print(f"❌ BolliOs status test failed: {e}")
        return False

def test_motion_tracking():
    print("\n=== Testing Motion Tracking ===")
    
    try:
        import MotionTracker
        
        # Test start motion tracking
        print("Testing start_motion_tracking...")
        result = MotionTracker.start_motion_tracking()
        print(f"Start result: {result}")
        
        if hasattr(MotionTracker, 'motion_tracker'):
            tracker = MotionTracker.motion_tracker
            print(f"Tracker is_active: {tracker.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Motion Tracking test failed: {e}")
        return False

def simulate_camera_command():
    print("\n=== Simulating Camera Command ===")
    
    try:
        import camera_opencv
        
        # Test the command that should work
        print("Testing camera_opencv.commandInput('motionTracking')...")
        camera_opencv.commandInput('motionTracking')
        
        return True
        
    except Exception as e:
        print(f"❌ Camera command test failed: {e}")
        return False

def main():
    print("🔍 Motion Tracking Debug Tool")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_imports,
        test_bollios_status,
        test_motion_tracking,
        simulate_camera_command
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🎯 Debug Results:")
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    if all(results):
        print("\n🎉 All tests passed! Motion tracking should work.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()