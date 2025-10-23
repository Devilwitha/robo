#!/usr/bin/env python3
# Simple feature test server for development
# This allows testing features without full WAVEGO setup

import asyncio
import websockets
import json
import threading
import time
from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Simple Flask app for static files
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Get current directory
dir_path = os.path.dirname(os.path.realpath(__file__))

@app.route('/')
def index():
    return send_from_directory(dir_path + '/dist', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(dir_path + '/dist', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(dir_path + '/dist/js', filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(dir_path + '/dist/css', filename)

@app.route('/img/<path:filename>')
def serve_img(filename):
    return send_from_directory(dir_path + '/dist/img', filename)

# Simple mock robot control
class MockRobot:
    def __init__(self):
        self.speed = 100
        
    def forward(self):
        print("MOCK: Robot moving forward")
    
    def backward(self):
        print("MOCK: Robot moving backward")
    
    def left(self):
        print("MOCK: Robot turning left")
    
    def right(self):
        print("MOCK: Robot turning right")
    
    def stop(self):
        print("MOCK: Robot stopped")
        
    def speedSet(self, speed):
        self.speed = speed
        print(f"MOCK: Speed set to {speed}")
        return True
    
    def getSpeed(self):
        return self.speed

# Mock CV modes
mock_cv_mode = 'none'
mock_robot = MockRobot()

# WebSocket message handler
async def handle_websocket(websocket, path):
    print(f"WebSocket connection from {websocket.remote_address}")
    
    try:
        async for message in websocket:
            print(f"Received: {message}")
            
            response = {
                'status': 'ok',
                'title': '',
                'data': None
            }
            
            try:
                # Try to parse as JSON
                if message.startswith('{'):
                    data = json.loads(message)
                else:
                    data = message
            except:
                data = message
            
            # Handle different commands
            if isinstance(data, str):
                if data == 'admin:123456':
                    # Authentication
                    response['title'] = 'auth'
                    response['data'] = 'authenticated'
                
                elif data == 'bolliOs':
                    print("MOCK: BolliOs activated")
                    response['title'] = 'bolliOs'
                    response['data'] = 'activated'
                
                elif data == 'bolliOsOff':
                    print("MOCK: BolliOs deactivated")
                    response['title'] = 'bolliOs'
                    response['data'] = 'deactivated'
                
                elif data == 'bolliOsStatus':
                    response['title'] = 'bolliOsStatus'
                    response['data'] = {
                        'active': True,
                        'running': True
                    }
                
                elif data == 'motionTracking':
                    global mock_cv_mode
                    mock_cv_mode = 'motionTracking'
                    print("MOCK: Motion tracking activated")
                    response['title'] = 'motionTracking'
                    response['data'] = 'activated'
                
                elif data == 'motionTrackingOff':
                    mock_cv_mode = 'none'
                    print("MOCK: Motion tracking deactivated")
                    response['title'] = 'motionTracking'
                    response['data'] = 'deactivated'
                
                elif data.startswith('cvMode:'):
                    mode = data.split(':')[1]
                    mock_cv_mode = mode
                    print(f"MOCK: CV mode set to {mode}")
                    response['title'] = 'cvMode'
                    response['data'] = mode
                
                elif data == 'system_shutdown':
                    print("MOCK: System shutdown requested")
                    response['title'] = 'system_shutdown'
                    response['data'] = 'shutting_down'
                
                elif data == 'stow_servos':
                    print("MOCK: Servos stowing")
                    response['title'] = 'stow_servos'
                    response['data'] = 'servos_stowed'
                
                elif 'wsB' in data:
                    # Speed command
                    try:
                        speed_str = data.replace('wsB', '').strip()
                        speed = int(speed_str)
                        mock_robot.speedSet(speed)
                        response['title'] = 'speed'
                        response['data'] = f'speed_set_{speed}'
                    except:
                        response['title'] = 'error'
                        response['data'] = 'invalid_speed'
                
                # Movement commands
                elif data == 'forward':
                    mock_robot.forward()
                elif data == 'backward':
                    mock_robot.backward()
                elif data == 'left':
                    mock_robot.left()
                elif data == 'right':
                    mock_robot.right()
                elif data == 'stop':
                    mock_robot.stop()
            
            elif isinstance(data, dict):
                # Handle JSON commands
                if data.get('action') == 'system_shutdown':
                    print("MOCK: System shutdown via JSON")
                    response['title'] = 'system_shutdown'
                    response['data'] = 'shutting_down'
                
                elif data.get('command') == 'speed':
                    speed = data.get('data', {}).get('value', 100)
                    mock_robot.speedSet(speed)
                    response['title'] = 'speed'
                    response['data'] = {'value': speed}
            
            # Send response
            await websocket.send(json.dumps(response))
            
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Start Flask in background
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Start WebSocket server
async def run_websocket():
    print("Starting WebSocket server on port 8888...")
    await websockets.serve(handle_websocket, "0.0.0.0", 8888)
    print("WebSocket server started")

if __name__ == '__main__':
    print("=== WAVEGO FEATURE TEST SERVER ===")
    print("Starting Flask server on port 5000...")
    print("Starting WebSocket server on port 8888...")
    print("Open http://localhost:5000 in your browser")
    print("=====================================")
    
    # Start Flask in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(1)
    
    # Start WebSocket server
    try:
        asyncio.run(run_websocket())
        # Keep running
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Server shutdown requested")
    except Exception as e:
        print(f"Server error: {e}")