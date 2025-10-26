#!/usr/bin/env python3
"""
Alternative WebSocket handler with better compatibility
This can be used if the main webServer.py still has issues
"""
import asyncio
import websockets
import json
import sys
import os

# Add the current directory to Python path to import other modules
sys.path.append(os.path.dirname(__file__))

try:
    import info
    import app
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    info = None
    app = None

flask_app = None

async def websocket_handler(websocket, path=None):
    """
    WebSocket handler that's compatible with different websockets library versions
    """
    client_addr = getattr(websocket, 'remote_address', 'unknown')
    print(f"INFO: New WebSocket connection from {client_addr}")
    
    try:
        async for message in websocket:
            try:
                # Try to parse as JSON first
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = message  # Keep as string if not JSON
                
                response = {
                    'status': 'ok',
                    'title': '',
                    'data': None
                }
                
                # Handle string commands
                if isinstance(data, str):
                    if flask_app and data not in ['get_info', 'scan']:
                        flask_app.commandInput(data)
                    
                    if data == 'get_info' and info:
                        response['title'] = 'get_info'
                        response['data'] = [
                            info.get_cpu_tempfunc(), 
                            info.get_cpu_use(), 
                            info.get_ram_info()
                        ]
                    elif data == 'scan':
                        response['title'] = 'scanResult'
                        response['data'] = [[3,60],[10,70],[10,80],[10,90],[10,100],[10,110],[3,120]]
                    elif data == 'findColor' and flask_app:
                        flask_app.modeselect('findColor')
                    elif data == 'motionGet' and flask_app:
                        flask_app.modeselect('watchDog')
                    elif data == 'stopCV' and flask_app:
                        flask_app.modeselect('none')
                
                # Handle JSON object commands
                elif isinstance(data, dict):
                    if data.get('title') == "findColorSet" and flask_app:
                        color = data.get('data')
                        if color and len(color) == 3:
                            flask_app.colorFindSet(color[0], color[1], color[2])
                
                # Send response
                await websocket.send(json.dumps(response))
                
            except Exception as e:
                print(f"Error processing message: {e}")
                error_response = {'status': 'error', 'message': str(e)}
                try:
                    await websocket.send(json.dumps(error_response))
                except:
                    break
                    
    except websockets.exceptions.ConnectionClosed:
        print(f"INFO: WebSocket connection from {client_addr} closed")
    except Exception as e:
        print(f"ERROR in WebSocket handler: {e}")

async def start_websocket_server():
    """Start the WebSocket server with compatibility fallbacks"""
    print("Starting WebSocket server on port 8888...")
    
    try:
        # Try modern async with syntax
        async with websockets.serve(websocket_handler, "0.0.0.0", 8888):
            print("✓ WebSocket server started successfully")
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Modern websockets failed: {e}")
        try:
            # Try older syntax
            server = await websockets.serve(websocket_handler, "0.0.0.0", 8888)
            print("✓ WebSocket server started (compatibility mode)")
            await server.wait_closed()
        except Exception as e2:
            print(f"✗ Could not start WebSocket server: {e2}")

if __name__ == "__main__":
    print("=== Alternative WebSocket Server ===")
    
    # Initialize Flask app if possible
    if app:
        try:
            flask_app = app.webapp()
            flask_app.startthread()
            print("✓ Flask app initialized")
        except Exception as e:
            print(f"Warning: Could not initialize Flask app: {e}")
    
    try:
        asyncio.run(start_websocket_server())
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server failed: {e}")