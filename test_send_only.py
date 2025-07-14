#!/usr/bin/env python3
"""
Test script that ONLY sends data - no receiving
"""

import serial
import time
import sys

def test_send_only(port='/dev/ttyUSB0'):
    print(f"\n=== Send-Only Test on {port} ===")
    print("This script ONLY sends data, it does NOT read anything\n")
    
    try:
        # Open serial port
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=0  # Non-blocking
        )
        
        # Clear any pending data (but don't read it)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print("Sending test message in 2 seconds...")
        time.sleep(2)
        
        # Send a test message
        test_msg = f"SEND_ONLY_TEST_{int(time.time())}\n"
        print(f"SENDING: {test_msg.strip()}")
        ser.write(test_msg.encode('ascii'))
        
        print("\nMessage sent. Waiting 3 seconds...")
        time.sleep(3)
        
        # Check if data is waiting (without reading it)
        if ser.in_waiting > 0:
            print(f"\n❌ WARNING: {ser.in_waiting} bytes are waiting in receive buffer!")
            print("This suggests the sent data is being echoed back.")
        else:
            print("\n✓ Good: No data in receive buffer")
            print("The sent message was NOT echoed back.")
        
        ser.close()
        print("\nTest complete.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    test_send_only(port)