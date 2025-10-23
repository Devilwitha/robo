#!/usr/bin/env python3
"""
WAVEGO Feature Debug Tool
========================
Simple tool to test WAVEGO features without full hardware setup.
This script simulates the robot responses and allows testing of web interface.
"""

import os
import sys
import webbrowser
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

# Simple HTTP Server for serving test files
class TestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

def start_test_server(port=8080):
    """Start simple HTTP server for testing"""
    server = HTTPServer(('localhost', port), TestHandler)
    print(f"🌐 Test-Server gestartet auf: http://localhost:{port}")
    print(f"📄 Öffne: http://localhost:{port}/feature-test.html")
    server.serve_forever()

def check_features():
    """Check which WAVEGO features are available"""
    print("🔍 Überprüfe WAVEGO Features...")
    
    features = {
        'Flask App': ('app.py', 'Web-Server für Roboter-Interface'),
        'WebSocket Server': ('webServer.py', 'WebSocket-Server für Echtzeitkommunikation'),
        'Camera Module': ('camera_opencv.py', 'Kamera und Computer Vision'),
        'Robot Control': ('robot.py', 'Roboter-Steuerung und Bewegung'),
        'BolliOs': ('BollshiiOs.py', 'Gyro-Balance-System'),
        'Object Recognition': ('object_recognition.py', 'Objekterkennung mit OpenCV'),
        'Gesture Recognition': ('gesture_recognition.py', 'Gestenerkennung mit MediaPipe'),
        'Motion Tracking': ('MotionTracker.py', 'Bewegungsverfolgung'),
        'Media Capture': ('media_capture.py', 'Foto- und Video-Aufnahme'),
        'Servo Control': ('servo_stow.py', 'Servo-Positionierung'),
    }
    
    print("\n📋 Feature-Status:")
    print("=" * 50)
    
    for feature_name, (filename, description) in features.items():
        if os.path.exists(filename):
            status = "✅ Verfügbar"
            color = "\033[92m"  # Green
        else:
            status = "❌ Nicht gefunden"
            color = "\033[91m"  # Red
        
        print(f"{color}{feature_name:<20} {status}\033[0m")
        print(f"   📄 {filename} - {description}")
    
    print("\n" + "=" * 50)

def check_web_interface():
    """Check web interface files"""
    print("\n🌐 Überprüfe Web-Interface...")
    
    web_files = {
        'Main HTML': 'dist/index.html',
        'BolliOs CSS': 'dist/css/bollios-switches.css', 
        'BolliOs JS': 'dist/js/bollios-switches.js',
        'Feature Controls': 'dist/js/feature-controls.js',
        'Keyboard Shortcuts': 'dist/js/keyboard-shortcuts.js',
        'Test Interface': 'feature-test.html'
    }
    
    print("\n🗂️ Web-Dateien:")
    print("=" * 40)
    
    for file_name, file_path in web_files.items():
        if os.path.exists(file_path):
            status = "✅ Vorhanden"
            color = "\033[92m"
        else:
            status = "❌ Fehlt"
            color = "\033[91m"
        
        print(f"{color}{file_name:<20} {status}\033[0m")
        print(f"   📁 {file_path}")

def test_connections():
    """Test various connection possibilities"""
    print("\n🔌 Teste Verbindungen...")
    
    # Test ports
    import socket
    
    test_ports = [
        (5000, 'Flask Web Server'),
        (8888, 'WebSocket Server'),
        (8080, 'Test Server')
    ]
    
    print("\n🚪 Port-Status:")
    print("=" * 30)
    
    for port, description in test_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            status = "🟢 Offen"
            color = "\033[92m"
        else:
            status = "🔴 Geschlossen"
            color = "\033[91m"
        
        print(f"{color}Port {port:<4} {status}\033[0m - {description}")

def show_debug_info():
    """Show debug information for troubleshooting"""
    print("\n🐛 Debug-Informationen:")
    print("=" * 40)
    
    # Python version
    print(f"🐍 Python Version: {sys.version}")
    
    # Current directory
    print(f"📁 Arbeitsverzeichnis: {os.getcwd()}")
    
    # Try importing modules
    modules = [
        'flask', 'websockets', 'cv2', 'numpy', 
        'mediapipe', 'serial', 'asyncio'
    ]
    
    print("\n📦 Python Module:")
    for module in modules:
        try:
            __import__(module)
            status = "✅ Installiert"
            color = "\033[92m"
        except ImportError:
            status = "❌ Fehlt"
            color = "\033[91m"
        
        print(f"{color}{module:<15} {status}\033[0m")

def main():
    """Main function"""
    print("🤖 WAVEGO Feature Debug Tool")
    print("=" * 40)
    
    while True:
        print("\n📋 Optionen:")
        print("1. 🔍 Features überprüfen")
        print("2. 🌐 Web-Interface überprüfen") 
        print("3. 🔌 Verbindungen testen")
        print("4. 🐛 Debug-Info anzeigen")
        print("5. 🚀 Test-Server starten")
        print("6. 🌍 Test-Interface öffnen")
        print("0. ❌ Beenden")
        
        try:
            choice = input("\n➤ Auswahl (0-6): ").strip()
            
            if choice == '0':
                print("👋 Auf Wiedersehen!")
                break
            elif choice == '1':
                check_features()
            elif choice == '2':
                check_web_interface()
            elif choice == '3':
                test_connections()
            elif choice == '4':
                show_debug_info()
            elif choice == '5':
                print("\n🚀 Starte Test-Server...")
                print("⚠️  Drücke Strg+C zum Beenden")
                try:
                    start_test_server()
                except KeyboardInterrupt:
                    print("\n⏹️  Server gestoppt")
            elif choice == '6':
                # Open test interface
                test_url = "file://" + os.path.abspath("feature-test.html")
                print(f"\n🌍 Öffne Test-Interface: {test_url}")
                try:
                    webbrowser.open(test_url)
                    print("✅ Browser geöffnet")
                except Exception as e:
                    print(f"❌ Fehler beim Öffnen: {e}")
                    print(f"📋 Kopiere diese URL in deinen Browser: {test_url}")
            else:
                print("❌ Ungültige Auswahl!")
                
        except KeyboardInterrupt:
            print("\n👋 Auf Wiedersehen!")
            break
        except Exception as e:
            print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    main()