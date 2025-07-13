#!/usr/bin/env python3
"""
Test script for Ollama integration on Raspberry Pi
"""

import requests
import json
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_interface import LLMManager
from logger import LoggerSetup

def test_ollama_direct():
    """Test Ollama API directly"""
    print("🧪 Testing Ollama API directly...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:11434/", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama not responding")
            return False
            
        # Test model list
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"📋 Available models: {[m.get('name') for m in models]}")
            
            # Check if tinyllama is available
            has_tinyllama = any('tinyllama' in m.get('name', '') for m in models)
            if has_tinyllama:
                print("✅ TinyLlama model found")
            else:
                print("❌ TinyLlama model not found")
                print("💡 Run: ollama pull tinyllama")
                return False
        else:
            print("❌ Could not list models")
            return False
            
        # Test generation
        print("🎯 Testing text generation...")
        payload = {
            "model": "tinyllama",
            "prompt": "Hello from Raspberry Pi!",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 50
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get('response', '')
            print(f"✅ Generated response: {generated_text[:100]}...")
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("💡 Start with: sudo systemctl start ollama")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_llm_manager():
    """Test our LLM manager integration"""
    print("\n🔧 Testing LLM Manager integration...")
    
    # Setup logging
    LoggerSetup.setup_logging(console_level="INFO")
    
    # Configure for Ollama
    config = {
        'interface_type': 'api',
        'api_endpoint': 'http://localhost:11434/api/generate',
        'model': 'tinyllama',
        'timeout': 30,
        'max_retries': 2,
        'max_tokens': 50,
        'temperature': 0.7
    }
    
    try:
        llm_manager = LLMManager(config)
        
        # Test availability
        if llm_manager.is_available():
            print("✅ LLM Manager reports Ollama is available")
        else:
            print("❌ LLM Manager cannot reach Ollama")
            return False
            
        # Test message processing
        test_prompts = [
            "Hello from ARM assembly!",
            "What is the weather like?",
            "Process this serial message: TEST MESSAGE FROM ACORN SYSTEM"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📤 Test {i}: '{prompt}'")
            start_time = time.time()
            
            response = llm_manager.process_message(prompt)
            elapsed = time.time() - start_time
            
            if response:
                print(f"✅ Response ({elapsed:.2f}s): {response[:100]}...")
            else:
                print(f"❌ No response after {elapsed:.2f}s")
                
        # Print statistics
        stats = llm_manager.get_stats()
        print(f"\n📊 Statistics:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Successful: {stats['successful_requests']}")
        print(f"  Failed: {stats['failed_requests']}")
        print(f"  Avg response time: {stats.get('average_response_time', 0):.2f}s")
        
        return stats['successful_requests'] > 0
        
    except Exception as e:
        print(f"❌ LLM Manager error: {e}")
        return False

def test_integration():
    """Test full serial client integration"""
    print("\n🔗 Testing full integration...")
    
    try:
        # Import main client
        from serial_client import SerialClient
        from message_processor import MessageProcessor
        
        # Test message processing pipeline
        processor = MessageProcessor()
        
        config = {
            'interface_type': 'api',
            'api_endpoint': 'http://localhost:11434/api/generate',
            'model': 'tinyllama',
            'timeout': 30,
            'max_tokens': 50
        }
        
        llm_manager = LLMManager(config)
        
        # Simulate serial messages
        test_messages = [
            "TEST MESSAGE FROM ACORN SYSTEM",
            "Hello from ARM assembly on Raspberry Pi",
            "Custom message with data: 12345"
        ]
        
        for msg in test_messages:
            print(f"\n📥 Processing: '{msg}'")
            
            # Process message
            processed = processor.process(msg)
            if not processed:
                print("❌ Message rejected by processor")
                continue
                
            print(f"✅ Processed: '{processed['cleaned']}'")
            
            # Format for LLM
            llm_input = processor.format_message_for_llm(processed)
            
            # Send to LLM
            response = llm_manager.process_message(llm_input)
            if response:
                print(f"🤖 LLM Response: {response[:100]}...")
            else:
                print("❌ LLM failed")
                
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🍓 TinyLLM Raspberry Pi Integration Test")
    print("=" * 50)
    
    tests = [
        ("Direct Ollama API", test_ollama_direct),
        ("LLM Manager", test_llm_manager),
        ("Full Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! TinyLLM is ready for Raspberry Pi.")
        print("\n🚀 Next steps:")
        print("  1. Run: python3 main.py --config config/rpi_config.yaml --test-mode")
        print("  2. Test serial connection: python3 main.py --serial-test")
        print("  3. Go live: python3 main.py --config config/rpi_config.yaml")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure Ollama is running: sudo systemctl status ollama")
        print("  2. Pull the model: ollama pull tinyllama")
        print("  3. Check logs: sudo journalctl -u ollama")

if __name__ == '__main__':
    main()