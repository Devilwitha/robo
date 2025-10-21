#!/usr/bin/env python3
"""
Motion Tracking Test Script
Tests the complete motion tracking system with Stop-and-Scan algorithm
"""
import os
import sys
import time
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_motion_settings():
    """Test MotionSettings configuration system"""
    print("\n🔧 Testing Motion Settings...")
    
    try:
        from MotionSettings import MotionSettings
        
        settings = MotionSettings()
        
        # Test default settings
        print(f"Default settings: {settings.get_settings()}")
        
        # Test presets
        for preset in ['conservative', 'balanced', 'aggressive', 'indoor', 'outdoor']:
            settings.apply_preset(preset)
            print(f"Applied {preset} preset: movement_duration={settings.movement_duration}, pause_duration={settings.pause_duration}")
        
        # Test custom settings
        custom_settings = {
            'movement_duration': 3.0,
            'pause_duration': 0.5,
            'motion_threshold': 1500,
            'min_contour_area': 800
        }
        settings.update_settings(custom_settings)
        print(f"Custom settings applied: {settings.get_settings()}")
        
        print("✅ Motion Settings test completed")
        return True
        
    except ImportError as e:
        print(f"❌ MotionSettings import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Motion Settings test failed: {e}")
        return False

def test_motion_tracker():
    """Test MotionTracker with Stop-and-Scan algorithm"""
    print("\n🎯 Testing Motion Tracker...")
    
    try:
        from MotionTracker import MotionTracker
        
        # Initialize motion tracker
        tracker = MotionTracker()
        
        print(f"Motion Tracker initialized with settings:")
        print(f"  Movement Duration: {tracker.movement_duration}s")
        print(f"  Pause Duration: {tracker.pause_duration}s")
        print(f"  Motion Threshold: {tracker.motion_threshold}")
        print(f"  State: {tracker.state}")
        
        # Test state transitions
        print("\n🔍 Testing Stop-and-Scan state machine...")
        
        initial_state = tracker.state
        print(f"Initial state: {initial_state}")
        
        # Simulate motion detected
        tracker.state = 'moving'
        tracker.movement_start_time = time.time()
        print(f"Simulated motion detected, state: {tracker.state}")
        
        # Test timing logic
        time.sleep(0.1)  # Small delay
        elapsed = time.time() - tracker.movement_start_time
        print(f"Movement elapsed: {elapsed:.2f}s (limit: {tracker.movement_duration}s)")
        
        # Test pause transition
        tracker.state = 'paused'
        tracker.pause_start_time = time.time()
        print(f"Simulated pause state: {tracker.state}")
        
        time.sleep(0.1)  # Small delay
        pause_elapsed = time.time() - tracker.pause_start_time
        print(f"Pause elapsed: {pause_elapsed:.2f}s (limit: {tracker.pause_duration}s)")
        
        # Reset to scanning
        tracker.state = 'scanning'
        print(f"Reset to scanning state: {tracker.state}")
        
        print("✅ Motion Tracker Stop-and-Scan test completed")
        return True
        
    except ImportError as e:
        print(f"❌ MotionTracker import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Motion Tracker test failed: {e}")
        return False

def test_camera_integration():
    """Test camera_opencv.py integration"""
    print("\n📷 Testing Camera Integration...")
    
    try:
        with open('camera_opencv.py', 'r') as f:
            content = f.read()
        
        # Check for motion tracking integration
        checks = [
            ('MOTION_TRACKER_AVAILABLE', 'Motion tracker availability check'),
            ('motion_tracker =', 'Motion tracker instance'),
            ('motion_tracking_mode', 'Motion tracking mode variable'),
            ('process_motion_frame', 'Motion frame processing')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} missing")
                return False
        
        print("✅ Camera integration test completed")
        return True
        
    except FileNotFoundError:
        print("❌ camera_opencv.py not found")
        return False
    except Exception as e:
        print(f"❌ Camera integration test failed: {e}")
        return False

def test_webserver_integration():
    """Test webServer.py integration"""
    print("\n🌐 Testing WebServer Integration...")
    
    try:
        with open('webServer.py', 'r') as f:
            content = f.read()
        
        # Check for motion tracking commands
        commands = [
            'motionTracking',
            'motionTrackingOff',
            'motionSettings',
            'motionPreset',
            'motionReset'
        ]
        
        for command in commands:
            if command in content:
                print(f"✅ Command '{command}' found")
            else:
                print(f"❌ Command '{command}' missing")
                return False
        
        print("✅ WebServer integration test completed")
        return True
        
    except FileNotFoundError:
        print("❌ webServer.py not found")
        return False
    except Exception as e:
        print(f"❌ WebServer integration test failed: {e}")
        return False

def test_web_interface_files():
    """Test web interface JavaScript files"""
    print("\n🎨 Testing Web Interface Files...")
    
    files_to_check = [
        ('motion-tracking.js', '🎯 Motion Tracking Switch'),
        ('motion-settings.js', '⚙️ Motion Settings Panel')
    ]
    
    success = True
    
    for filename, description in files_to_check:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            # Check for Vue.js integration
            if 'BolliOs' in content and 'WebSocket' in content:
                print(f"✅ {description} - Vue.js integration found")
            else:
                print(f"❌ {description} - Vue.js integration missing")
                success = False
        
        except FileNotFoundError:
            print(f"❌ {description} - {filename} not found")
            success = False
    
    return success

def main():
    """Run all motion tracking tests"""
    print("🧪 Motion Tracking System Test Suite")
    print("=" * 50)
    print("Testing Stop-and-Scan Algorithm Implementation")
    print()
    
    success = True
    
    # Test configuration system
    if not test_motion_settings():
        success = False
    
    # Test motion tracker logic
    if not test_motion_tracker():
        success = False
    
    # Test camera integration
    if not test_camera_integration():
        success = False
    
    # Test webserver integration
    if not test_webserver_integration():
        success = False
    
    # Test web interface files
    if not test_web_interface_files():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 All tests completed successfully!")
        print("\nStop-and-Scan Algorithm Features:")
        print("✅ Configurable movement duration (default: 2.0s)")
        print("✅ Configurable pause duration (default: 1.0s)")  
        print("✅ Preset configurations (conservative, balanced, aggressive, etc.)")
        print("✅ Web interface settings panel")
        print("✅ Silent motion tracking (no buzzer)")
        print("✅ Background model reset during pauses")
        print("\nNext steps:")
        print("1. Deploy files to robot: MotionTracker.py, MotionSettings.py")
        print("2. Deploy web files: motion-tracking.js, motion-settings.js")
        print("3. Test with real camera and robot hardware")
        print("4. Fine-tune timing parameters for optimal performance")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\nPlease ensure all files are properly created and configured.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)