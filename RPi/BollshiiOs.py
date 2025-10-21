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
        print('BolliOs: Gyro balance mode activated')
        
        # Start balance thread
        balance_thread = threading.Thread(target=balance_loop)
        balance_thread.daemon = True
        balance_thread.start()
        
        # Visual feedback
        robot.lightCtrl('green', 0)
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
        
        # Wait for thread to finish (with timeout)
        if balance_thread and balance_thread.is_alive():
            balance_thread.join(timeout=2.0)
            if balance_thread.is_alive():
                print('BolliOs: Warning - balance thread did not stop cleanly')
        
        # Stop all movements
        robot.stopLR()
        robot.stopFB()
        
        # Visual feedback
        robot.lightCtrl('blue', 0)
        robot.buzzerCtrl(1, 0)
        time.sleep(0.1)
        robot.buzzerCtrl(0, 0)

def balance_loop():
    """Main balance loop - simulates gyro-based balancing"""
    global balance_running
    
    print('BolliOs: Starting balance loop...')
    balance_cycles = 0
    
    while balance_running:
        try:
            balance_cycles += 1
            
            # Use the robot's steady mode for actual balancing
            # This should activate the gyro-based balance control on the Arduino
            robot.steadyMode()
            
            # Visual indication every 50 cycles (approximately every 5 seconds)
            if balance_cycles % 50 == 0:
                robot.lightCtrl('green', 0)
                print(f'BolliOs: Balance active - cycle {balance_cycles}')
                time.sleep(0.05)
                robot.lightCtrl('cyan', 0)
            
            # Longer delay for balance mode to prevent overloading the Arduino
            time.sleep(0.1)
            
        except Exception as e:
            print(f"BolliOs: Error in balance loop: {e}")
            # On error, stop balancing gracefully
            robot.stopLR()
            robot.stopFB()
            time.sleep(0.5)
            break
    
    # Cleanup when exiting balance loop
    robot.stopLR()
    robot.stopFB()
    robot.lightCtrl('blue', 0)
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