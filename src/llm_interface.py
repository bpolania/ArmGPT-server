import subprocess
import requests
import json
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class LLMInterface(ABC):
    """Abstract base class for LLM interfaces"""
    
    @abstractmethod
    def generate(self, prompt: str) -> Optional[str]:
        """Generate response from LLM"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM is available"""
        pass


class CommandLineLLM(LLMInterface):
    """LLM interface using command line tool"""
    
    def __init__(self, config: Dict[str, Any]):
        self.command = config.get('command', 'tinyllm')
        self.timeout = config.get('timeout', 30)
        self.logger = logging.getLogger(__name__)
        
    def generate(self, prompt: str) -> Optional[str]:
        """Generate response using command line tool
        
        Args:
            prompt: Input prompt for LLM
            
        Returns:
            Generated response or None if failed
        """
        try:
            # Prepare command
            cmd = [self.command, prompt]
            
            self.logger.debug(f"Executing LLM command: {' '.join(cmd)}")
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                self.logger.debug(f"LLM response: {response}")
                return response
            else:
                self.logger.error(f"LLM command failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"LLM command timed out after {self.timeout} seconds")
            return None
        except FileNotFoundError:
            self.logger.error(f"LLM command '{self.command}' not found")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error calling LLM: {e}")
            return None
            
    def is_available(self) -> bool:
        """Check if command line tool is available"""
        try:
            result = subprocess.run(
                [self.command, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class APILLM(LLMInterface):
    """LLM interface using HTTP API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.endpoint = config.get('api_endpoint', 'http://localhost:11434/api/generate')
        self.timeout = config.get('timeout', 30)
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.logger = logging.getLogger(__name__)
        
    def generate(self, prompt: str) -> Optional[str]:
        """Generate response using HTTP API
        
        Args:
            prompt: Input prompt for LLM
            
        Returns:
            Generated response or None if failed
        """
        try:
            # Prepare request payload for Ollama API
            payload = {
                'model': self.config.get('model', 'tinyllama'),
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': self.config.get('temperature', 0.7),
                    'num_predict': self.config.get('max_tokens', 100)
                }
            }
            
            self.logger.debug(f"Sending request to LLM API: {self.endpoint}")
            self.logger.debug(f"Payload: {payload}")
            
            # Make API request
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # Ollama returns response in 'response' field
                generated_text = data.get('response', '')
                self.logger.debug(f"LLM response: {generated_text}")
                return generated_text.strip()
            else:
                self.logger.error(f"LLM API error: {response.status_code} - {response.text}")
                return None
                
        except requests.Timeout:
            self.logger.error(f"LLM API request timed out after {self.timeout} seconds")
            return None
        except requests.ConnectionError:
            self.logger.error(f"Failed to connect to LLM API at {self.endpoint}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error calling LLM API: {e}")
            return None
            
    def is_available(self) -> bool:
        """Check if Ollama API is available"""
        try:
            # Check Ollama root endpoint
            health_endpoint = self.endpoint.replace('/api/generate', '/')
            response = requests.get(health_endpoint, timeout=5)
            
            # Ollama returns "Ollama is running" message
            if response.status_code == 200:
                # Also check if our model is available
                model_endpoint = self.endpoint.replace('/api/generate', '/api/tags')
                model_response = requests.get(model_endpoint, timeout=5)
                if model_response.status_code == 200:
                    models = model_response.json().get('models', [])
                    model_name = self.config.get('model', 'tinyllama')
                    return any(model.get('name', '').startswith(model_name) for model in models)
            return False
        except:
            return False


class MockLLM(LLMInterface):
    """Mock LLM interface for testing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.responses = [
            "This is a mock response to your message.",
            "I understand you sent: {prompt}",
            "Mock LLM processed your input successfully.",
            "Response generated for testing purposes."
        ]
        self.response_index = 0
        self.logger = logging.getLogger(__name__)
        
    def generate(self, prompt: str) -> Optional[str]:
        """Generate mock response
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        # Simulate processing delay
        time.sleep(0.5)
        
        # Generate response
        response = self.responses[self.response_index].format(prompt=prompt)
        self.response_index = (self.response_index + 1) % len(self.responses)
        
        self.logger.debug(f"Mock LLM response: {response}")
        return response
        
    def is_available(self) -> bool:
        """Mock LLM is always available"""
        return True


class LLMManager:
    """Manager class for LLM interfaces with retry logic"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.interface_type = config.get('interface_type', 'mock')
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.logger = logging.getLogger(__name__)
        
        # Initialize appropriate interface
        self.llm = self._create_interface()
        
        # Performance tracking
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0,
            'average_response_time': 0
        }
        
    def _create_interface(self) -> LLMInterface:
        """Create appropriate LLM interface based on config"""
        if self.interface_type == 'command':
            self.logger.info("Using command line LLM interface")
            return CommandLineLLM(self.config)
        elif self.interface_type == 'api':
            self.logger.info("Using API LLM interface")
            return APILLM(self.config)
        else:
            self.logger.info("Using mock LLM interface for testing")
            return MockLLM(self.config)
            
    def process_message(self, message: str) -> Optional[str]:
        """Process message through LLM with retry logic
        
        Args:
            message: Input message
            
        Returns:
            LLM response or None if failed
        """
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"LLM: Forwarding to TinyLLM (attempt {attempt + 1}/{self.max_retries})...")
                
                response = self.llm.generate(message)
                
                if response:
                    # Success
                    elapsed_time = time.time() - start_time
                    self.stats['successful_requests'] += 1
                    self.stats['total_response_time'] += elapsed_time
                    self.stats['average_response_time'] = (
                        self.stats['total_response_time'] / self.stats['successful_requests']
                    )
                    
                    self.logger.info(f"LLM: Response received ({elapsed_time:.3f}s): \"{response}\"")
                    return response
                    
                # Failed, retry if attempts remain
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"LLM request failed, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
        # All attempts failed
        self.stats['failed_requests'] += 1
        self.logger.error("All LLM request attempts failed")
        return None
        
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self.llm.is_available()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get LLM processing statistics"""
        return self.stats.copy()
        
    def reset_stats(self):
        """Reset statistics"""
        for key in self.stats:
            self.stats[key] = 0
        self.logger.info("LLM statistics reset")