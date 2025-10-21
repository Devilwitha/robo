#!/usr/bin/env python3
# File name   : MotionSettings.py
# Description : Configuration interface for Motion Tracking parameters
# Author      : WAVEGO Team
# Date        : 2024

import json
import os

class MotionSettings:
    def __init__(self, config_file='motion_config.json'):
        self.config_file = config_file
        self.default_settings = {
            # Stop-and-Scan Timing
            'movement_duration': 2.0,      # Seconds to move toward motion
            'pause_duration': 1.0,         # Seconds to pause and scan
            'background_reset_time': 0.5,  # Seconds to wait before resetting background
            
            # Motion Detection
            'min_area': 1500,              # Minimum area for motion detection
            'tracking_sensitivity': 20,    # Motion detection threshold (higher = less sensitive)
            'movement_threshold': 60,      # Pixel threshold for movement commands
            'motion_timeout': 5.0,         # Seconds before giving up on motion
            
            # Advanced Settings
            'background_learning_rate': 0.2,  # How fast background adapts (lower = more stable)
            'gaussian_blur_size': 21,         # Blur kernel size for noise reduction
            'dilate_iterations': 2,           # Morphological operations for noise reduction
            'contour_area_filter': True,      # Filter small contours
            
            # Behavior Settings
            'enable_vertical_movement': False,  # Use camera servo for vertical tracking
            'aggressive_movement': False,       # More responsive but less stable
            'debug_mode': True                  # Show detailed debug information
        }
        
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = self.default_settings.copy()
                merged.update(settings)
                return merged
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading motion settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Save current settings to file"""
        try:
            settings_to_save = settings or self.settings
            with open(self.config_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            print(f"Motion settings saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving motion settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def update_settings(self, new_settings):
        """Update multiple settings at once"""
        self.settings.update(new_settings)
        return self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def get_preset(self, preset_name):
        """Get predefined setting presets"""
        presets = {
            'conservative': {
                'movement_duration': 1.5,
                'pause_duration': 1.5,
                'tracking_sensitivity': 25,
                'background_learning_rate': 0.15,
                'aggressive_movement': False
            },
            'balanced': {
                'movement_duration': 2.0,
                'pause_duration': 1.0,
                'tracking_sensitivity': 20,
                'background_learning_rate': 0.2,
                'aggressive_movement': False
            },
            'aggressive': {
                'movement_duration': 2.5,
                'pause_duration': 0.8,
                'tracking_sensitivity': 15,
                'background_learning_rate': 0.25,
                'aggressive_movement': True
            },
            'indoor': {
                'movement_duration': 1.8,
                'pause_duration': 1.2,
                'tracking_sensitivity': 22,
                'min_area': 1200,
                'background_learning_rate': 0.18
            },
            'outdoor': {
                'movement_duration': 2.2,
                'pause_duration': 0.9,
                'tracking_sensitivity': 18,
                'min_area': 2000,
                'background_learning_rate': 0.22
            }
        }
        return presets.get(preset_name, {})
    
    def apply_preset(self, preset_name):
        """Apply a predefined preset"""
        preset = self.get_preset(preset_name)
        if preset:
            self.update_settings(preset)
            print(f"Applied motion tracking preset: {preset_name}")
            return True
        else:
            print(f"Unknown preset: {preset_name}")
            return False
    
    def get_all_settings(self):
        """Get all current settings"""
        return self.settings.copy()
    
    def print_settings(self):
        """Print current settings in a readable format"""
        print("\n=== Motion Tracking Settings ===")
        print(f"Movement Duration: {self.settings['movement_duration']}s")
        print(f"Pause Duration: {self.settings['pause_duration']}s")
        print(f"Sensitivity: {self.settings['tracking_sensitivity']}")
        print(f"Min Area: {self.settings['min_area']} pixels")
        print(f"Movement Threshold: {self.settings['movement_threshold']} pixels")
        print(f"Debug Mode: {self.settings['debug_mode']}")
        print("===============================\n")

# Global settings instance
motion_settings = MotionSettings()

def get_motion_setting(key, default=None):
    """Quick access to motion settings"""
    return motion_settings.get(key, default)

def set_motion_setting(key, value):
    """Quick access to set motion settings"""
    motion_settings.set(key, value)
    motion_settings.save_settings()

def apply_motion_preset(preset_name):
    """Quick access to apply presets"""
    return motion_settings.apply_preset(preset_name)