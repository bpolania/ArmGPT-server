#!/usr/bin/env python3
"""
Diagnose serial port configuration and echo issues
"""

import serial
import termios
import sys
import os
from datetime import datetime

def diagnose_serial(port='/dev/ttyUSB0'):
    """Check serial port settings that might cause echo"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log file with timestamp
    log_filename = f"logs/serial_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Open log file
    with open(log_filename, 'w') as log_file:
        def log_print(message):
            """Print to both console and log file"""
            print(message)
            log_file.write(message + '\n')
            log_file.flush()
        
        log_print(f"\n=== Serial Port Diagnostics for {port} ===")
        log_print(f"Timestamp: {datetime.now()}\n")
        
        try:
            # Open serial port
            ser = serial.Serial(port, 9600, timeout=1)
            
            # Get file descriptor
            fd = ser.fileno()
            
            # Get terminal attributes
            attrs = termios.tcgetattr(fd)
            
            log_print("Current Serial Port Settings:")
            log_print(f"Port: {port}")
            log_print(f"Baudrate: {ser.baudrate}")
            log_print(f"Is Open: {ser.is_open}")
            
            # Check echo settings
            log_print("\nChecking Echo Settings:")
            
            echo_issues = []
            
            # ECHO flag
            if attrs[3] & termios.ECHO:
                log_print("❌ ECHO is ENABLED - This will cause local echo!")
                echo_issues.append("ECHO")
            else:
                log_print("✓ ECHO is disabled")
                
            # ECHOE flag
            if attrs[3] & termios.ECHOE:
                log_print("❌ ECHOE is ENABLED")
                echo_issues.append("ECHOE")
            else:
                log_print("✓ ECHOE is disabled")
                
            # ECHOK flag
            if attrs[3] & termios.ECHOK:
                log_print("❌ ECHOK is ENABLED")
                echo_issues.append("ECHOK")
            else:
                log_print("✓ ECHOK is disabled")
                
            # ECHONL flag
            if attrs[3] & termios.ECHONL:
                log_print("❌ ECHONL is ENABLED")
                echo_issues.append("ECHONL")
            else:
                log_print("✓ ECHONL is disabled")
                
            # Check if it's in canonical mode
            if attrs[3] & termios.ICANON:
                log_print("\n⚠️  Port is in CANONICAL mode (line-based)")
            else:
                log_print("\n✓ Port is in RAW mode")
                
            # Summary
            log_print("\n=== DIAGNOSIS SUMMARY ===")
            if echo_issues:
                log_print(f"❌ Found echo issues: {', '.join(echo_issues)}")
                log_print("\nTo disable echo, run:")
                log_print(f"python3 fix_serial_echo.py {port}")
                log_print("or")
                log_print(f"stty -F {port} -echo")
            else:
                log_print("✓ No echo issues detected")
                log_print("The serial echo feedback loop is NOT caused by local echo settings.")
                log_print("Check for other causes like hardware loopback or terminal settings.")
            
            ser.close()
            
            log_print(f"\n✓ Diagnostics saved to: {log_filename}")
            
        except Exception as e:
            log_print(f"\nError: {e}")
            log_print(f"\nDiagnostics saved to: {log_filename}")
            sys.exit(1)

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    diagnose_serial(port)