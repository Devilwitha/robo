#!/usr/bin/env python3
import asyncio
import websockets
import json

SERVER_IP = "192.168.178.52"
SERVER_PORT = 8888
WEBSOCKET_URI = f"ws://{SERVER_IP}:{SERVER_PORT}"

async def test_connection():
    try:
        print(f"Connecting to {WEBSOCKET_URI}...")
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print("✅ WebSocket connection successful!")
            
            # Test basic commands
            test_commands = ["forward", "backward", "left", "right", "DS", "TS"]
            
            for cmd in test_commands:
                print(f"Sending: {cmd}")
                await websocket.send(cmd)
                await asyncio.sleep(0.5)
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"Response: {response}")
                except asyncio.TimeoutError:
                    print("No response received")
            
            print("✅ All test commands sent successfully!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - Server not running on port 8888")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("=== WAVEGO Connection Test ===")
    try:
        asyncio.run(test_connection())
    except KeyboardInterrupt:
        print("Test stopped.")