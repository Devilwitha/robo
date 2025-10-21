#!/usr/bin/env python3
# File name   : speed_manager.py
# Description : Centralized speed management system

import json
import time
import threading

class SpeedManager:
    def __init__(self):
        self.current_speed = 100  # Default speed (1-100)
        self.lock = threading.Lock()
        self.speed_history = []
        
    def set_speed(self, speed):
        """Set movement speed with validation and logging"""
        with self.lock:
            # Validate speed range
            if not isinstance(speed, (int, float)):
                try:
                    speed = float(speed)
                except (ValueError, TypeError):
                    print(f"SpeedManager: Invalid speed type: {type(speed)}")
                    return False
            
            # Clamp to valid range
            speed = max(1, min(100, int(speed)))
            
            # Update current speed
            old_speed = self.current_speed
            self.current_speed = speed
            
            # Log speed change
            timestamp = time.time()
            self.speed_history.append((timestamp, old_speed, speed))
            
            # Keep only last 10 speed changes
            if len(self.speed_history) > 10:
                self.speed_history = self.speed_history[-10:]
            
            print(f"SpeedManager: Speed changed from {old_speed} to {speed}")
            return True
    
    def get_speed(self):
        """Get current speed"""
        with self.lock:
            return self.current_speed
    
    def get_speed_percentage(self):
        """Get speed as percentage (0.01 to 1.0)"""
        with self.lock:
            return self.current_speed / 100.0
    
    def get_history(self):
        """Get speed change history"""
        with self.lock:
            return self.speed_history.copy()
    
    def reset(self):
        """Reset to default speed"""
        self.set_speed(100)
        print("SpeedManager: Reset to default speed (100)")

# Global speed manager instance
speed_manager = SpeedManager()

def set_global_speed(speed):
    """Set global movement speed"""
    return speed_manager.set_speed(speed)

def get_global_speed():
    """Get global movement speed"""
    return speed_manager.get_speed()

def get_global_speed_percentage():
    """Get global speed as percentage"""
    return speed_manager.get_speed_percentage()

if __name__ == "__main__":
    # Test the speed manager
    print("Testing SpeedManager...")
    
    print(f"Initial speed: {get_global_speed()}")
    
    set_global_speed(50)
    print(f"After setting 50: {get_global_speed()}")
    
    set_global_speed("75")
    print(f"After setting '75': {get_global_speed()}")
    
    set_global_speed(150)  # Should clamp to 100
    print(f"After setting 150: {get_global_speed()}")
    
    set_global_speed(0)    # Should clamp to 1
    print(f"After setting 0: {get_global_speed()}")
    
    print("Speed history:")
    for timestamp, old, new in speed_manager.get_history():
        print(f"  {time.ctime(timestamp)}: {old} -> {new}")