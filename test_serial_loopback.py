#!/usr/bin/env python3
"""
Test for serial loopback - helps identify where echoes are coming from
"""

import serial
import time
import sys
import os
from datetime import datetime
import threading

def test_loopback(port='/dev/ttyUSB0', baudrate=9600):
    """Test if messages are being looped back through serial connection"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create log file with timestamp
    log_filename = f"logs/serial_loopback_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    received_messages = []
    test_complete = False
    
    def read_thread(ser, log_file):
        """Thread to continuously read from serial port"""
        while not test_complete:
            try:
                if ser.in_waiting > 0:
                    data = ser.readline()
                    if data:
                        timestamp = datetime.now()
                        message = data.decode('ascii', errors='ignore').strip()
                        if message:
                            received_messages.append((timestamp, message))
                            log_msg = f"[{timestamp}] RECEIVED: {message}"
                            print(log_msg)
                            log_file.write(log_msg + '\n')
                            log_file.flush()
                else:
                    time.sleep(0.01)
            except Exception as e:
                log_msg = f"Read error: {e}"
                print(log_msg)
                log_file.write(log_msg + '\n')
                break
    
    with open(log_filename, 'w') as log_file:
        def log_print(message):
            """Print to both console and log file"""
            print(message)
            log_file.write(message + '\n')
            log_file.flush()
        
        log_print(f"\n=== Serial Loopback Test ===")
        log_print(f"Port: {port}")
        log_print(f"Baudrate: {baudrate}")
        log_print(f"Timestamp: {datetime.now()}\n")
        
        try:
            # Open serial port
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            log_print("Serial port opened successfully")
            log_print("Starting read thread...")
            
            # Start read thread
            reader = threading.Thread(target=read_thread, args=(ser, log_file))
            reader.daemon = True
            reader.start()
            
            # Wait a moment
            time.sleep(1)
            
            # Test 1: Send unique test message
            log_print("\n=== TEST 1: Simple Message ===")
            test_msg_1 = f"TEST_{int(time.time())}\n"
            send_time_1 = datetime.now()
            log_print(f"[{send_time_1}] SENDING: {test_msg_1.strip()}")
            ser.write(test_msg_1.encode('ascii'))
            
            # Wait for potential echo
            time.sleep(2)
            
            # Test 2: Send AI-formatted message
            log_print("\n=== TEST 2: AI Response Format ===")
            test_msg_2 = f"AI: Test response {int(time.time())}\n---\n"
            send_time_2 = datetime.now()
            log_print(f"[{send_time_2}] SENDING: {test_msg_2.strip()}")
            ser.write(test_msg_2.encode('ascii'))
            
            # Wait for potential echo
            time.sleep(2)
            
            # Test 3: Send without newline
            log_print("\n=== TEST 3: Message Without Newline ===")
            test_msg_3 = f"NO_NEWLINE_{int(time.time())}"
            send_time_3 = datetime.now()
            log_print(f"[{send_time_3}] SENDING: {test_msg_3}")
            ser.write(test_msg_3.encode('ascii'))
            
            # Wait
            time.sleep(2)
            
            # Stop read thread
            test_complete = True
            reader.join(timeout=1)
            
            # Analysis
            log_print("\n=== ANALYSIS ===")
            
            sent_messages = [
                (send_time_1, test_msg_1.strip()),
                (send_time_2, test_msg_2.strip()),
                (send_time_3, test_msg_3)
            ]
            
            # Check for echoes
            echoes_found = []
            for sent_time, sent_msg in sent_messages:
                for recv_time, recv_msg in received_messages:
                    # Check if received message matches sent message
                    if sent_msg in recv_msg or recv_msg in sent_msg:
                        time_diff = (recv_time - sent_time).total_seconds()
                        if 0 <= time_diff <= 1:  # Echo within 1 second
                            echoes_found.append({
                                'sent': sent_msg,
                                'received': recv_msg,
                                'delay': time_diff
                            })
            
            if echoes_found:
                log_print(f"\n❌ ECHO DETECTED! Found {len(echoes_found)} echoed message(s):")
                for echo in echoes_found:
                    log_print(f"  Sent: '{echo['sent']}'")
                    log_print(f"  Received: '{echo['received']}'")
                    log_print(f"  Delay: {echo['delay']:.3f} seconds")
                    log_print("")
                
                log_print("POSSIBLE CAUSES:")
                log_print("1. Physical loopback in serial cable (TX connected to RX)")
                log_print("2. USB serial adapter with internal loopback")
                log_print("3. Another process on the system echoing serial data")
                log_print("4. Virtual serial port with loopback enabled")
                
            else:
                log_print("\n✓ NO ECHO DETECTED")
                log_print("Messages sent were NOT received back.")
                log_print("The serial connection appears to be working correctly.")
                
                if received_messages:
                    log_print(f"\nNote: Received {len(received_messages)} message(s) from other source:")
                    for recv_time, recv_msg in received_messages[:5]:  # Show first 5
                        log_print(f"  [{recv_time}] {recv_msg}")
            
            # Check if this might be the same device
            log_print("\n=== DEVICE INFO ===")
            log_print(f"Port name: {ser.name}")
            log_print(f"Port settings: {ser.get_settings()}")
            
            ser.close()
            log_print(f"\n✓ Test log saved to: {log_filename}")
            
        except serial.SerialException as e:
            log_print(f"\nSerial error: {e}")
            log_print("\nPossible issues:")
            log_print("- Port doesn't exist or is already in use")
            log_print("- Permission denied (add user to dialout group)")
            log_print("- Wrong port name")
        except Exception as e:
            log_print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    
    test_loopback(port, baudrate)