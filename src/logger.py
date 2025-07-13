import logging
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style
from typing import Optional


# Initialize colorama for cross-platform colored output
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console"""
    
    # Color mappings for different log levels
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }
    
    # Component color mappings
    COMPONENT_COLORS = {
        'SERIAL': Fore.BLUE,
        'PROCESS': Fore.MAGENTA,
        'LLM': Fore.CYAN,
        'LOG': Fore.WHITE,
        'SYSTEM': Fore.YELLOW
    }
    
    def format(self, record):
        # Get the original formatted message
        original = super().format(record)
        
        # Get color for log level
        level_color = self.COLORS.get(record.levelname, Fore.WHITE)
        
        # Extract component from message if present
        component = None
        component_color = Fore.WHITE
        
        for comp, color in self.COMPONENT_COLORS.items():
            if record.getMessage().startswith(f"{comp}:"):
                component = comp
                component_color = color
                break
                
        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Build colored output
        if component:
            # Message has component prefix
            msg_parts = record.getMessage().split(':', 1)
            if len(msg_parts) == 2:
                colored_output = (
                    f"{Fore.WHITE}[{timestamp}] "
                    f"{level_color}{record.levelname:<8} "
                    f"{component_color}{component}:{Style.RESET_ALL} "
                    f"{msg_parts[1].strip()}"
                )
            else:
                colored_output = (
                    f"{Fore.WHITE}[{timestamp}] "
                    f"{level_color}{record.levelname:<8} "
                    f"{Style.RESET_ALL}{record.getMessage()}"
                )
        else:
            # Standard message
            colored_output = (
                f"{Fore.WHITE}[{timestamp}] "
                f"{level_color}{record.levelname:<8} "
                f"{Style.RESET_ALL}{record.getMessage()}"
            )
            
        return colored_output


class LoggerSetup:
    """Setup and configure logging for the application"""
    
    @staticmethod
    def setup_logging(
        console_level: str = "INFO",
        file_level: str = "DEBUG",
        log_file: Optional[str] = None,
        console_enabled: bool = True
    ) -> logging.Logger:
        """Setup logging configuration
        
        Args:
            console_level: Log level for console output
            file_level: Log level for file output
            log_file: Path to log file
            console_enabled: Whether to enable console logging
            
        Returns:
            Configured root logger
        """
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        root_logger.handlers = []
        
        # Console handler with colored output
        if console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, console_level.upper()))
            
            # Use colored formatter for console
            console_formatter = ColoredFormatter(
                '%(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with detailed output
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, file_level.upper()))
            
            # Use standard formatter for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
        return root_logger
        
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance with the given name
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


# Utility functions for consistent logging patterns
def log_serial_event(logger: logging.Logger, message: str, level: str = "INFO"):
    """Log a serial-related event with consistent formatting"""
    getattr(logger, level.lower())(f"SERIAL: {message}")


def log_process_event(logger: logging.Logger, message: str, level: str = "INFO"):
    """Log a processing-related event with consistent formatting"""
    getattr(logger, level.lower())(f"PROCESS: {message}")


def log_llm_event(logger: logging.Logger, message: str, level: str = "INFO"):
    """Log an LLM-related event with consistent formatting"""
    getattr(logger, level.lower())(f"LLM: {message}")


def log_system_event(logger: logging.Logger, message: str, level: str = "INFO"):
    """Log a system-related event with consistent formatting"""
    getattr(logger, level.lower())(f"SYSTEM: {message}")


# Example output formats for reference
def print_log_examples():
    """Print example log outputs to show formatting"""
    print("\n" + "="*60)
    print("Example Log Output Formats:")
    print("="*60 + "\n")
    
    # Simulate different log messages
    examples = [
        (Fore.WHITE + "[12:34:56.789] " + Fore.GREEN + "INFO     " + 
         Fore.BLUE + "SERIAL:" + Style.RESET_ALL + " Waiting for data..."),
        
        (Fore.WHITE + "[12:34:57.123] " + Fore.GREEN + "INFO     " + 
         Fore.BLUE + "SERIAL:" + Style.RESET_ALL + " Received: \"TEST MESSAGE FROM ACORN SYSTEM\""),
        
        (Fore.WHITE + "[12:34:57.124] " + Fore.GREEN + "INFO     " + 
         Fore.MAGENTA + "PROCESS:" + Style.RESET_ALL + " Cleaned message: \"TEST MESSAGE FROM ACORN SYSTEM\""),
        
        (Fore.WHITE + "[12:34:57.125] " + Fore.GREEN + "INFO     " + 
         Fore.CYAN + "LLM:" + Style.RESET_ALL + " Forwarding to TinyLLM..."),
        
        (Fore.WHITE + "[12:34:58.456] " + Fore.GREEN + "INFO     " + 
         Fore.CYAN + "LLM:" + Style.RESET_ALL + " Response received (1.331s): \"[AI response here]\""),
        
        (Fore.WHITE + "[12:34:58.457] " + Fore.GREEN + "INFO     " + 
         Fore.WHITE + "LOG:" + Style.RESET_ALL + " Transaction logged to file"),
        
        (Fore.WHITE + "[12:35:00.000] " + Fore.RED + "ERROR    " + 
         Style.RESET_ALL + "Serial port /dev/ttyUSB0 not found"),
        
        (Fore.WHITE + "[12:35:00.001] " + Fore.YELLOW + "WARNING  " + 
         Fore.YELLOW + "SYSTEM:" + Style.RESET_ALL + " TinyLLM timeout after 30 seconds")
    ]
    
    for example in examples:
        print(example)
    
    print("\n" + "="*60 + "\n")