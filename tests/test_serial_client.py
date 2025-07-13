#!/usr/bin/env python3
"""Test script for serial client functionality"""

import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from serial_client import SerialClient
from message_processor import MessageProcessor
from llm_interface import LLMManager
from logger import LoggerSetup


def test_message_processor():
    """Test message processing functionality"""
    print("Testing Message Processor...")
    
    processor = MessageProcessor()
    
    test_messages = [
        "TEST MESSAGE FROM ACORN SYSTEM",
        "  TEST MESSAGE FROM ACORN SYSTEM\n",
        "Custom message with special chars: !@#$%",
        "",  # Empty message
        "A" * 600,  # Too long
        "   \n\r   ",  # Whitespace only
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\nTest {i}: '{msg[:50]}{'...' if len(msg) > 50 else ''}'")
        result = processor.process(msg)
        if result:
            print(f"  ✓ Valid - Type: {result['type']}, Length: {result['length']}")
        else:
            print(f"  ✗ Invalid message")
            
    print(f"\nProcessor Stats: {processor.get_stats()}")


def test_llm_interface():
    """Test LLM interface functionality"""
    print("\nTesting LLM Interface...")
    
    # Test with mock interface
    config = {
        'interface_type': 'mock',
        'timeout': 5,
        'max_retries': 2
    }
    
    llm_manager = LLMManager(config)
    
    test_prompts = [
        "TEST MESSAGE FROM ACORN SYSTEM",
        "Hello from ARM assembly!",
        "Process this custom message",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nLLM Test {i}: '{prompt}'")
        response = llm_manager.process_message(prompt)
        if response:
            print(f"  ✓ Response: {response}")
        else:
            print(f"  ✗ No response")
            
    print(f"\nLLM Stats: {llm_manager.get_stats()}")


def test_integration():
    """Test integration between components"""
    print("\nTesting Integration...")
    
    # Setup logging
    logger = LoggerSetup.setup_logging(console_level="INFO", console_enabled=True)
    
    # Setup components
    processor = MessageProcessor()
    llm_manager = LLMManager({'interface_type': 'mock'})
    
    def process_pipeline(raw_message):
        """Test processing pipeline"""
        print(f"\nProcessing: '{raw_message}'")
        
        # Process message
        processed = processor.process(raw_message)
        if not processed:
            print("  ✗ Message rejected")
            return
            
        print(f"  ✓ Processed: '{processed['cleaned']}'")
        
        # Format for LLM
        llm_input = processor.format_message_for_llm(processed)
        print(f"  → LLM Input: '{llm_input}'")
        
        # Get LLM response
        response = llm_manager.process_message(llm_input)
        if response:
            print(f"  ✓ LLM Response: '{response}'")
        else:
            print(f"  ✗ LLM failed")
            
    # Test pipeline
    test_messages = [
        "TEST MESSAGE FROM ACORN SYSTEM",
        "Custom ARM message with data",
        "   Messy message with spaces   \n\r",
    ]
    
    for msg in test_messages:
        process_pipeline(msg)
        
    print(f"\nFinal Stats:")
    print(f"  Processor: {processor.get_stats()}")
    print(f"  LLM: {llm_manager.get_stats()}")


def main():
    """Run all tests"""
    print("="*60)
    print("TinyLLM Serial Client - Component Tests")
    print("="*60)
    
    try:
        test_message_processor()
        test_llm_interface()
        test_integration()
        
        print("\n" + "="*60)
        print("All tests completed successfully! 🎉")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()