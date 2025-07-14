#!/usr/bin/env python3
"""
Check all available serial devices and their properties
"""

import os
import subprocess
from datetime import datetime

def check_serial_devices():
    """List and analyze all serial devices"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log file with timestamp
    log_filename = f"logs/serial_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    with open(log_filename, 'w') as log_file:
        def log_print(message):
            """Print to both console and log file"""
            print(message)
            log_file.write(message + '\n')
            log_file.flush()
        
        log_print(f"\n=== Serial Device Check ===")
        log_print(f"Timestamp: {datetime.now()}\n")
        
        # List all tty devices
        log_print("=== Available Serial Devices ===")
        
        # Check /dev/ttyUSB*
        log_print("\nUSB Serial devices (/dev/ttyUSB*):")
        try:
            usb_devices = subprocess.run(['ls', '-la', '/dev/ttyUSB*'], 
                                       capture_output=True, text=True, shell=True)
            if usb_devices.returncode == 0:
                log_print(usb_devices.stdout)
            else:
                log_print("No /dev/ttyUSB* devices found")
        except Exception as e:
            log_print(f"Error checking USB devices: {e}")
        
        # Check /dev/ttyACM*
        log_print("\nACM devices (/dev/ttyACM*):")
        try:
            acm_devices = subprocess.run(['ls', '-la', '/dev/ttyACM*'], 
                                       capture_output=True, text=True, shell=True)
            if acm_devices.returncode == 0:
                log_print(acm_devices.stdout)
            else:
                log_print("No /dev/ttyACM* devices found")
        except Exception as e:
            log_print(f"Error checking ACM devices: {e}")
        
        # Check dmesg for USB serial info
        log_print("\n=== Recent USB Serial Messages (dmesg) ===")
        try:
            dmesg = subprocess.run(['dmesg', '|', 'grep', '-i', 'ttyUSB'], 
                                 capture_output=True, text=True, shell=True)
            if dmesg.returncode == 0 and dmesg.stdout:
                log_print(dmesg.stdout)
            else:
                log_print("No recent USB serial messages in dmesg")
        except Exception as e:
            log_print(f"Error checking dmesg: {e}")
        
        # Check lsusb for USB devices
        log_print("\n=== USB Devices (lsusb) ===")
        try:
            lsusb = subprocess.run(['lsusb'], capture_output=True, text=True)
            if lsusb.returncode == 0:
                log_print(lsusb.stdout)
            else:
                log_print("Could not list USB devices")
        except Exception as e:
            log_print(f"Error running lsusb: {e}")
        
        # Check who's using the serial port
        log_print("\n=== Processes Using Serial Ports ===")
        try:
            # Check for /dev/ttyUSB0 specifically
            lsof = subprocess.run(['lsof', '/dev/ttyUSB0'], 
                                capture_output=True, text=True)
            if lsof.returncode == 0 and lsof.stdout:
                log_print("Processes using /dev/ttyUSB0:")
                log_print(lsof.stdout)
            else:
                log_print("No processes currently using /dev/ttyUSB0")
        except Exception as e:
            log_print(f"Error checking processes: {e}")
        
        # Check serial port info using stty
        log_print("\n=== Serial Port Settings (stty) ===")
        try:
            for device in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0']:
                if os.path.exists(device):
                    log_print(f"\nSettings for {device}:")
                    stty = subprocess.run(['stty', '-F', device, '-a'], 
                                        capture_output=True, text=True)
                    if stty.returncode == 0:
                        log_print(stty.stdout)
                    else:
                        log_print(f"Could not read settings: {stty.stderr}")
        except Exception as e:
            log_print(f"Error checking stty: {e}")
        
        log_print(f"\n✓ Device check saved to: {log_filename}")
        
        # Recommendations
        log_print("\n=== RECOMMENDATIONS ===")
        log_print("1. If you see only one /dev/ttyUSB0, both Pis might be using the same device")
        log_print("2. Check your cable - ensure it's a proper null modem cable, not a loopback cable")
        log_print("3. Verify each Pi has its own USB serial adapter")
        log_print("4. Try using different serial ports on each Pi (e.g., /dev/ttyUSB0 and /dev/ttyUSB1)")

if __name__ == "__main__":
    check_serial_devices()