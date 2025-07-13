# Changelog

All notable changes to the ArmGPT-server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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