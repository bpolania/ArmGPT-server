import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime


class MessageProcessor:
    """Processes and validates messages received from serial port"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize message processor
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.max_message_length = self.config.get('max_message_length', 512)
        
        # Statistics tracking
        self.stats = {
            'total_messages': 0,
            'valid_messages': 0,
            'invalid_messages': 0,
            'test_messages': 0,
            'custom_messages': 0,
            'empty_messages': 0,
            'oversized_messages': 0
        }
        
    def process(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """Process and validate a raw message
        
        Args:
            raw_message: Raw message string from serial port
            
        Returns:
            Dict containing processed message info or None if invalid
        """
        self.stats['total_messages'] += 1
        
        # Initial cleaning
        message = self._clean_message(raw_message)
        
        # Validate message
        validation_result = self._validate_message(message)
        if not validation_result['valid']:
            self.stats['invalid_messages'] += 1
            self.logger.warning(f"Invalid message: {validation_result['reason']}")
            return None
            
        self.stats['valid_messages'] += 1
        
        # Classify message type
        message_type = self._classify_message(message)
        
        # Update type-specific stats
        if message_type == 'test':
            self.stats['test_messages'] += 1
        elif message_type == 'custom':
            self.stats['custom_messages'] += 1
            
        # Create processed message dictionary
        processed = {
            'raw': raw_message,
            'cleaned': message,
            'type': message_type,
            'length': len(message),
            'timestamp': datetime.now().isoformat(),
            'valid': True
        }
        
        self.logger.debug(f"Processed message: {processed}")
        return processed
        
    def _clean_message(self, raw_message: str) -> str:
        """Clean and normalize message
        
        Args:
            raw_message: Raw message string
            
        Returns:
            Cleaned message string
        """
        # Remove leading/trailing whitespace
        message = raw_message.strip()
        
        # Remove any control characters except newlines (which we'll handle separately)
        message = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', message)
        
        # Replace multiple spaces with single space
        message = re.sub(r'\s+', ' ', message)
        
        # Remove trailing newlines/carriage returns
        message = message.rstrip('\r\n')
        
        return message
        
    def _validate_message(self, message: str) -> Dict[str, Any]:
        """Validate a cleaned message
        
        Args:
            message: Cleaned message string
            
        Returns:
            Dict with 'valid' bool and 'reason' if invalid
        """
        # Check if empty
        if not message:
            self.stats['empty_messages'] += 1
            return {'valid': False, 'reason': 'Empty message'}
            
        # Check length
        if len(message) > self.max_message_length:
            self.stats['oversized_messages'] += 1
            return {'valid': False, 'reason': f'Message exceeds max length ({self.max_message_length})'}
            
        # Check for minimum meaningful content (at least 3 characters)
        if len(message) < 3:
            return {'valid': False, 'reason': 'Message too short'}
            
        # Check if message contains only whitespace
        if message.isspace():
            return {'valid': False, 'reason': 'Message contains only whitespace'}
            
        # Check for suspicious patterns (potential corruption)
        if self._has_suspicious_patterns(message):
            return {'valid': False, 'reason': 'Message contains suspicious patterns'}
            
        return {'valid': True}
        
    def _has_suspicious_patterns(self, message: str) -> bool:
        """Check for patterns that might indicate corruption
        
        Args:
            message: Message to check
            
        Returns:
            bool: True if suspicious patterns found
        """
        # Check for excessive non-ASCII characters
        non_ascii_count = sum(1 for c in message if ord(c) > 127)
        if non_ascii_count > len(message) * 0.2:  # More than 20% non-ASCII
            return True
            
        # Check for null bytes (shouldn't happen after cleaning, but double-check)
        if '\x00' in message:
            return True
            
        # Check for excessive repetition (might indicate stuck buffer)
        if len(message) > 10:
            # Check if message is just repeated characters
            if len(set(message)) < 3:
                return True
                
        return False
        
    def _classify_message(self, message: str) -> str:
        """Classify message type based on content
        
        Args:
            message: Cleaned message
            
        Returns:
            Message type string
        """
        # Check for known test message
        if message == "TEST MESSAGE FROM ACORN SYSTEM":
            return 'test'
            
        # Check for patterns that might indicate system messages
        system_patterns = [
            r'^TEST\s+',
            r'^ACORN\s+',
            r'^SYSTEM\s+',
            r'^\[.*\]$'  # Messages in brackets
        ]
        
        for pattern in system_patterns:
            if re.match(pattern, message, re.IGNORECASE):
                return 'system'
                
        # Default to custom message
        return 'custom'
        
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics
        
        Returns:
            Dictionary of statistics
        """
        stats_copy = self.stats.copy()
        
        # Calculate percentages
        if stats_copy['total_messages'] > 0:
            stats_copy['valid_percentage'] = (stats_copy['valid_messages'] / stats_copy['total_messages']) * 100
            stats_copy['test_percentage'] = (stats_copy['test_messages'] / stats_copy['total_messages']) * 100
            stats_copy['custom_percentage'] = (stats_copy['custom_messages'] / stats_copy['total_messages']) * 100
        else:
            stats_copy['valid_percentage'] = 0
            stats_copy['test_percentage'] = 0
            stats_copy['custom_percentage'] = 0
            
        return stats_copy
        
    def reset_stats(self):
        """Reset statistics counters"""
        for key in self.stats:
            self.stats[key] = 0
        self.logger.info("Message processor statistics reset")
        
    def format_message_for_llm(self, processed_message: Dict[str, Any]) -> str:
        """Format processed message for LLM consumption
        
        Args:
            processed_message: Processed message dictionary
            
        Returns:
            Formatted string for LLM
        """
        # Extract the cleaned message
        message = processed_message.get('cleaned', '')
        message_type = processed_message.get('type', 'unknown')
        
        # Add context based on message type
        if message_type == 'test':
            # For test messages, we might want to add context
            return f"[ARM System Test] {message}"
        elif message_type == 'system':
            return f"[ARM System Message] {message}"
        else:
            # For custom messages, return as-is
            return message
            
    def batch_process(self, messages: List[str]) -> List[Dict[str, Any]]:
        """Process multiple messages at once
        
        Args:
            messages: List of raw message strings
            
        Returns:
            List of processed message dictionaries
        """
        processed = []
        for message in messages:
            result = self.process(message)
            if result:
                processed.append(result)
                
        return processed