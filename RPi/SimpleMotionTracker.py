#!/usr/bin/env python3
"""
SimpleMotionTracker.py - Simplified Motion Tracking that definitely works
No complex dependencies, just basic motion detection and robot movement
"""

import cv2
import numpy as np
import time
import threading

# Simple global state
motion_active = False
motion_thread = None
stop_motion = False

class SimpleMotionTracker:
    def __init__(self):
        self.active = False
        self.background = None
        
    def start(self):
        """Start simple motion tracking"""
        global motion_active, motion_thread, stop_motion
        
        if not motion_active:
            motion_active = True
            stop_motion = False
            print("SimpleMotionTracker: Starting motion detection")
            return True
        return False
    
    def stop(self):
        """Stop simple motion tracking"""
        global motion_active, stop_motion
        
        if motion_active:
            motion_active = False
            stop_motion = True
            print("SimpleMotionTracker: Stopping motion detection")
            return True
        return False
    
    def process_frame(self, frame):
        """Process frame for motion detection - simplified version"""
        global motion_active
        
        if not motion_active:
            cv2.putText(frame, 'Simple Motion Tracking: INACTIVE', (40, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return frame
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Initialize background if needed
            if self.background is None:
                self.background = gray.copy().astype("float")
                cv2.putText(frame, 'Simple Motion Tracking: Initializing background...', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                return frame
            
            # Update background
            cv2.accumulateWeighted(gray, self.background, 0.5)
            
            # Calculate difference
            frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.background))
            
            # Threshold
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            largest_area = 0
            motion_center = None
            
            # Check for significant motion
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Minimum area threshold
                    motion_detected = True
                    if area > largest_area:
                        largest_area = area
                        x, y, w, h = cv2.boundingRect(contour)
                        motion_center = (x + w//2, y + h//2)
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(frame, motion_center, 10, (0, 0, 255), -1)
            
            # Display status
            if motion_detected and motion_center:
                cv2.putText(frame, f'MOTION DETECTED! Target: {motion_center}', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f'Area: {int(largest_area)}', (40, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Simple robot movement toward motion
                self._move_toward_target(motion_center, frame.shape[1])
                
            else:
                cv2.putText(frame, 'Simple Motion Tracking: SCANNING...', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(frame, 'No significant motion detected', (40, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                
                # Stop robot when no motion
                self._stop_robot()
            
        except Exception as e:
            print(f"SimpleMotionTracker Error: {e}")
            cv2.putText(frame, f'ERROR: {str(e)[:50]}', (40, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return frame
    
    def _move_toward_target(self, target_center, frame_width):
        """Move robot toward detected motion"""
        try:
            # Import robot module when needed
            import robot
            
            center_x = target_center[0]
            frame_center = frame_width // 2
            
            # Simple left/right movement based on target position
            if center_x < frame_center - 50:
                # Target is on the left, turn left
                robot.set_car_run(3, 30)  # Left turn
                print(f"SimpleMotionTracker: Turning LEFT (target at {center_x})")
            elif center_x > frame_center + 50:
                # Target is on the right, turn right  
                robot.set_car_run(4, 30)  # Right turn
                print(f"SimpleMotionTracker: Turning RIGHT (target at {center_x})")
            else:
                # Target is centered, move forward
                robot.set_car_run(1, 25)  # Forward
                print(f"SimpleMotionTracker: Moving FORWARD (target centered at {center_x})")
                
        except ImportError:
            print("SimpleMotionTracker: robot module not available")
        except Exception as e:
            print(f"SimpleMotionTracker: Movement error: {e}")
    
    def _stop_robot(self):
        """Stop robot movement"""
        try:
            import robot
            robot.set_car_run(5)  # Stop
        except:
            pass

# Global instance
simple_tracker = SimpleMotionTracker()

# Module interface functions
def start_motion_tracking():
    """Start simple motion tracking"""
    return simple_tracker.start()

def stop_motion_tracking():
    """Stop simple motion tracking"""
    return simple_tracker.stop()

def get_motion_status():
    """Get motion tracking status"""
    return {'active': motion_active}

def process_motion_frame(frame):
    """Process frame for motion detection"""
    return simple_tracker.process_frame(frame)

if __name__ == "__main__":
    print("SimpleMotionTracker: Test mode")
    print("Available functions:", [f for f in dir() if not f.startswith('_')])