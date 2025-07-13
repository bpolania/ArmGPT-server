#!/usr/bin/env python3
"""
TinyLLM Serial Client - Main Entry Point

This script creates a Python client that receives serial data from an ARM 
assembly program and forwards messages to TinyLLM for AI processing.
"""

import argparse
import yaml
import os
import sys
import time
import signal
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from serial_client import SerialClient
from message_processor import MessageProcessor
from llm_interface import LLMManager
from logger import LoggerSetup, log_serial_event, log_process_event, log_llm_event, log_system_event


class TinyLLMSerialClient:
    """Main application class"""
    
    def __init__(self, config_path: str, test_mode: bool = False):
        """Initialize the client
        
        Args:
            config_path: Path to configuration file
            test_mode: Whether to run in test mode
        """
        self.config = self._load_config(config_path)
        self.test_mode = test_mode
        self.running = False
        
        # Setup logging
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', 'logs/serial_client.log')
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        self.logger = LoggerSetup.setup_logging(
            console_level=log_config.get('level', 'INFO'),
            file_level=log_config.get('file_level', 'DEBUG'),
            log_file=log_file,
            console_enabled=log_config.get('console', True)
        )
        
        # Initialize components
        self.serial_client = SerialClient(self.config.get('serial', {}))
        self.message_processor = MessageProcessor(self.config.get('client', {}))
        self.llm_manager = LLMManager(self.config.get('tinyllm', {}))
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in configuration file: {e}")
            sys.exit(1)
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        log_system_event(self.logger, "Shutdown signal received, stopping client...")
        self.stop()
        
    def message_callback(self, raw_message: str):
        """Callback to handle received messages
        
        Args:
            raw_message: Raw message from serial port
        """
        # Process the message
        processed = self.message_processor.process(raw_message)
        
        if not processed:
            log_process_event(self.logger, "Message rejected by processor", "warning")
            return
            
        log_process_event(self.logger, f"Cleaned message: \"{processed['cleaned']}\"")
        
        # Format for LLM
        llm_input = self.message_processor.format_message_for_llm(processed)
        
        # Forward to LLM
        response = self.llm_manager.process_message(llm_input)
        
        if response:
            log_llm_event(self.logger, f"Processing complete")
            # Log the transaction
            self._log_transaction(processed, response)
        else:
            log_llm_event(self.logger, "Failed to get response", "error")
            
    def _log_transaction(self, processed_message: dict, llm_response: str):
        """Log complete transaction to file
        
        Args:
            processed_message: Processed message dictionary
            llm_response: Response from LLM
        """
        transaction = {
            'timestamp': processed_message['timestamp'],
            'input_raw': processed_message['raw'],
            'input_cleaned': processed_message['cleaned'],
            'message_type': processed_message['type'],
            'llm_response': llm_response
        }
        
        # Write to transaction log (optional separate file)
        transaction_log = self.config.get('logging', {}).get('transaction_file')
        if transaction_log:
            try:
                with open(transaction_log, 'a') as f:
                    f.write(f"{yaml.dump(transaction, default_flow_style=False)}\n---\n")
            except Exception as e:
                self.logger.error(f"Failed to write transaction log: {e}")
                
    def run_test_mode(self):
        """Run in test mode with predefined messages"""
        log_system_event(self.logger, "Starting in TEST MODE")
        
        test_config = self.config.get('test', {})
        test_messages = test_config.get('test_messages', [
            "TEST MESSAGE FROM ACORN SYSTEM",
            "Hello from test mode!"
        ])
        
        for i, message in enumerate(test_messages, 1):
            log_serial_event(self.logger, f"Simulating message {i}/{len(test_messages)}: \"{message}\"")
            self.message_callback(message)
            time.sleep(2)  # Delay between messages
            
        log_system_event(self.logger, "Test mode completed")
        
    def run_serial_test_mode(self):
        """Run serial-only test mode (no LLM processing)"""
        log_system_event(self.logger, "Starting SERIAL TEST MODE")
        
        def simple_callback(message):
            processed = self.message_processor.process(message)
            if processed:
                log_process_event(self.logger, f"Would forward to LLM: \"{processed['cleaned']}\"")
            else:
                log_process_event(self.logger, "Message rejected", "warning")
                
        try:
            self.serial_client.start(simple_callback)
            log_serial_event(self.logger, "Ready for serial data (no LLM processing)...")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            log_system_event(self.logger, "Serial test mode interrupted")
        finally:
            self.serial_client.stop()
            
    def run(self):
        """Run the main application"""
        log_system_event(self.logger, "Starting TinyLLM Serial Client")
        
        # Check LLM availability
        if not self.llm_manager.is_available():
            log_llm_event(self.logger, "LLM not available, continuing anyway...", "warning")
            
        try:
            # Start serial client
            self.serial_client.start(self.message_callback)
            log_serial_event(self.logger, "Ready to receive messages...")
            
            self.running = True
            
            # Main loop
            while self.running:
                time.sleep(1)
                
                # Periodically log statistics
                if int(time.time()) % 60 == 0:  # Every minute
                    self._log_statistics()
                    
        except KeyboardInterrupt:
            log_system_event(self.logger, "Application interrupted by user")
        except Exception as e:
            log_system_event(self.logger, f"Unexpected error: {e}", "error")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the application"""
        self.running = False
        
        log_system_event(self.logger, "Stopping serial client...")
        self.serial_client.stop()
        
        # Log final statistics
        self._log_statistics()
        
        log_system_event(self.logger, "Application stopped")
        
    def _log_statistics(self):
        """Log performance statistics"""
        serial_stats = self.serial_client.get_stats()
        processor_stats = self.message_processor.get_stats()
        llm_stats = self.llm_manager.get_stats()
        
        log_system_event(self.logger, 
            f"Stats - Messages: {processor_stats['total_messages']}, "
            f"Valid: {processor_stats['valid_messages']}, "
            f"LLM Success: {llm_stats['successful_requests']}, "
            f"Avg Response: {llm_stats.get('average_response_time', 0):.2f}s"
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='TinyLLM Serial Client')
    
    parser.add_argument(
        '--config', '-c',
        default='config/client_config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--test-mode', '-t',
        action='store_true',
        help='Run in test mode with simulated messages'
    )
    
    parser.add_argument(
        '--serial-test', '-s',
        action='store_true',
        help='Test serial reception only (no LLM processing)'
    )
    
    parser.add_argument(
        '--port', '-p',
        help='Override serial port (e.g., /dev/ttyUSB0)'
    )
    
    parser.add_argument(
        '--baudrate', '-b',
        type=int,
        help='Override baudrate (e.g., 9600)'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Override log level'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output (DEBUG level)'
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = args.config
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        print("Creating default configuration...")
        
        # Create default config directory
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Create basic config
        default_config = {
            'serial': {'port': '/dev/ttyUSB0', 'baudrate': 9600},
            'tinyllm': {'interface_type': 'mock'},
            'logging': {'level': 'INFO', 'console': True}
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
            
        print(f"Default configuration created at {config_path}")
        print("Please edit the configuration file and run again.")
        sys.exit(1)
        
    try:
        # Initialize client
        client = TinyLLMSerialClient(config_path, args.test_mode)
        
        # Apply command line overrides
        if args.port:
            client.config['serial']['port'] = args.port
        if args.baudrate:
            client.config['serial']['baudrate'] = args.baudrate
        if args.log_level:
            client.config['logging']['level'] = args.log_level
        if args.verbose:
            client.config['logging']['level'] = 'DEBUG'
            
        # Run appropriate mode
        if args.test_mode:
            client.run_test_mode()
        elif args.serial_test:
            client.run_serial_test_mode()
        else:
            client.run()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()