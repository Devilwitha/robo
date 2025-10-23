#!/usr/bin/env python3
# File name   : MotionTracker.py
# Description : Motion detection and tracking system for WAVEGO with Stop-and-Scan logic
# Author      : WAVEGO Team
# Date        : 2024

import cv2
import numpy as np
import datetime
import threading
import time
import robot

# Optional import for settings
try:
    from MotionSettings import motion_settings
    SETTINGS_AVAILABLE = True
except ImportError:
    print("MotionSettings not available, using default values")
    SETTINGS_AVAILABLE = False
    motion_settings = None

class MotionTracker:
    def __init__(self):
        self.is_active = False
        self.tracking_thread = None
        self.avg_background = None
        self.motion_detected = False
        self.last_motion_time = None
        self.motion_center_x = 0
        self.motion_center_y = 0
        self.motion_area = 0
        
        # Load settings or use defaults
        if SETTINGS_AVAILABLE:
            self.movement_duration = motion_settings.get('movement_duration', 2.0)
            self.pause_duration = motion_settings.get('pause_duration', 1.0)
            self.background_reset_time = motion_settings.get('background_reset_time', 0.5)
            self.min_area = motion_settings.get('min_area', 1500)
            self.motion_timeout = motion_settings.get('motion_timeout', 5.0)
            self.tracking_sensitivity = motion_settings.get('tracking_sensitivity', 20)
            self.movement_threshold = motion_settings.get('movement_threshold', 60)
            self.background_learning_rate = motion_settings.get('background_learning_rate', 0.2)
            self.gaussian_blur_size = motion_settings.get('gaussian_blur_size', 21)
            self.dilate_iterations = motion_settings.get('dilate_iterations', 2)
            self.enable_vertical_movement = motion_settings.get('enable_vertical_movement', False)
            self.debug_mode = motion_settings.get('debug_mode', True)
        else:
            # Default values
            self.movement_duration = 2.0
            self.pause_duration = 1.0
            self.background_reset_time = 0.5
            self.min_area = 1500
            self.motion_timeout = 5.0
            self.tracking_sensitivity = 20
            self.movement_threshold = 60
            self.background_learning_rate = 0.2
            self.gaussian_blur_size = 21
            self.dilate_iterations = 2
            self.enable_vertical_movement = False
            self.debug_mode = True
        
        # Movement state tracking
        self.is_moving = False
        self.movement_start_time = None
        self.pause_start_time = None
        self.scanning_mode = True  # True = scanning, False = moving
        
        print(f"MotionTracker initialized with Stop-and-Scan logic")
        if self.debug_mode:
            print(f"  - Movement: {self.movement_duration}s, Pause: {self.pause_duration}s")
            print(f"  - Sensitivity: {self.tracking_sensitivity}, Min Area: {self.min_area}")
    
    def reload_settings(self):
        """Reload settings from file"""
        if SETTINGS_AVAILABLE:
            motion_settings.load_settings()
            # Update all parameters
            self.movement_duration = motion_settings.get('movement_duration', self.movement_duration)
            self.pause_duration = motion_settings.get('pause_duration', self.pause_duration)
            self.background_reset_time = motion_settings.get('background_reset_time', self.background_reset_time)
            self.min_area = motion_settings.get('min_area', self.min_area)
            self.motion_timeout = motion_settings.get('motion_timeout', self.motion_timeout)
            self.tracking_sensitivity = motion_settings.get('tracking_sensitivity', self.tracking_sensitivity)
            self.movement_threshold = motion_settings.get('movement_threshold', self.movement_threshold)
            self.background_learning_rate = motion_settings.get('background_learning_rate', self.background_learning_rate)
            self.gaussian_blur_size = motion_settings.get('gaussian_blur_size', self.gaussian_blur_size)
            self.dilate_iterations = motion_settings.get('dilate_iterations', self.dilate_iterations)
            self.enable_vertical_movement = motion_settings.get('enable_vertical_movement', self.enable_vertical_movement)
            self.debug_mode = motion_settings.get('debug_mode', self.debug_mode)
            print("Motion tracking settings reloaded")
        else:
            print("Settings not available, using current values")
    
    def start_tracking(self):
        """Start motion detection and tracking"""
        if self.is_active:
            print("Motion tracking already active")
            return True
            
        try:
            self.is_active = True
            self.avg_background = None  # Reset background model
            self.scanning_mode = True
            self.is_moving = False
            
            # Turn on blue LEDs to indicate motion tracking mode
            robot.lightCtrl('blue', 0)
            
            print("Motion tracking started - Stop-and-Scan mode - Blue LEDs ON")
            return True
            
        except Exception as e:
            print(f"Failed to start motion tracking: {e}")
            self.is_active = False
            return False
    
    def stop_tracking(self):
        """Stop motion detection and tracking"""
        if not self.is_active:
            print("Motion tracking not active")
            return True
            
        try:
            self.is_active = False
            self.motion_detected = False
            self.scanning_mode = True
            self.is_moving = False
            
            # Stop any ongoing movement
            robot.stopFB()
            robot.stopLR()
            
            # Turn off LEDs
            robot.lightCtrl('blue', 1)
            
            print("Motion tracking stopped")
            return True
            
        except Exception as e:
            print(f"Error stopping motion tracking: {e}")
            return False
    
    def get_status(self):
        """Get current motion tracking status"""
        return {
            'active': self.is_active,
            'motion_detected': self.motion_detected,
            'motion_center': (self.motion_center_x, self.motion_center_y),
            'motion_area': self.motion_area,
            'scanning_mode': self.scanning_mode,
            'is_moving': self.is_moving
        }
    
    def _stop_and_enter_scan_mode(self):
        """Stop robot movement and enter scanning mode"""
        try:
            # Stop all movement
            robot.stopFB()
            robot.stopLR()
            
            self.is_moving = False
            self.scanning_mode = True
            self.pause_start_time = time.time()
            
            print(f"STOP-AND-SCAN: Entering scan mode for {self.pause_duration}s")
            
            # Wait a moment for robot to stabilize before resetting background
            time.sleep(self.background_reset_time)
            self.avg_background = None  # Reset background model after stopping
            
        except Exception as e:
            print(f"Error entering scan mode: {e}")
    
    def _start_movement_toward_motion(self, frame_width, frame_height):
        """Start movement toward detected motion"""
        try:
            self.is_moving = True
            self.scanning_mode = False
            self.movement_start_time = time.time()
            
            # Calculate movement based on motion position
            center_x = frame_width // 2
            center_y = frame_height // 2
            x_diff = self.motion_center_x - center_x
            y_diff = self.motion_center_y - center_y
            
            if self.debug_mode:
                print(f"STOP-AND-SCAN: Starting movement for {self.movement_duration}s")
                print(f"Motion at ({self.motion_center_x}, {self.motion_center_y}), frame center ({center_x}, {center_y})")
            
            # Horizontal movement (left/right)
            if abs(x_diff) > self.movement_threshold:
                if x_diff > 0:
                    # Motion is to the right, turn right
                    robot.right()
                    if self.debug_mode:
                        print(f"Motion tracking: Turning RIGHT toward motion at x={self.motion_center_x}")
                else:
                    # Motion is to the left, turn left  
                    robot.left()
                    if self.debug_mode:
                        print(f"Motion tracking: Turning LEFT toward motion at x={self.motion_center_x}")
            else:
                # Motion is centered horizontally, move forward
                robot.forward()
                if self.debug_mode:
                    print(f"Motion tracking: Moving FORWARD toward centered motion")
            
            # Optional: Vertical movement with camera servo
            if self.enable_vertical_movement and abs(y_diff) > self.movement_threshold:
                if y_diff > 0:
                    # Motion is below center, look down slightly
                    robot.lookDown()
                    if self.debug_mode:
                        print(f"Motion tracking: Looking DOWN toward motion at y={self.motion_center_y}")
                else:
                    # Motion is above center, look up slightly  
                    robot.lookUp()
                    if self.debug_mode:
                        print(f"Motion tracking: Looking UP toward motion at y={self.motion_center_y}")
                
        except Exception as e:
            print(f"Error starting movement: {e}")
    
    def process_frame(self, frame):
        """Process frame for motion detection with Stop-and-Scan logic"""
        if not self.is_active:
            return frame
            
        try:
            current_time = time.time()
            timestamp = datetime.datetime.now()
            
            # Check movement/pause timing
            if self.is_moving and self.movement_start_time:
                # Check if movement duration is over
                if current_time - self.movement_start_time >= self.movement_duration:
                    self._stop_and_enter_scan_mode()
            
            elif self.scanning_mode and self.pause_start_time:
                # Check if pause duration is over without new motion
                if current_time - self.pause_start_time >= self.pause_duration:
                    # No new motion found during pause, continue scanning
                    self.pause_start_time = current_time  # Reset pause timer
                    print("STOP-AND-SCAN: Continuing scan - no motion detected")
            
            # Only do motion detection during scanning mode
            if not self.scanning_mode:
                # Display movement status
                time_remaining = self.movement_duration - (current_time - self.movement_start_time)
                cv2.putText(frame, f'Moving toward motion - {time_remaining:.1f}s remaining', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, 'Stop-and-Scan Mode: MOVING', (40, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
                return frame
            
            # Motion detection during scanning mode
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (self.gaussian_blur_size, self.gaussian_blur_size), 0)
            
            # Initialize background model
            if self.avg_background is None:
                if self.debug_mode:
                    print("[INFO] Initializing motion detection background model...")
                self.avg_background = gray.copy().astype("float")
                cv2.putText(frame, 'Stop-and-Scan: Initializing background...', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
                return frame
            
            # Update background model (configurable learning rate)
            cv2.accumulateWeighted(gray, self.avg_background, self.background_learning_rate)
            frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg_background))
            
            # Threshold and find contours
            thresh = cv2.threshold(frame_delta, self.tracking_sensitivity, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=self.dilate_iterations)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Reset motion detection
            self.motion_detected = False
            largest_contour = None
            largest_area = 0
            
            # Find largest motion area
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_area and area > largest_area:
                    largest_area = area
                    largest_contour = contour
            
            # Process motion if detected during scanning
            if largest_contour is not None and self.scanning_mode:
                # Calculate motion center
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    self.motion_center_x = int(M["m10"] / M["m00"])
                    self.motion_center_y = int(M["m01"] / M["m00"])
                    self.motion_area = largest_area
                    self.motion_detected = True
                    self.last_motion_time = timestamp
                    
                    # Draw motion rectangle
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (self.motion_center_x, self.motion_center_y), 5, (0, 0, 255), -1)
                    
                    # Start movement toward motion
                    self._start_movement_toward_motion(frame.shape[1], frame.shape[0])
                    
                    # Display status
                    cv2.putText(frame, f'Motion Detected! Starting movement...', (40, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, f'Target: ({self.motion_center_x}, {self.motion_center_y}) Area: {int(largest_area)}', (40, 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)
            
            # Display scanning status
            elif self.scanning_mode:
                scan_time_remaining = self.pause_duration - (current_time - (self.pause_start_time or current_time))
                cv2.putText(frame, 'Stop-and-Scan Mode: SCANNING for motion', (40, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
                if self.pause_start_time:
                    cv2.putText(frame, f'Scan cycle: {scan_time_remaining:.1f}s remaining', (40, 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)
                
        except Exception as e:
            print(f"Error in motion tracking: {e}")
            cv2.putText(frame, 'Motion Tracking Error', (40, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        
        return frame

# Global motion tracker instance
motion_tracker = MotionTracker()

def start_motion_tracking():
    """Start motion tracking system"""
    return motion_tracker.start_tracking()

def stop_motion_tracking():
    """Stop motion tracking system"""  
    return motion_tracker.stop_tracking()

def get_motion_status():
    """Get motion tracking status"""
    return motion_tracker.get_status()

def process_motion_frame(frame):
    """Process frame for motion detection"""
    return motion_tracker.process_frame(frame)