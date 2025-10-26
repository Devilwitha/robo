#!/usr/bin/env python3
"""
WAVEGO Simple GUI Controller
Simple GUI application for controlling WAVEGO robot with controller configuration.
No camera stream integration - lightweight version.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import asyncio
import time
import websockets
import pygame
import requests

class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_file="wavego_config.json"):
        self.config_file = config_file
        self.default_config = {
            "connection": {
                "host": "192.168.178.52",
                "websocket_port": 8888,
                "http_port": 5000,
                "auto_connect": True
            },
            "controller": {
                "steering_axis": 0,
                "accelerator_axis": 1,
                "brake_axis": 6,
                "steering_threshold": 0.3,
                "pedal_threshold": 0.3
            }
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                return self.merge_configs(self.default_config, config)
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def merge_configs(self, default, loaded):
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result

class ConnectionDialog:
    """Dialog for entering connection settings"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connect to WAVEGO Robot")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        
        # Focus and wait
        self.host_entry.focus_set()
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="WAVEGO Robot Connection", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Connection settings
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Host/IP
        ttk.Label(conn_frame, text="Robot IP/Hostname:").pack(anchor=tk.W)
        self.host_var = tk.StringVar(value=self.config.get("connection", {}).get("host", ""))
        self.host_entry = ttk.Entry(conn_frame, textvariable=self.host_var, width=30)
        self.host_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Ports
        ports_frame = ttk.Frame(conn_frame)
        ports_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ports_frame, text="WebSocket Port:").pack(side=tk.LEFT)
        self.ws_port_var = tk.StringVar(value=str(self.config.get("connection", {}).get("websocket_port", 8888)))
        ws_port_entry = ttk.Entry(ports_frame, textvariable=self.ws_port_var, width=8)
        ws_port_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(ports_frame, text="HTTP Port:").pack(side=tk.LEFT)
        self.http_port_var = tk.StringVar(value=str(self.config.get("connection", {}).get("http_port", 5000)))
        http_port_entry = ttk.Entry(ports_frame, textvariable=self.http_port_var, width=8)
        http_port_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Auto-connect
        self.auto_connect_var = tk.BooleanVar(value=self.config.get("connection", {}).get("auto_connect", True))
        auto_check = ttk.Checkbutton(conn_frame, text="Auto-connect on startup", 
                                    variable=self.auto_connect_var)
        auto_check.pack(anchor=tk.W)
        
        # Test connection
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill=tk.X, pady=(0, 20))
        
        test_btn = ttk.Button(test_frame, text="Test Connection", command=self.test_connection)
        test_btn.pack()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Connect", command=self.connect).pack(side=tk.RIGHT)
    
    def test_connection(self):
        """Test connection to robot"""
        host = self.host_var.get().strip()
        try:
            ws_port = int(self.ws_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid WebSocket port number")
            return
        
        if not host:
            messagebox.showerror("Error", "Please enter a host/IP address")
            return
        
        # Test WebSocket connection
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, ws_port))
            sock.close()
            
            if result == 0:
                messagebox.showinfo("Success", f"WebSocket connection to {host}:{ws_port} successful!")
            else:
                messagebox.showwarning("Warning", f"Could not connect to WebSocket port {ws_port}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {e}")
    
    def connect(self):
        """Validate and return connection settings"""
        host = self.host_var.get().strip()
        
        if not host:
            messagebox.showerror("Error", "Please enter a host/IP address")
            return
        
        try:
            ws_port = int(self.ws_port_var.get())
            http_port = int(self.http_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port numbers")
            return
        
        self.result = {
            "host": host,
            "websocket_port": ws_port,
            "http_port": http_port,
            "auto_connect": self.auto_connect_var.get()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.result = None
        self.dialog.destroy()

class ControllerConfigDialog:
    """Dialog for configuring controller settings"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.result = None
        
        # Initialize pygame for controller detection
        pygame.init()
        pygame.joystick.init()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Controller Configuration")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        self.update_controller_info()
        
        # Start live testing
        self.testing = True
        self.test_controller()
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Controller Configuration", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Controller info
        info_frame = ttk.LabelFrame(main_frame, text="Detected Controllers", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.controller_info = ttk.Label(info_frame, text="Detecting controllers...")
        self.controller_info.pack()
        
        # Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Axis Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Steering axis
        steering_frame = ttk.Frame(config_frame)
        steering_frame.pack(fill=tk.X, pady=2)
        ttk.Label(steering_frame, text="Steering Axis:", width=15).pack(side=tk.LEFT)
        self.steering_var = tk.StringVar(value=str(self.config.get("controller", {}).get("steering_axis", 0)))
        ttk.Entry(steering_frame, textvariable=self.steering_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Accelerator axis
        accel_frame = ttk.Frame(config_frame)
        accel_frame.pack(fill=tk.X, pady=2)
        ttk.Label(accel_frame, text="Accelerator Axis:", width=15).pack(side=tk.LEFT)
        self.accel_var = tk.StringVar(value=str(self.config.get("controller", {}).get("accelerator_axis", 1)))
        ttk.Entry(accel_frame, textvariable=self.accel_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Brake axis
        brake_frame = ttk.Frame(config_frame)
        brake_frame.pack(fill=tk.X, pady=2)
        ttk.Label(brake_frame, text="Brake Axis:", width=15).pack(side=tk.LEFT)
        self.brake_var = tk.StringVar(value=str(self.config.get("controller", {}).get("brake_axis", 6)))
        ttk.Entry(brake_frame, textvariable=self.brake_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Thresholds
        thresh_frame = ttk.LabelFrame(main_frame, text="Sensitivity Thresholds", padding="10")
        thresh_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Steering threshold
        steer_thresh_frame = ttk.Frame(thresh_frame)
        steer_thresh_frame.pack(fill=tk.X, pady=2)
        ttk.Label(steer_thresh_frame, text="Steering Threshold:", width=15).pack(side=tk.LEFT)
        self.steer_thresh_var = tk.StringVar(value=str(self.config.get("controller", {}).get("steering_threshold", 0.3)))
        ttk.Entry(steer_thresh_frame, textvariable=self.steer_thresh_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Pedal threshold
        pedal_thresh_frame = ttk.Frame(thresh_frame)
        pedal_thresh_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pedal_thresh_frame, text="Pedal Threshold:", width=15).pack(side=tk.LEFT)
        self.pedal_thresh_var = tk.StringVar(value=str(self.config.get("controller", {}).get("pedal_threshold", 0.3)))
        ttk.Entry(pedal_thresh_frame, textvariable=self.pedal_thresh_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Live test
        test_frame = ttk.LabelFrame(main_frame, text="Live Test", padding="10")
        test_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.test_text = tk.Text(test_frame, height=8, font=("Courier", 8))
        test_scrollbar = ttk.Scrollbar(test_frame, orient=tk.VERTICAL, command=self.test_text.yview)
        self.test_text.configure(yscrollcommand=test_scrollbar.set)
        
        self.test_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        test_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=tk.RIGHT)
    
    def update_controller_info(self):
        """Update controller information display"""
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            controller_count = pygame.joystick.get_count()
            if controller_count == 0:
                info_text = "No controllers detected"
            else:
                info_lines = [f"Found {controller_count} controller(s):"]
                for i in range(controller_count):
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    info_lines.append(f"  {i}: {joy.get_name()}")
                    info_lines.append(f"      Axes: {joy.get_numaxes()}, Buttons: {joy.get_numbuttons()}")
                info_text = "\n".join(info_lines)
            
            self.controller_info.configure(text=info_text)
        except Exception as e:
            self.controller_info.configure(text=f"Error detecting controllers: {e}")
    
    def test_controller(self):
        """Live test controller inputs"""
        if not self.testing:
            return
        
        try:
            pygame.event.pump()
            
            if pygame.joystick.get_count() > 0:
                joy = pygame.joystick.Joystick(0)
                if not joy.get_init():
                    joy.init()
                
                # Get axis values
                axes_info = []
                for i in range(min(joy.get_numaxes(), 10)):  # Limit to first 10 axes
                    value = joy.get_axis(i)
                    axes_info.append(f"Axis {i}: {value:6.3f}")
                
                # Update test display
                self.test_text.delete(1.0, tk.END)
                self.test_text.insert(tk.END, "Live Controller Test:\n")
                self.test_text.insert(tk.END, "-" * 30 + "\n")
                for info in axes_info:
                    self.test_text.insert(tk.END, info + "\n")
                
                # Auto-scroll to bottom
                self.test_text.see(tk.END)
            else:
                self.test_text.delete(1.0, tk.END)
                self.test_text.insert(tk.END, "No controller connected for testing")
        
        except Exception as e:
            self.test_text.delete(1.0, tk.END)
            self.test_text.insert(tk.END, f"Test error: {e}")
        
        # Schedule next update
        if self.testing:
            self.dialog.after(100, self.test_controller)
    
    def save(self):
        """Save controller configuration"""
        try:
            config = {
                "steering_axis": int(self.steering_var.get()),
                "accelerator_axis": int(self.accel_var.get()),
                "brake_axis": int(self.brake_var.get()),
                "steering_threshold": float(self.steer_thresh_var.get()),
                "pedal_threshold": float(self.pedal_thresh_var.get())
            }
            
            # Validate values
            for key, value in config.items():
                if "axis" in key and (value < 0 or value > 20):
                    raise ValueError(f"Invalid axis number: {value}")
                elif "threshold" in key and (value < 0.0 or value > 1.0):
                    raise ValueError(f"Invalid threshold: {value}")
            
            self.result = config
            self.testing = False
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid configuration: {e}")
    
    def cancel(self):
        """Cancel configuration"""
        self.result = None
        self.testing = False
        self.dialog.destroy()

class WAVEGOController:
    """Main WAVEGO controller application"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Connection state
        self.connected = False
        self.websocket = None
        self.websocket_task = None
        
        # Controller state
        self.joystick = None
        self.controller_active = False
        self.last_fb_command = None
        self.last_lr_command = None
        
        # Rate limiting for WebSocket messages
        self.last_send_time = 0
        self.min_send_interval = 0.05  # 50ms minimum between messages
        
        # Initialize Pygame
        pygame.init()
        pygame.joystick.init()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("WAVEGO Robot Controller")
        self.root.geometry("800x600")
        
        self.create_gui()
        
        # Auto-connect if enabled
        if self.config.get("connection", {}).get("auto_connect", False):
            self.auto_connect()
    
    def create_gui(self):
        """Create the main GUI"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")
        self.create_control_panel(self.control_frame)
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Connection status
        ttk.Label(self.status_frame, text="Status:").pack(side=tk.LEFT)
        self.conn_status_var = tk.StringVar(value="Disconnected")
        ttk.Label(self.status_frame, textvariable=self.conn_status_var, 
                 foreground="red").pack(side=tk.LEFT, padx=(5, 20))
        
        # Connect button
        self.connect_btn = ttk.Button(self.status_frame, text="Connect", 
                                     command=self.show_connection_dialog)
        self.connect_btn.pack(side=tk.LEFT)
        
        # Controller status
        ttk.Label(self.status_frame, text="Controller:").pack(side=tk.LEFT, padx=(20, 0))
        self.controller_status_var = tk.StringVar(value="Inactive")
        ttk.Label(self.status_frame, textvariable=self.controller_status_var).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_control_panel(self, parent):
        """Create control panel"""
        # Left side - Manual controls
        left_frame = ttk.LabelFrame(parent, text="Manual Controls", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Movement controls
        move_frame = ttk.LabelFrame(left_frame, text="Movement", padding="10")
        move_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Forward/Back
        fb_frame = ttk.Frame(move_frame)
        fb_frame.pack(pady=5)
        ttk.Button(fb_frame, text="Forward", command=lambda: self.send_command("forward")).pack()
        ttk.Button(fb_frame, text="Backward", command=lambda: self.send_command("backward")).pack(pady=(5, 0))
        
        # Left/Right
        lr_frame = ttk.Frame(move_frame)
        lr_frame.pack(pady=5)
        lr_sub_frame = ttk.Frame(lr_frame)
        lr_sub_frame.pack()
        ttk.Button(lr_sub_frame, text="Left", command=lambda: self.send_command("left")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(lr_sub_frame, text="Right", command=lambda: self.send_command("right")).pack(side=tk.LEFT)
        
        # Stop buttons
        stop_frame = ttk.Frame(move_frame)
        stop_frame.pack(pady=10)
        ttk.Button(stop_frame, text="Stop Movement", command=lambda: self.send_command("DS")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(stop_frame, text="Stop Turn", command=lambda: self.send_command("TS")).pack(side=tk.LEFT)
        
        # Camera controls
        cam_frame = ttk.LabelFrame(left_frame, text="Camera", padding="10")
        cam_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Camera movement
        cam_move_frame = ttk.Frame(cam_frame)
        cam_move_frame.pack(pady=5)
        ttk.Button(cam_move_frame, text="Look Up", command=lambda: self.send_command("up")).pack()
        
        cam_lr_frame = ttk.Frame(cam_frame)
        cam_lr_frame.pack(pady=5)
        cam_lr_sub_frame = ttk.Frame(cam_lr_frame)
        cam_lr_sub_frame.pack()
        ttk.Button(cam_lr_sub_frame, text="Look Left", command=lambda: self.send_command("lookleft")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cam_lr_sub_frame, text="Look Right", command=lambda: self.send_command("lookright")).pack(side=tk.LEFT)
        
        ttk.Button(cam_frame, text="Look Down", command=lambda: self.send_command("down")).pack(pady=(5, 0))
        
        # Camera stop
        cam_stop_frame = ttk.Frame(cam_frame)
        cam_stop_frame.pack(pady=10)
        ttk.Button(cam_stop_frame, text="Stop UD", command=lambda: self.send_command("UDstop")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cam_stop_frame, text="Stop LR", command=lambda: self.send_command("LRstop")).pack(side=tk.LEFT)
        
        # Special functions
        special_frame = ttk.LabelFrame(left_frame, text="Special Functions", padding="10")
        special_frame.pack(fill=tk.X)
        
        special_btn_frame = ttk.Frame(special_frame)
        special_btn_frame.pack()
        ttk.Button(special_btn_frame, text="Handshake", command=lambda: self.send_command("handshake")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(special_btn_frame, text="Jump", command=lambda: self.send_command("jump")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(special_btn_frame, text="Steady", command=lambda: self.send_command("steady")).pack(side=tk.LEFT)
        
        # Right side - Controller and status
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Controller panel
        self.create_controller_panel(right_frame)
        
        # Status log
        log_frame = ttk.LabelFrame(right_frame, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=12, font=("Courier", 8))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_controller_panel(self, parent):
        """Create controller configuration panel"""
        ctrl_frame = ttk.LabelFrame(parent, text="Controller", padding="10")
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Controller info
        self.controller_info_var = tk.StringVar(value="No controller detected")
        info_label = ttk.Label(ctrl_frame, textvariable=self.controller_info_var, font=("Arial", 9))
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Controller buttons
        ctrl_btn_frame = ttk.Frame(ctrl_frame)
        ctrl_btn_frame.pack(fill=tk.X)
        
        ttk.Button(ctrl_btn_frame, text="Configure", command=self.show_controller_config).pack(side=tk.LEFT, padx=(0, 5))
        
        self.controller_toggle_btn = ttk.Button(ctrl_btn_frame, text="Enable", command=self.toggle_controller)
        self.controller_toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(ctrl_btn_frame, text="Refresh", command=self.refresh_controller).pack(side=tk.LEFT)
        
        # Initialize controller
        self.refresh_controller()
    
    def show_connection_dialog(self):
        """Show connection configuration dialog"""
        dialog = ConnectionDialog(self.root, self.config)
        if dialog.result:
            # Update config
            self.config["connection"] = dialog.result
            self.config_manager.save_config(self.config)
            
            # Connect
            self.connect_to_robot(dialog.result["host"], dialog.result["websocket_port"])
    
    def show_controller_config(self):
        """Show controller configuration dialog"""
        dialog = ControllerConfigDialog(self.root, self.config)
        if dialog.result:
            # Update config
            self.config["controller"] = dialog.result
            self.config_manager.save_config(self.config)
            
            # Refresh controller
            self.refresh_controller()
            self.log_message("Controller configuration updated")
    
    def auto_connect(self):
        """Automatically connect using saved settings"""
        conn_config = self.config.get("connection", {})
        host = conn_config.get("host")
        port = conn_config.get("websocket_port", 8888)
        
        if host:
            self.log_message(f"Auto-connecting to {host}:{port}...")
            self.connect_to_robot(host, port)
    
    def connect_to_robot(self, host, port):
        """Connect to robot WebSocket"""
        if self.connected:
            self.disconnect()
        
        self.log_message(f"Connecting to {host}:{port}...")
        self.conn_status_var.set("Connecting...")
        self.connect_btn.configure(text="Connecting...", state=tk.DISABLED)
        
        def connect_thread():
            try:
                # Create event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Connect with compression disabled to prevent assertion errors
                websocket_uri = f"ws://{host}:{port}"
                websocket = loop.run_until_complete(websockets.connect(
                    websocket_uri, 
                    compression=None  # Disable compression to prevent assertion errors
                ))
                
                self.websocket = websocket
                self.connected = True
                
                # Update UI in main thread
                self.root.after(0, self.on_connected)
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.on_connection_error(error_msg))
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def disconnect(self):
        """Disconnect from robot"""
        if self.websocket:
            try:
                asyncio.run(self.websocket.close())
            except:
                pass
        
        self.websocket = None
        self.connected = False
        self.root.after(0, self.on_disconnected)
    
    def on_connected(self):
        """Called when connected"""
        self.conn_status_var.set("Connected")
        self.connect_btn.configure(text="Disconnect", command=self.disconnect, state=tk.NORMAL)
        self.log_message("Connected successfully!")
        
        # Start controller monitoring if enabled
        if self.controller_active:
            self.monitor_controller()
    
    def on_connection_error(self, error_msg):
        """Called when connection fails"""
        self.conn_status_var.set("Disconnected")
        self.connect_btn.configure(text="Connect", command=self.show_connection_dialog, state=tk.NORMAL)
        self.log_message(f"Connection failed: {error_msg}")
    
    def on_disconnected(self):
        """Called when disconnected"""
        self.conn_status_var.set("Disconnected")
        self.connect_btn.configure(text="Connect", command=self.show_connection_dialog, state=tk.NORMAL)
        self.log_message("Disconnected")
    
    def send_command(self, command):
        """Send command to robot with rate limiting"""
        if not self.connected or not self.websocket:
            self.log_message(f"Cannot send '{command}' - not connected")
            return
        
        # Rate limiting - prevent flooding
        current_time = time.time()
        if current_time - self.last_send_time < self.min_send_interval:
            return  # Skip this command to prevent flooding
        
        self.last_send_time = current_time
        
        def send_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.websocket.send(command))
                self.root.after(0, lambda: self.log_message(f"Sent: {command}"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"Send error: {error_msg}"))
        
        thread = threading.Thread(target=send_async, daemon=True)
        thread.start()
    
    def refresh_controller(self):
        """Refresh controller detection"""
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            controller_count = pygame.joystick.get_count()
            if controller_count > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                controller_name = self.joystick.get_name()
                self.controller_info_var.set(f"Controller: {controller_name}")
                self.controller_toggle_btn.configure(state=tk.NORMAL)
                self.log_message(f"Controller detected: {controller_name}")
            else:
                self.joystick = None
                self.controller_info_var.set("No controller detected")
                self.controller_toggle_btn.configure(state=tk.DISABLED)
                if self.controller_active:
                    self.controller_active = False
                    self.controller_status_var.set("Inactive")
                self.log_message("No controller detected")
        
        except Exception as e:
            self.controller_info_var.set(f"Controller error: {e}")
            self.log_message(f"Controller detection error: {e}")
    
    def toggle_controller(self):
        """Toggle controller enable/disable"""
        if not self.joystick:
            self.log_message("No controller available")
            return
        
        self.controller_active = not self.controller_active
        
        if self.controller_active:
            self.controller_toggle_btn.configure(text="Disable")
            self.controller_status_var.set("Active")
            self.log_message("Controller activated")
            if self.connected:
                self.monitor_controller()
        else:
            self.controller_toggle_btn.configure(text="Enable")
            self.controller_status_var.set("Inactive")
            self.log_message("Controller deactivated")
    
    def monitor_controller(self):
        """Monitor controller input and send commands"""
        if not self.controller_active or not self.joystick or not self.connected:
            return
        
        try:
            pygame.event.pump()
            
            # Get controller configuration
            controller_config = self.config.get("controller", {})
            steering_axis = controller_config.get("steering_axis", 0)
            accel_axis = controller_config.get("accelerator_axis", 1)
            brake_axis = controller_config.get("brake_axis", 6)
            steering_threshold = controller_config.get("steering_threshold", 0.3)
            pedal_threshold = controller_config.get("pedal_threshold", 0.3)
            
            # Read axis values
            try:
                steering_value = self.joystick.get_axis(steering_axis)
                accel_value = self.joystick.get_axis(accel_axis)
                brake_value = self.joystick.get_axis(brake_axis)
            except pygame.error:
                self.log_message("Controller disconnected")
                self.refresh_controller()
                return
            
            # Process steering
            current_lr_command = None
            if abs(steering_value) > steering_threshold:
                if steering_value < -steering_threshold:
                    current_lr_command = "left"
                elif steering_value > steering_threshold:
                    current_lr_command = "right"
            else:
                current_lr_command = "TS"  # Stop turning
            
            # Process forward/backward (handle different pedal configurations)
            current_fb_command = None
            
            # Normalize pedal values (some controllers use -1 to +1, others 0 to +1)
            if accel_value < 0:
                # Controller uses -1 to +1 range
                accel_normalized = (accel_value + 1) / 2
            else:
                # Controller uses 0 to +1 range
                accel_normalized = accel_value
            
            if brake_value < 0:
                # Controller uses -1 to +1 range
                brake_normalized = (brake_value + 1) / 2
            else:
                # Controller uses 0 to +1 range
                brake_normalized = brake_value
            
            # Determine forward/backward command
            if accel_normalized > pedal_threshold:
                current_fb_command = "forward"
            elif brake_normalized > pedal_threshold:
                current_fb_command = "backward"
            else:
                current_fb_command = "DS"  # Stop movement
            
            # Send commands only if they changed
            if current_fb_command != self.last_fb_command:
                self.send_command(current_fb_command)
                self.last_fb_command = current_fb_command
            
            if current_lr_command != self.last_lr_command:
                self.send_command(current_lr_command)
                self.last_lr_command = current_lr_command
        
        except Exception as e:
            self.log_message(f"Controller error: {e}")
        
        # Schedule next check
        self.root.after(50, self.monitor_controller)  # 20 FPS
    
    def log_message(self, message):
        """Add message to activity log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log size
        if self.log_text.index(tk.END).split('.')[0] > '100':
            self.log_text.delete(1.0, "20.0")
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            self.disconnect()
        
        pygame.quit()
        self.root.destroy()

def main():
    """Main entry point"""
    app = WAVEGOController()
    app.run()

if __name__ == "__main__":
    main()