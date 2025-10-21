#!/usr/bin/env python3
# File name   : simple_speed_test.py
# Description : Simple test for speed functionality without external dependencies

def test_speed_parsing():
    """Test speed command parsing like in camera_opencv.py"""
    
    print("=== Simple Speed Test ===")
    
    # Test cases for wsB command parsing
    test_commands = [
        "wsB 50",
        "wsB 100", 
        "wsB 1",
        "wsB 0",     # Should be clamped to 1
        "wsB 150",   # Should be clamped to 100
        "wsB abc",   # Should fail
        "wsB",       # Should fail
        "forward",   # Not a speed command
    ]
    
    for cmd in test_commands:
        print(f"\nTesting command: '{cmd}'")
        
        if 'wsB' in cmd:
            print(f'SPEED COMMAND: Processing {cmd}')
            try:
                parts = cmd.split()
                if len(parts) >= 2:
                    speedMove = int(parts[1])
                    print(f'SPEED COMMAND: Extracted speed value: {speedMove}')
                    
                    # Clamp speed to valid range (1-100)
                    clamped_speed = max(1, min(100, speedMove))
                    if clamped_speed != speedMove:
                        print(f'SPEED COMMAND: Speed clamped from {speedMove} to {clamped_speed}')
                    
                    print(f'SPEED COMMAND: Final speed: {clamped_speed}')
                else:
                    print(f'SPEED COMMAND: Invalid format, expected "wsB <number>", got: {cmd}')
            except (ValueError, IndexError) as e:
                print(f'SPEED COMMAND: Error parsing: {cmd}, Error: {e}')
        else:
            print(f"Not a speed command: {cmd}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_speed_parsing()