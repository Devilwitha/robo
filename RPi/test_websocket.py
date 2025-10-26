#!/usr/bin/env python3
"""
Test WebSocket server compatibility
"""
import asyncio
import websockets
import json

async def test_websocket_client():
    """Test connecting to the WAVEGO WebSocket server"""
    print("Testing WebSocket connection to localhost:8888...")
    
    try:
        # Connect to the WebSocket server
        async with websockets.connect("ws://localhost:8888") as websocket:
            print("✓ Successfully connected to WebSocket server")
            
            # Test sending a simple command
            await websocket.send("get_info")
            print("✓ Sent 'get_info' command")
            
            # Wait for response
            response = await websocket.recv()
            print(f"✓ Received response: {response[:100]}...")
            
            # Test sending JSON command
            json_command = json.dumps({"title": "test", "data": "hello"})
            await websocket.send(json_command)
            print("✓ Sent JSON command")
            
            response2 = await websocket.recv()
            print(f"✓ Received response: {response2[:100]}...")
            
            print("✓ WebSocket test completed successfully!")
            
    except ConnectionRefusedError:
        print("✗ Could not connect - WebSocket server not running")
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")

if __name__ == "__main__":
    print("=== WebSocket Test Client ===")
    print("This script tests the WebSocket server functionality")
    print("Make sure the WAVEGO service is running first")
    print()
    
    try:
        asyncio.run(test_websocket_client())
    except KeyboardInterrupt:
        print("Test interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")