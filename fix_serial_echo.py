#!/usr/bin/env python3
"""
Fix serial port echo issue by disabling local echo
"""

import serial
import termios
import sys
import os
import subprocess
from datetime import datetime

def disable_serial_echo(port='/dev/ttyUSB0'):
    """Disable local echo on serial port"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log file with timestamp
    log_filename = f"logs/serial_echo_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Open log file
    with open(log_filename, 'w') as log_file:
        def log_print(message):
            """Print to both console and log file"""
            print(message)
            log_file.write(message + '\n')
            log_file.flush()
        
        log_print(f"\n=== Fixing Serial Echo on {port} ===")
        log_print(f"Timestamp: {datetime.now()}\n")
        
        try:
            # First, diagnose the current state
            log_print("=== BEFORE FIX ===")
            ser = serial.Serial(port, 9600, timeout=1)
            fd = ser.fileno()
            before_attrs = termios.tcgetattr(fd)
            
            log_print("Current echo flags:")
            log_print(f"ECHO: {'ENABLED' if before_attrs[3] & termios.ECHO else 'disabled'}")
            log_print(f"ECHOE: {'ENABLED' if before_attrs[3] & termios.ECHOE else 'disabled'}")
            log_print(f"ECHOK: {'ENABLED' if before_attrs[3] & termios.ECHOK else 'disabled'}")
            log_print(f"ECHONL: {'ENABLED' if before_attrs[3] & termios.ECHONL else 'disabled'}")
            
            ser.close()
            
            # Method 1: Using stty command (most reliable)
            log_print("\n=== APPLYING FIX ===")
            log_print("Method 1: Using stty command...")
            
            # Use subprocess for better error handling
            stty_cmd = f"stty -F {port} -echo -echoe -echok -echonl"
            try:
                result = subprocess.run(stty_cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    log_print("✓ Successfully disabled echo using stty")
                    log_print(f"Command: {stty_cmd}")
                else:
                    log_print("❌ Failed to run stty command")
                    log_print(f"Error: {result.stderr}")
            except Exception as e:
                log_print(f"❌ stty command failed: {e}")
                
            # Method 2: Using termios
            log_print("\nMethod 2: Using termios...")
            ser = serial.Serial(port, 9600, timeout=1)
            fd = ser.fileno()
            
            # Get current attributes
            attrs = termios.tcgetattr(fd)
            
            # Disable all echo flags
            attrs[3] &= ~termios.ECHO
            attrs[3] &= ~termios.ECHOE
            attrs[3] &= ~termios.ECHOK
            attrs[3] &= ~termios.ECHONL
            
            # Apply new attributes
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
            
            log_print("✓ Successfully disabled echo using termios")
            
            # Verify the change
            log_print("\n=== VERIFICATION ===")
            new_attrs = termios.tcgetattr(fd)
            
            all_disabled = True
            log_print("Echo flags after fix:")
            
            if new_attrs[3] & termios.ECHO:
                log_print("❌ ECHO is still ENABLED!")
                all_disabled = False
            else:
                log_print("✓ ECHO is disabled")
                
            if new_attrs[3] & termios.ECHOE:
                log_print("❌ ECHOE is still ENABLED!")
                all_disabled = False
            else:
                log_print("✓ ECHOE is disabled")
                
            if new_attrs[3] & termios.ECHOK:
                log_print("❌ ECHOK is still ENABLED!")
                all_disabled = False
            else:
                log_print("✓ ECHOK is disabled")
                
            if new_attrs[3] & termios.ECHONL:
                log_print("❌ ECHONL is still ENABLED!")
                all_disabled = False
            else:
                log_print("✓ ECHONL is disabled")
            
            ser.close()
            
            log_print("\n=== RESULT ===")
            if all_disabled:
                log_print("✓ Serial echo fix applied successfully!")
                log_print("All echo flags have been disabled.")
                log_print("\nNext steps:")
                log_print("1. Run your Python client")
                log_print("2. Test if the echo feedback loop is resolved")
                log_print("3. If the issue persists, check the diagnostic logs")
            else:
                log_print("⚠️  Some echo flags could not be disabled")
                log_print("The issue might require additional investigation")
            
            log_print(f"\n✓ Fix log saved to: {log_filename}")
            
        except Exception as e:
            log_print(f"\nError: {e}")
            log_print(f"\nFix log saved to: {log_filename}")
            sys.exit(1)

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    disable_serial_echo(port)