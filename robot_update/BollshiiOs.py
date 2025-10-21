#!/usr/bin/env python3
# File name   : BollshiiOs.py
# Description : Gyro balance control system for the robot
import time
import json
import serial
import threading
import robot

# Gyro balance mode state
gyro_balance_active = False
balance_thread = None
balance_running = False

def start_gyro_balance():
    """Start the gyro balance mode"""
    global gyro_balance_active, balance_thread, balance_running
    
    if not gyro_balance_active:
        gyro_balance_active = True
        balance_running = True
        print('BolliOs: Gyro balance mode activated (WITHOUT steady mode)')
        
        # Set LEDs to green immediately when activated
        robot.lightCtrl('green', 0)
        
        # Start balance thread
        balance_thread = threading.Thread(target=balance_loop)
        balance_thread.daemon = True
        balance_thread.start()
        
        # Audio feedback
        robot.buzzerCtrl(1, 0)
        time.sleep(0.1)
        robot.buzzerCtrl(0, 0)

def stop_gyro_balance():
    """Stop the gyro balance mode"""
    global gyro_balance_active, balance_running, balance_thread
    
    if gyro_balance_active:
        gyro_balance_active = False
        balance_running = False
        print('BolliOs: Gyro balance mode deactivated')
        
        # Also stop motion tracking when BolliOs is stopped
        try:
            import MotionTracker
            if hasattr(MotionTracker, 'motion_tracker') and MotionTracker.motion_tracker.is_active:
                MotionTracker.stop_motion_tracking()
                print("BolliOs: Motion Tracking also stopped (BolliOs deactivated)")
        except ImportError:
            pass  # Motion Tracker not available
        
        # Wait for thread to finish (with timeout)
        if balance_thread and balance_thread.is_alive():
            balance_thread.join(timeout=2.0)
            if balance_thread.is_alive():
                print('BolliOs: Warning - balance thread did not stop cleanly')
        
        # Stop all movements
        robot.stopLR()
        robot.stopFB()
        
        # Set LEDs to blue when deactivated
        robot.lightCtrl('blue', 0)
        print('BolliOs: LEDs set to BLUE (inactive)')
        
        # Audio feedback
        robot.buzzerCtrl(1, 0)
        time.sleep(0.1)
        robot.buzzerCtrl(0, 0)

def balance_loop():
    """Main balance loop - simulates gyro-based balancing without steady mode"""
    global balance_running
    
    print('BolliOs: Starting balance loop...')
    balance_cycles = 0
    
    # Ensure LEDs are green at start of balance loop
    robot.lightCtrl('green', 0)
    
    while balance_running:
        try:
            balance_cycles += 1
            
            # Keep LEDs green during active balancing
            robot.lightCtrl('green', 0)
            
            # Custom gyro balance logic WITHOUT steady mode
            # Instead of steady mode, implement simple balance movements
            # This prevents interference with motion tracking
            
            # Simple balance simulation - small adjustments only
            # In real implementation, this would read gyro data and make corrections
            
            # Status indication every 100 cycles (approximately every 10 seconds)
            if balance_cycles % 100 == 0:
                print(f'BolliOs: Balance active - cycle {balance_cycles}, LEDs: GREEN (NO STEADY)')
            
            # Longer delay for balance mode to prevent overloading
            time.sleep(0.1)
            
        except Exception as e:
            print(f"BolliOs: Error in balance loop: {e}")
            # On error, stop balancing gracefully
            robot.stopLR()
            robot.stopFB()
            robot.lightCtrl('red', 0)  # Red to indicate error
            time.sleep(0.5)
            break
    
    # Cleanup when exiting balance loop
    robot.stopLR()
    robot.stopFB()
    robot.lightCtrl('blue', 0)  # Blue when inactive
    print('BolliOs: Balance loop ended gracefully')

def toggle_gyro_balance():
    """Toggle gyro balance mode on/off"""
    if gyro_balance_active:
        stop_gyro_balance()
    else:
        start_gyro_balance()

def get_status():
    """Get current status of gyro balance mode"""
    return {
        'active': gyro_balance_active,
        'running': balance_running
    }

if __name__ == '__main__':
    # Test the module
    print("BolliOs: Testing gyro balance system...")
    start_gyro_balance()
    time.sleep(5)
    stop_gyro_balance()
    print("BolliOs: Test completed")