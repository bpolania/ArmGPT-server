import serial
import time
import threading
import queue
import logging
from typing import Optional, Callable, Dict, Any
import signal
import sys


class SerialClient:
    """Handles serial communication with ARM assembly sender"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize serial client with configuration
        
        Args:
            config: Dictionary containing serial port configuration
        """
        self.config = config
        self.port = None
        self.running = False
        self.message_queue = queue.Queue()
        self.logger = logging.getLogger(__name__)
        self.read_thread = None
        self.reconnect_attempts = config.get('reconnect_attempts', 5)
        self.reconnect_delay = config.get('reconnect_delay', 2)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("Received shutdown signal, closing serial connection...")
        self.stop()
        sys.exit(0)
        
    def connect(self) -> bool:
        """Connect to serial port with configuration
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Extract serial configuration
            serial_config = {
                'port': self.config.get('port', '/dev/ttyUSB0'),
                'baudrate': self.config.get('baudrate', 9600),
                'bytesize': serial.EIGHTBITS,
                'parity': serial.PARITY_NONE,
                'stopbits': serial.STOPBITS_ONE,
                'timeout': self.config.get('timeout', 1),
                'xonxoff': False,
                'rtscts': False,
                'dsrdtr': False
            }
            
            self.logger.info(f"Connecting to serial port {serial_config['port']} at {serial_config['baudrate']} baud...")
            self.port = serial.Serial(**serial_config)
            
            # Clear any buffered data
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
            
            self.logger.info("Serial connection established successfully")
            return True
            
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to serial port: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from serial port"""
        if self.port and self.port.is_open:
            try:
                self.port.close()
                self.logger.info("Serial port closed")
            except Exception as e:
                self.logger.error(f"Error closing serial port: {e}")
                
    def start(self, message_callback: Optional[Callable[[str], None]] = None):
        """Start reading from serial port in separate thread
        
        Args:
            message_callback: Optional callback function to handle received messages
        """
        if not self.port or not self.port.is_open:
            if not self.connect():
                raise RuntimeError("Cannot start - serial port not connected")
                
        self.running = True
        self.read_thread = threading.Thread(target=self._read_loop, args=(message_callback,))
        self.read_thread.daemon = True
        self.read_thread.start()
        self.logger.info("Serial reading thread started")
        
    def stop(self):
        """Stop reading from serial port"""
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=2)
        self.disconnect()
        
    def _read_loop(self, message_callback: Optional[Callable[[str], None]] = None):
        """Main reading loop running in separate thread
        
        Args:
            message_callback: Optional callback to handle messages
        """
        consecutive_errors = 0
        
        while self.running:
            try:
                if not self.port or not self.port.is_open:
                    self.logger.warning("Serial port not open, attempting reconnection...")
                    if not self._reconnect():
                        time.sleep(self.reconnect_delay)
                        continue
                        
                # Read data from serial port
                if self.port.in_waiting > 0:
                    try:
                        # Read available data
                        raw_data = self.port.readline()
                        
                        if raw_data:
                            # Decode and clean the message
                            message = raw_data.decode('ascii', errors='ignore').strip()
                            
                            if message:
                                self.logger.debug(f"Received raw data: {raw_data}")
                                self.logger.info(f"Received message: '{message}'")
                                
                                # Add to queue
                                self.message_queue.put(message)
                                
                                # Call callback if provided
                                if message_callback:
                                    message_callback(message)
                                    
                                consecutive_errors = 0
                                
                    except UnicodeDecodeError as e:
                        self.logger.error(f"Failed to decode message: {e}")
                        self.logger.debug(f"Raw bytes: {raw_data}")
                        
                else:
                    # No data available, sleep briefly
                    time.sleep(0.01)
                    
            except serial.SerialException as e:
                consecutive_errors += 1
                self.logger.error(f"Serial error (attempt {consecutive_errors}): {e}")
                
                if consecutive_errors >= 3:
                    self.logger.warning("Multiple serial errors, attempting reconnection...")
                    self._reconnect()
                    consecutive_errors = 0
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in read loop: {e}")
                time.sleep(0.1)
                
    def _reconnect(self) -> bool:
        """Attempt to reconnect to serial port
        
        Returns:
            bool: True if reconnection successful
        """
        self.disconnect()
        
        for attempt in range(self.reconnect_attempts):
            self.logger.info(f"Reconnection attempt {attempt + 1}/{self.reconnect_attempts}...")
            
            if self.connect():
                self.logger.info("Reconnection successful")
                return True
                
            time.sleep(self.reconnect_delay)
            
        self.logger.error("Failed to reconnect after all attempts")
        return False
        
    def get_message(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get message from queue
        
        Args:
            timeout: Maximum time to wait for message
            
        Returns:
            str or None: Message if available, None if timeout
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def send_message(self, message: str) -> bool:
        """Send message over serial port (if needed for bidirectional communication)
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if sent successfully
        """
        if not self.port or not self.port.is_open:
            self.logger.error("Cannot send - serial port not connected")
            return False
            
        try:
            # Ensure message ends with newline
            if not message.endswith('\n'):
                message += '\n'
                
            # Send in smaller chunks to avoid buffer overflow
            chunk_size = 64  # Safe size for most serial buffers
            message_bytes = message.encode('ascii')
            
            for i in range(0, len(message_bytes), chunk_size):
                chunk = message_bytes[i:i+chunk_size]
                self.port.write(chunk)
                time.sleep(0.01)  # Small delay between chunks
                
            self.logger.debug(f"Sent message: '{message.strip()}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
            
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics
        
        Returns:
            dict: Connection statistics
        """
        return {
            'connected': self.port.is_open if self.port else False,
            'port': self.config.get('port', 'Unknown'),
            'baudrate': self.config.get('baudrate', 'Unknown'),
            'messages_in_queue': self.message_queue.qsize(),
            'thread_alive': self.read_thread.is_alive() if self.read_thread else False
        }