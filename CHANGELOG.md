# Changelog

All notable changes to the ArmGPT-server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-07-13

### ⚠️ Issue Identified - Serial Echo Feedback Loop

#### Problem Description
During testing with bidirectional serial communication, a feedback loop was discovered where the Python client receives its own transmitted messages back through the serial port. This creates an infinite loop where:

1. ARM sender sends initial message to Python client
2. Python client processes message and sends AI response back via serial
3. **PROBLEM**: The sent AI response is immediately received back on the same serial port
4. Python client treats the echoed message as new input and forwards it to LLM again
5. This creates an endless conversation loop between the AI and itself

#### Evidence from Logs
- Every sent message appears as received within milliseconds
- "AI:" prefixes accumulate in messages: `"AI: AI: User: ..."`
- Even separator strings like `"---"` get processed as messages
- System processes 10+ messages in rapid succession, all variations of the same echoed content

#### Root Cause Analysis
The serial port appears to be configured in a loopback mode where:
- TX (transmit) and RX (receive) are physically connected, OR
- The ARM device is echoing back everything it receives, OR
- Both devices are connected to the same serial endpoints

#### Proposed Solution: Echo Detection
Implement message echo detection in the Python client to filter out recently sent messages:

```python
def _is_echo_message(self, received_message):
    """Check if received message is an echo of recently sent message"""
    # Check against recently sent messages
    # Ignore messages that start with "AI:" prefix
    # Ignore separator strings like "---"
```

#### ❓ **Question for Review**
**Is echo detection the right approach, or should we focus on preventing the feedback loop at the hardware/protocol level?**

Alternative approaches to consider:
1. **Protocol-level solution**: Implement message direction indicators or handshaking
2. **Hardware verification**: Ensure serial cable/connection isn't creating physical loopback
3. **Configuration check**: Verify ARM device isn't configured to echo responses
4. **Separate channels**: Use different serial ports or communication methods for TX/RX

The echo detection approach treats the symptom but may not address the root cause. Should we investigate the hardware/protocol configuration first?

---

## [1.0.0] - 2025-01-13

### Added - Complete TinyLLM Serial Client Implementation

#### 🎯 Core Components
- **Serial Client Module** (`src/serial_client.py`)
  - USB serial communication with ARM assembly sender
  - Auto-reconnection and error recovery
  - Threaded message reading with proper signal handling
  - Configurable timeouts and retry logic

- **Message Processor** (`src/message_processor.py`)
  - Message cleaning and validation
  - Type classification (test vs custom messages)
  - Content filtering and safety checks
  - Comprehensive statistics tracking

- **LLM Interface** (`src/llm_interface.py`)
  - Modular LLM integration supporting multiple backends
  - Ollama API integration optimized for TinyLlama
  - Command-line and HTTP API support
  - Mock interface for testing
  - Automatic retry logic with performance monitoring

- **Logging System** (`src/logger.py`)
  - Colored console output with component-based prefixes
  - File logging with configurable levels
  - Real-time performance statistics
  - Transaction logging for audit trails

#### 🍓 Raspberry Pi Optimization
- **Ollama Integration**
  - TinyLlama model (1.1B parameters) for CPU-only inference
  - Raspberry Pi 4 optimized configuration
  - Memory and performance limits
  - Temperature and resource monitoring

- **Automated Setup** (`install_tinyllm_rpi.sh`)
  - One-script Ollama installation on ARM64
  - Automatic TinyLlama model download
  - Python dependencies installation
  - User permissions configuration (dialout group)
  - System service setup

#### ⚙️ Configuration Management
- **Default Configuration** (`config/client_config.yaml`)
  - Mock interface for development and testing
  - Configurable serial port settings
  - Logging and performance parameters

- **Raspberry Pi Configuration** (`config/rpi_config.yaml`)
  - Ollama API endpoint configuration
  - Pi-optimized timeouts and response limits
  - Hardware monitoring settings
  - Memory and CPU usage limits

#### 🧪 Testing and Validation
- **Component Tests** (`tests/test_serial_client.py`)
  - Unit tests for all core modules
  - Message processing validation
  - Integration pipeline testing

- **Ollama Integration Tests** (`test_ollama.py`)
  - Direct Ollama API testing
  - Model availability verification
  - Performance benchmarking
  - Full pipeline validation

- **Multiple Test Modes**
  - Mock mode for development
  - Serial-only testing for hardware validation
  - Full integration testing with actual LLM

#### 📚 Documentation
- **Main README** (`README.md`)
  - Project overview and architecture
  - Quick start guide with Ollama focus
  - Configuration examples
  - Comprehensive troubleshooting guide

- **Raspberry Pi Guide** (`README_RASPBERRY_PI.md`)
  - Complete Pi setup instructions
  - Hardware requirements and optimization
  - Performance expectations and monitoring
  - Production deployment guide

#### 🎛️ Main Application
- **Entry Point** (`main.py`)
  - CLI interface with comprehensive argument parsing
  - Multiple operation modes (normal, test, serial-only)
  - Configuration loading and validation
  - Graceful shutdown handling
  - Real-time statistics monitoring

#### 🔧 Development Tools
- **Git Configuration** (`.gitignore`)
  - Python cache files exclusion
  - Log files and temporary files filtering
  - IDE and OS-specific file exclusion

- **Dependencies** (`requirements.txt`)
  - PySerial for serial communication
  - Colorama for colored terminal output
  - PyYAML for configuration parsing
  - Requests for HTTP API calls

### Features

#### 📡 Serial Communication
- **9600 baud USB serial** communication matching ARM assembly specs
- **Automatic device detection** and reconnection
- **Robust error handling** with hardware buffer management
- **Message validation** and type classification

#### 🤖 AI Integration
- **Ollama API integration** with TinyLlama model
- **CPU-optimized inference** for Raspberry Pi
- **Configurable response limits** for performance
- **Automatic retry logic** with failure recovery

#### 📊 Monitoring and Logging
- **Real-time colored console** output with component prefixes
- **Comprehensive file logging** with configurable levels
- **Performance statistics** tracking
- **Hardware monitoring** (temperature, memory, CPU)

#### 🔒 Security and Reliability
- **Input validation** preventing malformed messages
- **Configurable message length** limits
- **Safe error handling** preventing crashes
- **No code execution** from serial input

### Technical Specifications

#### System Requirements
- **Raspberry Pi 4** (4GB RAM minimum, 8GB recommended)
- **64-bit Raspberry Pi OS** (required for Ollama)
- **USB-to-USB serial cable** for Pi-to-Pi communication
- **10GB+ free disk space** for model storage

#### Performance Benchmarks
- **Response Time**: 3-8 seconds on Raspberry Pi 4
- **Memory Usage**: 1-3GB during inference
- **CPU Usage**: 20-80% during generation
- **Serial Latency**: <100ms for message reception

#### Compatibility
- **ARM Assembly Sender**: Full compatibility with existing sender
- **Message Formats**: ASCII text with newline terminators
- **Baud Rates**: 9600 baud (configurable)
- **Hardware**: USB serial devices (/dev/ttyUSB*, /dev/ttyACM*)

### Architecture

#### Data Flow
```
ARM Assembly → Serial Port → Python Client → Ollama/TinyLlama → AI Response
```

#### Component Structure
```
src/
├── serial_client.py      # Serial communication handler
├── message_processor.py  # Message cleaning and validation
├── llm_interface.py      # TinyLLM/Ollama integration
└── logger.py            # Logging and monitoring system
```

#### Configuration Hierarchy
```
CLI Arguments → YAML Config → Default Values
```

### Deployment

#### Development Environment
- Mock LLM interface for testing without hardware
- Component unit tests for isolated validation
- Integration tests with simulated data

#### Production Environment
- Ollama with TinyLlama on Raspberry Pi
- Systemd service for automatic startup
- Log rotation and monitoring
- Performance optimization for ARM hardware

### Known Issues
- **GPU Warning**: Ollama shows GPU warning on Pi (expected, CPU-only mode works fine)
- **PyYAML Dependency**: May need manual installation on some Pi configurations
- **Group Permissions**: User logout/login required after dialout group addition

### Migration Notes
- **Project Structure**: Flattened from nested `tinyllm-serial-client/` directory
- **Configuration**: Default config uses mock interface, Pi config uses Ollama
- **Commands**: All examples updated to use `python3` and Pi-specific configs

### Contributors
- Implementation and documentation created with AI assistance
- Optimized for Raspberry Pi ARM architecture
- Tested on Raspberry Pi 4 with USB serial communication

---

## Version History

### [1.0.0] - 2025-01-13
- Initial release with complete TinyLLM Serial Client implementation
- Ollama/TinyLlama integration for Raspberry Pi
- Comprehensive documentation and setup automation
- Full ARM assembly → AI processing pipeline